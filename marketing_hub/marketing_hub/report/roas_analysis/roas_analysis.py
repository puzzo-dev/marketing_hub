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
			"options": "Marketing Campaign",
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
	"""Get ROAS data grouped by campaign using bulk aggregation"""
	conditions = get_conditions(filters)

	# Get campaigns
	campaigns = frappe.db.sql(f"""
		SELECT
			c.name as campaign
		FROM `tabMarketing Campaign` c
		WHERE c.docstatus < 2
		{conditions}
		ORDER BY c.creation DESC
	""", filters, as_dict=1)

	if not campaigns:
		return []

	campaign_names = [c.campaign for c in campaigns]

	# Bulk fetch all metrics in 3 queries
	metrics_map = get_bulk_campaign_metrics(campaign_names)

	# Bulk fetch channels
	channel_rows = frappe.db.sql("""
		SELECT parent, social_media_network
		FROM `tabMarketing Campaign Channel`
		WHERE parenttype = 'Marketing Campaign'
		AND parent IN %(campaigns)s
	""", {"campaigns": campaign_names}, as_dict=1)

	channels_map = {}
	for row in channel_rows:
		channels_map.setdefault(row.parent, []).append(row.social_media_network)

	data = []
	for campaign in campaigns:
		row = metrics_map.get(campaign.campaign, {})
		row["campaign"] = campaign.campaign
		row["channels"] = ", ".join(channels_map.get(campaign.campaign, [])) or "-"

		min_roas = filters.get("min_roas", 0)
		if row.get("roas", 0) >= min_roas:
			data.append(row)

	return data


def get_bulk_campaign_metrics(campaign_names):
	"""Fetch metrics for multiple campaigns in bulk (3 queries total)"""
	if not campaign_names:
		return {}

	# 1. Analytics aggregation
	analytics = frappe.db.sql("""
		SELECT
			campaign,
			SUM(spend) as spend,
			SUM(impressions) as impressions,
			SUM(clicks) as clicks
		FROM `tabAnalytics Daily Log`
		WHERE campaign IN %(campaigns)s
		GROUP BY campaign
	""", {"campaigns": campaign_names}, as_dict=1)

	analytics_map = {a.campaign: a for a in analytics}

	# 2. Leads count
	leads = frappe.db.sql("""
		SELECT campaign_name as campaign, COUNT(*) as leads
		FROM `tabLead`
		WHERE campaign_name IN %(campaigns)s
		GROUP BY campaign_name
	""", {"campaigns": campaign_names}, as_dict=1)

	leads_map = {l.campaign: l.leads for l in leads}

	# 3. Revenue from Sales Orders
	revenue = frappe.db.sql("""
		SELECT campaign, COALESCE(SUM(grand_total), 0) as revenue
		FROM `tabSales Order`
		WHERE campaign IN %(campaigns)s
		AND docstatus = 1
		GROUP BY campaign
	""", {"campaigns": campaign_names}, as_dict=1)

	revenue_map = {r.campaign: r.revenue for r in revenue}

	# Build metrics map
	metrics_map = {}
	for name in campaign_names:
		spend = analytics_map.get(name, {}).get("spend") or 0
		impressions = analytics_map.get(name, {}).get("impressions") or 0
		clicks = analytics_map.get(name, {}).get("clicks") or 0
		leads_count = leads_map.get(name, 0)
		rev = revenue_map.get(name, 0)

		metrics_map[name] = {
			"spend": spend,
			"impressions": impressions,
			"clicks": clicks,
			"leads": leads_count,
			"revenue": rev,
			"roas": rev / spend if spend > 0 else 0,
			"ctr": (clicks / impressions) * 100 if impressions > 0 else 0,
			"cpc": spend / clicks if clicks > 0 else 0,
			"cpl": spend / leads_count if leads_count > 0 else 0,
		}

	return metrics_map


def get_channel_data(filters):
	"""Get ROAS data grouped by channel using bulk metrics"""
	conditions = get_conditions(filters)

	campaigns = frappe.db.sql(f"""
		SELECT name
		FROM `tabMarketing Campaign`
		WHERE docstatus < 2
		{conditions}
	""", filters, as_dict=1)

	if not campaigns:
		return []

	campaign_names = [c.name for c in campaigns]
	metrics_map = get_bulk_campaign_metrics(campaign_names)

	# Bulk fetch channels
	channel_rows = frappe.db.sql("""
		SELECT parent, social_media_network
		FROM `tabMarketing Campaign Channel`
		WHERE parenttype = 'Marketing Campaign'
		AND parent IN %(campaigns)s
	""", {"campaigns": campaign_names}, as_dict=1)

	campaign_channels = {}
	for row in channel_rows:
		campaign_channels.setdefault(row.parent, []).append(row.social_media_network)

	# Aggregate by channel
	channel_data = {}

	for campaign in campaigns:
		channel_names = campaign_channels.get(campaign.name, [])
		metrics = metrics_map.get(campaign.name, {})

		for channel in channel_names:
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

			channel_count = len(channel_names) or 1
			channel_data[channel]["spend"] += metrics.get("spend", 0) / channel_count
			channel_data[channel]["revenue"] += metrics.get("revenue", 0) / channel_count
			channel_data[channel]["impressions"] += metrics.get("impressions", 0) / channel_count
			channel_data[channel]["clicks"] += metrics.get("clicks", 0) / channel_count
			channel_data[channel]["leads"] += metrics.get("leads", 0) / channel_count

	# Calculate derived metrics
	data = []
	for channel, metrics in channel_data.items():
		metrics["roas"] = metrics["revenue"] / metrics["spend"] if metrics["spend"] > 0 else 0
		metrics["ctr"] = (metrics["clicks"] / metrics["impressions"]) * 100 if metrics["impressions"] > 0 else 0
		metrics["cpc"] = metrics["spend"] / metrics["clicks"] if metrics["clicks"] > 0 else 0
		metrics["cpl"] = metrics["spend"] / metrics["leads"] if metrics["leads"] > 0 else 0

		min_roas = filters.get("min_roas", 0)
		if metrics["roas"] >= min_roas:
			data.append(metrics)

	data.sort(key=lambda x: x["roas"], reverse=True)
	return data


def get_monthly_data(filters):
	"""Get ROAS data grouped by month"""
	date_conditions = get_date_conditions(filters)

	monthly_data = frappe.db.sql(f"""
		SELECT
			DATE_FORMAT(log_date, '%%Y-%%m') as month,
			SUM(spend) as spend,
			SUM(revenue) as revenue,
			SUM(impressions) as impressions,
			SUM(clicks) as clicks
		FROM `tabAnalytics Daily Log`
		WHERE 1=1
		{date_conditions}
		GROUP BY DATE_FORMAT(log_date, '%%Y-%%m')
		ORDER BY month DESC
	""", filters, as_dict=1)

	data = []
	for row in monthly_data:
		row["roas"] = row["revenue"] / row["spend"] if row.get("spend") and row["spend"] > 0 else 0
		row["ctr"] = (row["clicks"] / row["impressions"]) * 100 if row.get("impressions") and row["impressions"] > 0 else 0
		row["cpc"] = row["spend"] / row["clicks"] if row.get("clicks") and row["clicks"] > 0 else 0

		# Get leads for this month (approximate)
		row["leads"] = 0
		row["cpl"] = 0

		# Apply minimum ROAS filter
		min_roas = filters.get("min_roas", 0)
		if row["roas"] >= min_roas:
			data.append(row)

	return data


def get_campaign_metrics(campaign):
	"""Get metrics for a single campaign"""
	analytics = frappe.db.sql("""
		SELECT
			SUM(spend) as cost,
			SUM(impressions) as impressions,
			SUM(clicks) as clicks
		FROM `tabAnalytics Daily Log`
		WHERE campaign = %s
	""", campaign, as_dict=1)

	metrics = {
		"spend": analytics[0].cost if analytics and analytics[0].cost else 0,
		"impressions": analytics[0].impressions if analytics and analytics[0].impressions else 0,
		"clicks": analytics[0].clicks if analytics and analytics[0].clicks else 0
	}

	# Get leads count
	leads_count = frappe.db.count("Lead", filters={"campaign_name": campaign})
	metrics["leads"] = leads_count

	# Get revenue from Sales Orders (directly linked to campaign)
	revenue = frappe.db.sql("""
		SELECT COALESCE(SUM(so.grand_total), 0) as revenue
		FROM `tabSales Order` so
		WHERE so.campaign = %s
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
		conditions.append("DATE(c.creation) >= %(from_date)s")

	if filters.get("to_date"):
		conditions.append("DATE(c.creation) <= %(to_date)s")

	return " AND " + " AND ".join(conditions) if conditions else ""


def get_date_conditions(filters):
	"""Build WHERE conditions for date range"""
	conditions = []

	if filters.get("from_date"):
		conditions.append("log_date >= %(from_date)s")

	if filters.get("to_date"):
		conditions.append("log_date <= %(to_date)s")

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
