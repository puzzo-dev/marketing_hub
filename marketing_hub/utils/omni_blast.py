# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import now_datetime, get_datetime

@frappe.whitelist()
def execute_blast(campaign_activity):
    """Execute omni-channel blast for a campaign activity"""

    activity = frappe.get_doc("Campaign Activity", campaign_activity)

    if activity.status not in ("Scheduled", "In Progress"):
        frappe.throw(_("Activity must be in Scheduled or In Progress status to execute"))

    # Check if it's time to execute
    if activity.scheduled_date and get_datetime(activity.scheduled_date) > now_datetime():
        return {"message": "Not yet time to execute"}

    # Update status
    activity.status = "In Progress"
    activity.save()
    frappe.db.commit()

    results = {}
    channels = [ch.strip() for ch in (activity.channels or "").split(",") if ch.strip()]

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
        except (frappe.ValidationError, frappe.DoesNotExistError) as e:
            frappe.log_error(f"Blast execution error for {channel}", str(e))
            results[channel] = {"status": "Error", "error": str(e)}

    # Update activity with results
    activity.status = "Completed"
    activity.results = frappe.as_json(results)
    activity.save()
    frappe.db.commit()

    return {"message": "Blast executed successfully", "results": results}


def execute_if_scheduled(doc, method):
    """Hook to auto-enqueue scheduled blasts as background jobs"""
    if doc.status == "Scheduled" and doc.scheduled_date and not doc.flags.get("auto_enqueued"):
        if get_datetime(doc.scheduled_date) <= now_datetime():
            try:
                doc.flags.auto_enqueued = True
                frappe.enqueue(
                    "marketing_hub.marketing_hub.doctype.campaign_activity.campaign_activity._run_execution_job",
                    campaign_activity=doc.name,
                    queue="default",
                    timeout=600,
                    job_id=f"campaign_activity_{doc.name}"
                )
            except (frappe.ValidationError, frappe.DoesNotExistError) as e:
                frappe.log_error("Scheduled blast enqueue failed", str(e))


def _execute_email_blast(activity):
    """Execute email blast to segment"""

    if not activity.segment:
        return {"status": "Error", "message": _("No segment defined")}

    # Get segment recipients
    segment = frappe.get_doc("Marketing Segment", activity.segment)
    recipients = _get_segment_recipients(segment, channel="Email")

    if activity.get("is_test_mode") and activity.get("test_emails"):
        test_emails = [e.strip() for e in activity.test_emails.split(",") if e.strip()]
        recipients = [{"email": e} for e in test_emails]

    # Get template
    template = _get_template(activity.campaign, "Email")

    if not template:
        return {"status": "Error", "message": "No email template found"}

    sent_count = 0
    for idx, recipient in enumerate(recipients):
        try:
            frappe.sendmail(
                recipients=[recipient.get("email")],
                subject=template.get("subject"),
                message=template.get("content"),
                reference_doctype="Campaign Activity",
                reference_name=activity.name
            )
            sent_count += 1
        except (frappe.ValidationError, frappe.OutgoingEmailError) as e:
            frappe.log_error(f"Email send failed to {recipient.get('email')}", str(e))

        # Commit every 100 emails to prevent memory buildup and allow recovery
        if (idx + 1) % 100 == 0:
            frappe.db.commit()

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

        recipients = _get_segment_recipients(segment, channel="WhatsApp")

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
                except (frappe.ValidationError, frappe.DoesNotExistError) as e:
                    frappe.log_error(f"WhatsApp blast error: {str(e)}", "Marketing Hub WhatsApp")
                    failed += 1

            return {
                "status": "Completed",
                "sent": sent,
                "failed": failed
            }
    except (frappe.ValidationError, frappe.DoesNotExistError) as e:
        frappe.log_error(f"WhatsApp blast execution error: {str(e)}", "Marketing Hub")
        return {"status": "Error", "message": str(e)}


def _execute_sms_blast(activity):
    """Execute SMS blast using Frappe SMS Settings"""
    from frappe.core.doctype.sms_settings.sms_settings import send_sms
    
    if not activity.segment:
        return {"status": "Error", "message": _("No segment defined")}

    # Check if SMS gateway is configured
    if not frappe.db.get_single_value("SMS Settings", "sms_gateway_url"):
        return {
            "status": "Error",
            "message": _("SMS gateway not configured. Please configure SMS Settings."),
            "count": 0
        }

    segment = frappe.get_doc("Marketing Segment", activity.segment)
    recipients = _get_segment_recipients(segment, channel="SMS")

    if not recipients:
        return {"status": "Error", "message": _("No recipients found in segment"), "count": 0}

    # Get message content
    message = activity.message or activity.content_html or ""
    if not message:
        return {"status": "Error", "message": _("No message content provided"), "count": 0}

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
    except (frappe.ValidationError, frappe.DoesNotExistError) as e:
        frappe.log_error("SMS Blast Error", str(e))
        return {
            "status": "Error",
            "message": f"SMS sending failed: {str(e)}",
            "count": 0
        }


def _execute_push_blast(activity):
    """Execute push notification blast (not yet implemented)"""
    if not activity.segment:
        return {"status": "Error", "message": _("No segment defined")}

    segment = frappe.get_doc("Marketing Segment", activity.segment)
    recipients = _get_segment_recipients(segment, channel="Push Notification")

    return {
        "status": "Not Implemented",
        "message": "Push notification service not yet integrated",
        "potential_recipients": len(recipients)
    }


def _get_segment_recipients(segment, channel=None):
    """Get list of recipients from segment and filter out suppressed contacts"""
    recipients = segment.get_segment_members(limit=5000)

    # Get Suppression List for this channel
    suppressed_contacts = set()
    if frappe.db.exists("DocType", "Suppression List"):
        supp_filters = {}
        if channel:
            supp_filters["channel"] = ["in", [channel, "All"]]
        else:
            supp_filters["channel"] = "All"

        suppressions = frappe.get_all("Suppression List", filters=supp_filters, fields=["contact_id"])
        suppressed_contacts = {s.contact_id for s in suppressions}

    # Remove duplicates and filter suppressed
    seen = set()
    unique_recipients = []
    for r in recipients:
        email = r.get("email") or r.get("email_id")
        mobile = r.get("mobile_no") or r.get("mobile") or r.get("phone")

        # Check suppression
        if (email and email in suppressed_contacts) or (mobile and mobile in suppressed_contacts):
            continue

        if email and email not in seen:
            seen.add(email)
            unique_recipients.append(r)
        elif not email and mobile and mobile not in seen:
            # If no email but has mobile, deduplicate by mobile
            seen.add(mobile)
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
    except (frappe.ValidationError, frappe.DoesNotExistError):
        return None

def _execute_meta_ads_blast(activity):
    """Execute Meta Ads campaign creation blast using GenericAdapter"""
    from marketing_hub.utils.social_adapter import publish_to_platform

    if not activity.segment:
        return {"status": "Error", "message": _("No segment defined")}

    segment = frappe.get_doc("Marketing Segment", activity.segment)
    recipients = _get_segment_recipients(segment)

    if not recipients:
        return {"status": "Error", "message": _("No recipients found in segment")}

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
        except (frappe.ValidationError, frappe.DoesNotExistError) as e:
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
        except (frappe.ValidationError, frappe.DoesNotExistError) as e:
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
