
import frappe

def has_app_permission(doc=None):
    if frappe.session.user == "Administrator":
        return True
    
    # Check if user has Marketing Manager or System Manager role
    roles = frappe.get_roles()
    if "Marketing Manager" in roles or "System Manager" in roles:
        return True
        
    return False
