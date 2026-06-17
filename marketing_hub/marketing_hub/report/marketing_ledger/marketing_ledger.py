# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	"""Return columns and data for Marketing Ledger report"""
	columns = get_columns()
	data = get_data(filters)

	return columns, data


def get_columns():
	"""Return report columns"""
	return [
		{
			"fieldname": "posting_date",
			"label": _("Posting Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "name",
			"label": _("Expense ID"),
			"fieldtype": "Link",
			"options": "Marketing Expense",
			"width": 150
		},
		{
			"fieldname": "campaign",
			"label": _("Campaign"),
			"fieldtype": "Link",
			"options": "Marketing Campaign",
			"width": 150
		},
		{
			"fieldname": "expense_category",
			"label": _("Category"),
			"fieldtype": "Data",
			"width": 130
		},
		{
			"fieldname": "expense_type",
			"label": _("Type"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "expense_account",
			"label": _("Account"),
			"fieldtype": "Link",
			"options": "Account",
			"width": 150
		},
		{
			"fieldname": "cost_center",
			"label": _("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"width": 120
		},
		{
			"fieldname": "project",
			"label": _("Project"),
			"fieldtype": "Link",
			"options": "Project",
			"width": 120
		},
		{
			"fieldname": "amount",
			"label": _("Amount"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "currency",
			"label": _("Currency"),
			"fieldtype": "Link",
			"options": "Currency",
			"width": 80
		},
		{
			"fieldname": "is_paid",
			"label": _("Paid"),
			"fieldtype": "Check",
			"width": 70
		},
		{
			"fieldname": "payment_account",
			"label": _("Payment Account"),
			"fieldtype": "Link",
			"options": "Account",
			"width": 150
		},
		{
			"fieldname": "gl_entry_posted",
			"label": _("GL Posted"),
			"fieldtype": "Check",
			"width": 80
		},
		{
			"fieldname": "remarks",
			"label": _("Remarks"),
			"fieldtype": "Small Text",
			"width": 200
		}
	]


def get_data(filters):
	"""Return report data"""
	conditions = get_conditions(filters)

	data = frappe.db.sql(f"""
		SELECT
			posting_date,
			name,
			campaign,
			expense_category,
			expense_type,
			expense_account,
			cost_center,
			project,
			amount,
			currency,
			is_paid,
			payment_account,
			gl_entry_posted,
			remarks
		FROM `tabMarketing Expense`
		WHERE docstatus = 1
		{conditions}
		ORDER BY posting_date DESC, name DESC
	""", filters, as_dict=1)

	return data


def get_conditions(filters):
	"""Build SQL conditions from filters"""
	conditions = []

	if filters.get("company"):
		conditions.append("company = %(company)s")

	if filters.get("from_date"):
		conditions.append("posting_date >= %(from_date)s")

	if filters.get("to_date"):
		conditions.append("posting_date <= %(to_date)s")

	if filters.get("campaign"):
		conditions.append("campaign = %(campaign)s")

	if filters.get("expense_category"):
		conditions.append("expense_category = %(expense_category)s")

	if filters.get("cost_center"):
		conditions.append("cost_center = %(cost_center)s")

	if filters.get("project"):
		conditions.append("project = %(project)s")

	if filters.get("expense_account"):
		conditions.append("expense_account = %(expense_account)s")

	return " AND " + " AND ".join(conditions) if conditions else ""
