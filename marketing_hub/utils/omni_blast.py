# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies NG and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import now_datetime, get_datetime

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

    results = run_channels(activity)

    # Update activity with results
    activity.status = "Completed"
    activity.results = frappe.as_json(results)
    activity.save()
    frappe.db.commit()

    return {"message": "Blast executed successfully", "results": results}


def _builtin_senders():
    """Channels the app sends itself. Each sender takes the activity and returns a result dict."""
    social = lambda name: (lambda activity: _execute_social_post_blast(activity, name))
    senders = {
        "Email": _execute_email_blast,
        "WhatsApp": _execute_whatsapp_blast,
        "SMS": _execute_sms_blast,
        "Push Notification": _execute_push_blast,
        "Meta Ads": _execute_meta_ads_blast,
    }
    for name in ("Facebook", "Instagram", "LinkedIn", "Twitter", "X"):
        senders[name] = social(name)
    return senders


def get_channel_senders():
    """Return {channel name: sender}. Built-in senders plus any an app registers.

    An app registers a sender in its hooks.py:

        marketing_hub_channel_senders = {"Telegram": "my_app.channels.send_telegram"}

    The sender is called with the Campaign Activity and returns a dict such as
    {"status": "Sent", "count": 12}. A registered name replaces a built-in one,
    and the last app in the install order wins.
    """
    senders = _builtin_senders()
    for name, paths in (frappe.get_hooks("marketing_hub_channel_senders") or {}).items():
        path = paths[-1] if isinstance(paths, (list, tuple)) else paths
        senders[name] = frappe.get_attr(path)
    return senders


@frappe.whitelist()
def list_channels():
    """Channels the Add channel screen can offer: each Social Media Network, and whether the app can send to it."""
    sender_names = set(get_channel_senders())
    networks = frappe.get_all(
        "Social Media Network",
        filters={"is_active": 1},
        fields=["network_name", "network_type", "auth_type", "supports_scheduling", "supports_media"],
        order_by="network_type asc, network_name asc",
    )
    for network in networks:
        network["has_sender"] = network["network_name"] in sender_names
    return networks


def run_channels(activity):
    """Send one activity through each of its channels and return per-channel results.

    Does not touch the activity status; callers own that.
    """
    results = {}
    channels = activity.activity_type.split("\n") if activity.activity_type else []
    senders = get_channel_senders()

    for channel in channels:
        sender = senders.get(channel)
        if not sender:
            results[channel] = {"status": "Not Implemented", "count": 0}
            continue
        try:
            results[channel] = sender(activity)
        except Exception as e:
            frappe.log_error(title=f"Blast execution error for {channel}", message=frappe.get_traceback())
            results[channel] = {"status": "Error", "error": str(e)}
    return results


def execute_if_scheduled(doc, method):
    """Hook to auto-execute scheduled blasts"""
    if doc.status == "Scheduled" and doc.scheduled_time:
        if get_datetime(doc.scheduled_time) <= now_datetime():
            try:
                execute_blast(doc.name)
            except Exception as e:
                frappe.log_error("Scheduled blast execution failed", str(e))


def _execute_email_blast(activity):
    """Hand an email blast to ERPNext's Campaign and Email Campaign.

    The app does not send mail itself. It builds the pieces ERPNext's daily
    scheduler (send_email_to_leads_or_contacts) needs: an Email Template, a Campaign
    whose schedule sends that template on day 0, an Email Group holding the segment's
    recipients, and an Email Campaign that enrols the group. ERPNext then renders and
    queues the mail, adds the unsubscribe link and records unsubscribes.

    Sending happens when ERPNext's daily job runs on the start date, not at an exact
    time, and the Email Template can only use the Email Group as `doc`, so the mail is
    the same for every recipient.
    """
    from frappe.utils import getdate, today

    if not activity.segment:
        return {"status": "Error", "message": "No segment defined"}

    existing = frappe.db.get_value("Campaign", {"campaign_name": activity.name})
    if existing:
        email_campaign = frappe.db.get_value("Email Campaign", {"campaign_name": existing}, "name")
        if email_campaign:
            return {"status": "Scheduled", "via": "ERPNext Email Campaign", "email_campaign": email_campaign}

    segment = frappe.get_doc("Marketing Segment", activity.segment)
    recipients = [r for r in _get_segment_recipients(segment) if r.get("email")]
    if not recipients:
        return {"status": "Error", "message": "The segment has no recipients with an email address"}

    template = _get_template(activity.campaign, "Email")
    if not template:
        return {"status": "Error", "message": "No email template found"}

    email_template = _ensure_email_template(activity, template)
    campaign = _ensure_erpnext_campaign(activity, email_template)
    group = _ensure_email_group(activity, recipients)

    start_date = max(getdate(activity.scheduled_date or today()), getdate(today()))
    email_campaign = frappe.get_doc(
        {
            "doctype": "Email Campaign",
            "campaign_name": campaign,
            "email_campaign_for": "Email Group",
            "recipient": group,
            "start_date": start_date,
            "sender": frappe.session.user,
        }
    ).insert(ignore_permissions=True)

    _record_on_exercise(activity, email_campaign.name, campaign, start_date)

    return {
        "status": "Scheduled",
        "via": "ERPNext Email Campaign",
        "email_campaign": email_campaign.name,
        "start_date": str(start_date),
        "recipients": len(recipients),
    }


def _record_on_exercise(activity, email_campaign, campaign, start_date):
    """List the Email Campaign on the exercise. ERPNext's Campaign doctypes have no
    brand, so the exercise is where a brand manager finds and is limited to them."""
    exercise = frappe.get_doc("Marketing Campaign", activity.campaign)
    if any(row.email_campaign == email_campaign for row in exercise.get("email_campaigns") or []):
        return
    exercise.append(
        "email_campaigns",
        {
            "activity": activity.name,
            "email_campaign": email_campaign,
            "erpnext_campaign": campaign,
            "start_date": start_date,
        },
    )
    exercise.save(ignore_permissions=True)


def _ensure_email_template(activity, template):
    name = f"{activity.name} email"
    if frappe.db.exists("Email Template", name):
        return name
    frappe.get_doc(
        {
            "doctype": "Email Template",
            "__newname": name,
            "subject": template.get("subject") or activity.activity_name,
            "use_html": 1,
            "response_html": template.get("content") or "",
        }
    ).insert(ignore_permissions=True)
    return name


def _ensure_erpnext_campaign(activity, email_template):
    existing = frappe.db.get_value("Campaign", {"campaign_name": activity.name})
    if existing:
        return existing
    return (
        frappe.get_doc(
            {
                "doctype": "Campaign",
                "campaign_name": activity.name,
                "campaign_schedules": [{"send_after_days": 0, "email_template": email_template}],
            }
        )
        .insert(ignore_permissions=True)
        .name
    )


def _ensure_email_group(activity, recipients):
    title = f"{activity.name} recipients"
    if not frappe.db.exists("Email Group", title):
        frappe.get_doc({"doctype": "Email Group", "title": title}).insert(ignore_permissions=True)
    for recipient in recipients:
        # Leave existing members alone, so an unsubscribe recorded by ERPNext is kept.
        if not frappe.db.exists("Email Group Member", {"email_group": title, "email": recipient["email"]}):
            frappe.get_doc(
                {"doctype": "Email Group Member", "email_group": title, "email": recipient["email"]}
            ).insert(ignore_permissions=True)
    return title


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
