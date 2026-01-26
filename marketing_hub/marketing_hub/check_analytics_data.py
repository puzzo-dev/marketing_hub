
import frappe

def check_data():
    count = frappe.db.count("Analytics Daily Log")
    print(f"Total Analytics Logs: {count}")
    
    if count > 0:
        sample = frappe.get_all("Analytics Daily Log", fields=["spend", "revenue", "impressions", "clicks"], limit=1)
        print(f"Sample Data: {sample}")
    else:
        print("Table is empty.")

check_data()
