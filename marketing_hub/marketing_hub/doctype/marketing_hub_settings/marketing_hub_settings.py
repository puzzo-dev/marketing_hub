# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class MarketingHubSettings(Document):
	def validate(self):
		"""Validate settings"""
		self.validate_session_timeout()
		self.validate_auto_post_interval()
		self.validate_agency_settings()
		self.validate_accounting_settings()

	def validate_session_timeout(self):
		"""Ensure session timeout is reasonable"""
		if self.session_timeout_days and self.session_timeout_days < 1:
			frappe.throw(_("Session Timeout must be at least 1 day"))
		if self.session_timeout_days and self.session_timeout_days > 365:
			frappe.throw(_("Session Timeout cannot exceed 365 days"))

	def validate_auto_post_interval(self):
		"""Ensure auto post interval is reasonable"""
		if self.auto_post_interval_minutes and self.auto_post_interval_minutes < 5:
			frappe.throw(_("Auto Post Interval must be at least 5 minutes"))
		if self.auto_post_interval_minutes and self.auto_post_interval_minutes > 1440:
			frappe.throw(_("Auto Post Interval cannot exceed 1440 minutes (24 hours)"))

	def validate_agency_settings(self):
		"""Validate agency-specific settings"""
		if self.agency_mode:
			if self.max_campaigns_per_client and self.max_campaigns_per_client < 1:
				frappe.throw(_("Max Campaigns per Client must be at least 1"))

	def validate_accounting_settings(self):
		"""Validate accounting settings"""
		if self.enable_gl_entry:
			if self.default_expense_account:
				# Validate that expense account is not a group account
				if frappe.db.get_value("Account", self.default_expense_account, "is_group"):
					frappe.throw(_("Default Expense Account cannot be a group account"))

			if self.default_cost_center:
				# Validate that cost center is not disabled
				if frappe.db.get_value("Cost Center", self.default_cost_center, "disabled"):
					frappe.throw(_("Default Cost Center is disabled"))


@frappe.whitelist()
def get_settings():
	"""Get Marketing Hub settings (single doctype)"""
	return frappe.get_single("Marketing Hub Settings").as_dict()


@frappe.whitelist()
def create_default_settings():
	"""Ensure Marketing Hub Settings exists (single doctype is auto-created)"""
	return frappe.get_single("Marketing Hub Settings").as_dict()

