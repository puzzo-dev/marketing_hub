# Copyright (c) 2026, Puxxo and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""Create standard Post Types"""
	
	post_types = [
		{
			"type_name": "Text",
			"type_code": "TEXT",
			"description": "Text-only post without media",
			"icon": "fa-align-left",
			"color": "#3498db"
		},
		{
			"type_name": "Image",
			"type_code": "IMAGE",
			"description": "Post with single image attachment",
			"icon": "fa-image",
			"color": "#e74c3c"
		},
		{
			"type_name": "Video",
			"type_code": "VIDEO",
			"description": "Post with video content",
			"icon": "fa-video",
			"color": "#9b59b6"
		},
		{
			"type_name": "Carousel",
			"type_code": "CAROUSEL",
			"description": "Multiple images or videos in a swipeable format",
			"icon": "fa-images",
			"color": "#f39c12"
		},
		{
			"type_name": "Story",
			"type_code": "STORY",
			"description": "Temporary content (24-hour duration)",
			"icon": "fa-clock",
			"color": "#1abc9c"
		},
		{
			"type_name": "Reel",
			"type_code": "REEL",
			"description": "Short-form vertical video content",
			"icon": "fa-film",
			"color": "#e67e22"
		},
		{
			"type_name": "Live",
			"type_code": "LIVE",
			"description": "Live streaming video content",
			"icon": "fa-broadcast-tower",
			"color": "#c0392b"
		},
		{
			"type_name": "Poll",
			"type_code": "POLL",
			"description": "Interactive poll post",
			"icon": "fa-poll",
			"color": "#16a085"
		}
	]
	
	for post_type_data in post_types:
		if not frappe.db.exists("Post Type", post_type_data["type_name"]):
			doc = frappe.get_doc({
				"doctype": "Post Type",
				**post_type_data,
				"is_active": 1
			})
			doc.insert(ignore_permissions=True)
			print(f"Created post type: {post_type_data['type_name']}")
		else:
			print(f"Post type already exists: {post_type_data['type_name']}")
