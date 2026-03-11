frappe.provide("frappe.dashboards.chart_sources");

frappe.dashboards.chart_sources["CAC Trend"] = {
	method: "marketing_hub.marketing_hub.dashboard_chart_source.cac_trend.cac_trend.get",
	filters: [],
};
