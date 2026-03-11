import frappe


@frappe.whitelist()
def has_app_permission():
	if frappe.session.user == "Administrator":
		return True

	roles = frappe.get_roles()
	if "Marketing Manager" in roles or "System Manager" in roles or "Marketing User" in roles:
		return True

	return False
