import frappe

def get_context(context):
	"""Get context for onboarding portal page"""
	context.no_cache = 1
	
	# Check if user is logged in
	if frappe.session.user == "Guest":
		frappe.throw("Please login to access this page", frappe.PermissionError)
	
	# Determine user mode (admin or agent)
	user_roles = frappe.get_roles(frappe.session.user)
	context.mode = "admin" if any(role in ["System Manager", "Marketing Manager"] for role in user_roles) else "agent"
	
	return context
