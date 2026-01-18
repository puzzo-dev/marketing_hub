# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

"""
Migration script to create Marketing Hub Settings for all companies
"""

import frappe

def execute():
	"""Create Marketing Hub Settings for all companies"""

	companies = frappe.get_all("Company", fields=["name"])

	for company in companies:
		company_name = company.get("name")

		# Check if settings already exist
		if not frappe.db.exists("Marketing Hub Settings", {"company": company_name}):
			try:
				settings = frappe.new_doc("Marketing Hub Settings")
				settings.company = company_name

				# Set sensible defaults
				settings.enable_auto_attribution = 1
				settings.enable_utm_tracking = 1
				settings.enable_session_tracking = 1
				settings.session_timeout_days = 30
				settings.enable_email_blast = 1
				settings.enable_auto_post = 1
				settings.auto_post_interval_minutes = 15
				settings.enable_analytics_sync = 1
				settings.analytics_sync_schedule = "0 2 * * *"
				settings.default_attribution_model = "Last Touch"
				settings.track_conversions = 1
				settings.enable_content_library = 1
				settings.enable_version_control = 1
				settings.notify_campaign_completion = 1
				settings.notify_blast_execution = 1
				settings.notify_analytics_sync = 1
				settings.sync_frequency = "Daily"

				# Check if old Marketing Hub Setup exists and migrate settings
				try:
					old_setup = frappe.get_single("Marketing Hub Setup")
					if old_setup:
						settings.agency_mode = 1 if old_setup.get("mode") == "Agency" else 0
				except:
					pass

				settings.insert(ignore_permissions=True)
				frappe.db.commit()

				print(f"Created Marketing Hub Settings for {company_name}")
			except Exception as e:
				frappe.log_error(f"Failed to create Marketing Hub Settings for {company_name}: {str(e)}")
				print(f"Error creating settings for {company_name}: {str(e)}")
