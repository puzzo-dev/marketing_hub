// Copyright (c) 2026, Your Name and contributors
// For license information, please see license.txt

frappe.query_reports["ROAS Analysis"] = {
	"filters": [
		{
			fieldname: "group_by",
			label: __("Group By"),
			fieldtype: "Select",
			options: "Campaign\nChannel\nMonth",
			default: "Campaign",
			reqd: 1
		},
		{
			fieldname: "campaign",
			label: __("Campaign"),
			fieldtype: "Link",
			options: "Campaign",
			depends_on: "eval:doc.group_by=='Campaign'"
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -3),
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
			fieldname: "min_roas",
			label: __("Minimum ROAS"),
			fieldtype: "Float",
			default: 0,
			description: "Only show results with ROAS >= this value"
		}
	],

	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		// Color-code ROAS
		if (column.fieldname === "roas" && data) {
			if (data.roas >= 4) {
				value = `<span style="color: green; font-weight: bold;">${value}</span>`;
			} else if (data.roas >= 3) {
				value = `<span style="color: green;">${value}</span>`;
			} else if (data.roas >= 2) {
				value = `<span style="color: orange;">${value}</span>`;
			} else if (data.roas > 0) {
				value = `<span style="color: red;">${value}</span>`;
			}
		}

		// Color-code CTR
		if (column.fieldname === "ctr" && data) {
			if (data.ctr >= 5) {
				value = `<span style="color: green; font-weight: bold;">${value}</span>`;
			} else if (data.ctr >= 2) {
				value = `<span style="color: orange;">${value}</span>`;
			}
		}

		return value;
	}
};
