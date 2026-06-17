import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def add_expense_fields():
	create_custom_field("Marketing Expense", {
		"fieldname": "exclude_from_campaign_totals",
		"label": "Exclude from Campaign Totals",
		"fieldtype": "Check",
		"insert_after": "campaign",
		"description": "Check this if this expense represents auto-synced ad spend already counted in Analytics logs to prevent double-counting.",
		"default": "0"
	})
	print("Marketing expense fields created.")

add_expense_fields()
