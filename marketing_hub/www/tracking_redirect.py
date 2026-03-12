import frappe


no_cache = True


def get_context(context):
	"""Handle tracking link redirect"""
	short_code = frappe.form_dict.get("short_code")
	if not short_code:
		frappe.throw("Invalid tracking link", frappe.DoesNotExistError)

	from marketing_hub.api.tracking import handle_redirect
	handle_redirect(short_code)
