"""
Dashboard & Analytics API
"""

import frappe
from frappe import _
from frappe.utils import add_days, today, get_datetime, add_months
from frappe.utils.data import flt


@frappe.whitelist()
def get_dashboard_data():
	"""
	Get dashboard overview data
	Returns: active campaigns, spend metrics, leads, ROI stats, and connectors status
	"""
	try:
		today_date = today()
		last_30_days = add_days(today_date, -30)

		# Active campaigns count
		active_campaigns = frappe.db.count("Marketing Campaign", {
			"status": "Active"
		})

		# Total spend (last 30 days)
		total_spend = frappe.db.get_value(
			"Analytics Daily Log",
			{"log_date": [">=", last_30_days]},
			"sum(spend)"
		) or 0.0

		# Previous period spend (for comparison)
		prev_period_start = add_days(last_30_days, -30)
		prev_period_spend = frappe.db.sql("""
			SELECT SUM(spend) FROM `tabAnalytics Daily Log`
			WHERE log_date >= %s AND log_date < %s
		""", (prev_period_start, last_30_days))[0][0] or 0.0

		# Leads generated (last 30 days)
		leads_generated = frappe.db.count("Lead", {
			"creation": [">=", last_30_days],
			"source": ["is", "set"]
		})

		# Previous period leads
		prev_period_leads = frappe.db.sql("""
			SELECT COUNT(*) FROM `tabLead`
			WHERE creation >= %s AND creation < %s
			AND source IS NOT NULL AND source != ''
		""", (prev_period_start, last_30_days))[0][0] or 0

		# Revenue (last 30 days) - from Analytics Daily Log
		total_revenue = frappe.db.get_value(
			"Analytics Daily Log",
			{"log_date": [">=", last_30_days]},
			"sum(revenue)"
		) or 0.0

		# Calculate ROI
		roi = ((total_revenue - total_spend) / total_spend * 100) if total_spend > 0 else 0

		# Calculate average ROAS
		avg_roas = frappe.db.get_value(
			"Analytics Daily Log",
			{"log_date": [">=", last_30_days], "roas": [">", 0]},
			"avg(roas)"
		) or 0.0

		# Recent activities
		recent_activities = frappe.get_all(
			"Campaign Activity",
			fields=["name", "subject", "status", "scheduled_date", "campaign"],
			filters={"creation": [">=", add_days(today_date, -7)]},
			order_by="creation desc",
			limit=5
		)

		# Top performing campaigns (by ROAS)
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
			GROUP BY c.name
			HAVING spend > 0
			ORDER BY roas DESC
			LIMIT 5
		""", {"from_date": last_30_days}, as_dict=True)

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
def get_analytics_data(from_date=None, to_date=None):
	"""
	Get analytics metrics for charts
	"""
	try:
		if not from_date:
			from_date = add_days(today(), -30)
		if not to_date:
			to_date = today()

		# Get daily metrics
		daily_metrics = frappe.db.sql("""
			SELECT
				log_date as date,
				SUM(impressions) as impressions,
				SUM(clicks) as clicks,
				SUM(spend) as spend,
				SUM(conversions) as conversions,
				SUM(revenue) as revenue,
				AVG(roas) as roas
			FROM `tabAnalytics Daily Log`
			WHERE log_date >= %(from_date)s AND log_date <= %(to_date)s
			GROUP BY log_date
			ORDER BY log_date ASC
		""", {"from_date": from_date, "to_date": to_date}, as_dict=True)

		for metric in daily_metrics:
			metric["ctr"] = (metric["clicks"] / metric["impressions"] * 100) if metric["impressions"] > 0 else 0
			metric["spend"] = flt(metric["spend"], 2)
			metric["revenue"] = flt(metric["revenue"], 2)
			metric["roas"] = flt(metric["roas"], 2)

		# Get channel breakdown
		channel_breakdown = frappe.db.sql("""
			SELECT
				channel,
				SUM(spend) as spend,
				SUM(revenue) as revenue,
				COUNT(DISTINCT campaign) as campaigns
			FROM `tabAnalytics Daily Log`
			WHERE log_date >= %(from_date)s AND log_date <= %(to_date)s
			GROUP BY channel
			ORDER BY spend DESC
		""", {"from_date": from_date, "to_date": to_date}, as_dict=True)

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
