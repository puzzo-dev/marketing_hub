
import frappe
import json

def verify_state():
    if not frappe.db.exists("Workspace", "Marketing Hub"):
        print("Workspace 'Marketing Hub' NOT FOUND in DB")
        return

    doc = frappe.get_doc("Workspace", "Marketing Hub")
    
    print(f"\n--- DATABASE STATE FOR 'Marketing Hub' ---")
    
    # Check Content String
    if "Marketing Revenue" in doc.content and "Marketing Spend" in doc.content:
        print("Content Header: OK (Contains KPI section with Revenue/Spend)")
    else:
        print("Content Header: FAIL (Missing KPI section)")
        print(f"Content snippet: {doc.content[:100]}...")

    # Check Child Table
    cards = [d.number_card_name for d in doc.number_cards]
    print(f"Linked Number Cards: {cards}")
    
    if "Marketing Revenue" in cards and "Marketing Spend" in cards:
         print("Number Cards Table: OK")
    else:
         print("Number Cards Table: FAIL")

    print(f"Public: {doc.public}")
    print("------------------------------------------\n")
