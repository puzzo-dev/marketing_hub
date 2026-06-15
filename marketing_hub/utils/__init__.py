# Marketing Hub Utils Module

import frappe


def get_company(company=None):
	"""Get the active company - explicit param or user default."""
	if company:
		return company
	return frappe.defaults.get_user_default("Company")
