"""
Dashboard & Analytics API
"""

import frappe
from frappe import _
from frappe.utils import add_days, today, get_datetime, add_months
from frappe.utils.data import flt


def _get_company(company=None):
	"""Get the active company - explicit param or user default"""
	if company:
		return company
	return frappe.defaults.get_user_default("Company")


def _campaign_company_condition(company, alias="c"):
	"""Return SQL condition for company filtering on campaigns"""
	if company:
		return f"AND {alias}.company = %(company)s"
	return ""


def _analytics_company_join(company):
	"""Return SQL join + condition to filter analytics by campaign company"""
	if company:
		return "JOIN `tabMarketing Campaign` mc ON mc.name = a.campaign AND mc.company = %(company)s"
	return ""


@frappe.whitelist()
def get_dashboard_data(company=None):
	"""
	Get dashboard overview data (cached for 5 minutes)
	Returns: active campaigns, spend metrics, leads, ROI stats, and connectors status
	"""
	company = _get_company(company)
	cache_key = f"marketing_hub:dashboard:{company or 'all'}"
	cached = frappe.cache().get_value(cache_key)
	if cached:
		return cached

	try:
		today_date = today()
		last_30_days = add_days(today_date, -30)
		prev_period_start = add_days(last_30_days, -30)

		params = {"company": company, "from_date": last_30_days, "prev_start": prev_period_start}

		campaign_filters = {"status": "Active"}
		if company:
			campaign_filters["company"] = company

		# Active campaigns count
		active_campaigns = frappe.db.count("Marketing Campaign", campaign_filters)

		company_join = _analytics_company_join(company)

		# Analytics Aggregation (Spend, Revenue, ROAS)
		analytics_data = frappe.db.sql(f"""
			SELECT
				SUM(CASE WHEN a.log_date >= %(from_date)s THEN a.spend ELSE 0 END) as total_spend,
				SUM(CASE WHEN a.log_date >= %(prev_start)s AND a.log_date < %(from_date)s THEN a.spend ELSE 0 END) as prev_period_spend,
				SUM(CASE WHEN a.log_date >= %(from_date)s THEN a.revenue ELSE 0 END) as total_revenue,
				AVG(CASE WHEN a.log_date >= %(from_date)s AND a.roas > 0 THEN a.roas ELSE NULL END) as avg_roas
			FROM `tabAnalytics Daily Log` a
			{company_join}
			WHERE a.log_date >= %(prev_start)s
		""", params, as_dict=True)

		total_spend = analytics_data[0].total_spend or 0.0 if analytics_data else 0.0
		prev_period_spend = analytics_data[0].prev_period_spend or 0.0 if analytics_data else 0.0
		total_revenue = analytics_data[0].total_revenue or 0.0 if analytics_data else 0.0
		avg_roas = analytics_data[0].avg_roas or 0.0 if analytics_data else 0.0

		# Leads Aggregation
		company_cond = "AND company = %(company)s" if company else ""
		leads_data = frappe.db.sql(f"""
			SELECT
				SUM(CASE WHEN creation >= %(from_date)s THEN 1 ELSE 0 END) as leads_generated,
				SUM(CASE WHEN creation >= %(prev_start)s AND creation < %(from_date)s THEN 1 ELSE 0 END) as prev_period_leads
			FROM `tabLead`
			WHERE creation >= %(prev_start)s
			AND source IS NOT NULL AND source != ''
			{company_cond}
		""", params, as_dict=True)

		leads_generated = leads_data[0].leads_generated or 0 if leads_data else 0
		prev_period_leads = leads_data[0].prev_period_leads or 0 if leads_data else 0

		# Calculate ROI
		roi = ((total_revenue - total_spend) / total_spend * 100) if total_spend > 0 else 0

		# Recent activities
		activity_filters = {"creation": [">=", add_days(today_date, -7)]}
		recent_activities = frappe.get_all(
			"Campaign Activity",
			fields=["name", "subject", "status", "scheduled_date", "campaign"],
			filters=activity_filters,
			order_by="creation desc",
			limit=5
		)

		# Top performing campaigns (by ROAS)
		company_cond = _campaign_company_condition(company)
		top_campaigns = frappe.db.sql(f"""
			SELECT
				c.name as campaign_name,
				c.campaign_name as title,
				SUM(a.spend) as spend,
				SUM(a.revenue) as revenue,
				AVG(a.roas) as roas
			FROM `tabMarketing Campaign` c
			LEFT JOIN `tabAnalytics Daily Log` a ON a.campaign = c.name
			WHERE a.log_date >= %(from_date)s
			{company_cond}
			GROUP BY c.name
			HAVING spend > 0
			ORDER BY roas DESC
			LIMIT 5
		""", params, as_dict=True)

		# Calculate percentage changes
		spend_change = _percentage_change(prev_period_spend, total_spend)
		leads_change = _percentage_change(prev_period_leads, leads_generated)

		result = {
			"active_campaigns": active_campaigns,
			"total_spend": flt(total_spend, 2),
			"spend_change": spend_change,
			"leads_generated": leads_generated,
			"leads_change": leads_change,
			"roi": flt(roi, 2),
			"avg_roas": flt(avg_roas, 2),
			"recent_activities": recent_activities,
			"top_campaigns": top_campaigns
		}

		frappe.cache().set_value(cache_key, result, expires_in_sec=300)
		return result

	except (frappe.DatabaseError, frappe.ValidationError) as e:
		frappe.log_error(f"Error fetching dashboard data: {str(e)}", "Dashboard API Error")
		return {
			"error": _("Failed to load dashboard data"),
			"active_campaigns": 0,
			"total_spend": 0,
			"leads_generated": 0,
			"roi": 0,
			"avg_roas": 0,
			"recent_activities": [],
			"top_campaigns": []
		}


@frappe.whitelist()
def get_analytics_data(from_date=None, to_date=None, company=None):
	"""
	Get analytics metrics for charts (cached for 10 minutes)
	"""
	if not from_date:
		from_date = add_days(today(), -30)
	if not to_date:
		to_date = today()

	company = _get_company(company)
	cache_key = f"marketing_hub:analytics:{company or 'all'}:{from_date}:{to_date}"
	cached = frappe.cache().get_value(cache_key)
	if cached:
		return cached

	try:
		company_join = _analytics_company_join(company)
		params = {"from_date": from_date, "to_date": to_date, "company": company}

		# Get daily metrics
		daily_metrics = frappe.db.sql(f"""
			SELECT
				a.log_date as date,
				SUM(a.impressions) as impressions,
				SUM(a.clicks) as clicks,
				SUM(a.spend) as spend,
				SUM(a.conversions) as conversions,
				SUM(a.revenue) as revenue,
				AVG(a.roas) as roas
			FROM `tabAnalytics Daily Log` a
			{company_join}
			WHERE a.log_date >= %(from_date)s AND a.log_date <= %(to_date)s
			GROUP BY a.log_date
			ORDER BY a.log_date ASC
		""", params, as_dict=True)

		for metric in daily_metrics:
			metric["ctr"] = (metric["clicks"] / metric["impressions"] * 100) if metric["impressions"] > 0 else 0
			metric["spend"] = flt(metric["spend"], 2)
			metric["revenue"] = flt(metric["revenue"], 2)
			metric["roas"] = flt(metric["roas"], 2)

		# Get channel breakdown
		channel_breakdown = frappe.db.sql(f"""
			SELECT
				a.channel,
				SUM(a.spend) as spend,
				SUM(a.revenue) as revenue,
				COUNT(DISTINCT a.campaign) as campaigns
			FROM `tabAnalytics Daily Log` a
			{company_join}
			WHERE a.log_date >= %(from_date)s AND a.log_date <= %(to_date)s
			GROUP BY a.channel
			ORDER BY spend DESC
		""", params, as_dict=True)

		result = {
			"daily_metrics": daily_metrics,
			"channel_breakdown": channel_breakdown
		}

		frappe.cache().set_value(cache_key, result, expires_in_sec=600)
		return result

	except (frappe.DatabaseError, frappe.ValidationError) as e:
		frappe.log_error(f"Error fetching analytics data: {str(e)}", "Analytics API Error")
		return {
			"error": _("Failed to load analytics data"),
			"daily_metrics": [],
			"channel_breakdown": []
		}


def _percentage_change(old_value, new_value):
	"""Calculate percentage change between two values"""
	if old_value == 0:
		return 100 if new_value > 0 else 0
	return flt(((new_value - old_value) / old_value) * 100, 2)


@frappe.whitelist()
def get_dashboard_charts(company=None):
	"""
	Get chart data for dashboard: spend trend, leads over time, channel breakdown, conversion funnel
	"""
	try:
		company = _get_company(company)
		from_date = add_days(today(), -30)
		to_date = today()
		params = {"company": company, "from_date": from_date, "to_date": to_date}
		company_join = _analytics_company_join(company)

		# Spend & Revenue trend (daily, last 30 days)
		spend_trend = frappe.db.sql(f"""
			SELECT
				a.log_date as date,
				SUM(a.spend) as spend,
				SUM(a.revenue) as revenue
			FROM `tabAnalytics Daily Log` a
			{company_join}
			WHERE a.log_date >= %(from_date)s AND a.log_date <= %(to_date)s
			GROUP BY a.log_date
			ORDER BY a.log_date ASC
		""", params, as_dict=True)

		for row in spend_trend:
			row["spend"] = flt(row["spend"], 2)
			row["revenue"] = flt(row["revenue"], 2)

		# Leads over time (daily, last 30 days)
		company_cond = "AND company = %(company)s" if company else ""
		leads_trend = frappe.db.sql(f"""
			SELECT DATE(creation) as date, COUNT(*) as leads
			FROM `tabLead`
			WHERE creation >= %(from_date)s AND creation <= %(to_date)s
			AND source IS NOT NULL AND source != ''
			{company_cond}
			GROUP BY DATE(creation)
			ORDER BY date ASC
		""", params, as_dict=True)

		# Channel spend breakdown (for donut chart)
		channel_breakdown = frappe.db.sql(f"""
			SELECT
				a.channel as channel,
				SUM(a.spend) as spend
			FROM `tabAnalytics Daily Log` a
			{company_join}
			WHERE a.log_date >= %(from_date)s AND a.log_date <= %(to_date)s
			AND a.channel IS NOT NULL AND a.channel != ''
			GROUP BY a.channel
			ORDER BY spend DESC
		""", params, as_dict=True)

		for row in channel_breakdown:
			row["spend"] = flt(row["spend"], 2)

		# Conversion funnel: impressions -> clicks -> conversions
		funnel_data = frappe.db.sql(f"""
			SELECT
				SUM(a.impressions) as impressions,
				SUM(a.clicks) as clicks,
				SUM(a.conversions) as conversions
			FROM `tabAnalytics Daily Log` a
			{company_join}
			WHERE a.log_date >= %(from_date)s AND a.log_date <= %(to_date)s
		""", params, as_dict=True)

		funnel = []
		if funnel_data and funnel_data[0]:
			fd = funnel_data[0]
			funnel = [
				{"stage": "Impressions", "value": int(fd.get("impressions") or 0)},
				{"stage": "Clicks", "value": int(fd.get("clicks") or 0)},
				{"stage": "Conversions", "value": int(fd.get("conversions") or 0)},
			]

		# Lead sources breakdown
		lead_sources = frappe.db.sql(f"""
			SELECT source, COUNT(*) as count
			FROM `tabLead`
			WHERE creation >= %(from_date)s AND creation <= %(to_date)s
			AND source IS NOT NULL AND source != ''
			{company_cond}
			GROUP BY source
			ORDER BY count DESC
			LIMIT 10
		""", params, as_dict=True)

		return {
			"spend_trend": spend_trend,
			"leads_trend": leads_trend,
			"channel_breakdown": channel_breakdown,
			"funnel": funnel,
			"lead_sources": lead_sources,
		}

	except (frappe.DatabaseError, frappe.ValidationError) as e:
		frappe.log_error(f"Error fetching dashboard charts: {str(e)}", "Dashboard Charts API Error")
		return {
			"spend_trend": [],
			"leads_trend": [],
			"channel_breakdown": [],
			"funnel": [],
			"lead_sources": [],
		}
