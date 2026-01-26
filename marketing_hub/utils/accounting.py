# Copyright (c) 2026, Puxxo and contributors
# For license information, please see license.txt

"""
Accounting utilities for Marketing Hub
Handles GL Entry creation for marketing expenses
"""

import frappe
from frappe import _
from frappe.utils import flt, nowdate, get_link_to_form


def make_gl_entries(doc, cancel=False):
	"""
	Create General Ledger entries for Marketing Expense
	
	Args:
		doc: Marketing Expense document
		cancel: Boolean indicating if this is a cancellation
	"""
	from erpnext.accounts.general_ledger import make_gl_entries as create_gl_entries
	
	gl_entries = []
	
	# Validate required fields
	if not doc.expense_account:
		frappe.throw(_("Expense Account is required to post GL entries"))
	
	if not doc.amount or flt(doc.amount) <= 0:
		frappe.throw(_("Amount must be greater than zero"))
	
	# Get cost center (use default if not specified)
	cost_center = doc.cost_center or get_default_cost_center(doc.company)
	
	# Debit Entry - Expense Account
	gl_entries.append(
		doc.get_gl_dict({
			"account": doc.expense_account,
			"debit": flt(doc.amount),
			"debit_in_account_currency": flt(doc.amount),
			"against": doc.payment_account if doc.is_paid else None,
			"cost_center": cost_center,
			"project": doc.project,
			"remarks": get_remarks(doc),
			"posting_date": doc.posting_date,
		}, item=doc)
	)
	
	# Credit Entry - Payment Account (if paid) or Payable Account
	if doc.is_paid and doc.payment_account:
		# Direct payment - credit the payment account
		gl_entries.append(
			doc.get_gl_dict({
				"account": doc.payment_account,
				"credit": flt(doc.amount),
				"credit_in_account_currency": flt(doc.amount),
				"against": doc.expense_account,
				"cost_center": cost_center,
				"project": doc.project,
				"remarks": get_remarks(doc),
				"posting_date": doc.posting_date,
			}, item=doc)
		)
	else:
		# Accrued expense - credit payable account
		payable_account = get_default_payable_account(doc.company)
		gl_entries.append(
			doc.get_gl_dict({
				"account": payable_account,
				"credit": flt(doc.amount),
				"credit_in_account_currency": flt(doc.amount),
				"against": doc.expense_account,
				"cost_center": cost_center,
				"project": doc.project,
				"remarks": get_remarks(doc),
				"posting_date": doc.posting_date,
			}, item=doc)
		)
	
	if gl_entries:
		create_gl_entries(gl_entries, cancel=cancel, adv_adj=False)
		return True
	
	return False


def get_remarks(doc):
	"""Generate remarks for GL entry"""
	remarks = []
	
	if doc.expense_category:
		category = frappe.get_cached_value("Marketing Expense Category", doc.expense_category, "category_name")
		remarks.append(f"Category: {category}")
	
	if doc.campaign:
		remarks.append(f"Campaign: {doc.campaign}")
	
	if doc.expense_type:
		remarks.append(f"Type: {doc.expense_type}")
	
	if doc.remarks:
		remarks.append(doc.remarks)
	
	return " | ".join(remarks) if remarks else f"Marketing Expense {doc.name}"


def get_default_cost_center(company):
	"""Get default cost center for company"""
	cost_center = frappe.get_cached_value("Company", company, "cost_center")
	
	if not cost_center:
		# Try to get first cost center for company
		cost_center = frappe.db.get_value("Cost Center", {
			"company": company,
			"is_group": 0
		}, "name")
	
	if not cost_center:
		frappe.throw(_("Please set default Cost Center for Company {0}").format(company))
	
	return cost_center


def get_default_payable_account(company):
	"""Get default payable account for marketing expenses"""
	
	# Try Marketing Hub Settings first
	settings = frappe.get_cached_doc("Marketing Hub Settings", company)
	if hasattr(settings, "default_payable_account") and settings.default_payable_account:
		return settings.default_payable_account
	
	# Try company default
	payable_account = frappe.get_cached_value("Company", company, "default_payable_account")
	
	if not payable_account:
		# Find any creditors account
		payable_account = frappe.db.get_value("Account", {
			"company": company,
			"account_type": "Payable",
			"is_group": 0
		}, "name")
	
	if not payable_account:
		frappe.throw(_("Please set default Payable Account for Company {0}").format(company))
	
	return payable_account


def validate_accounting_entries(doc):
	"""Validate accounting fields before submission"""
	
	# Validate expense account
	if doc.expense_account:
		account_details = frappe.db.get_value("Account", doc.expense_account, 
			["company", "is_group", "account_type"], as_dict=True)
		
		if not account_details:
			frappe.throw(_("Invalid Expense Account"))
		
		if account_details.company != doc.company:
			frappe.throw(_("Expense Account must belong to Company {0}").format(doc.company))
		
		if account_details.is_group:
			frappe.throw(_("Expense Account cannot be a group account"))
		
		if account_details.account_type != "Expense Account":
			frappe.throw(_("Please select an Expense type account"))
	
	# Validate payment account
	if doc.is_paid and doc.payment_account:
		account_details = frappe.db.get_value("Account", doc.payment_account,
			["company", "is_group", "account_type"], as_dict=True)
		
		if not account_details:
			frappe.throw(_("Invalid Payment Account"))
		
		if account_details.company != doc.company:
			frappe.throw(_("Payment Account must belong to Company {0}").format(doc.company))
		
		if account_details.is_group:
			frappe.throw(_("Payment Account cannot be a group account"))
		
		if account_details.account_type not in ["Bank", "Cash"]:
			frappe.throw(_("Payment Account must be of type Bank or Cash"))
	
	# Validate cost center
	if doc.cost_center:
		cost_center_company = frappe.get_cached_value("Cost Center", doc.cost_center, "company")
		if cost_center_company != doc.company:
			frappe.throw(_("Cost Center must belong to Company {0}").format(doc.company))
	
	# Validate project
	if doc.project:
		project_company = frappe.get_cached_value("Project", doc.project, "company")
		if project_company != doc.company:
			frappe.throw(_("Project must belong to Company {0}").format(doc.company))


def get_expense_account_from_category(expense_category, company):
	"""Get expense account from Marketing Expense Category"""
	
	if not expense_category:
		return None
	
	account = frappe.db.get_value("Marketing Expense Category", expense_category, "accounting_account")
	
	if account:
		# Verify account belongs to company
		account_company = frappe.get_cached_value("Account", account, "company")
		if account_company == company:
			return account
	
	return None


def create_payment_entry(marketing_expense):
	"""Create Payment Entry for Marketing Expense"""
	
	from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
	
	# This would be used if we want to create a separate payment entry
	# For now, GL entries handle immediate payment
	pass


def get_marketing_expense_summary(filters=None):
	"""
	Get summary of marketing expenses
	Used in reports and dashboards
	"""
	
	if not filters:
		filters = {}
	
	conditions = []
	values = []
	
	if filters.get("company"):
		conditions.append("company = %s")
		values.append(filters["company"])
	
	if filters.get("campaign"):
		conditions.append("campaign = %s")
		values.append(filters["campaign"])
	
	if filters.get("from_date"):
		conditions.append("posting_date >= %s")
		values.append(filters["from_date"])
	
	if filters.get("to_date"):
		conditions.append("posting_date <= %s")
		values.append(filters["to_date"])
	
	if filters.get("expense_category"):
		conditions.append("expense_category = %s")
		values.append(filters["expense_category"])
	
	where_clause = " AND ".join(conditions) if conditions else "1=1"
	
	query = f"""
		SELECT 
			expense_category,
			COUNT(*) as count,
			SUM(amount) as total_amount,
			AVG(amount) as avg_amount,
			SUM(CASE WHEN is_paid = 1 THEN amount ELSE 0 END) as paid_amount,
			SUM(CASE WHEN is_paid = 0 THEN amount ELSE 0 END) as unpaid_amount
		FROM `tabMarketing Expense`
		WHERE docstatus = 1 AND {where_clause}
		GROUP BY expense_category
		ORDER BY total_amount DESC
	"""
	
	return frappe.db.sql(query, tuple(values), as_dict=True)


def check_budget_exceeded(doc):
	"""Check if marketing expense exceeds budget"""
	
	if not doc.campaign:
		return False
	
	# Get campaign budget
	budget = frappe.db.get_value("Marketing Campaign", doc.campaign, ["budget", "total_spent"], as_dict=True)
	
	if not budget or not budget.budget:
		return False
	
	# Calculate total spent including this expense
	total_with_current = flt(budget.total_spent) + flt(doc.amount)
	
	if total_with_current > flt(budget.budget):
		budget_link = get_link_to_form("Marketing Campaign", doc.campaign)
		frappe.msgprint(
			_("Warning: This expense will cause Campaign {0} to exceed its budget of {1}. Total spent will be {2}").format(
				budget_link,
				frappe.utils.fmt_money(budget.budget, currency=doc.currency),
				frappe.utils.fmt_money(total_with_current, currency=doc.currency)
			),
			indicator="orange",
			alert=True
		)
		return True
	
	return False


def update_campaign_spent_amount(doc, method=None):
	"""Update Campaign's total_spent field"""
	
	if not doc.campaign:
		return
	
	# Calculate total spent for this campaign
	total_spent = frappe.db.sql("""
		SELECT SUM(amount)
		FROM `tabMarketing Expense`
		WHERE campaign = %s AND docstatus = 1
	""", doc.campaign)[0][0] or 0
	
	# Update campaign
	frappe.db.set_value("Marketing Campaign", doc.campaign, "total_spent", flt(total_spent), update_modified=False)
