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
        platform = post.get("platform", "").lower()

        if platform == "meta" or platform == "facebook":
            result = _publish_to_meta(post)
        elif platform == "twitter" or platform == "x":
            result = _publish_to_twitter(post)
        elif platform == "linkedin":
            result = _publish_to_linkedin(post)
        elif platform == "instagram":
            result = _publish_to_instagram(post)
        else:
            result = {"status": "Error", "message": f"Platform {platform} not supported"}

        # Update post with results
        post.status = "Published" if result.get("status") == "Success" else "Failed"
        post.post_results = frappe.as_json(result)
        post.published_time = now_datetime()
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


def _publish_to_meta(post):
    """Publish to Meta (Facebook/Instagram) - Stub implementation"""
    # TODO: Implement Meta Graph API integration
    # Requires: App ID, App Secret, Page Access Token

    try:
        # Get ad account/page credentials
        ad_account = _get_ad_account(post.company, "Meta")

        if not ad_account:
            return {"status": "Error", "message": "No Meta ad account configured"}

        # Stub - would call Meta Graph API here
        # POST https://graph.facebook.com/v18.0/{page-id}/feed

        return {
            "status": "Stub",
            "message": "Meta API integration required",
            "post_id": None,
            "platform_url": None
        }
    except Exception as e:
        return {"status": "Error", "error": str(e)}


def _publish_to_twitter(post):
    """Publish to Twitter/X - Stub implementation"""
    # TODO: Implement Twitter API v2 integration
    # Requires: API Key, API Secret, Access Token, Access Token Secret

    try:
        ad_account = _get_ad_account(post.company, "Twitter")

        if not ad_account:
            return {"status": "Error", "message": "No Twitter ad account configured"}

        # Stub - would call Twitter API here
        # POST https://api.twitter.com/2/tweets

        return {
            "status": "Stub",
            "message": "Twitter API integration required",
            "post_id": None,
            "platform_url": None
        }
    except Exception as e:
        return {"status": "Error", "error": str(e)}


def _publish_to_linkedin(post):
    """Publish to LinkedIn - Stub implementation"""
    # TODO: Implement LinkedIn API integration
    # Requires: Client ID, Client Secret, Access Token

    try:
        ad_account = _get_ad_account(post.company, "LinkedIn")

        if not ad_account:
            return {"status": "Error", "message": "No LinkedIn ad account configured"}

        # Stub - would call LinkedIn API here
        # POST https://api.linkedin.com/v2/ugcPosts

        return {
            "status": "Stub",
            "message": "LinkedIn API integration required",
            "post_id": None,
            "platform_url": None
        }
    except Exception as e:
        return {"status": "Error", "error": str(e)}


def _publish_to_instagram(post):
    """Publish to Instagram - Stub implementation"""
    # Uses Meta Graph API
    # Requires: Business Account, Instagram Account ID, Access Token

    try:
        ad_account = _get_ad_account(post.company, "Meta")

        if not ad_account:
            return {"status": "Error", "message": "No Instagram/Meta account configured"}

        # Stub - would call Meta Graph API for Instagram
        # POST https://graph.facebook.com/v18.0/{instagram-account-id}/media

        return {
            "status": "Stub",
            "message": "Instagram API integration required",
            "post_id": None,
            "platform_url": None
        }
    except Exception as e:
        return {"status": "Error", "error": str(e)}


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
            fields=["name", "account_id", "access_token"],
            limit=1
        )
        return account[0] if account else None
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
