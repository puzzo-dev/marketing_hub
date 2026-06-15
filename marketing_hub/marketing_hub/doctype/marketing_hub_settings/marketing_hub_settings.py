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
		self.validate_company_settings()

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

	def validate_company_settings(self):
		"""Validate per-company settings"""
		if not self.company_settings:
			return

		companies_seen = set()
		for row in self.company_settings:
			if row.company in companies_seen:
				frappe.throw(_("Duplicate company entry: {0}").format(row.company))
			companies_seen.add(row.company)

			if row.default_expense_account:
				account_company = frappe.db.get_value("Account", row.default_expense_account, "company")
				if account_company != row.company:
					frappe.throw(
						_("Row {0}: Expense Account {1} does not belong to company {2}").format(
							row.idx, row.default_expense_account, row.company
						)
					)
				if frappe.db.get_value("Account", row.default_expense_account, "is_group"):
					frappe.throw(
						_("Row {0}: Expense Account cannot be a group account").format(row.idx)
					)

			if row.default_cost_center:
				cc_company = frappe.db.get_value("Cost Center", row.default_cost_center, "company")
				if cc_company != row.company:
					frappe.throw(
						_("Row {0}: Cost Center {1} does not belong to company {2}").format(
							row.idx, row.default_cost_center, row.company
						)
					)

			if row.default_payable_account:
				pa_company = frappe.db.get_value("Account", row.default_payable_account, "company")
				if pa_company != row.company:
					frappe.throw(
						_("Row {0}: Payable Account {1} does not belong to company {2}").format(
							row.idx, row.default_payable_account, row.company
						)
					)

	def get_company_settings(self, company):
		"""Get settings for a specific company from the child table"""
		for row in (self.company_settings or []):
			if row.company == company:
				return row
		return None


@frappe.whitelist()
def get_company_defaults(company=None):
	"""Get per-company defaults. Falls back to user's default company."""
	if not company:
		company = frappe.defaults.get_user_default("Company")
	if not company:
		return {}

	settings = frappe.get_single("Marketing Hub Settings")
	row = settings.get_company_settings(company)
	if not row:
		return {"company": company}

	return {
		"company": company,
		"default_expense_account": row.default_expense_account,
		"default_cost_center": row.default_cost_center,
		"default_payable_account": row.default_payable_account,
		"default_email_sender": row.default_email_sender,
	}


@frappe.whitelist()
def get_settings():
	"""Get Marketing Hub settings (single doctype)"""
	return frappe.get_single("Marketing Hub Settings").as_dict()


@frappe.whitelist()
def create_default_settings():
	"""Ensure Marketing Hub Settings exists (single doctype is auto-created)"""
	return frappe.get_single("Marketing Hub Settings").as_dict()

