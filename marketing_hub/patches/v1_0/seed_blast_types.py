# Copyright (c) 2026, Puxxo and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""Create standard Blast Types"""
	
	blast_types = [
		{
			"type_name": "Immediate",
			"type_code": "IMMEDIATE",
			"description": "Publish immediately to all networks at once",
			"requires_scheduling": 0,
			"supports_time_zones": 0,
			"icon": "fa-bolt",
			"color": "#e74c3c"
		},
		{
			"type_name": "Scheduled",
			"type_code": "SCHEDULED",
			"description": "Publish at a specific date and time",
			"requires_scheduling": 1,
			"supports_time_zones": 0,
			"icon": "fa-clock",
			"color": "#3498db"
		},
		{
			"type_name": "Staggered",
			"type_code": "STAGGERED",
			"description": "Publish to networks with intervals between each",
			"requires_scheduling": 1,
			"supports_time_zones": 0,
			"icon": "fa-layer-group",
			"color": "#9b59b6"
		},
		{
			"type_name": "Time Zone Optimized",
			"type_code": "TIMEZONE_OPT",
			"description": "Publish at optimal time for each audience time zone",
			"requires_scheduling": 1,
			"supports_time_zones": 1,
			"icon": "fa-globe",
			"color": "#1abc9c"
		},
		{
			"type_name": "A/B Test",
			"type_code": "AB_TEST",
			"description": "Test different versions with audience segments",
			"requires_scheduling": 0,
			"supports_time_zones": 0,
			"icon": "fa-flask",
			"color": "#f39c12"
		}
	]
	
	for blast_type_data in blast_types:
		if not frappe.db.exists("Blast Type", blast_type_data["type_name"]):
			doc = frappe.get_doc({
				"doctype": "Blast Type",
				**blast_type_data,
				"is_active": 1
			})
			doc.insert(ignore_permissions=True)
			print(f"Created blast type: {blast_type_data['type_name']}")
		else:
			print(f"Blast type already exists: {blast_type_data['type_name']}")
