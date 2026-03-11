# Copyright (c) 2026, Puxxo and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data, filters)
	
	return columns, data, None, chart


def get_columns():
	"""Return report columns"""
	return [
		{
			"fieldname": "campaign_name",
			"label": _("Campaign"),
			"fieldtype": "Link",
			"options": "Marketing Campaign",
			"width": 200
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "budget_amount",
			"label": _("Budget"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "actual_spent",
			"label": _("Actual Spent"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "variance",
			"label": _("Variance"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "variance_percentage",
			"label": _("Variance %"),
			"fieldtype": "Percent",
			"width": 100
		},
		{
			"fieldname": "utilization_percentage",
			"label": _("Budget Utilization %"),
			"fieldtype": "Percent",
			"width": 130
		},
		{
			"fieldname": "total_leads",
			"label": _("Leads Generated"),
			"fieldtype": "Int",
			"width": 110
		},
		{
			"fieldname": "cost_per_lead",
			"label": _("Cost per Lead"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "revenue",
			"label": _("Revenue"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "roi_percentage",
			"label": _("ROI %"),
			"fieldtype": "Percent",
			"width": 100
		}
	]


def get_data(filters):
	"""Get report data"""
	conditions = get_conditions(filters)
	
	# Get campaigns with budget
	campaigns = frappe.db.sql(f"""
		SELECT
			name as campaign_name,
			campaign_name as title,
			status
		FROM `tabMarketing Campaign`
		WHERE 1=1
		{conditions}
		ORDER BY name DESC
	""", filters, as_dict=1)
	
	for campaign in campaigns:
		# Get budget from Campaign
		budget = frappe.db.get_value("Marketing Campaign", campaign.campaign_name, "budget") or 0
		campaign["budget_amount"] = flt(budget)
		
		# Get actual spent from Marketing Expenses
		actual_spent = frappe.db.sql("""
			SELECT COALESCE(SUM(amount), 0)
			FROM `tabMarketing Expense`
			WHERE campaign = %s
			AND docstatus = 1
		""", campaign.campaign_name)[0][0] or 0
		campaign["actual_spent"] = flt(actual_spent)
		
		# Calculate variance
		campaign["variance"] = flt(campaign["budget_amount"]) - flt(actual_spent)
		
		# Calculate variance percentage
		if campaign["budget_amount"]:
			campaign["variance_percentage"] = (campaign["variance"] / campaign["budget_amount"]) * 100
			campaign["utilization_percentage"] = (actual_spent / campaign["budget_amount"]) * 100
		else:
			campaign["variance_percentage"] = 0
			campaign["utilization_percentage"] = 0
		
		# Get leads generated
		total_leads = frappe.db.count("Lead", filters={"campaign_name": campaign.campaign_name})
		campaign["total_leads"] = total_leads
		
		# Calculate cost per lead
		if total_leads > 0:
			campaign["cost_per_lead"] = actual_spent / total_leads
		else:
			campaign["cost_per_lead"] = 0
		
		# Get revenue (from Opportunities or Sales Orders)
		revenue = frappe.db.sql("""
			SELECT COALESCE(SUM(grand_total), 0)
			FROM `tabSales Order`
			WHERE docstatus = 1
			AND EXISTS (
				SELECT 1 FROM `tabLead`
				WHERE name = `tabSales Order`.customer
				AND campaign_name = %s
			)
		""", campaign.campaign_name)[0][0] or 0
		campaign["revenue"] = flt(revenue)
		
		# Calculate ROI
		if actual_spent > 0:
			campaign["roi_percentage"] = ((revenue - actual_spent) / actual_spent) * 100
		else:
			campaign["roi_percentage"] = 0
	
	return campaigns


def get_conditions(filters):
	"""Build WHERE conditions"""
	conditions = []
	
	if filters.get("company"):
		conditions.append("AND company = %(company)s")
	
	if filters.get("status"):
		conditions.append("AND status = %(status)s")
	
	if filters.get("from_date"):
		conditions.append("AND creation >= %(from_date)s")
	
	if filters.get("to_date"):
		conditions.append("AND creation <= %(to_date)s")
	
	return " ".join(conditions)


def get_chart_data(data, filters):
	"""Generate chart data for visualization"""
	
	if not data:
		return None
	
	# Prepare data for chart - Budget vs Actual
	labels = []
	budget_values = []
	actual_values = []
	
	for row in data[:10]:  # Top 10 campaigns
		labels.append(row.get("campaign_name"))
		budget_values.append(flt(row.get("budget_amount", 0)))
		actual_values.append(flt(row.get("actual_spent", 0)))
	
	return {
		"data": {
			"labels": labels,
			"datasets": [
				{
					"name": _("Budget"),
					"values": budget_values
				},
				{
					"name": _("Actual Spent"),
					"values": actual_values
				}
			]
		},
		"type": "bar",
		"colors": ["#98D8C8", "#F7464A"],
		"axisOptions": {
			"xAxisMode": "tick",
			"xIsSeries": 1
		},
		"barOptions": {
			"stacked": 0,
			"spaceRatio": 0.3
		}
	}
