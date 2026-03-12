"""
Campaign API
"""

import frappe
from frappe import _
from frappe.utils.data import flt


def _get_company(company=None):
	"""Get the active company - explicit param, filter, or user default"""
	if company:
		return company
	return frappe.defaults.get_user_default("Company")


@frappe.whitelist()
def get_campaign_list(filters=None, limit=20, offset=0):
	"""Get campaign list with calculated metrics"""
	try:
		if filters and isinstance(filters, str):
			import json
			filters = json.loads(filters)

		filters = filters or {}
		base_filters = {}
		if filters.get("status"):
			base_filters["status"] = filters["status"]
		if filters.get("campaign_name"):
			base_filters["campaign_name"] = ["like", f"%{filters['campaign_name']}%"]

		company = _get_company(filters.get("company"))
		if company:
			base_filters["company"] = company

		campaigns = frappe.get_all(
			"Marketing Campaign",
			fields=[
				"name", "campaign_name", "description", "status",
				"budget", "creation", "modified"
			],
			filters=base_filters,
			order_by="modified desc",
			limit=limit,
			start=offset
		)

		# Enrich with metrics from Analytics Daily Log
		for campaign in campaigns:
			metrics = frappe.db.sql("""
				SELECT
					SUM(spend) as spend,
					SUM(revenue) as revenue,
					SUM(impressions) as impressions,
					SUM(clicks) as clicks,
					SUM(conversions) as conversions,
					AVG(roas) as roas
				FROM `tabAnalytics Daily Log`
				WHERE campaign = %(campaign)s
			""", {"campaign": campaign.name}, as_dict=True)

			if metrics and metrics[0]:
				campaign.update({
					"spend": flt(metrics[0].spend or 0, 2),
					"revenue": flt(metrics[0].revenue or 0, 2),
					"impressions": metrics[0].impressions or 0,
					"clicks": metrics[0].clicks or 0,
					"conversions": metrics[0].conversions or 0,
					"roas": flt(metrics[0].roas or 0, 2)
				})
			else:
				campaign.update({
					"spend": 0, "revenue": 0, "impressions": 0,
					"clicks": 0, "conversions": 0, "roas": 0
				})

			if campaign.budget:
				campaign["budget_utilization"] = flt((campaign.spend / campaign.budget) * 100, 2)
			else:
				campaign["budget_utilization"] = 0

			campaign["leads_count"] = frappe.db.count("Lead", {"campaign_name": campaign.campaign_name})

		total_count = frappe.db.count("Marketing Campaign", base_filters)

		return {
			"campaigns": campaigns,
			"total_count": total_count,
			"has_more": (offset + limit) < total_count
		}

	except Exception as e:
		frappe.log_error(f"Error fetching campaign list: {str(e)}", "Campaigns API Error")
		return {"error": _("Failed to load campaigns"), "campaigns": [], "total_count": 0, "has_more": False}


@frappe.whitelist()
def get_campaign_metrics(campaign):
	"""Get aggregated metrics for a specific campaign"""
	try:
		metrics = frappe.db.sql("""
			SELECT
				COALESCE(SUM(spend), 0) as spend,
				COALESCE(SUM(revenue), 0) as revenue,
				CASE WHEN COALESCE(SUM(spend), 0) > 0
					THEN SUM(revenue) / SUM(spend)
					ELSE 0
				END as roas,
				COALESCE(SUM(impressions), 0) as impressions,
				COALESCE(SUM(clicks), 0) as clicks,
				COALESCE(SUM(conversions), 0) as conversions
			FROM `tabAnalytics Daily Log`
			WHERE campaign = %s
		""", (campaign,), as_dict=True)

		if metrics and metrics[0]:
			return {
				"spend": flt(metrics[0].spend, 2),
				"revenue": flt(metrics[0].revenue, 2),
				"roas": flt(metrics[0].roas, 2),
				"impressions": metrics[0].impressions or 0,
				"clicks": metrics[0].clicks or 0,
				"conversions": metrics[0].conversions or 0,
			}
		return {"spend": 0, "revenue": 0, "roas": 0, "impressions": 0, "clicks": 0, "conversions": 0}
	except Exception as e:
		frappe.log_error(f"Error fetching campaign metrics: {str(e)}", "Campaign Metrics API Error")
		return {"spend": 0, "revenue": 0, "roas": 0, "impressions": 0, "clicks": 0, "conversions": 0}


@frappe.whitelist()
def update_campaign(name, data):
	"""Update an existing marketing campaign"""
	try:
		if isinstance(data, str):
			import json
			data = json.loads(data)

		doc = frappe.get_doc("Marketing Campaign", name)
		for field in ["campaign_name", "status", "description", "budget", "start_date", "end_date", "company", "is_omni_campaign"]:
			if field in data:
				doc.set(field, data[field])
		doc.save()
		return {"success": True, "name": doc.name}
	except Exception as e:
		frappe.log_error(f"Error updating campaign: {str(e)}", "Campaign Update Error")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def create_campaign(data):
	"""Create a new campaign"""
	try:
		if isinstance(data, str):
			import json
			data = json.loads(data)

		campaign = frappe.get_doc({
			"doctype": "Marketing Campaign",
			"campaign_name": data.get("campaign_name"),
			"description": data.get("description"),
			"status": data.get("status", "Planning"),
			"budget": data.get("budget", 0),
			"company": data.get("company") or _get_company(),
		})

		campaign.insert()
		frappe.db.commit()

		return {
			"success": True,
			"campaign_name": campaign.name,
			"message": _("Campaign created successfully")
		}

	except Exception as e:
		frappe.log_error(f"Error creating campaign: {str(e)}", "Campaign Creation Error")
		return {"success": False, "error": _("Failed to create campaign: {0}").format(str(e))}
