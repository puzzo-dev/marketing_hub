# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate

from erpnext.accounts.general_ledger import make_gl_entries


class MarketingExpense(Document):
	def validate(self):
		self.validate_accounts()
		self.set_currency()

	def validate_accounts(self):
		"""Validate expense and payment accounts"""
		if not frappe.db.get_value("Account", self.expense_account, "is_group") == 0:
			frappe.throw(_("Expense Account {0} cannot be a group account").format(self.expense_account))

		if self.is_paid and self.payment_account:
			if not frappe.db.get_value("Account", self.payment_account, "is_group") == 0:
				frappe.throw(_("Payment Account {0} cannot be a group account").format(self.payment_account))

	def set_currency(self):
		"""Set currency from company if not set"""
		if not self.currency:
			self.currency = frappe.get_cached_value("Company", self.company, "default_currency")

	def on_submit(self):
		"""Make GL entries on submit"""
		self.make_gl_entries()

	def on_cancel(self):
		"""Cancel GL entries"""
		self.make_gl_entries(cancel=True)

	def make_gl_entries(self, cancel=False):
		"""Create General Ledger entries for the expense"""
		if not cancel and self.gl_entry_posted:
			return

		gl_entries = self.get_gl_entries()

		if gl_entries:
			make_gl_entries(gl_entries, cancel=cancel, adv_adj=False)

			if not cancel:
				self.db_set("gl_entry_posted", 1)
			else:
				self.db_set("gl_entry_posted", 0)

	def get_gl_entries(self):
		"""Build GL entry list"""
		gl_entries = []

		# Expense account entry (Debit)
		gl_entries.append(
			self.get_gl_dict({
				"account": self.expense_account,
				"debit": flt(self.amount),
				"debit_in_account_currency": flt(self.amount),
				"against": self.payment_account if self.is_paid else None,
				"cost_center": self.cost_center,
				"project": self.project,
				"remarks": self.remarks or "Marketing Expense",
			})
		)

		# Payment account entry (Credit) - if paid
		if self.is_paid and self.payment_account:
			gl_entries.append(
				self.get_gl_dict({
					"account": self.payment_account,
					"credit": flt(self.amount),
					"credit_in_account_currency": flt(self.amount),
					"against": self.expense_account,
					"cost_center": self.cost_center,
					"project": self.project,
					"remarks": self.remarks or "Marketing Expense Payment",
				})
			)

		return gl_entries

	def get_gl_dict(self, args):
		"""Build GL entry dict"""
		gl_dict = frappe._dict({
			"posting_date": getdate(self.posting_date),
			"voucher_type": self.doctype,
			"voucher_no": self.name,
			"company": self.company,
			"account_currency": self.currency,
		})
		gl_dict.update(args)
		return gl_dict


@frappe.whitelist()
def get_default_expense_account(company):
	"""Get default marketing expense account"""
	settings = frappe.get_doc("Marketing Hub Settings", company)
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
	campaign_doc = frappe.get_doc("Campaign", campaign)
	budget = campaign_doc.budget if hasattr(campaign_doc, 'budget') else 0

	return {
		"total_expenses": total_expenses,
		"budget": budget,
		"remaining": budget - total_expenses if budget else None,
		"utilization_percentage": (total_expenses / budget * 100) if budget else 0
	}
