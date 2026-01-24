frappe.query_reports["Marketing Expense Analysis"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			reqd: 1
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1
		},
		{
			fieldname: "campaign",
			label: __("Campaign"),
			fieldtype: "Link",
			options: "Campaign"
		},
		{
			fieldname: "expense_category",
			label: __("Expense Category"),
			fieldtype: "Link",
			options: "Marketing Expense Category"
		},
		{
			fieldname: "cost_center",
			label: __("Cost Center"),
			fieldtype: "Link",
			options: "Cost Center"
		},
		{
			fieldname: "project",
			label: __("Project"),
			fieldtype: "Link",
			options: "Project"
		},
		{
			fieldname: "is_paid",
			label: __("Is Paid"),
			fieldtype: "Check"
		}
	],
	
	formatter: function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		
		if (column.fieldname == "amount") {
			if (data.amount > 10000) {
				value = "<span style='color: red;'>" + value + "</span>";
			}
		}
		
		if (column.fieldname == "gl_entry_posted" && data.gl_entry_posted == 1) {
			value = "<span style='color: green;'>✓</span>";
		}
		
		return value;
	}
};
