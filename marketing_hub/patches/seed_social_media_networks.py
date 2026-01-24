# -*- coding: utf-8 -*-
# Copyright (c) 2026, Puzzo and Contributors
# License: MIT

"""
Seed data for Social Media Networks
Creates standard network/channel records including OOH, Email, SMS
"""

import frappe


def execute():
	"""Create seed data for Social Media Networks"""
	
	networks = [
		# Out of Home (OOH) Networks
		{
			"network_name": "Billboard",
			"network_code": "billboard",
			"network_type": "Out of Home (OOH)",
			"supports_scheduling": 1,
			"supports_media": 1,
			"post_types": "Static Image\nDigital Display\nVideo",
			"description": "Billboard advertising - large format outdoor displays",
			"is_active": 1
		},
		{
			"network_name": "Transit Ads",
			"network_code": "transit",
			"network_type": "Out of Home (OOH)",
			"supports_scheduling": 1,
			"supports_media": 1,
			"post_types": "Static Poster\nDigital Display",
			"description": "Bus, subway, train station advertising",
			"is_active": 1
		},
		{
			"network_name": "Street Furniture",
			"network_code": "street_furniture",
			"network_type": "Out of Home (OOH)",
			"supports_scheduling": 1,
			"supports_media": 1,
			"post_types": "Static Poster\nBacklit Display",
			"description": "Bus shelters, kiosks, public displays",
			"is_active": 1
		},
		# Email
		{
			"network_name": "Email",
			"network_code": "email",
			"network_type": "Email",
			"supports_scheduling": 1,
			"supports_media": 1,
			"post_types": "HTML Email\nPlain Text",
			"description": "Email marketing campaigns",
			"is_active": 1
		},
		# SMS
		{
			"network_name": "SMS",
			"network_code": "sms",
			"network_type": "SMS",
			"supports_scheduling": 1,
			"supports_media": 0,
			"max_text_length": 160,
			"post_types": "Text",
			"description": "SMS/Text message marketing",
			"is_active": 1
		},
		# WhatsApp
		{
			"network_name": "WhatsApp Business",
			"network_code": "whatsapp",
			"network_type": "Messaging",
			"supports_scheduling": 1,
			"supports_media": 1,
			"max_text_length": 4096,
			"post_types": "Text\nImage\nVideo\nDocument",
			"description": "WhatsApp Business API messaging",
			"is_active": 1
		},
		# Additional Social Media (if not already created)
		{
			"network_name": "TikTok",
			"network_code": "tiktok",
			"network_type": "Social Media",
			"supports_scheduling": 1,
			"supports_media": 1,
			"max_text_length": 2200,
			"post_types": "Video\nImage",
			"description": "TikTok short-form video platform",
			"is_active": 1
		},
		{
			"network_name": "Pinterest",
			"network_code": "pinterest",
			"network_type": "Social Media",
			"supports_scheduling": 1,
			"supports_media": 1,
			"max_text_length": 500,
			"post_types": "Pin (Image)\nVideo Pin\nIdea Pin",
			"description": "Pinterest visual discovery platform",
			"is_active": 1
		},
		{
			"network_name": "Snapchat",
			"network_code": "snapchat",
			"network_type": "Social Media",
			"supports_scheduling": 0,
			"supports_media": 1,
			"post_types": "Snap\nStory\nSpotlight",
			"description": "Snapchat ephemeral messaging",
			"is_active": 1
		}
	]
	
	for network_data in networks:
		# Check if already exists
		if frappe.db.exists("Social Media Network", network_data["network_name"]):
			print(f"Network {network_data['network_name']} already exists, skipping")
			continue
		
		try:
			network = frappe.get_doc({
				"doctype": "Social Media Network",
				**network_data
			})
			network.insert(ignore_permissions=True)
			print(f"Created network: {network_data['network_name']}")
		except Exception as e:
			print(f"Failed to create {network_data['network_name']}: {str(e)}")
			frappe.log_error(f"Failed to create network seed data: {str(e)}")
	
	frappe.db.commit()
	print("Social Media Network seed data created successfully")
