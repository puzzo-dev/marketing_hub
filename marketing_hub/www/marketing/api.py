"""
Marketing Hub API Endpoints
Provides data for the Vue.js SPA portal
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
		company = frappe.defaults.get_user_default("Company")
		
		# Get date ranges
		today_date = today()
		last_month = add_months(today_date, -1)
		last_30_days = add_days(today_date, -30)
		
		# Active campaigns count
		active_campaigns = frappe.db.count("Campaign", {
			"status": "Running"
		})
		
		# Connectors Status (Merged from analytics.py)
		connectors = frappe.get_all("Analytics Connector",
			fields=["name", "connector_name", "platform", "sync_status", "last_sync_date"],
			filters={"enabled": 1},
			order_by="platform"
		)
		
		# Total spend (last 30 days)
		total_spend = frappe.db.get_value(
			"Analytics Daily Log",
			{"date": [">=", last_30_days]},
			"sum(cost)"
		) or 0.0
		
		# Previous period spend (for comparison)
		prev_period_start = add_days(last_30_days, -30)
		prev_period_spend = frappe.db.get_value(
			"Analytics Daily Log",
			{"date": [">=", prev_period_start], "date": ["<", last_30_days]},
			"sum(cost)"
		) or 0.0
		
		# Leads generated (last 30 days)
		leads_generated = frappe.db.count("Lead", {
			"creation": [">=", last_30_days],
			"source": ["is", "set"]
		})
		
		# Previous period leads
		prev_period_leads = frappe.db.count("Lead", {
			"creation": [">=", prev_period_start],
			"creation": ["<", last_30_days],
			"source": ["is", "set"]
		})
		
		# Revenue (last 30 days) - from Analytics Daily Log conversions
		total_revenue = frappe.db.get_value(
			"Analytics Daily Log",
			{"date": [">=", last_30_days]},
			"sum(conversion_value)"
		) or 0.0
		
		# Calculate ROI
		roi = ((total_revenue - total_spend) / total_spend * 100) if total_spend > 0 else 0
		
		# Calculate average ROAS
		avg_roas = frappe.db.get_value(
			"Analytics Daily Log",
			{"date": [">=", last_30_days], "roas": [">", 0]},
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
				SUM(a.cost) as spend,
				SUM(a.conversion_value) as revenue,
				AVG(a.roas) as roas
			FROM `tabCampaign` c
			LEFT JOIN `tabAnalytics Daily Log` a ON a.campaign = c.name
			WHERE a.date >= %(from_date)s
			GROUP BY c.name
			HAVING spend > 0
			ORDER BY roas DESC
			LIMIT 5
		""", {"from_date": last_30_days}, as_dict=True)
		
		# Calculate percentage changes
		spend_change = calculate_percentage_change(prev_period_spend, total_spend)
		leads_change = calculate_percentage_change(prev_period_leads, leads_generated)
		
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
	Args:
		from_date: Start date (defaults to 30 days ago)
		to_date: End date (defaults to today)
	Returns: Daily metrics array
	"""
	try:
		# Default date range
		if not from_date:
			from_date = add_days(today(), -30)
		if not to_date:
			to_date = today()
		
		# Get daily metrics
		daily_metrics = frappe.db.sql("""
			SELECT 
				date,
				SUM(impressions) as impressions,
				SUM(clicks) as clicks,
				SUM(cost) as spend,
				SUM(conversions) as conversions,
				SUM(conversion_value) as revenue,
				AVG(roas) as roas
			FROM `tabAnalytics Daily Log`
			WHERE date >= %(from_date)s AND date <= %(to_date)s
			GROUP BY date
			ORDER BY date ASC
		""", {"from_date": from_date, "to_date": to_date}, as_dict=True)
		
		# Calculate CTR for each day
		for metric in daily_metrics:
			metric["ctr"] = (metric["clicks"] / metric["impressions"] * 100) if metric["impressions"] > 0 else 0
			metric["spend"] = flt(metric["spend"], 2)
			metric["revenue"] = flt(metric["revenue"], 2)
			metric["roas"] = flt(metric["roas"], 2)
		
		# Get channel breakdown
		channel_breakdown = frappe.db.sql("""
			SELECT 
				platform,
				SUM(cost) as spend,
				SUM(conversion_value) as revenue,
				COUNT(DISTINCT campaign) as campaigns
			FROM `tabAnalytics Daily Log`
			WHERE date >= %(from_date)s AND date <= %(to_date)s
			GROUP BY platform
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


@frappe.whitelist()
def get_campaign_list(filters=None, limit=20, offset=0):
	"""
	Get campaign list with calculated metrics
	Args:
		filters: Dict of filters to apply
		limit: Number of records to return
		offset: Pagination offset
	Returns: List of campaigns with metrics
	"""
	try:
		if filters and isinstance(filters, str):
			import json
			filters = json.loads(filters)
		
		filters = filters or {}
		
		# Build base filters
		base_filters = {}
		if filters.get("status"):
			base_filters["status"] = filters["status"]
		if filters.get("campaign_name"):
			base_filters["campaign_name"] = ["like", f"%{filters['campaign_name']}%"]
		
		# Get campaigns
		campaigns = frappe.get_all(
			"Campaign",
			fields=[
				"name",
				"campaign_name",
				"description",
				"status",
				"budget",
				"creation",
				"modified"
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
					SUM(cost) as spend,
					SUM(conversion_value) as revenue,
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
					"spend": 0,
					"revenue": 0,
					"impressions": 0,
					"clicks": 0,
					"conversions": 0,
					"roas": 0
				})
			
			# Calculate budget utilization
			if campaign.budget:
				campaign["budget_utilization"] = flt((campaign.spend / campaign.budget) * 100, 2)
			else:
				campaign["budget_utilization"] = 0
			
			# Get lead count
			campaign["leads_count"] = frappe.db.count("Lead", {"campaign_name": campaign.campaign_name})
		
		# Get total count for pagination
		total_count = frappe.db.count("Campaign", base_filters)
		
		return {
			"campaigns": campaigns,
			"total_count": total_count,
			"has_more": (offset + limit) < total_count
		}
		
	except Exception as e:
		frappe.log_error(f"Error fetching campaign list: {str(e)}", "Campaigns API Error")
		return {
			"error": _("Failed to load campaigns"),
			"campaigns": [],
			"total_count": 0,
			"has_more": False
		}


@frappe.whitelist()
def get_social_posts(filters=None, limit=20, offset=0):
	"""
	Get social posts with engagement metrics
	Args:
		filters: Dict of filters to apply
		limit: Number of records to return
		offset: Pagination offset
	Returns: List of social posts
	"""
	try:
		if filters and isinstance(filters, str):
			import json
			filters = json.loads(filters)
		
		filters = filters or {}
		
		# Build base filters
		base_filters = {}
		if filters.get("status"):
			base_filters["status"] = filters["status"]
		if filters.get("platform"):
			base_filters["platform"] = filters["platform"]
		if filters.get("campaign"):
			base_filters["campaign"] = filters["campaign"]
		
		# Get social posts
		posts = frappe.get_all(
			"Social Post",
			fields=[
				"name",
				"post_title",
				"platform",
				"post_type",
				"status",
				"scheduled_time",
				"published_time",
				"campaign",
				"content",
				"impressions",
				"reach",
				"clicks",
				"likes",
				"comments_count",
				"shares",
				"engagement_rate",
				"creation",
				"modified"
			],
			filters=base_filters,
			order_by="modified desc",
			limit=limit,
			start=offset
		)
		
		# Enrich with network details
		for post in posts:
			if post.platform:
				network = frappe.db.get_value(
					"Social Media Network",
					post.platform,
					["network_name", "icon", "network_type"],
					as_dict=True
				)
				if network:
					post["network_name"] = network.network_name
					post["network_icon"] = network.icon
					post["network_type"] = network.network_type
			
			# Format content preview (first 100 chars)
			if post.content:
				import re
				clean_content = re.sub(r'<[^>]+>', '', post.content or '')
				post["content_preview"] = clean_content[:100] + "..." if len(clean_content) > 100 else clean_content
		
		# Get total count for pagination
		total_count = frappe.db.count("Social Post", base_filters)
		
		# Get status counts for filter pills
		status_counts = frappe.db.sql("""
			SELECT status, COUNT(*) as count
			FROM `tabSocial Post`
			GROUP BY status
		""", as_dict=True)
		
		return {
			"posts": posts,
			"total_count": total_count,
			"has_more": (offset + limit) < total_count,
			"status_counts": {item.status: item.count for item in status_counts}
		}
		
	except Exception as e:
		frappe.log_error(f"Error fetching social posts: {str(e)}", "Social Posts API Error")
		return {
			"error": _("Failed to load social posts"),
			"posts": [],
			"total_count": 0,
			"has_more": False,
			"status_counts": {}
		}


@frappe.whitelist()
def create_campaign(data):
	"""
	Create a new campaign from frontend form
	Args:
		data: Campaign data dict
	Returns: Campaign name
	"""
	try:
		if isinstance(data, str):
			import json
			data = json.loads(data)
		
		campaign = frappe.get_doc({
			"doctype": "Campaign",
			"campaign_name": data.get("campaign_name"),
			"description": data.get("description"),
			"status": data.get("status", "Planning"),
			"budget": data.get("budget", 0)
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
		return {
			"success": False,
			"error": _("Failed to create campaign: {0}").format(str(e))
		}


@frappe.whitelist()
def create_social_post(data):
	"""
	Create a new social post from frontend form
	Args:
		data: Social post data dict
	Returns: Post name
	"""
	try:
		if isinstance(data, str):
			import json
			data = json.loads(data)
		
		post = frappe.get_doc({
			"doctype": "Social Post",
			"post_title": data.get("post_title"),
			"platform": data.get("platform"),
			"post_type": data.get("post_type", "Text"),
			"status": data.get("status", "Draft"),
			"content": data.get("content"),
			"campaign": data.get("campaign"),
			"scheduled_time": data.get("scheduled_time")
		})
		
		post.insert()
		frappe.db.commit()
		
		return {
			"success": True,
			"post_name": post.name,
			"message": _("Social post created successfully")
		}
		
	except Exception as e:
		frappe.log_error(f"Error creating social post: {str(e)}", "Social Post Creation Error")
		return {
			"success": False,
			"error": _("Failed to create social post: {0}").format(str(e))
		}


def calculate_percentage_change(old_value, new_value):
	"""
	Calculate percentage change between two values
	Returns: Percentage change as float
	"""
	if old_value == 0:
		return 100 if new_value > 0 else 0
	
	change = ((new_value - old_value) / old_value) * 100
	return flt(change, 2)


@frappe.whitelist()
def get_content_list(filters=None, limit=20, offset=0):
	"""
	Get content assets with details
	Args:
		filters: Dict of filters to apply
		limit: Number of records to return
		offset: Pagination offset
	Returns: List of content assets
	"""
	try:
		if filters and isinstance(filters, str):
			import json
			filters = json.loads(filters)
		
		filters = filters or {}
		
		# Build base filters
		base_filters = {}
		if filters.get("status"):
			base_filters["status"] = filters["status"]
		if filters.get("content_type"):
			base_filters["content_type"] = filters["content_type"]
		if filters.get("campaign"):
			base_filters["campaign"] = filters["campaign"]
			
		# Get content assets
		content_list = frappe.get_all(
			"Content Asset",
			fields=[
				"name",
				"asset_name",
				"content_type",
				"status",
				"campaign",
				"creation",
				"modified",
				"owner"
			],
			filters=base_filters,
			order_by="modified desc",
			limit=limit,
			start=offset
		)
		
		# Enrich with campaign name
		for content in content_list:
			if content.campaign:
				content["campaign_name"] = frappe.db.get_value("Campaign", content.campaign, "campaign_name")
				
		total_count = frappe.db.count("Content Asset", base_filters)
		
		return {
			"content": content_list,
			"total_count": total_count,
			"has_more": (offset + limit) < total_count
		}
		
	except Exception as e:
		frappe.log_error(f"Error fetching content list: {str(e)}", "Content List API Error")
		return {
			"error": _("Failed to load content list"),
			"content": [],
			"total_count": 0,
			"has_more": False
		}


@frappe.whitelist()
def update_content_status(names, status):
	"""
	Bulk update status for content assets
	Args:
		names: List of content names
		status: New status
	"""
	try:
		if isinstance(names, str):
			import json
			names = json.loads(names)
			
		for name in names:
			frappe.db.set_value("Content Asset", name, "status", status)
			
		frappe.db.commit()
		return {"success": True, "message": _("Status updated successfully")}
		
	except Exception as e:
		frappe.log_error(f"Error updating content status: {str(e)}", "Content Update API Error")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_content_details(name):
	"""
	Get full details for a content asset
	"""
	try:
		doc = frappe.get_doc("Content Asset", name)
		return {"success": True, "doc": doc}
	except Exception as e:
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_expense_list(filters=None, limit=20, offset=0):
	"""
	Get marketing expenses list
	Args:
		filters: Dict of filters
		limit: Number of records
		offset: Pagination offset
	"""
	try:
		if filters and isinstance(filters, str):
			import json
			filters = json.loads(filters)
		
		filters = filters or {}
		
		# Base filters
		base_filters = {}
		if filters.get("campaign"):
			base_filters["campaign"] = filters["campaign"]
		if filters.get("expense_type"):
			base_filters["expense_type"] = filters["expense_type"]
			
		# Get expenses
		expenses = frappe.get_all(
			"Marketing Expense",
			fields=[
				"name",
				"expense_title",
				"campaign",
				"amount",
				"expense_date",
				"expense_type",
				"vendor",
				"status"
			],
			filters=base_filters,
			order_by="expense_date desc",
			limit=limit,
			start=offset
		)
		
		# Enrich
		for expense in expenses:
			if expense.campaign:
				expense["campaign_name"] = frappe.db.get_value("Campaign", expense.campaign, "campaign_name")
				
		total_count = frappe.db.count("Marketing Expense", base_filters)
		
		return {
			"expenses": expenses,
			"total_count": total_count,
			"has_more": (offset + limit) < total_count
		}
	except Exception as e:
		frappe.log_error(f"Error fetching expenses: {str(e)}", "Expense API Error")
		return {"error": str(e), "expenses": []}


@frappe.whitelist()
def get_budget_overview():
	"""
	Get budget vs actuals overview
	"""
	try:
		# Total Budget (Sum of all campaign budgets)
		total_budget = frappe.db.sql("""
			SELECT SUM(budget) FROM `tabCampaign` WHERE status != 'Completed'
		""")[0][0] or 0.0
		
		# Total Spend (from Analytics Daily Log + Manual Expenses)
		ad_spend = frappe.db.sql("""
			SELECT SUM(cost) FROM `tabAnalytics Daily Log`
		""")[0][0] or 0.0
		
		manual_spend = frappe.db.sql("""
			SELECT SUM(amount) FROM `tabMarketing Expense` WHERE status = 'Approved'
		""")[0][0] or 0.0
		
		total_spend = ad_spend + manual_spend
		
		# Monthly trend (last 6 months)
		idx = 0
		trend_labels = []
		trend_budget = []
		trend_actual = []
		
		from frappe.utils import add_months, get_first_day, get_last_day
		
		for i in range(5, -1, -1):
			month_start = add_months(today(), -i)
			month_start = get_first_day(month_start)
			month_end = get_last_day(month_start)
			
			label = get_datetime(month_start).strftime("%b %Y")
			trend_labels.append(label)
			
			# Monthly Actual
			m_ad_spend = frappe.db.sql("""
				SELECT SUM(cost) FROM `tabAnalytics Daily Log` 
				WHERE date BETWEEN %s AND %s
			""", (month_start, month_end))[0][0] or 0.0
			
			m_manual_spend = frappe.db.sql("""
				SELECT SUM(amount) FROM `tabMarketing Expense` 
				WHERE expense_date BETWEEN %s AND %s AND status = 'Approved'
			""", (month_start, month_end))[0][0] or 0.0
			
			trend_actual.append(flt(m_ad_spend + m_manual_spend, 2))
			
			# Estimated monthly budget (Total Active Budget / 12 for rough calc, or custom logic)
			# For now, just using a flat line of avg budget
			trend_budget.append(flt(total_budget / 12, 2)) # Placeholder logic
			
		return {
			"total_budget": flt(total_budget, 2),
			"total_spend": flt(total_spend, 2),
			"remaining_budget": flt(total_budget - total_spend, 2),
			"utilization": flt((total_spend / total_budget * 100) if total_budget > 0 else 0, 2),
			"chart": {
				"labels": trend_labels,
				"budget": trend_budget,
				"actual": trend_actual
			}
		}
	except Exception as e:
		frappe.log_error(f"Error fetching budget overview: {str(e)}", "Budget API Error")
		return {"error": str(e)}


@frappe.whitelist()
def create_expense(data):
	"""
	Create a new marketing expense
	"""
	try:
		if isinstance(data, str):
			import json
			data = json.loads(data)
			
		expense = frappe.get_doc({
			"doctype": "Marketing Expense",
			"expense_title": data.get("title"),
			"campaign": data.get("campaign"),
			"amount": data.get("amount"),
			"expense_date": data.get("date") or today(),
			"expense_type": data.get("type"),
			"vendor": data.get("vendor"),
			"description": data.get("description"),
			"status": "Pending"
		})
		
		expense.insert()
		return {"success": True, "message": _("Expense logged successfully")}
	except Exception as e:
		frappe.log_error(f"Error creating expense: {str(e)}", "Expense Creation Error")
		return {"success": False, "error": str(e)}


# --- Content Management Methods (Merged from content.py) ---

@frappe.whitelist()
def get_asset_stats():
	"""Get asset library statistics"""
	try:
		stats = {
			"total_assets": frappe.db.count("Content Asset"),
			"by_type": frappe.db.sql("""
				SELECT content_type as asset_type, COUNT(*) as count
				FROM `tabContent Asset`
				GROUP BY content_type
				ORDER BY count DESC
			""", as_dict=True),
			"by_status": frappe.db.sql("""
				SELECT status, COUNT(*) as count
				FROM `tabContent Asset`
				GROUP BY status
			""", as_dict=True)
		}
		return stats
	except Exception as e:
		return {"total_assets": 0, "by_type": [], "by_status": []}

@frappe.whitelist()
def upload_file(file, asset_name=None, asset_type=None, channel=None):
	"""
	Handle file upload and create asset
	"""
	try:
		file_doc = frappe.get_doc("File", {"file_url": file})
		
		# Create Content Asset automatically
		asset = frappe.get_doc({
			"doctype": "Content Asset",
			"asset_name": asset_name or file_doc.file_name,
			"content_type": asset_type or "Image",
			"file_url": file, # Map to fields in your doctype
			"status": "Draft"
		})
		
		asset.insert()
		return {"success": True, "asset": asset.name}
	except Exception as e:
		return {"success": False, "error": str(e)}

