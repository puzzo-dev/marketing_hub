# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class MarketingHubSettings(Document):
	def validate(self):
		"""Validate settings"""
		self.validate_session_timeout()
		self.validate_auto_post_interval()
		self.validate_agency_settings()

	def validate_session_timeout(self):
		"""Ensure session timeout is reasonable"""
		if self.session_timeout_days and self.session_timeout_days < 1:
			frappe.throw("Session Timeout must be at least 1 day")
		if self.session_timeout_days and self.session_timeout_days > 365:
			frappe.throw("Session Timeout cannot exceed 365 days")

	def validate_auto_post_interval(self):
		"""Ensure auto post interval is reasonable"""
		if self.auto_post_interval_minutes and self.auto_post_interval_minutes < 5:
			frappe.throw("Auto Post Interval must be at least 5 minutes")
		if self.auto_post_interval_minutes and self.auto_post_interval_minutes > 1440:
			frappe.throw("Auto Post Interval cannot exceed 1440 minutes (24 hours)")

	def validate_agency_settings(self):
		"""Validate agency-specific settings"""
		if self.agency_mode:
			if self.max_campaigns_per_client and self.max_campaigns_per_client < 1:
				frappe.throw("Max Campaigns per Client must be at least 1")


@frappe.whitelist()
def get_settings(company=None):
	"""Get Marketing Hub settings for a company"""
	if not company:
		company = frappe.defaults.get_user_default("Company")

	if not company:
		return None

	settings = frappe.db.get_value(
		"Marketing Hub Settings",
		{"company": company},
		"*",
		as_dict=1
	)

	return settings


@frappe.whitelist()
def create_default_settings(company):
	"""Create default settings for a company"""
	if frappe.db.exists("Marketing Hub Settings", {"company": company}):
		return frappe.get_doc("Marketing Hub Settings", {"company": company})

	settings = frappe.new_doc("Marketing Hub Settings")
	settings.company = company
	settings.insert(ignore_permissions=True)

	return settings
