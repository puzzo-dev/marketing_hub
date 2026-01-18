# Copyright (c) 2026, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	chart = get_chart_data(data, filters)

	return columns, data, None, chart


def get_columns(filters):
	"""Return columns for ROAS Analysis report"""
	group_by = filters.get("group_by", "Campaign")

	columns = []

	if group_by == "Campaign":
		columns.append({
			"fieldname": "campaign",
			"label": _("Campaign"),
			"fieldtype": "Link",
			"options": "Campaign",
			"width": 200
		})
		columns.append({
			"fieldname": "channels",
			"label": _("Channels"),
			"fieldtype": "Data",
			"width": 150
		})
	elif group_by == "Channel":
		columns.append({
			"fieldname": "channel",
			"label": _("Channel"),
			"fieldtype": "Data",
			"width": 150
		})
	elif group_by == "Month":
		columns.append({
			"fieldname": "month",
			"label": _("Month"),
			"fieldtype": "Data",
			"width": 120
		})

	# Common metrics columns
	columns.extend([
		{
			"fieldname": "spend",
			"label": _("Spend"),
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
			"fieldname": "roas",
			"label": _("ROAS"),
			"fieldtype": "Float",
			"width": 100,
			"precision": 2
		},
		{
			"fieldname": "impressions",
			"label": _("Impressions"),
			"fieldtype": "Int",
			"width": 110
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
			"fieldname": "cpc",
			"label": _("CPC"),
			"fieldtype": "Currency",
			"width": 100
		},
		{
			"fieldname": "leads",
			"label": _("Leads"),
			"fieldtype": "Int",
			"width": 80
		},
		{
			"fieldname": "cpl",
			"label": _("CPL"),
			"fieldtype": "Currency",
			"width": 100
		}
	])

	return columns


def get_data(filters):
	"""Get ROAS Analysis data based on grouping"""
	group_by = filters.get("group_by", "Campaign")

	if group_by == "Campaign":
		return get_campaign_data(filters)
	elif group_by == "Channel":
		return get_channel_data(filters)
	elif group_by == "Month":
		return get_monthly_data(filters)

	return []


def get_campaign_data(filters):
	"""Get ROAS data grouped by campaign"""
	conditions = get_conditions(filters)

	# Get campaigns
	campaigns = frappe.db.sql("""
		SELECT
			c.name as campaign,
			c.channels_used as channels
		FROM `tabCampaign` c
		WHERE c.docstatus = 0
		{conditions}
		ORDER BY c.start_date DESC
	""".format(conditions=conditions), filters, as_dict=1)

	data = []

	for campaign in campaigns:
		row = get_campaign_metrics(campaign.campaign)
		row["campaign"] = campaign.campaign
		row["channels"] = campaign.channels or ""

		# Only include if meets minimum ROAS threshold
		min_roas = filters.get("min_roas", 0)
		if row["roas"] >= min_roas:
			data.append(row)

	return data


def get_channel_data(filters):
	"""Get ROAS data grouped by channel"""
	# Get all campaigns within date range
	conditions = get_date_conditions(filters)

	campaigns = frappe.db.sql("""
		SELECT name, channels_used
		FROM `tabCampaign`
		WHERE docstatus = 0
		{conditions}
	""".format(conditions=conditions), filters, as_dict=1)

	# Aggregate by channel
	channel_data = {}

	for campaign in campaigns:
		channels = (campaign.channels_used or "").split(",")
		metrics = get_campaign_metrics(campaign.name)

		for channel in channels:
			channel = channel.strip()
			if not channel:
				continue

			if channel not in channel_data:
				channel_data[channel] = {
					"channel": channel,
					"spend": 0,
					"revenue": 0,
					"impressions": 0,
					"clicks": 0,
					"leads": 0
				}

			# Divide metrics equally among channels
			channel_count = len([c for c in channels if c.strip()])
			channel_data[channel]["spend"] += metrics["spend"] / channel_count
			channel_data[channel]["revenue"] += metrics["revenue"] / channel_count
			channel_data[channel]["impressions"] += metrics["impressions"] / channel_count
			channel_data[channel]["clicks"] += metrics["clicks"] / channel_count
			channel_data[channel]["leads"] += metrics["leads"] / channel_count

	# Calculate derived metrics
	data = []
	for channel, metrics in channel_data.items():
		metrics["roas"] = metrics["revenue"] / metrics["spend"] if metrics["spend"] > 0 else 0
		metrics["ctr"] = (metrics["clicks"] / metrics["impressions"]) * 100 if metrics["impressions"] > 0 else 0
		metrics["cpc"] = metrics["spend"] / metrics["clicks"] if metrics["clicks"] > 0 else 0
		metrics["cpl"] = metrics["spend"] / metrics["leads"] if metrics["leads"] > 0 else 0

		# Apply minimum ROAS filter
		min_roas = filters.get("min_roas", 0)
		if metrics["roas"] >= min_roas:
			data.append(metrics)

	# Sort by ROAS descending
	data.sort(key=lambda x: x["roas"], reverse=True)

	return data


def get_monthly_data(filters):
	"""Get ROAS data grouped by month"""
	# Get analytics data grouped by month
	date_conditions = get_date_conditions(filters)

	monthly_data = frappe.db.sql("""
		SELECT
			DATE_FORMAT(date, '%%Y-%%m') as month,
			SUM(spend) as spend,
			SUM(impressions) as impressions,
			SUM(clicks) as clicks
		FROM `tabAnalytics Daily Log`
		WHERE 1=1
		{conditions}
		GROUP BY DATE_FORMAT(date, '%%Y-%%m')
		ORDER BY month DESC
	""".format(conditions=date_conditions), filters, as_dict=1)

	data = []

	for row in monthly_data:
		# Get revenue and leads for this month
		month_start = row.month + "-01"
		month_end = frappe.utils.get_last_day(month_start).strftime("%Y-%m-%d")

		revenue_data = frappe.db.sql("""
			SELECT
				COUNT(DISTINCT l.name) as leads,
				COALESCE(SUM(so.grand_total), 0) as revenue
			FROM `tabLead` l
			LEFT JOIN `tabSales Order` so ON so.party_name = l.name AND so.docstatus = 1
			WHERE l.creation BETWEEN %s AND %s
		""", (month_start, month_end), as_dict=1)

		row["revenue"] = revenue_data[0].revenue if revenue_data else 0
		row["leads"] = revenue_data[0].leads if revenue_data else 0

		# Calculate metrics
		row["roas"] = row["revenue"] / row["spend"] if row["spend"] > 0 else 0
		row["ctr"] = (row["clicks"] / row["impressions"]) * 100 if row["impressions"] > 0 else 0
		row["cpc"] = row["spend"] / row["clicks"] if row["clicks"] > 0 else 0
		row["cpl"] = row["spend"] / row["leads"] if row["leads"] > 0 else 0

		# Format month for display
		row["month"] = frappe.utils.formatdate(month_start, "MMM YYYY")

		# Apply minimum ROAS filter
		min_roas = filters.get("min_roas", 0)
		if row["roas"] >= min_roas:
			data.append(row)

	return data


def get_campaign_metrics(campaign):
	"""Get metrics for a single campaign"""
	# Get spend and engagement from Analytics Daily Log
	analytics = frappe.db.sql("""
		SELECT
			SUM(spend) as spend,
			SUM(impressions) as impressions,
			SUM(clicks) as clicks
		FROM `tabAnalytics Daily Log`
		WHERE campaign = %s
	""", campaign, as_dict=1)

	metrics = {
		"spend": analytics[0].spend if analytics and analytics[0].spend else 0,
		"impressions": analytics[0].impressions if analytics and analytics[0].impressions else 0,
		"clicks": analytics[0].clicks if analytics and analytics[0].clicks else 0
	}

	# Get leads count
	leads_count = frappe.db.count("Lead", filters={"campaign_name": campaign})
	metrics["leads"] = leads_count

	# Get revenue from Sales Orders
	revenue = frappe.db.sql("""
		SELECT COALESCE(SUM(so.grand_total), 0) as revenue
		FROM `tabSales Order` so
		INNER JOIN `tabLead` l ON so.party_name = l.name
		WHERE l.campaign_name = %s
		AND so.docstatus = 1
	""", campaign, as_dict=1)

	metrics["revenue"] = revenue[0].revenue if revenue else 0

	# Calculate derived metrics
	metrics["roas"] = metrics["revenue"] / metrics["spend"] if metrics["spend"] > 0 else 0
	metrics["ctr"] = (metrics["clicks"] / metrics["impressions"]) * 100 if metrics["impressions"] > 0 else 0
	metrics["cpc"] = metrics["spend"] / metrics["clicks"] if metrics["clicks"] > 0 else 0
	metrics["cpl"] = metrics["spend"] / metrics["leads"] if metrics["leads"] > 0 else 0

	return metrics


def get_conditions(filters):
	"""Build WHERE conditions for campaigns"""
	conditions = []

	if filters.get("campaign"):
		conditions.append("c.name = %(campaign)s")

	if filters.get("from_date"):
		conditions.append("c.start_date >= %(from_date)s")

	if filters.get("to_date"):
		conditions.append("c.end_date <= %(to_date)s")

	return " AND " + " AND ".join(conditions) if conditions else ""


def get_date_conditions(filters):
	"""Build WHERE conditions for date range"""
	conditions = []

	if filters.get("from_date"):
		conditions.append("date >= %(from_date)s")

	if filters.get("to_date"):
		conditions.append("date <= %(to_date)s")

	return " AND " + " AND ".join(conditions) if conditions else ""


def get_chart_data(data, filters):
	"""Generate chart for ROAS visualization"""
	if not data:
		return None

	group_by = filters.get("group_by", "Campaign")

	labels = []
	roas_values = []

	for row in data[:10]:  # Limit to top 10
		if group_by == "Campaign":
			labels.append(row.get("campaign", "")[:20])
		elif group_by == "Channel":
			labels.append(row.get("channel", ""))
		elif group_by == "Month":
			labels.append(row.get("month", ""))

		roas_values.append(row.get("roas", 0))

	return {
		"data": {
			"labels": labels,
			"datasets": [
				{
					"name": "ROAS",
					"values": roas_values
				}
			]
		},
		"type": "bar",
		"height": 300,
		"colors": ["#f39c12"]
	}
