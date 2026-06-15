# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import get_datetime, now_datetime


@frappe.whitelist()
def execute_blast(campaign_activity):
    """Execute omni-channel blast for a campaign activity"""

    activity = frappe.get_doc("Campaign Activity", campaign_activity)

    if activity.status != "Scheduled":
        frappe.throw(_("Activity must be in Scheduled status to execute"))

    # Check if it's time to execute
    if activity.scheduled_time and get_datetime(activity.scheduled_time) > now_datetime():
        return {"message": "Not yet time to execute"}

    # Update status
    activity.status = "Running"
    activity.save()
    frappe.db.commit()

    results = {}
    channels = activity.activity_type.split("\n") if activity.activity_type else []

    for channel in channels:
        try:
            if channel == "Email":
                results[channel] = _execute_email_blast(activity)
            elif channel == "WhatsApp":
                results[channel] = _execute_whatsapp_blast(activity)
            elif channel == "SMS":
                results[channel] = _execute_sms_blast(activity)
            elif channel == "Push Notification":
                results[channel] = _execute_push_blast(activity)
            elif channel == "Meta Ads":
                results[channel] = _execute_meta_ads_blast(activity)
            elif channel in ("Facebook", "Instagram", "LinkedIn", "Twitter", "X"):
                results[channel] = _execute_social_post_blast(activity, channel)
            else:
                results[channel] = {"status": "Not Implemented", "count": 0}
        except Exception as e:
            frappe.log_error(f"Blast execution error for {channel}", str(e))
            results[channel] = {"status": "Error", "error": str(e)}

    # Update activity with results
    activity.status = "Completed"
    activity.results = frappe.as_json(results)
    activity.save()
    frappe.db.commit()

    return {"message": "Blast executed successfully", "results": results}


def execute_if_scheduled(doc, method):
    """Hook to auto-execute scheduled blasts"""
    if doc.status == "Scheduled" and doc.scheduled_time:
        if get_datetime(doc.scheduled_time) <= now_datetime():
            try:
                execute_blast(doc.name)
            except Exception as e:
                frappe.log_error("Scheduled blast execution failed", str(e))


def _execute_email_blast(activity):
    """Execute email blast to segment"""

    if not activity.segment:
        return {"status": "Error", "message": "No segment defined"}

    # Get segment recipients
    segment = frappe.get_doc("Marketing Segment", activity.segment)
    recipients = _get_segment_recipients(segment)

    # Get template
    template = _get_template(activity.campaign, "Email")

    if not template:
        return {"status": "Error", "message": "No email template found"}

    sent_count = 0
    for recipient in recipients:
        try:
            frappe.sendmail(
                recipients=[recipient.get("email")],
                subject=template.get("subject"),
                message=template.get("content"),
                reference_doctype="Campaign Activity",
                reference_name=activity.name
            )
            sent_count += 1
        except Exception as e:
            frappe.log_error(f"Email send failed to {recipient.get('email')}", str(e))

    return {"status": "Completed", "sent": sent_count, "total": len(recipients)}


def _execute_whatsapp_blast(activity):
    """Execute WhatsApp blast using frappe_whatsapp app"""
    try:
        # Check if frappe_whatsapp is installed
        if not frappe.db.exists("DocType", "WhatsApp Message"):
            frappe.throw(_("frappe_whatsapp app is not installed"))

        # Check if WhatsApp is enabled
        default_account = frappe.get_cached_value(
            "WhatsApp Settings", "WhatsApp Settings", "default_outgoing_account"
        )
        if not default_account:
            frappe.throw(_("No default WhatsApp account configured"))

        if not activity.segment:
            return {"status": "Error", "message": "No segment defined"}

        segment = frappe.get_doc("Marketing Segment", activity.segment)
        template = _get_template(activity.get("parent"), "WhatsApp")

        if not template:
            frappe.throw(_("WhatsApp template is required for WhatsApp blast"))

        recipients = _get_segment_recipients(segment)

        # Create bulk WhatsApp message if available
        if frappe.db.exists("DocType", "Bulk WhatsApp Message"):
            bulk_message = frappe.new_doc("Bulk WhatsApp Message")
            bulk_message.campaign_reference = activity.get("parent")
            bulk_message.campaign_activity = activity.get("name")
            bulk_message.whatsapp_account = default_account
            bulk_message.use_template = 1

            # Add recipients
            for recipient in recipients:
                mobile = recipient.get("mobile_no") or recipient.get("mobile")
                if mobile:
                    bulk_message.append("recipients", {
                        "mobile_number": mobile,
                        "recipient_name": recipient.get("customer_name") or recipient.get("lead_name"),
                        "recipient_data": frappe.as_json(recipient)
                    })

            bulk_message.insert()
            bulk_message.submit()

            return {
                "status": "Completed",
                "sent": bulk_message.recipient_count,
                "failed": 0,
                "bulk_message": bulk_message.name
            }
        else:
            # Fallback: Create individual messages
            sent = 0
            failed = 0

            for recipient in recipients:
                mobile = recipient.get("mobile_no") or recipient.get("mobile")
                if not mobile:
                    failed += 1
                    continue

                try:
                    wa_message = frappe.new_doc("WhatsApp Message")
                    wa_message.to = mobile
                    wa_message.message_type = "Template"
                    wa_message.whatsapp_account = default_account
                    wa_message.campaign_reference = activity.get("parent")
                    wa_message.flags.custom_ref_doc = recipient
                    wa_message.insert()
                    sent += 1
                except Exception as e:
                    frappe.log_error(f"WhatsApp blast error: {str(e)}", "Marketing Hub WhatsApp")
                    failed += 1

            return {
                "status": "Completed",
                "sent": sent,
                "failed": failed
            }
    except Exception as e:
        frappe.log_error(f"WhatsApp blast execution error: {str(e)}", "Marketing Hub")
        return {"status": "Error", "message": str(e)}


def _execute_sms_blast(activity):
    """Execute SMS blast using Frappe SMS Settings"""
    from frappe.core.doctype.sms_settings.sms_settings import send_sms
    
    if not activity.segment:
        return {"status": "Error", "message": "No segment defined"}

    # Check if SMS gateway is configured
    if not frappe.db.get_single_value("SMS Settings", "sms_gateway_url"):
        return {
            "status": "Error",
            "message": "SMS gateway not configured. Please configure SMS Settings.",
            "count": 0
        }

    segment = frappe.get_doc("Marketing Segment", activity.segment)
    recipients = _get_segment_recipients(segment)

    if not recipients:
        return {"status": "Error", "message": "No recipients found in segment", "count": 0}

    # Get message content
    message = activity.message or activity.content_html or ""
    if not message:
        return {"status": "Error", "message": "No message content provided", "count": 0}

    # Strip HTML tags for SMS (plain text only)
    from frappe.utils import strip_html_tags
    message = strip_html_tags(message)

    # Truncate to 160 characters for standard SMS
    if len(message) > 160:
        message = message[:157] + "..."

    # Collect mobile numbers
    mobile_numbers = []
    for recipient in recipients:
        mobile = recipient.get("mobile_no") or recipient.get("phone")
        if mobile:
            mobile_numbers.append(mobile)

    if not mobile_numbers:
        return {"status": "Error", "message": "No valid mobile numbers found", "count": 0}

    # Send SMS via Frappe SMS gateway
    try:
        send_sms(mobile_numbers, message, success_msg=False)
        
        return {
            "status": "Success",
            "message": f"SMS sent to {len(mobile_numbers)} recipients",
            "count": len(mobile_numbers),
            "channel": "SMS"
        }
    except Exception as e:
        frappe.log_error("SMS Blast Error", str(e))
        return {
            "status": "Error",
            "message": f"SMS sending failed: {str(e)}",
            "count": 0
        }


def _execute_push_blast(activity):
    """Execute push notification blast (stub)"""
    # TODO: Integrate with push notification service

    if not activity.segment:
        return {"status": "Error", "message": "No segment defined"}

    segment = frappe.get_doc("Marketing Segment", activity.segment)
    recipients = _get_segment_recipients(segment)

    # Stub implementation
    return {
        "status": "Stub",
        "message": "Push notification service required",
        "potential_recipients": len(recipients)
    }


def _get_segment_recipients(segment):
    """Get list of recipients from segment"""
    recipients = []

    # Get from Customers if segment has customer filters
    if segment.get("customer_group"):
        customers = frappe.get_all(
            "Customer",
            filters={"customer_group": segment.customer_group},
            fields=["name", "email_id as email", "mobile_no"]
        )
        recipients.extend(customers)

    # Get from Leads if segment has lead filters
    if segment.get("lead_source"):
        leads = frappe.get_all(
            "Lead",
            filters={"source": segment.lead_source},
            fields=["name", "email_id as email", "mobile_no"]
        )
        recipients.extend(leads)

    # Remove duplicates by email
    seen = set()
    unique_recipients = []
    for r in recipients:
        if r.get("email") and r["email"] not in seen:
            seen.add(r["email"])
            unique_recipients.append(r)

    return unique_recipients



def _get_template(campaign, channel_type):
    """Get marketing template for campaign and channel"""
    try:
        template = frappe.get_all(
            "Marketing Template",
            filters={
                "campaign": campaign,
                "channel": channel_type
            },
            fields=["name", "subject", "content"],
            limit=1
        )
        return template[0] if template else None
    except Exception:
        return None

def _execute_meta_ads_blast(activity):
    """Execute Meta Ads campaign creation blast using GenericAdapter"""
    from marketing_hub.utils.social_adapter import publish_to_platform

    if not activity.segment:
        return {"status": "Error", "message": "No segment defined"}

    segment = frappe.get_doc("Marketing Segment", activity.segment)
    recipients = _get_segment_recipients(segment)

    if not recipients:
        return {"status": "Error", "message": "No recipients found in segment"}

    # Check for a linked Social Post for Meta
    social_posts = frappe.get_all(
        "Social Post",
        filters={
            "campaign_activity": activity.name,
            "platform": ["in", ["Meta Ads", "Facebook", "Instagram"]],
            "status": ["not in", ["Published", "Deleted"]]
        },
        pluck="name"
    )

    if not social_posts:
        return {
            "status": "Error",
            "message": "No Meta/Facebook/Instagram Social Posts found for this activity"
        }

    published = 0
    failed = 0
    for post_name in social_posts:
        try:
            post = frappe.get_doc("Social Post", post_name)
            result = publish_to_platform(post)
            if result.get("success"):
                published += 1
            else:
                failed += 1
        except Exception as e:
            frappe.log_error(f"Meta blast post error: {str(e)}", "Omni Blast Meta")
            failed += 1

    return {
        "status": "Completed" if published > 0 else "Error",
        "published": published,
        "failed": failed,
        "potential_recipients": len(recipients)
    }


def _execute_social_post_blast(activity, channel):
    """Execute social media blast for a specific channel via GenericAdapter."""
    from marketing_hub.utils.social_adapter import publish_to_platform

    if not activity.segment:
        return {"status": "Error", "message": "No segment defined"}

    # Find Social Posts for this activity and channel
    social_posts = frappe.get_all(
        "Social Post",
        filters={
            "campaign_activity": activity.name,
            "platform": channel,
            "status": ["not in", ["Published", "Deleted"]]
        },
        pluck="name"
    )

    if not social_posts:
        return {
            "status": "Error",
            "message": f"No {channel} Social Posts found for this activity"
        }

    published = 0
    failed = 0

    for post_name in social_posts:
        try:
            post = frappe.get_doc("Social Post", post_name)
            result = publish_to_platform(post)
            if result.get("success"):
                published += 1
            else:
                failed += 1
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(
                f"Social blast error for {channel} post {post_name}: {str(e)}",
                "Omni Blast Social"
            )
            failed += 1
            frappe.db.rollback()

    return {
        "status": "Completed" if published > 0 else "Error",
        "published": published,
        "failed": failed
    }
