
import frappe

def check_status():
    print("--- WORKSPACES ---")
    workspaces = frappe.get_all("Workspace", filters={"module": "Marketing Hub"}, fields=["name", "label", "public"])
    for w in workspaces:
        print(f"Workspace: {w.name} | Label: {w.label} | Public: {w.public}")

    print("\n--- ANALYTICS DATA ---")
    count = frappe.db.count("Analytics Daily Log")
    print(f"Total Logs: {count}")
    if count > 0:
        sums = frappe.db.sql("SELECT SUM(spend), SUM(revenue) FROM `tabAnalytics Daily Log`")[0]
        print(f"Total Spend: {sums[0]}")
        print(f"Total Revenue: {sums[1]}")

check_status()
