"""
Social Posts API
"""

import frappe


@frappe.whitelist()
def get_social_posts(filters=None, limit=20, offset=0):
	"""Get social posts with engagement metrics"""
	try:
		filters = frappe.parse_json(filters) if filters else {}
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
			limit=limit,
			start=offset
		)

		import re
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

	except Exception as e:
		frappe.log_error(f"Error fetching social posts: {str(e)}", "Social Posts API Error")
		return {"error": str(e), "posts": [], "total_count": 0, "has_more": False, "status_counts": {}}


@frappe.whitelist()
def create_social_post(data):
	"""Create a new social post"""
	try:
		data = frappe.parse_json(data)

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

		return {"success": True, "post_name": post.name, "message": "Social post created successfully"}

	except Exception as e:
		frappe.log_error(f"Error creating social post: {str(e)}", "Social Post Creation Error")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def update_social_post(name, data):
	"""Update an existing social post"""
	try:
		data = frappe.parse_json(data)

		doc = frappe.get_doc("Social Post", name)
		for field in ["post_title", "content", "platform", "post_type", "status",
					   "scheduled_time", "hashtags", "mentions", "target_audience",
					   "enable_comments", "enable_sharing", "media_attachment", "media_type"]:
			if field in data:
				doc.set(field, data[field])
		doc.save()
		return {"success": True, "name": doc.name}
	except Exception as e:
		frappe.log_error(f"Error updating social post: {str(e)}", "Social Post Update Error")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def publish_social_post(name):
	"""Trigger immediate publishing of a social post"""
	try:
		doc = frappe.get_doc("Social Post", name)
		if doc.status not in ("Draft", "Scheduled"):
			return {"success": False, "error": "Only Draft or Scheduled posts can be published"}

		from marketing_hub.utils.auto_post import publish_post
		result = publish_post(doc)
		return {"success": True, "result": result}
	except Exception as e:
		frappe.log_error(f"Error publishing social post: {str(e)}", "Social Post Publish Error")
		return {"success": False, "error": str(e)}
