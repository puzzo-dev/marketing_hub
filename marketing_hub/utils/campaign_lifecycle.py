import frappe
from frappe.utils import today

def update_campaign_statuses():
	"""Daily job to auto-transition campaign statuses"""
	current_date = today()
	
	# 1. Start Approved campaigns
	approved_campaigns = frappe.get_all("Marketing Campaign", 
		filters={"status": "Approved", "start_date": ["<=", current_date]},
		fields=["name", "end_date"]
	)
	for c in approved_campaigns:
		if c.end_date and c.end_date < current_date:
			frappe.db.set_value("Marketing Campaign", c.name, "status", "Completed")
		else:
			frappe.db.set_value("Marketing Campaign", c.name, "status", "Active")
			
	# 2. Complete Active campaigns that reached end date
	ended_campaigns = frappe.get_all("Marketing Campaign",
		filters={"status": "Active", "end_date": ["<", current_date]},
		fields=["name"]
	)
	for c in ended_campaigns:
		frappe.db.set_value("Marketing Campaign", c.name, "status", "Completed")
		
	# 3. Pause Active campaigns if agency subscription expired
	agency_mode = frappe.db.get_single_value("Marketing Hub Settings", "agency_mode")
	if agency_mode:
		active_campaigns = frappe.get_all("Marketing Campaign",
			filters={"status": "Active", "customer": ["is", "set"]},
			fields=["name", "customer"]
		)
		for c in active_campaigns:
			sub_check = frappe.call("marketing_hub.utils.agency_mode.check_client_subscription", client=c.customer)
			if not sub_check.get("valid"):
				frappe.db.set_value("Marketing Campaign", c.name, "status", "Paused")
				frappe.log_error(f"Campaign {c.name} paused due to expired subscription for {c.customer}", "Campaign Paused")
