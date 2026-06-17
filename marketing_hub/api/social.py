"""
Social Posts API
"""

import json
import re

import frappe
from frappe import _


@frappe.whitelist()
def get_social_posts(filters=None, limit=20, offset=0):
	"""Get social posts with engagement metrics"""
	try:
		if filters and isinstance(filters, str):
			filters = json.loads(filters)

		filters = filters or {}
		base_filters = {}
		if filters.get("status"):
			base_filters["status"] = filters["status"]
		if filters.get("platform"):
			base_filters["platform"] = filters["platform"]
		if filters.get("campaign"):
			base_filters["campaign"] = filters["campaign"]

		posts = frappe.get_all(
			"Social Post",
			fields=[
				"name", "post_title", "platform", "post_type", "status",
				"scheduled_time", "published_time", "campaign", "content",
				"impressions", "reach", "clicks", "likes", "comments_count",
				"shares", "engagement_rate", "creation", "modified"
			],
			filters=base_filters,
			order_by="modified desc",
			limit=min(int(limit), 100),
			start=offset
		)

		for post in posts:
			if post.platform:
				network = frappe.db.get_value(
					"Social Media Network",
					post.platform,
					["network_name", "icon", "network_type"],
					as_dict=True
				)
				if network:
					post["network_name"] = network.network_name
					post["network_icon"] = network.icon
					post["network_type"] = network.network_type

			if post.content:
				clean_content = re.sub(r'<[^>]+>', '', post.content or '')
				post["content_preview"] = clean_content[:100] + "..." if len(clean_content) > 100 else clean_content

		total_count = frappe.db.count("Social Post", base_filters)

		status_counts = frappe.db.sql("""
			SELECT status, COUNT(*) as count
			FROM `tabSocial Post`
			GROUP BY status
		""", as_dict=True)

		return {
			"posts": posts,
			"total_count": total_count,
			"has_more": (offset + limit) < total_count,
			"status_counts": {item.status: item.count for item in status_counts}
		}

	except (json.JSONDecodeError, frappe.DatabaseError) as e:
		frappe.log_error(f"Error fetching social posts: {str(e)}", "Social Posts API Error")
		return {"error": str(e), "posts": [], "total_count": 0, "has_more": False, "status_counts": {}}


@frappe.whitelist()
def create_social_post(data):
	"""Create a new social post"""
	try:
		if isinstance(data, str):
			data = json.loads(data)

		frappe.has_permission("Social Post", throw=True)
		post = frappe.get_doc({
			"doctype": "Social Post",
			"post_title": data.get("post_title"),
			"platform": data.get("platform"),
			"post_type": data.get("post_type", "Text"),
			"status": data.get("status", "Draft"),
			"content": data.get("content"),
			"campaign": data.get("campaign"),
			"scheduled_time": data.get("scheduled_time")
		})

		post.insert()
		frappe.db.commit()

		return {"success": True, "post_name": post.name, "message": _("Social post created successfully")}

	except (frappe.ValidationError, frappe.DuplicateEntryError) as e:
		frappe.log_error(f"Error creating social post: {str(e)}", "Social Post Creation Error")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def update_social_post(name, data):
	"""Update an existing social post"""
	try:
		if isinstance(data, str):
			data = json.loads(data)

		doc = frappe.get_doc("Social Post", name)
		doc.check_permission("write")
		for field in ["post_title", "content", "platform", "post_type", "status",
					   "scheduled_time", "hashtags", "mentions", "target_audience",
					   "enable_comments", "enable_sharing", "media_attachment", "media_type"]:
			if field in data:
				doc.set(field, data[field])
		doc.save()
		return {"success": True, "name": doc.name}
	except (frappe.PermissionError, frappe.ValidationError) as e:
		frappe.log_error(f"Error updating social post: {str(e)}", "Social Post Update Error")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def publish_social_post(name):
	"""Trigger immediate publishing of a social post"""
	try:
		doc = frappe.get_doc("Social Post", name)
		doc.check_permission("write")
		if doc.status not in ("Draft", "Scheduled"):
			return {"success": False, "error": _("Only Draft or Scheduled posts can be published")}

		from marketing_hub.utils.auto_post import publish_post
		result = publish_post(doc)
		return {"success": True, "result": result}
	except (frappe.PermissionError, frappe.ValidationError) as e:
		frappe.log_error(f"Error publishing social post: {str(e)}", "Social Post Publish Error")
		return {"success": False, "error": str(e)}
