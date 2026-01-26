
import frappe

def verify_rename():
    if frappe.db.exists("Workspace", "Social Connect"):
        print("PASS: 'Social Connect' Workspace found.")
        doc = frappe.get_doc("Workspace", "Social Connect")
        print(f"Title: {doc.title}")
        print(f"Public: {doc.public}")
    else:
        print("FAIL: 'Social Connect' Workspace NOT found.")

verify_rename()
