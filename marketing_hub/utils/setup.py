import frappe

def create_ab_test_doctype():
	if not frappe.db.exists("DocType", "A-B Test"):
		doc = frappe.get_doc({
			"doctype": "DocType",
			"name": "A-B Test",
			"module": "Marketing Hub",
			"custom": 1,
			"autoname": "format:ABT-{######}",
			"fields": [
				{
					"fieldname": "test_name",
					"fieldtype": "Data",
					"label": "Test Name",
					"reqd": 1,
					"in_list_view": 1
				},
				{
					"fieldname": "status",
					"fieldtype": "Select",
					"label": "Status",
					"options": "Draft\nRunning\nCompleted",
					"default": "Draft",
					"in_list_view": 1
				},
				{
					"fieldname": "campaign",
					"fieldtype": "Link",
					"label": "Campaign",
					"options": "Marketing Campaign",
					"reqd": 1,
					"in_list_view": 1
				},
				{
					"fieldname": "segment",
					"fieldtype": "Link",
					"label": "Target Segment",
					"options": "Marketing Segment",
					"reqd": 1
				},
				{
					"fieldname": "test_metric",
					"fieldtype": "Select",
					"label": "Winning Metric",
					"options": "Open Rate\nClick Rate\nConversion Rate",
					"default": "Click Rate",
					"reqd": 1
				},
				{
					"fieldname": "column_break_1",
					"fieldtype": "Column Break"
				},
				{
					"fieldname": "split_percentage",
					"fieldtype": "Percent",
					"label": "Test Group Size (%)",
					"default": 20,
					"description": "Percentage of segment to receive variants. Remaining will receive winner."
				},
				{
					"fieldname": "test_duration_hours",
					"fieldtype": "Int",
					"label": "Test Duration (Hours)",
					"default": 24
				},
				{
					"fieldname": "winner",
					"fieldtype": "Data",
					"label": "Winning Variant",
					"read_only": 1
				},
				{
					"fieldname": "section_break_variants",
					"fieldtype": "Section Break",
					"label": "Variants"
				},
				{
					"fieldname": "variant_a_template",
					"fieldtype": "Link",
					"label": "Variant A Template",
					"options": "Marketing Template"
				},
				{
					"fieldname": "variant_b_template",
					"fieldtype": "Link",
					"label": "Variant B Template",
					"options": "Marketing Template"
				}
			],
			"permissions": [
				{
					"role": "Marketing Manager",
					"read": 1,
					"write": 1,
					"create": 1,
					"delete": 1
				}
			]
		})
		doc.insert(ignore_permissions=True)
		frappe.db.commit()
		print("A/B Test DocType created.")
	else:
		print("A/B Test DocType already exists.")

create_ab_test_doctype()
