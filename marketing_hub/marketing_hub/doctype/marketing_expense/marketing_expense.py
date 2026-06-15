# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate

from marketing_hub.utils.accounting import (
	check_budget_exceeded,
	get_expense_account_from_category,
	make_gl_entries,
	update_campaign_spent_amount,
	validate_accounting_entries,
)


class MarketingExpense(Document):
	def validate(self):
		self.set_defaults()
		self.set_currency()
		validate_accounting_entries(self)
	
	def set_defaults(self):
		"""Set default accounts from category and company"""
		# Set expense account from category if not set
		if not self.expense_account and self.expense_category:
			account = get_expense_account_from_category(self.expense_category, self.company)
			if account:
				self.expense_account = account
		
		# Set default cost center if not set
		if not self.cost_center:
			self.cost_center = frappe.get_cached_value("Company", self.company, "cost_center")
	
	def set_currency(self):
		"""Set currency from company if not set"""
		if not self.currency:
			self.currency = frappe.get_cached_value("Company", self.company, "default_currency")
	
	def before_submit(self):
		"""Validate before submit"""
		# Check budget
		check_budget_exceeded(self)
	
	def on_submit(self):
		"""Make GL entries and update campaign on submit"""
		self.make_gl_entries()
		update_campaign_spent_amount(self)
	
	def on_cancel(self):
		"""Cancel GL entries and update campaign"""
		self.make_gl_entries(cancel=True)
		update_campaign_spent_amount(self)
	
	def make_gl_entries(self, cancel=False):
		"""Create General Ledger entries for the expense"""
		if not cancel and self.gl_entry_posted:
			return
		
		# Use utility function to create GL entries
		success = make_gl_entries(self, cancel=cancel)
		
		if success:
			if not cancel:
				self.db_set("gl_entry_posted", 1)
			else:
				self.db_set("gl_entry_posted", 0)


@frappe.whitelist()
def get_default_expense_account(company):
	"""Get default marketing expense account"""
	settings = frappe.get_cached_doc("Marketing Hub Settings")
	return settings.default_expense_account if settings else None


@frappe.whitelist()
def get_campaign_budget_status(campaign, company):
	"""Get budget status for a campaign"""
	if not campaign:
		return {}

	# Get total expenses for campaign
	total_expenses = frappe.db.sql("""
		SELECT SUM(amount) as total
		FROM `tabMarketing Expense`
		WHERE campaign = %s
		AND company = %s
		AND docstatus = 1
	""", (campaign, company), as_dict=1)[0].total or 0

	# Get campaign budget
	campaign_doc = frappe.get_doc("Marketing Campaign", campaign)
	budget = campaign_doc.budget if hasattr(campaign_doc, 'budget') else 0

	return {
		"total_expenses": total_expenses,
		"budget": budget,
		"remaining": budget - total_expenses if budget else None,
		"utilization_percentage": (total_expenses / budget * 100) if budget else 0
	}
