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
	Get dashboard overview data
	Returns: active campaigns, spend metrics, leads, ROI stats, and connectors status
	"""
	try:
		today_date = today()
		last_30_days = add_days(today_date, -30)
		prev_period_start = add_days(last_30_days, -30)

		company = _get_company(company)
		params = {"company": company, "from_date": last_30_days, "prev_start": prev_period_start}

		campaign_filters = {"status": "Active"}
		if company:
			campaign_filters["company"] = company

		# Active campaigns count
		active_campaigns = frappe.db.count("Marketing Campaign", campaign_filters)

		company_join = _analytics_company_join(company)

		# Total spend (last 30 days)
		total_spend = frappe.db.sql("""
			SELECT SUM(a.spend) FROM `tabAnalytics Daily Log` a
			{company_join}
			WHERE a.log_date >= %(from_date)s
		""".format(company_join=company_join), params)[0][0] or 0.0

		# Previous period spend (for comparison)
		prev_period_spend = frappe.db.sql("""
			SELECT SUM(a.spend) FROM `tabAnalytics Daily Log` a
			{company_join}
			WHERE a.log_date >= %(prev_start)s AND a.log_date < %(from_date)s
		""".format(company_join=company_join), params)[0][0] or 0.0

		# Leads generated (last 30 days)
		lead_filters = {"creation": [">=", last_30_days], "source": ["is", "set"]}
		if company:
			lead_filters["company"] = company

		leads_generated = frappe.db.count("Lead", lead_filters)

		prev_lead_filters = {
			"creation": [">=", prev_period_start],
			"creation": ["<", last_30_days],
			"source": ["is", "set"],
		}
		if company:
			prev_lead_filters["company"] = company

		prev_period_leads = frappe.db.sql("""
			SELECT COUNT(*) FROM `tabLead`
			WHERE creation >= %(prev_start)s AND creation < %(from_date)s
			AND source IS NOT NULL AND source != ''
			{company_cond}
		""".format(company_cond="AND company = %(company)s" if company else ""), params)[0][0] or 0

		# Revenue (last 30 days) - from Analytics Daily Log
		total_revenue = frappe.db.sql("""
			SELECT SUM(a.revenue) FROM `tabAnalytics Daily Log` a
			{company_join}
			WHERE a.log_date >= %(from_date)s
		""".format(company_join=company_join), params)[0][0] or 0.0

		# Calculate ROI
		roi = ((total_revenue - total_spend) / total_spend * 100) if total_spend > 0 else 0

		# Calculate average ROAS
		avg_roas = frappe.db.sql("""
			SELECT AVG(a.roas) FROM `tabAnalytics Daily Log` a
			{company_join}
			WHERE a.log_date >= %(from_date)s AND a.roas > 0
		""".format(company_join=company_join), params)[0][0] or 0.0

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
		top_campaigns = frappe.db.sql("""
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
		""".format(company_cond=company_cond), params, as_dict=True)

		# Calculate percentage changes
		spend_change = _percentage_change(prev_period_spend, total_spend)
		leads_change = _percentage_change(prev_period_leads, leads_generated)

		return {
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

	except Exception as e:
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
	Get analytics metrics for charts
	"""
	try:
		if not from_date:
			from_date = add_days(today(), -30)
		if not to_date:
			to_date = today()

		company = _get_company(company)
		company_join = _analytics_company_join(company)
		params = {"from_date": from_date, "to_date": to_date, "company": company}

		# Get daily metrics
		daily_metrics = frappe.db.sql("""
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
		""".format(company_join=company_join), params, as_dict=True)

		for metric in daily_metrics:
			metric["ctr"] = (metric["clicks"] / metric["impressions"] * 100) if metric["impressions"] > 0 else 0
			metric["spend"] = flt(metric["spend"], 2)
			metric["revenue"] = flt(metric["revenue"], 2)
			metric["roas"] = flt(metric["roas"], 2)

		# Get channel breakdown
		channel_breakdown = frappe.db.sql("""
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
		""".format(company_join=company_join), params, as_dict=True)

		return {
			"daily_metrics": daily_metrics,
			"channel_breakdown": channel_breakdown
		}

	except Exception as e:
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
