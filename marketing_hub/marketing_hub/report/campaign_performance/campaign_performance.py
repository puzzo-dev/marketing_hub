# Copyright (c) 2026, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)

	return columns, data


def get_columns():
	"""Return columns for Campaign Performance report"""
	return [
		{
			"fieldname": "campaign",
			"label": _("Campaign"),
			"fieldtype": "Link",
			"options": "Campaign",
			"width": 200
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "start_date",
			"label": _("Start Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "end_date",
			"label": _("End Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "budget",
			"label": _("Budget"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "spend",
			"label": _("Spend"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "leads",
			"label": _("Leads"),
			"fieldtype": "Int",
			"width": 80
		},
		{
			"fieldname": "opportunities",
			"label": _("Opportunities"),
			"fieldtype": "Int",
			"width": 120
		},
		{
			"fieldname": "quotations",
			"label": _("Quotations"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "sales_orders",
			"label": _("Sales Orders"),
			"fieldtype": "Int",
			"width": 120
		},
		{
			"fieldname": "revenue",
			"label": _("Revenue"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "conversion_rate",
			"label": _("Conv. Rate %"),
			"fieldtype": "Percent",
			"width": 110
		},
		{
			"fieldname": "roas",
			"label": _("ROAS"),
			"fieldtype": "Float",
			"width": 80,
			"precision": 2
		},
		{
			"fieldname": "roi",
			"label": _("ROI %"),
			"fieldtype": "Percent",
			"width": 80
		}
	]


def get_data(filters):
	"""Get Campaign Performance data"""
	conditions = get_conditions(filters)

	# Get campaigns with basic data
	campaigns = frappe.db.sql("""
		SELECT
			c.name as campaign,
			c.campaign_name,
			c.status,
			c.start_date,
			c.end_date,
			c.budget,
			c.description
		FROM `tabCampaign` c
		WHERE c.docstatus = 0
		{conditions}
		ORDER BY c.start_date DESC
	""".format(conditions=conditions), filters, as_dict=1)

	data = []

	for campaign in campaigns:
		row = {
			"campaign": campaign.campaign,
			"status": campaign.status,
			"start_date": campaign.start_date,
			"end_date": campaign.end_date,
			"budget": campaign.budget or 0
		}

		# Get spend from Analytics Daily Log
		spend = frappe.db.sql("""
			SELECT SUM(spend) as total_spend
			FROM `tabAnalytics Daily Log`
			WHERE campaign = %s
		""", campaign.campaign, as_dict=1)

		row["spend"] = spend[0].total_spend if spend and spend[0].total_spend else 0

		# Get leads count
		leads_count = frappe.db.count("Lead", filters={"campaign_name": campaign.campaign})
		row["leads"] = leads_count

		# Get opportunities count (via Lead)
		opportunities_count = frappe.db.sql("""
			SELECT COUNT(DISTINCT o.name) as count
			FROM `tabOpportunity` o
			INNER JOIN `tabLead` l ON o.party_name = l.name
			WHERE l.campaign_name = %s
			AND o.opportunity_from = 'Lead'
		""", campaign.campaign, as_dict=1)

		row["opportunities"] = opportunities_count[0].count if opportunities_count else 0

		# Get quotations count (via Lead)
		quotations_count = frappe.db.sql("""
			SELECT COUNT(DISTINCT q.name) as count
			FROM `tabQuotation` q
			INNER JOIN `tabLead` l ON q.party_name = l.name
			WHERE l.campaign_name = %s
			AND q.quotation_to = 'Lead'
		""", campaign.campaign, as_dict=1)

		row["quotations"] = quotations_count[0].count if quotations_count else 0

		# Get sales orders count and revenue (via Lead)
		sales_data = frappe.db.sql("""
			SELECT
				COUNT(DISTINCT so.name) as count,
				SUM(so.grand_total) as revenue
			FROM `tabSales Order` so
			INNER JOIN `tabLead` l ON so.party_name = l.name
			WHERE l.campaign_name = %s
			AND so.customer = l.name
			AND so.docstatus = 1
		""", campaign.campaign, as_dict=1)

		row["sales_orders"] = sales_data[0].count if sales_data and sales_data[0].count else 0
		row["revenue"] = sales_data[0].revenue if sales_data and sales_data[0].revenue else 0

		# Calculate conversion rate (Leads to Sales Orders)
		if row["leads"] > 0:
			row["conversion_rate"] = (row["sales_orders"] / row["leads"]) * 100
		else:
			row["conversion_rate"] = 0

		# Calculate ROAS (Return on Ad Spend)
		if row["spend"] > 0:
			row["roas"] = row["revenue"] / row["spend"]
		else:
			row["roas"] = 0

		# Calculate ROI
		if row["spend"] > 0:
			row["roi"] = ((row["revenue"] - row["spend"]) / row["spend"]) * 100
		else:
			row["roi"] = 0

		data.append(row)

	return data


def get_conditions(filters):
	"""Build WHERE conditions from filters"""
	conditions = []

	if filters.get("campaign"):
		conditions.append("c.name = %(campaign)s")

	if filters.get("status"):
		conditions.append("c.status = %(status)s")

	if filters.get("from_date"):
		conditions.append("c.start_date >= %(from_date)s")

	if filters.get("to_date"):
		conditions.append("c.end_date <= %(to_date)s")

	return " AND " + " AND ".join(conditions) if conditions else ""
