
import frappe

def cleanup_workspace():
    if frappe.db.exists("Workspace", "Marketing Connect"):
        frappe.delete_doc("Workspace", "Marketing Connect", force=True)
        print("Deleted duplicate workspace 'Marketing Connect'.")
    else:
        print("Workspace 'Marketing Connect' already removed.")

cleanup_workspace()
