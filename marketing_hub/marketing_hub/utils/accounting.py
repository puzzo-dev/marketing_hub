# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Accounting and Ledger utilities for Marketing Hub
"""

import frappe
from frappe import _
from frappe.utils import flt, getdate

from erpnext.accounts.general_ledger import make_gl_entries as _make_gl_entries
from erpnext.accounts.doctype.budget.budget import validate_expense_against_budget


def make_gl_entries(doc, cancel=False):
    """Wrapper for make_marketing_gl_entry compatible with Marketing Expense calls"""
    return make_marketing_gl_entry(
        voucher_type=doc.doctype,
        voucher_no=doc.name,
        company=doc.company,
        posting_date=doc.posting_date,
        expense_account=doc.expense_account,
        amount=doc.amount,
        cost_center=doc.cost_center,
        campaign=doc.campaign,
        cancel=cancel
    )

def validate_accounting_entries(doc):
    """Validate basic accounting rules"""
    if not doc.company:
        frappe.throw(_("Company is required"))
    if doc.amount <= 0:
        frappe.throw(_("Amount must be greater than zero"))

def get_expense_account_from_category(category, company):
    """Get expense account linked to category"""
    # Assuming Marketing Expense Category has a link to Account or default
    if frappe.db.has_column("Marketing Expense Category", "default_account"):
         return frappe.db.get_value("Marketing Expense Category", category, "default_account")
    return None

def check_budget_exceeded(doc):
    """Check if expense exceeds campaign budget"""
    if not doc.campaign:
        return

    settings = get_marketing_hub_settings(doc.company)
    if not settings or not settings.validate_budget:
        return

    campaign = frappe.get_doc("Marketing Campaign", doc.campaign)
    if not campaign.budget:
        # No budget set, assume unlimited? or strict? usually unlimited.
        return

    # Calculate current total spent (excluding this doc if it's new, but including if submitting)
    # Actually for 'before_submit', this doc is not in GL yet.
    current_spent = flt(campaign.total_actual_cost) # Assuming field exists
    
    if (current_spent + flt(doc.amount)) > flt(campaign.budget):
        frappe.throw(
            _("Campaign Budget Exceeded. Budget: {0}, Spent: {1}, This Expense: {2}").format(
                campaign.budget, current_spent, doc.amount
            )
        )

def update_campaign_spent_amount(doc):
    """Update total spend on Campaign"""
    if not doc.campaign:
        return
        
    # Recalculate from expenses to be safe
    total = frappe.db.sql("""
        SELECT SUM(amount) FROM `tabMarketing Expense`
        WHERE campaign=%s AND docstatus=1
    """, doc.campaign)[0][0] or 0
    
    frappe.db.set_value("Campaign", doc.campaign, "total_actual_cost", flt(total))

def make_marketing_gl_entry(
	voucher_type,
	voucher_no,
	company,
	posting_date,
	expense_account,
	amount,
	payment_account=None,
	cost_center=None,
	project=None,
	campaign=None,
	remarks=None,
	cancel=False
):
	"""
	Create General Ledger entries for marketing expenses

	Args:
		voucher_type: Document type (e.g., "Campaign", "Marketing Expense")
		voucher_no: Document name
		company: Company name
		posting_date: Posting date
		expense_account: Marketing expense account
		amount: Expense amount
		payment_account: Payment/credit account (optional)
		cost_center: Cost center (optional)
		project: Project (optional)
		campaign: Campaign (optional)
		remarks: Additional remarks (optional)
		cancel: Cancel entries if True

	Returns:
		List of GL entries created
	"""

	# Get settings
	settings = get_marketing_hub_settings(company)

	# Validate settings
	if not settings:
		frappe.throw(_("Marketing Hub Settings not found for company {0}").format(company))

	if not settings.enable_gl_entry:
		return []

	# Use default accounts from settings if not provided
	if not expense_account:
		expense_account = settings.default_expense_account

	if not cost_center:
		cost_center = settings.default_cost_center

	if not expense_account:
		frappe.throw(_("Marketing Expense Account not set in Marketing Hub Settings"))

	# Get currency
	currency = frappe.get_cached_value("Company", company, "default_currency")

	# Build GL entries
	gl_entries = []

	# Expense entry (Debit)
	gl_entries.append({
		"posting_date": getdate(posting_date),
		"account": expense_account,
		"debit": flt(amount),
		"debit_in_account_currency": flt(amount),
		"against": payment_account or "TBD",
		"cost_center": cost_center,
		"project": project,
		"voucher_type": voucher_type,
		"voucher_no": voucher_no,
		"company": company,
		"account_currency": currency,
		"remarks": remarks or f"Marketing expense from {voucher_type}",
	})

	# Payment entry (Credit) if payment account specified
	if payment_account:
		gl_entries.append({
			"posting_date": getdate(posting_date),
			"account": payment_account,
			"credit": flt(amount),
			"credit_in_account_currency": flt(amount),
			"against": expense_account,
			"cost_center": cost_center,
			"project": project,
			"voucher_type": voucher_type,
			"voucher_no": voucher_no,
			"company": company,
			"account_currency": currency,
			"remarks": remarks or f"Payment for marketing expense from {voucher_type}",
		})

	# Validate against budget if enabled
	# Note: validate_expense_against_budget checks ERPNext Cost Center Budgets.
	# Our check_budget_exceeded checks CAMPAIGN budgets. Both are valid.
	if settings.validate_budget and not cancel:
		validate_expense_against_budget(
			{
				"account": expense_account,
				"cost_center": cost_center,
				"company": company,
			},
			{"posting_date": getdate(posting_date), "doctype": voucher_type}
		)

	# Make GL entries
	if gl_entries:
		_make_gl_entries(gl_entries, cancel=cancel, adv_adj=False)

	return gl_entries


def get_marketing_hub_settings(company):
	"""Get Marketing Hub Settings for a company"""
	try:
		return frappe.get_single("Marketing Hub Settings")
	except frappe.DoesNotExistError:
		return None


def get_marketing_expense_account(company):
	"""Get default marketing expense account"""
	settings = get_marketing_hub_settings(company)
	return settings.default_expense_account if settings else None


def get_marketing_cost_center(company):
	"""Get default marketing cost center"""
	settings = get_marketing_hub_settings(company)
	return settings.default_cost_center if settings else None


@frappe.whitelist()
def get_campaign_ledger_summary(campaign, company=None):
	"""
	Get ledger summary for a campaign

	Args:
		campaign: Campaign name
		company: Company name (optional)

	Returns:
		dict: Summary with total expenses, budget, and utilization
	"""
	if not company:
		campaign_doc = frappe.get_doc("Marketing Campaign", campaign)
		company = campaign_doc.company if hasattr(campaign_doc, 'company') else None

	# Get total expenses from Marketing Expense
	total_expenses = frappe.db.sql("""
		SELECT SUM(amount) as total
		FROM `tabMarketing Expense`
		WHERE campaign = %s
		AND docstatus = 1
		{company_filter}
	""".format(
		company_filter="AND company = %(company)s" if company else ""
	), {"campaign": campaign, "company": company}, as_dict=1)[0].total or 0

	# Get campaign budget
	campaign_doc = frappe.get_doc("Marketing Campaign", campaign)
	budget = campaign_doc.budget if hasattr(campaign_doc, 'budget') else 0

	# Calculate utilization
	utilization = (total_expenses / budget * 100) if budget else 0
	remaining = budget - total_expenses if budget else None

	return {
		"campaign": campaign,
		"company": company,
		"total_expenses": total_expenses,
		"budget": budget,
		"remaining": remaining,
		"utilization_percentage": utilization,
		"over_budget": total_expenses > budget if budget else False
	}


@frappe.whitelist()
def get_marketing_ledger_summary(company, from_date=None, to_date=None):
	"""
	Get overall marketing ledger summary for a company

	Args:
		company: Company name
		from_date: Start date (optional)
		to_date: End date (optional)

	Returns:
		dict: Summary with total expenses by category
	"""
	filters = {"company": company, "docstatus": 1}

	if from_date:
		filters["posting_date"] = [">=", from_date]
	if to_date:
		if "posting_date" in filters:
			filters["posting_date"] = ["between", [from_date, to_date]]
		else:
			filters["posting_date"] = ["<=", to_date]

	# Get expenses by category
	expenses_by_category = frappe.db.sql("""
		SELECT
			expense_category,
			SUM(amount) as total,
			COUNT(*) as count
		FROM `tabMarketing Expense`
		WHERE company = %(company)s
		AND docstatus = 1
		{date_filter}
		GROUP BY expense_category
		ORDER BY total DESC
	""".format(
		date_filter=get_date_filter_sql(from_date, to_date)
	), {"company": company, "from_date": from_date, "to_date": to_date}, as_dict=1)

	# Get total
	total_expenses = sum(row.total for row in expenses_by_category)

	return {
		"company": company,
		"from_date": from_date,
		"to_date": to_date,
		"total_expenses": total_expenses,
		"expenses_by_category": expenses_by_category,
		"category_count": len(expenses_by_category)
	}


def get_date_filter_sql(from_date, to_date):
	"""Build date filter SQL"""
	if from_date and to_date:
		return "AND posting_date BETWEEN %(from_date)s AND %(to_date)s"
	elif from_date:
		return "AND posting_date >= %(from_date)s"
	elif to_date:
		return "AND posting_date <= %(to_date)s"
	return ""
