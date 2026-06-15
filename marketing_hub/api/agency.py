"""
Agency Mode API — Client management, project integration, agency dashboard
"""

import frappe
from frappe import _
from frappe.utils import add_days, add_months, today
from frappe.utils.data import flt


def _is_agency_mode():
	try:
		return bool(frappe.db.get_single_value("Marketing Hub Settings", "agency_mode"))
	except Exception:
		return False


@frappe.whitelist()
def get_clients(filters=None, limit=20, offset=0):
	"""Get client list with subscription and campaign stats"""
	if not _is_agency_mode():
		return {"clients": [], "has_more": False, "mode": "internal"}

	if filters and isinstance(filters, str):
		import json
		filters = json.loads(filters)
	filters = filters or {}

	# Get customers that have subscriptions or campaigns linked
	base_filters = {}
	if filters.get("search"):
		base_filters["customer_name"] = ["like", f"%{filters['search']}%"]

	# Get all customers with active subscriptions
	subscribed_clients = frappe.db.sql("""
		SELECT DISTINCT cs.client
		FROM `tabClient Subscription` cs
		WHERE cs.status = 'Active' AND cs.end_date >= %(today)s
	""", {"today": today()}, as_list=True)
	subscribed_set = {r[0] for r in subscribed_clients}

	# Get all customers linked to campaigns
	campaign_clients = frappe.db.sql("""
		SELECT DISTINCT customer FROM `tabMarketing Campaign`
		WHERE customer IS NOT NULL AND customer != ''
	""", as_list=True)
	campaign_client_set = {r[0] for r in campaign_clients}

	# Union of all relevant customers
	all_client_names = subscribed_set | campaign_client_set

	if not all_client_names:
		return {"clients": [], "has_more": False}

	# Apply search filter
	client_filters = {"name": ["in", list(all_client_names)]}
	if base_filters.get("customer_name"):
		client_filters["customer_name"] = base_filters["customer_name"]

	customers = frappe.get_all(
		"Customer",
		fields=["name", "customer_name", "customer_type", "territory", "customer_group"],
		filters=client_filters,
		order_by="customer_name asc",
		limit=int(limit) + 1,
		start=int(offset)
	)

	has_more = len(customers) > int(limit)
	customers = customers[:int(limit)]

	# Enrich each client with stats
	for client in customers:
		# Active subscription
		sub = frappe.db.sql("""
			SELECT cs.name, cs.package, cs.status, cs.end_date, ap.package_name
			FROM `tabClient Subscription` cs
			LEFT JOIN `tabAgency Package` ap ON ap.name = cs.package
			WHERE cs.client = %(client)s AND cs.status = 'Active' AND cs.end_date >= %(today)s
			ORDER BY cs.end_date DESC LIMIT 1
		""", {"client": client.name, "today": today()}, as_dict=True)
		client["subscription"] = sub[0] if sub else None

		# Campaign counts
		client["active_campaigns"] = frappe.db.count(
			"Marketing Campaign",
			filters={"customer": client.name, "status": "Active"}
		)
		client["total_campaigns"] = frappe.db.count(
			"Marketing Campaign",
			filters={"customer": client.name}
		)

		# Linked projects count
		client["projects"] = frappe.db.count(
			"Project",
			filters={"customer": client.name, "status": "Open"}
		)

		# Total spend (from Analytics Daily Log via campaigns)
		spend = frappe.db.sql("""
			SELECT SUM(a.spend) as total_spend
			FROM `tabAnalytics Daily Log` a
			JOIN `tabMarketing Campaign` mc ON mc.name = a.campaign
			WHERE mc.customer = %(client)s
		""", {"client": client.name})
		client["total_spend"] = flt(spend[0][0] if spend and spend[0][0] else 0, 2)

	return {
		"clients": customers,
		"has_more": has_more
	}


@frappe.whitelist()
def get_client_detail(client):
	"""Get detailed client info with campaigns, subscription, and projects"""
	if not _is_agency_mode():
		frappe.throw(_("System is not in Agency mode"))

	customer = frappe.get_doc("Customer", client)

	# Active subscription
	subs = frappe.get_all(
		"Client Subscription",
		filters={"client": client, "status": "Active", "end_date": [">=", today()]},
		fields=["name", "package", "status", "start_date", "end_date", "monthly_fee"],
		order_by="end_date desc",
		limit=1
	)

	# Get package limits if subscription exists
	package_info = None
	if subs:
		try:
			pkg = frappe.get_doc("Agency Package", subs[0].package)
			package_info = {
				"name": pkg.name,
				"package_name": pkg.package_name,
				"campaign_limit": pkg.campaign_limit or 0,
				"blast_limit": pkg.blast_limit or 0,
				"social_post_limit": pkg.social_post_limit or 0,
				"included_channels": (pkg.included_channels or "").split("\n"),
			}
		except Exception:
			pass

	# Campaigns for this client
	campaigns = frappe.get_all(
		"Marketing Campaign",
		filters={"customer": client},
		fields=["name", "campaign_name", "status", "budget", "total_spent", "project", "start_date", "end_date"],
		order_by="modified desc",
		limit=50
	)

	# Projects linked to this customer
	projects = frappe.get_all(
		"Project",
		filters={"customer": client},
		fields=["name", "project_name", "status", "priority", "expected_start_date", "expected_end_date", "estimated_costing"],
		order_by="modified desc",
		limit=50
	)

	# Total spend
	spend = frappe.db.sql("""
		SELECT SUM(a.spend) as total_spend, SUM(a.revenue) as total_revenue
		FROM `tabAnalytics Daily Log` a
		JOIN `tabMarketing Campaign` mc ON mc.name = a.campaign
		WHERE mc.customer = %(client)s
	""", {"client": client}, as_dict=True)

	return {
		"customer": {
			"name": customer.name,
			"customer_name": customer.customer_name,
			"customer_type": customer.customer_type,
			"territory": customer.territory,
		},
		"subscription": subs[0] if subs else None,
		"package": package_info,
		"campaigns": campaigns,
		"projects": projects,
		"total_spend": flt(spend[0].total_spend if spend else 0, 2),
		"total_revenue": flt(spend[0].total_revenue if spend else 0, 2),
		"active_campaigns": len([c for c in campaigns if c.status == "Active"]),
	}


@frappe.whitelist()
def get_agency_overview():
	"""Dashboard overview for agency mode"""
	if not _is_agency_mode():
		return {"mode": "internal"}

	today_date = today()

	active_subs = frappe.db.count(
		"Client Subscription",
		filters={"status": "Active", "end_date": [">=", today_date]}
	)

	# Unique clients with active subscriptions
	active_clients = frappe.db.sql("""
		SELECT COUNT(DISTINCT client) FROM `tabClient Subscription`
		WHERE status = 'Active' AND end_date >= %(today)s
	""", {"today": today_date})[0][0] or 0

	# Total active campaigns across all clients
	active_campaigns = frappe.db.count(
		"Marketing Campaign",
		filters={"status": "Active", "customer": ["is", "set"]}
	)

	# Subscriptions expiring within 30 days
	expiring = frappe.get_all(
		"Client Subscription",
		filters={
			"status": "Active",
			"end_date": ["between", [today_date, add_days(today_date, 30)]]
		},
		fields=["name", "client", "client_name", "end_date", "package"],
		order_by="end_date asc"
	)

	# Top clients by spend (last 30 days)
	top_clients = frappe.db.sql("""
		SELECT
			mc.customer as client,
			c.customer_name as client_name,
			COUNT(DISTINCT mc.name) as campaigns,
			SUM(a.spend) as total_spend,
			SUM(a.revenue) as total_revenue
		FROM `tabMarketing Campaign` mc
		JOIN `tabCustomer` c ON c.name = mc.customer
		LEFT JOIN `tabAnalytics Daily Log` a ON a.campaign = mc.name
			AND a.log_date >= %(from_date)s
		WHERE mc.customer IS NOT NULL AND mc.customer != ''
		GROUP BY mc.customer
		ORDER BY total_spend DESC
		LIMIT 5
	""", {"from_date": add_days(today_date, -30)}, as_dict=True)

	# Open projects count
	open_projects = frappe.db.sql("""
		SELECT COUNT(DISTINCT p.name)
		FROM `tabProject` p
		JOIN `tabMarketing Campaign` mc ON mc.project = p.name
		WHERE p.status = 'Open'
	""")[0][0] or 0

	return {
		"mode": "agency",
		"active_clients": active_clients,
		"active_subscriptions": active_subs,
		"active_campaigns": active_campaigns,
		"open_projects": open_projects,
		"expiring_soon": expiring,
		"top_clients": top_clients,
	}


@frappe.whitelist()
def get_customer_options(search=None):
	"""Get customer list for autocomplete"""
	filters = {}
	if search:
		filters["customer_name"] = ["like", f"%{search}%"]

	customers = frappe.get_all(
		"Customer",
		fields=["name", "customer_name"],
		filters=filters,
		order_by="customer_name asc",
		limit=20
	)
	return customers


@frappe.whitelist()
def get_project_options(customer=None, search=None):
	"""Get project list for autocomplete, optionally filtered by customer"""
	filters = {"status": ["in", ["Open", "Completed"]]}
	if customer:
		filters["customer"] = customer
	if search:
		filters["project_name"] = ["like", f"%{search}%"]

	projects = frappe.get_all(
		"Project",
		fields=["name", "project_name", "status", "customer"],
		filters=filters,
		order_by="project_name asc",
		limit=20
	)
	return projects
