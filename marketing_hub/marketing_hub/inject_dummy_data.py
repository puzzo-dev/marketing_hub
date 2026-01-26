
import frappe
from frappe.utils import nowdate, add_days
import random

def create_dummy_data():
    if frappe.db.count("Analytics Daily Log") > 0:
        print("Data already exists. Skipping.")
        return

    print("Creating dummy analytics logs...")
    
    # Create dummy Ad Account if needed
    ad_account_name = None
    if frappe.db.exists("Ad Account", {"account_name": "Test Ad Account"}):
        ad_account_name = frappe.db.get_value("Ad Account", {"account_name": "Test Ad Account"}, "name")
    else:
        ad_acc = frappe.new_doc("Ad Account")
        ad_acc.account_name = "Test Ad Account"
        ad_acc.social_media_network = "Meta Ads"
        ad_acc.account_id = "ACT_123456789"
        ad_acc.status = "Active"
        ad_acc.save(ignore_permissions=True)
        ad_account_name = ad_acc.name
    
    # Create a dummy connector first if needed
    connector_name = None
    if frappe.db.exists("Analytics Connector", {"connector_name": "Test Connector"}):
        connector_name = frappe.db.get_value("Analytics Connector", {"connector_name": "Test Connector"}, "name")
    else:
        c = frappe.new_doc("Analytics Connector")
        c.connector_name = "Test Connector"
        c.platform = "Meta Ads"
        c.ad_account = ad_account_name
        c.status = "Active"
        c.save(ignore_permissions=True)
        connector_name = c.name

    # Create dummy logs for last 30 days
    for i in range(30):
        log = frappe.new_doc("Analytics Daily Log")
        log.log_date = add_days(nowdate(), -i)
        log.connector = connector_name # Use correct connector ID
        log.channel = "Meta Ads"
        log.impressions = random.randint(1000, 5000)
        log.clicks = random.randint(50, 200)
        log.spend = random.randint(100, 500)
        log.revenue = log.spend * random.uniform(2.5, 5.0) # ROAS 2.5-5.0
        log.save(ignore_permissions=True)
        frappe.db.commit()

    print(f"Created 30 dummy logs.")

create_dummy_data()
