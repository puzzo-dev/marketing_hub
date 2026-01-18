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
			"width": 180
		},
		{
			"fieldname": "campaign_name",
			"label": _("Campaign Name"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "channels_used",
			"label": _("Channels"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "created_date",
			"label": _("Created"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "impressions",
			"label": _("Impressions"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "clicks",
			"label": _("Clicks"),
			"fieldtype": "Int",
			"width": 80
		},
		{
			"fieldname": "ctr",
			"label": _("CTR %"),
			"fieldtype": "Percent",
			"width": 80
		},
		{
			"fieldname": "cost",
			"label": _("Cost"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "cpc",
			"label": _("CPC"),
			"fieldtype": "Currency",
			"width": 100
		},
		{
			"fieldname": "conversions",
			"label": _("Conversions"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "conversion_rate",
			"label": _("Conv. Rate %"),
			"fieldtype": "Percent",
			"width": 110
		},
		{
			"fieldname": "leads",
			"label": _("Leads"),
			"fieldtype": "Int",
			"width": 80
		},
		{
			"fieldname": "revenue",
			"label": _("Revenue"),
			"fieldtype": "Currency",
			"width": 120
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
			c.description,
			DATE(c.creation) as created_date
		FROM `tabCampaign` c
		WHERE c.docstatus < 2
		{conditions}
		ORDER BY c.creation DESC
	""".format(conditions=conditions), filters, as_dict=1)

	data = []

	for campaign in campaigns:
		# Get custom field: channels_used
		channels = frappe.db.get_value("Campaign", campaign.campaign, "channels_used") or ""

		row = {
			"campaign": campaign.campaign,
			"campaign_name": campaign.campaign_name,
			"channels_used": channels.replace("\n", ", ") if channels else "-",
			"created_date": campaign.created_date
		}

		# Get analytics data from Analytics Daily Log
		analytics = frappe.db.sql("""
			SELECT
				SUM(impressions) as impressions,
				SUM(clicks) as clicks,
				SUM(cost) as cost,
				SUM(conversions) as conversions
			FROM `tabAnalytics Daily Log`
			WHERE campaign = %s
		""", campaign.campaign, as_dict=1)

		if analytics and analytics[0].impressions:
			row["impressions"] = analytics[0].impressions or 0
			row["clicks"] = analytics[0].clicks or 0
			row["cost"] = analytics[0].cost or 0
			row["conversions"] = analytics[0].conversions or 0

			# Calculate CTR
			if row["impressions"] > 0:
				row["ctr"] = (row["clicks"] / row["impressions"]) * 100
			else:
				row["ctr"] = 0

			# Calculate CPC
			if row["clicks"] > 0:
				row["cpc"] = row["cost"] / row["clicks"]
			else:
				row["cpc"] = 0

			# Calculate conversion rate
			if row["clicks"] > 0:
				row["conversion_rate"] = (row["conversions"] / row["clicks"]) * 100
			else:
				row["conversion_rate"] = 0
		else:
			row["impressions"] = 0
			row["clicks"] = 0
			row["cost"] = 0
			row["conversions"] = 0
			row["ctr"] = 0
			row["cpc"] = 0
			row["conversion_rate"] = 0

		# Get leads count (attributed via UTM or campaign_name)
		leads_count = frappe.db.count("Lead", filters={
			"campaign_name": campaign.campaign
		})
		row["leads"] = leads_count

		# Get revenue from Sales Orders linked to campaign leads
		revenue_data = frappe.db.sql("""
			SELECT SUM(so.grand_total) as revenue
			FROM `tabSales Order` so
			WHERE so.campaign = %s
			AND so.docstatus = 1
		""", campaign.campaign, as_dict=1)

		row["revenue"] = revenue_data[0].revenue if revenue_data and revenue_data[0].revenue else 0

		# Calculate ROAS (Return on Ad Spend)
		if row["cost"] > 0:
			row["roas"] = row["revenue"] / row["cost"]
		else:
			row["roas"] = 0

		# Calculate ROI
		if row["cost"] > 0:
			row["roi"] = ((row["revenue"] - row["cost"]) / row["cost"]) * 100
		else:
			row["roi"] = 0

		data.append(row)

	return data


def get_conditions(filters):
	"""Build WHERE conditions from filters"""
	conditions = []

	if filters.get("campaign"):
		conditions.append("c.name = %(campaign)s")

	if filters.get("company"):
		conditions.append("c.company = %(company)s")

	if filters.get("from_date"):
		conditions.append("DATE(c.creation) >= %(from_date)s")

	if filters.get("to_date"):
		conditions.append("DATE(c.creation) <= %(to_date)s")

	return " AND " + " AND ".join(conditions) if conditions else ""
