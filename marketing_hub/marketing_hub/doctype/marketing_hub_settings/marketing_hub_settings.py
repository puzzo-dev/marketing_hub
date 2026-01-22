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

	def onload(self):
		"""Load connected doctypes"""
		self.load_connected_doctypes()

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

	def load_connected_doctypes(self):
		"""Load all doctypes connected to Marketing Hub"""
		if not self.connected_doctypes:
			self.sync_connected_doctypes()

	def sync_connected_doctypes(self):
		"""Sync connected doctypes - discover and populate"""
		# Define core Marketing Hub doctypes
		core_doctypes = [
			{"doctype_name": "Campaign", "integration_type": "Source", "status": "Active",
			 "description": "Marketing campaigns and initiatives"},
			{"doctype_name": "Social Post", "integration_type": "Source", "status": "Active",
			 "description": "Social media posts and scheduling"},
			{"doctype_name": "Marketing Expense", "integration_type": "Target", "status": "Active",
			 "description": "Marketing expense tracking and ledger"},
			{"doctype_name": "Lead", "integration_type": "Target", "status": "Active",
			 "description": "Leads generated from marketing campaigns"},
			{"doctype_name": "Contact", "integration_type": "Bidirectional", "status": "Active",
			 "description": "Contact management and segmentation"},
			{"doctype_name": "Email Queue", "integration_type": "Target", "status": "Active",
			 "description": "Email blast and campaign emails"},
			{"doctype_name": "Journal Entry", "integration_type": "Target", "status": "Active",
			 "description": "Accounting entries for marketing expenses"},
			{"doctype_name": "GL Entry", "integration_type": "Target", "status": "Active",
			 "description": "General ledger entries for financial tracking"},
		]

		# Clear existing connections
		self.connected_doctypes = []

		# Add core doctypes
		for doctype_info in core_doctypes:
			self.append("connected_doctypes", doctype_info)


@frappe.whitelist()
def sync_connections(docname):
	"""Sync connected doctypes for a settings document"""
	doc = frappe.get_doc("Marketing Hub Settings", docname)
	doc.sync_connected_doctypes()
	doc.save()
	frappe.msgprint(_("Connected DocTypes synced successfully"))
	return doc


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
