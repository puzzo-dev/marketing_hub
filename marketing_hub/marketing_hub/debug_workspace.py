
import frappe
import json

def debug_workspace():
    workspace_name = "Marketing Hub"
    
    # 1. Check if Doc exists
    if not frappe.db.exists("Workspace", workspace_name):
        print(f"Workspace '{workspace_name}' does not exist in DB!")
        return

    doc = frappe.get_doc("Workspace", workspace_name)
    
    # 2. Check public status
    print(f"Workspace Public: {doc.public}")
    print(f"Workspace Modified: {doc.modified}")
    print(f"Is Custom: {doc.get('is_custom')}") # Often used in user customizations

    # 3. Check for shadowing (User-specific workspace)
    # Check if there are other workspaces that might shadow this one
    shadows = frappe.get_all("Workspace", filters={"for_user": ["is", "set"], "module": "Marketing Hub"}, fields=["name", "for_user"])
    if shadows:
        print(f"Found user-specific workspaces: {shadows}")

    # 4. Force Reload from File
    # This reads the JSON from the module path and updates the DB record
    try:
        from frappe.modules import reload_doc
        reload_doc("marketing_hub", "workspace", "marketing_hub", force=True)
        print("Forced reload of Marketing Hub workspace from file.")
        
        # Verify changes after reload
        new_doc = frappe.get_doc("Workspace", workspace_name)
        
        # Check if new content string contains "Marketing Revenue"
        if "Marketing Revenue" in new_doc.content:
            print("SUCCESS: 'Marketing Revenue' found in workspace content after reload.")
        else:
            print("FAILURE: 'Marketing Revenue' NOT found in workspace content even after reload.")
            
    except Exception as e:
        print(f"Error reloading doc: {e}")

    frappe.db.commit()

debug_workspace()
