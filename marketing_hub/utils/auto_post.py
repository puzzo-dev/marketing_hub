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
        fields=["name"]
    )

    for post_name in due_posts:
        try:
            post = frappe.get_doc("Social Post", post_name.name)
            publish_post(post)
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(f"Auto-post failed for {post_name.name}", str(e))
            frappe.db.rollback()


@frappe.whitelist()
def publish_post(post):
    """Publish a social post to the configured platform"""

    if isinstance(post, str):
        post = frappe.get_doc("Social Post", post)

    if post.status == "Published":
        frappe.throw(_("Post is already published"))

    # Update status
    post.status = "Publishing"
    post.save()
    frappe.db.commit()

    try:
        # Use GenericAdapter for all platforms
        from marketing_hub.utils.social_adapters import GenericAdapter
        
        # Get the ad account for this platform
        ad_account = _get_ad_account(post.company, post.platform)
        if not ad_account:
            result = {"status": "Error", "message": f"No ad account configured for {post.platform}"}
        else:
            # Initialize adapter and publish
            adapter = GenericAdapter(ad_account)
            result = adapter.publish(post.content, post.media_file)

        # Update post with results
        post.status = "Published" if result.get("status") == "Success" else "Failed"
        post.post_results = frappe.as_json(result)
        post.published_time = now_datetime()
        
        if result.get("post_id"):
            post.post_id = result.get("post_id")
        if result.get("platform_url"):
            post.platform_url = result.get("platform_url")
        
        post.save()
        frappe.db.commit()

        return result

    except Exception as e:
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
    except Exception:
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
