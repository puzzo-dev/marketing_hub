import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def add_drip_fields():
	fields = [
		{"fieldname": "drip_sequence_section", "label": "Drip Sequence Logic", "fieldtype": "Section Break", "insert_after": "status", "collapsible": 1},
		{"fieldname": "parent_activity", "label": "Parent Activity (Trigger)", "fieldtype": "Link", "options": "Campaign Activity", "insert_after": "drip_sequence_section"},
		{"fieldname": "trigger_condition", "label": "Trigger Condition", "fieldtype": "Select", "options": "\nOn Sent\nOn Opened\nOn Clicked\nOn Bounced", "insert_after": "parent_activity", "depends_on": "eval:doc.parent_activity"},
		{"fieldname": "delay_days", "label": "Delay (Days)", "fieldtype": "Int", "insert_after": "trigger_condition", "depends_on": "eval:doc.parent_activity", "default": "0"},
		{"fieldname": "delay_hours", "label": "Delay (Hours)", "fieldtype": "Int", "insert_after": "delay_days", "depends_on": "eval:doc.parent_activity", "default": "0"},
	]
	
	for f in fields:
		create_custom_field("Campaign Activity", f)
		
	print("Drip sequence fields created.")

add_drip_fields()
