# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import now_datetime, get_datetime

def publish_scheduled_posts():
    """Scheduler function to publish scheduled social posts"""

    # Get all posts scheduled for now or earlier that are still in Draft/Scheduled status
    due_posts = frappe.get_all(
        "Social Post",
        filters={
            "status": ["in", ["Draft", "Scheduled"]],
            "scheduled_time": ["<=", now_datetime()]
        },
        fields=["name"],
        limit_page_length=100
    )

    for post_name in due_posts:
        try:
            post = frappe.get_doc("Social Post", post_name.name)
            publish_post(post)
            frappe.db.commit()
        except (frappe.ValidationError, frappe.DoesNotExistError) as e:
            frappe.log_error(f"Auto-post failed for {post_name.name}", str(e))
            frappe.db.rollback()


@frappe.whitelist()
def publish_post(post):
    """Publish a social post to the configured platform.
    Uses the unified social_adapter.publish_to_platform() for consistent
    adapter resolution (including custom adapter classes) and token handling.
    """
    from marketing_hub.utils.social_adapter import publish_to_platform

    if isinstance(post, str):
        post = frappe.get_doc("Social Post", post)

    if post.status == "Published":
        frappe.throw(_("Post is already published"))

    # Update status
    post.status = "Publishing"
    post.save()
    frappe.db.commit()

    try:
        # Use unified adapter resolution — handles custom adapters, token refresh, etc.
        result = publish_to_platform(post)

        # publish_to_platform already updates post.status, platform_post_id, etc.
        # Just store the full result JSON for debugging
        post.reload()
        post.post_results = frappe.as_json(result)

        if result.get("url"):
            post.platform_url = result.get("url")

        post.save()
        frappe.db.commit()

        return result

    except (frappe.ValidationError, frappe.DoesNotExistError) as e:
        post.status = "Failed"
        post.post_results = frappe.as_json({"status": "Error", "error": str(e)})
        post.save()
        frappe.db.commit()
        frappe.log_error("Post publishing failed", str(e))
        raise


def _get_ad_account(company, platform):
    """Get ad account configuration for company and platform"""
    try:
        account = frappe.get_all(
            "Ad Account",
            filters={
                "company": company,
                "platform": platform,
                "status": "Active"
            },
            fields=["name"],
            limit=1
        )
        return account[0].name if account else None
    except (frappe.ValidationError, frappe.DoesNotExistError):
        return None


@frappe.whitelist()
def preview_post(post):
    """Generate preview of social post"""
    if isinstance(post, str):
        post = frappe.get_doc("Social Post", post)

    return {
        "platform": post.platform,
        "content": post.content,
        "media": post.get("media_url"),
        "scheduled_time": post.scheduled_time
    }
