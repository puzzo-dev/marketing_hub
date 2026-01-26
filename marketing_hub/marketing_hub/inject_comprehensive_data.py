
import frappe
from frappe.utils import nowdate, add_days
import random

def inject_data():
    print("Injecting comprehensive demo data...")
    
    # Ensure Marketing Hub Settings exist
    try:
        if not frappe.db.exists("Company", "Test Company"):
             # Fallback if Test Company doesn't exist
             company = frappe.db.get_value("Company", {"is_group": 0})
        else:
             company = "Test Company"

        s = frappe.get_single("Marketing Hub Settings")
        s.company = company
        s.save(ignore_permissions=True)
        frappe.db.commit() # Commit to ensure it's available
    except Exception as e:
        print(f"Warning: Could not init settings: {e}")

    # 1. Marketing Campaigns (for Campaign Performance Overview)
    for i in range(10):
        if not frappe.db.exists("Marketing Campaign", f"Demo Campaign {i}"):
            c = frappe.new_doc("Marketing Campaign")
            c.campaign_name = f"Demo Campaign {i}"
            c.status = random.choice(["Active", "Completed"])
            c.start_date = add_days(nowdate(), -random.randint(0, 60))
            c.end_date = add_days(nowdate(), random.randint(0, 30))
            c.total_budget = random.randint(1000, 10000)
            c.save(ignore_permissions=True)
    print("Created 10 Marketing Campaigns.")

    # 2. Social Posts (for Channel Distribution)
    platforms = ["Facebook", "LinkedIn", "Twitter", "Instagram"]
    
    # Ensure Social Media Networks exist
    for p in platforms:
        if not frappe.db.exists("Social Media Network", p):
            n = frappe.new_doc("Social Media Network")
            n.network_name = p
            n.network_code = p.lower().replace(" ", "_") # Add mandatory field
            n.save(ignore_permissions=True)

    # Ensure Post Type exists
    if not frappe.db.exists("Post Type", "Regular"):
        pt = frappe.new_doc("Post Type")
        pt.type_name = "Regular" # Correct field name
        pt.save(ignore_permissions=True)

    for i in range(20):
        p = frappe.new_doc("Social Post")
        p.headline = f"Demo Post {i}"
        p.post_title = f"Demo Post Title {i}"
        p.post_type = "Regular" # Now valid Link
        p.content = f"This is the content for demo post {i}."
        p.platform = random.choice(platforms)
        p.status = "Published" # Correct status value
        p.scheduled_time = add_days(nowdate(), -random.randint(0, 30))
        p.save(ignore_permissions=True)
    print("Created 20 Social Posts.")

inject_data()
