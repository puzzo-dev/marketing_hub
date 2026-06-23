# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies NG and contributors
# For license information, please see license.txt

"""
Migration script to create Marketing Hub Settings for all companies
"""

import frappe

def execute():
	"""Ensure Marketing Hub Settings has sensible defaults (single doctype)"""

	settings = frappe.get_single("Marketing Hub Settings")

	# Only set defaults if company is not yet configured
	if not settings.company:
		default_company = frappe.defaults.get_global_default("company")
		if default_company:
			settings.company = default_company

	# Set sensible defaults for unset fields
	defaults = {
		"enable_auto_attribution": 1,
		"enable_utm_tracking": 1,
		"enable_email_blast": 1,
		"enable_auto_post": 1,
		"enable_analytics_sync": 1,
		"enable_content_library": 1,
		"enable_version_control": 1,
		"sync_frequency": "Daily",
	}

	changed = False
	for field, value in defaults.items():
		if not settings.get(field):
			settings.set(field, value)
			changed = True

	if changed or not settings.company:
		try:
			settings.save(ignore_permissions=True)
			frappe.db.commit()
			print("Marketing Hub Settings defaults applied")
		except Exception as e:
			frappe.log_error(f"Failed to update Marketing Hub Settings: {str(e)}")
			print(f"Error updating Marketing Hub Settings: {str(e)}")
