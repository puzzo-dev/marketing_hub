# Copyright (c) 2026, Puxxo and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""Create standard Media Types"""
	
	media_types = [
		{
			"type_name": "Image",
			"type_code": "IMAGE",
			"description": "Static image files (JPEG, PNG, WebP)",
			"file_extensions": "jpg, jpeg, png, gif, webp, svg",
			"max_file_size_mb": 10,
			"icon": "fa-file-image",
			"color": "#3498db"
		},
		{
			"type_name": "Video",
			"type_code": "VIDEO",
			"description": "Video files (MP4, MOV, AVI)",
			"file_extensions": "mp4, mov, avi, mkv, webm",
			"max_file_size_mb": 500,
			"icon": "fa-file-video",
			"color": "#9b59b6"
		},
		{
			"type_name": "GIF",
			"type_code": "GIF",
			"description": "Animated GIF files",
			"file_extensions": "gif",
			"max_file_size_mb": 15,
			"icon": "fa-gif",
			"color": "#e74c3c"
		},
		{
			"type_name": "Document",
			"type_code": "DOCUMENT",
			"description": "PDF and document files",
			"file_extensions": "pdf, doc, docx, ppt, pptx, xls, xlsx",
			"max_file_size_mb": 25,
			"icon": "fa-file-pdf",
			"color": "#e67e22"
		},
		{
			"type_name": "Audio",
			"type_code": "AUDIO",
			"description": "Audio files (MP3, WAV)",
			"file_extensions": "mp3, wav, ogg, m4a",
			"max_file_size_mb": 50,
			"icon": "fa-file-audio",
			"color": "#1abc9c"
		},
		{
			"type_name": "Infographic",
			"type_code": "INFOGRAPHIC",
			"description": "Infographic designs and charts",
			"file_extensions": "jpg, jpeg, png, svg, pdf",
			"max_file_size_mb": 15,
			"icon": "fa-chart-bar",
			"color": "#f39c12"
		},
		{
			"type_name": "Text",
			"type_code": "TEXT",
			"description": "Plain text and markdown files",
			"file_extensions": "txt, md, csv",
			"max_file_size_mb": 1,
			"icon": "fa-file-alt",
			"color": "#34495e"
		},
		{
			"type_name": "HTML",
			"type_code": "HTML",
			"description": "HTML email templates",
			"file_extensions": "html, htm",
			"max_file_size_mb": 2,
			"icon": "fa-code",
			"color": "#16a085"
		}
	]
	
	for media_type_data in media_types:
		if not frappe.db.exists("Media Type", media_type_data["type_name"]):
			doc = frappe.get_doc({
				"doctype": "Media Type",
				**media_type_data,
				"is_active": 1
			})
			doc.insert(ignore_permissions=True)
			print(f"Created media type: {media_type_data['type_name']}")
		else:
			print(f"Media type already exists: {media_type_data['type_name']}")
