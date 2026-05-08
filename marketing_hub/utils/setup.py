import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def create_engagement_score_field():
	create_custom_field("Lead", {
		"fieldname": "engagement_score",
		"label": "Engagement Score",
		"fieldtype": "Int",
		"insert_after": "status",
		"read_only": 1,
		"default": "0"
	})
	print("Engagement score field created on Lead.")

create_engagement_score_field()
