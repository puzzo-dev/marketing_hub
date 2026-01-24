# -*- coding: utf-8 -*-
# Copyright (c) 2026, Puzzo and Contributors
# License: MIT

"""
Seed data for Marketing Expense Categories
Creates standard expense category records
"""

import frappe


def execute():
	"""Create seed data for Marketing Expense Categories"""
	
	categories = [
		{
			"category_name": "Advertising",
			"category_code": "ADS",
			"description": "Paid advertising expenses (digital and traditional media)",
			"is_active": 1
		},
		{
			"category_name": "Content Creation",
			"category_code": "CONTENT",
			"description": "Content production costs (articles, videos, graphics, photography)",
			"is_active": 1
		},
		{
			"category_name": "Social Media",
			"category_code": "SOCIAL",
			"description": "Social media marketing expenses (ads, tools, management)",
			"is_active": 1
		},
		{
			"category_name": "Email Marketing",
			"category_code": "EMAIL",
			"description": "Email campaign costs (ESP fees, design, list management)",
			"is_active": 1
		},
		{
			"category_name": "SEO/SEM",
			"category_code": "SEO",
			"description": "Search engine optimization and marketing expenses",
			"is_active": 1
		},
		{
			"category_name": "Events",
			"category_code": "EVENTS",
			"description": "Event marketing costs (trade shows, conferences, webinars)",
			"is_active": 1
		},
		{
			"category_name": "Print Media",
			"category_code": "PRINT",
			"description": "Print advertising and collateral (magazines, newspapers, brochures)",
			"is_active": 1
		},
		{
			"category_name": "Influencer Marketing",
			"category_code": "INFLUENCER",
			"description": "Influencer partnerships and sponsored content",
			"is_active": 1
		},
		{
			"category_name": "Agency Fees",
			"category_code": "AGENCY",
			"description": "Marketing agency and consultant fees",
			"is_active": 1
		},
		{
			"category_name": "Software Tools",
			"category_code": "SOFTWARE",
			"description": "Marketing software and tool subscriptions",
			"is_active": 1
		},
		{
			"category_name": "Out of Home (OOH)",
			"category_code": "OOH",
			"description": "Billboard, transit, and outdoor advertising",
			"is_active": 1
		},
		{
			"category_name": "PR & Communications",
			"category_code": "PR",
			"description": "Public relations and corporate communications",
			"is_active": 1
		},
		{
			"category_name": "Market Research",
			"category_code": "RESEARCH",
			"description": "Market research, surveys, and analysis",
			"is_active": 1
		},
		{
			"category_name": "Other",
			"category_code": "OTHER",
			"description": "Miscellaneous marketing expenses",
			"is_active": 1
		}
	]
	
	for category_data in categories:
		# Check if already exists
		if frappe.db.exists("Marketing Expense Category", category_data["category_name"]):
			print(f"Category {category_data['category_name']} already exists, skipping")
			continue
		
		try:
			category = frappe.get_doc({
				"doctype": "Marketing Expense Category",
				**category_data
			})
			category.insert(ignore_permissions=True)
			print(f"Created category: {category_data['category_name']}")
		except Exception as e:
			print(f"Failed to create {category_data['category_name']}: {str(e)}")
			frappe.log_error(f"Failed to create expense category seed data: {str(e)}")
	
	frappe.db.commit()
	print("Marketing Expense Category seed data created successfully")
