# -*- coding: utf-8 -*-
# Copyright (c) 2026, Puzzo and Contributors
# License: MIT

"""
Update Social Media Network specs
Adds missing fields data for existing networks
"""

import frappe


def execute():
	"""Update existing Social Media Networks with specs"""
	
	network_specs = {
		"Facebook": {
			"max_text_length": 63206,
			"supports_html": 0,
			"max_hashtags": 30,
			"max_mentions": 50,
			"max_images": 10,
			"max_videos": 1
		},
		"Instagram": {
			"max_text_length": 2200,
			"supports_html": 0,
			"max_hashtags": 30,
			"max_mentions": 30,
			"max_images": 10,
			"max_videos": 1
		},
		"Twitter/X": {
			"max_text_length": 280,
			"supports_html": 0,
			"max_hashtags": 10,
			"max_mentions": 10,
			"max_images": 4,
			"max_videos": 1
		},
		"LinkedIn": {
			"max_text_length": 3000,
			"supports_html": 0,
			"max_hashtags": 3,
			"max_mentions": 50,
			"max_images": 9,
			"max_videos": 1
		},
		"Meta Ads": {
			"max_text_length": 125,
			"supports_html": 0,
			"max_hashtags": 5,
			"max_mentions": 5,
			"max_images": 10,
			"max_videos": 1
		},
		"Google Ads": {
			"max_text_length": 90,
			"supports_html": 0,
			"max_hashtags": 0,
			"max_mentions": 0,
			"max_images": 20,
			"max_videos": 5
		},
		"LinkedIn Ads": {
			"max_text_length": 150,
			"supports_html": 0,
			"max_hashtags": 3,
			"max_mentions": 5,
			"max_images": 1,
			"max_videos": 1
		},
		"TikTok": {
			"max_text_length": 2200,
			"supports_html": 0,
			"max_hashtags": 20,
			"max_mentions": 20,
			"max_images": 35,
			"max_videos": 1
		},
		"Pinterest": {
			"max_text_length": 500,
			"supports_html": 0,
			"max_hashtags": 20,
			"max_mentions": 5,
			"max_images": 5,
			"max_videos": 1
		},
		"YouTube": {
			"max_text_length": 5000,
			"supports_html": 1,
			"max_hashtags": 15,
			"max_mentions": 20,
			"max_images": 1,
			"max_videos": 1
		},
		"SMS": {
			"max_text_length": 160,
			"supports_html": 0,
			"max_hashtags": 0,
			"max_mentions": 0,
			"max_images": 0,
			"max_videos": 0
		},
		"Email": {
			"max_text_length": None,
			"supports_html": 1,
			"max_hashtags": 0,
			"max_mentions": 100,
			"max_images": 50,
			"max_videos": 10
		},
		"WhatsApp Business": {
			"max_text_length": 4096,
			"supports_html": 0,
			"max_hashtags": 0,
			"max_mentions": 5,
			"max_images": 10,
			"max_videos": 1
		},
		"Billboard": {
			"max_text_length": 100,
			"supports_html": 0,
			"max_hashtags": 0,
			"max_mentions": 0,
			"max_images": 1,
			"max_videos": 0
		},
		"Transit Ads": {
			"max_text_length": 50,
			"supports_html": 0,
			"max_hashtags": 0,
			"max_mentions": 0,
			"max_images": 1,
			"max_videos": 0
		},
		"Street Furniture": {
			"max_text_length": 75,
			"supports_html": 0,
			"max_hashtags": 0,
			"max_mentions": 0,
			"max_images": 1,
			"max_videos": 0
		}
	}
	
	for network_name, specs in network_specs.items():
		if not frappe.db.exists("Social Media Network", network_name):
			print(f"Network {network_name} does not exist, skipping")
			continue
		
		try:
			for field, value in specs.items():
				if value is not None:
					frappe.db.set_value(
						"Social Media Network",
						network_name,
						field,
						value,
						update_modified=False
					)
			
			print(f"Updated specs for: {network_name}")
		except Exception as e:
			print(f"Failed to update {network_name}: {str(e)}")
			frappe.log_error(f"Failed to update network specs: {str(e)}")
	
	frappe.db.commit()
	print("Social Media Network specs updated successfully")
