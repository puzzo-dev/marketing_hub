frappe.query_reports["Campaign Performance"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": "From Date",
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": "To Date",
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "status",
			"label": "Status",
			"fieldtype": "Select",
			"options": "\nPlanning\nRunning\nPaused\nCompleted",
			"default": ""
		}
	]
};
