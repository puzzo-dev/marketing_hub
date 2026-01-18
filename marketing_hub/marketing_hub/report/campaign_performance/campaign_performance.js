// Copyright (c) 2026, Your Name and contributors
// For license information, please see license.txt

frappe.query_reports["Campaign Performance"] = {
	"filters": [
		{
			fieldname: "campaign",
			label: __("Campaign"),
			fieldtype: "Link",
			options: "Campaign"
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company"
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -3)
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today()
		}
	],

	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		// Color-code ROAS
		if (column.fieldname === "roas" && data) {
			if (data.roas >= 3) {
				value = `<span style="color: green; font-weight: bold;">${value}</span>`;
			} else if (data.roas >= 2) {
				value = `<span style="color: orange; font-weight: bold;">${value}</span>`;
			} else if (data.roas > 0) {
				value = `<span style="color: red;">${value}</span>`;
			}
		}

		// Color-code ROI
		if (column.fieldname === "roi" && data) {
			if (data.roi >= 100) {
				value = `<span style="color: green; font-weight: bold;">${value}</span>`;
			} else if (data.roi >= 0) {
				value = `<span style="color: orange;">${value}</span>`;
			} else {
				value = `<span style="color: red;">${value}</span>`;
			}
		}

		// Color-code conversion rate
		if (column.fieldname === "conversion_rate" && data) {
			if (data.conversion_rate >= 10) {
				value = `<span style="color: green; font-weight: bold;">${value}</span>`;
			} else if (data.conversion_rate >= 5) {
				value = `<span style="color: orange;">${value}</span>`;
			}
		}

		return value;
	}
};
