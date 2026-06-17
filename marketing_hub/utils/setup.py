import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def add_multi_touch_fields():
	fields = [
		{"fieldname": "first_touch_campaign", "label": "First Touch Campaign", "fieldtype": "Data", "insert_after": "utm_medium", "read_only": 1},
		{"fieldname": "first_touch_source", "label": "First Touch Source", "fieldtype": "Data", "insert_after": "first_touch_campaign", "read_only": 1},
		{"fieldname": "first_touch_medium", "label": "First Touch Medium", "fieldtype": "Data", "insert_after": "first_touch_source", "read_only": 1},
		{"fieldname": "last_touch_campaign", "label": "Last Touch Campaign", "fieldtype": "Data", "insert_after": "first_touch_medium", "read_only": 1},
		{"fieldname": "last_touch_source", "label": "Last Touch Source", "fieldtype": "Data", "insert_after": "last_touch_campaign", "read_only": 1},
		{"fieldname": "last_touch_medium", "label": "Last Touch Medium", "fieldtype": "Data", "insert_after": "last_touch_source", "read_only": 1},
	]
	
	for f in fields:
		create_custom_field("Lead", f)
		
	print("Multi-touch fields created.")

add_multi_touch_fields()
