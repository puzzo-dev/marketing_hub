frappe.query_reports["Campaign Budget vs Actual"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company")
		},
		{
			fieldname: "status",
			label: __("Campaign Status"),
			fieldtype: "Select",
			options: "\nPlanning\nIn Progress\nCompleted\nCancelled"
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -6)
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today()
		}
	],
	
	formatter: function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		
		// Highlight over-budget campaigns
		if (column.fieldname == "variance" && data.variance < 0) {
			value = "<span style='color: red; font-weight: bold;'>" + value + "</span>";
		}
		
		// Highlight positive ROI
		if (column.fieldname == "roi_percentage") {
			if (data.roi_percentage > 0) {
				value = "<span style='color: green;'>" + value + "</span>";
			} else if (data.roi_percentage < 0) {
				value = "<span style='color: red;'>" + value + "</span>";
			}
		}
		
		// Color code utilization percentage
		if (column.fieldname == "utilization_percentage") {
			if (data.utilization_percentage > 100) {
				value = "<span style='color: red; font-weight: bold;'>" + value + "</span>";
			} else if (data.utilization_percentage > 80) {
				value = "<span style='color: orange;'>" + value + "</span>";
			} else {
				value = "<span style='color: green;'>" + value + "</span>";
			}
		}
		
		return value;
	}
};
