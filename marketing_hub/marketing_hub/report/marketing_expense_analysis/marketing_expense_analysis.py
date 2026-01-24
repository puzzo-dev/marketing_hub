# Copyright (c) 2026, Puxxo and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data, filters)
	
	return columns, data, None, chart


def get_columns():
	"""Return report columns"""
	return [
		{
			"fieldname": "posting_date",
			"label": _("Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "name",
			"label": _("Expense ID"),
			"fieldtype": "Link",
			"options": "Marketing Expense",
			"width": 130
		},
		{
			"fieldname": "campaign",
			"label": _("Campaign"),
			"fieldtype": "Link",
			"options": "Campaign",
			"width": 150
		},
		{
			"fieldname": "expense_category",
			"label": _("Category"),
			"fieldtype": "Link",
			"options": "Marketing Expense Category",
			"width": 150
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
			"fieldname": "amount",
			"label": _("Amount"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "is_paid",
			"label": _("Paid"),
			"fieldtype": "Check",
			"width": 80
		},
		{
			"fieldname": "payment_account",
			"label": _("Payment Account"),
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
			"fieldname": "gl_entry_posted",
			"label": _("GL Posted"),
			"fieldtype": "Check",
			"width": 90
		}
	]


def get_data(filters):
	"""Get report data"""
	conditions = get_conditions(filters)
	
	data = frappe.db.sql(f"""
		SELECT
			posting_date,
			name,
			campaign,
			expense_category,
			expense_type,
			expense_account,
			amount,
			is_paid,
			payment_account,
			cost_center,
			project,
			gl_entry_posted,
			company
		FROM `tabMarketing Expense`
		WHERE docstatus = 1
		{conditions}
		ORDER BY posting_date DESC, name DESC
	""", filters, as_dict=1)
	
	return data


def get_conditions(filters):
	"""Build WHERE conditions"""
	conditions = []
	
	if filters.get("company"):
		conditions.append("AND company = %(company)s")
	
	if filters.get("campaign"):
		conditions.append("AND campaign = %(campaign)s")
	
	if filters.get("expense_category"):
		conditions.append("AND expense_category = %(expense_category)s")
	
	if filters.get("from_date"):
		conditions.append("AND posting_date >= %(from_date)s")
	
	if filters.get("to_date"):
		conditions.append("AND posting_date <= %(to_date)s")
	
	if filters.get("is_paid") is not None:
		conditions.append("AND is_paid = %(is_paid)s")
	
	if filters.get("cost_center"):
		conditions.append("AND cost_center = %(cost_center)s")
	
	if filters.get("project"):
		conditions.append("AND project = %(project)s")
	
	return " ".join(conditions)


def get_chart_data(data, filters):
	"""Generate chart data for visualization"""
	
	if not data:
		return None
	
	# Group by category
	category_totals = {}
	for row in data:
		category = row.get("expense_category") or "Uncategorized"
		category_totals[category] = category_totals.get(category, 0) + flt(row.get("amount", 0))
	
	# Sort by amount
	sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
	
	return {
		"data": {
			"labels": [cat[0] for cat in sorted_categories[:10]],  # Top 10
			"datasets": [
				{
					"name": _("Total Expenses"),
					"values": [cat[1] for cat in sorted_categories[:10]]
				}
			]
		},
		"type": "bar",
		"colors": ["#4C9AFF"],
		"axisOptions": {
			"xAxisMode": "tick",
			"xIsSeries": 1
		},
		"barOptions": {
			"stacked": 0,
			"spaceRatio": 0.5
		}
	}
