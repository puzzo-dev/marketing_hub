import frappe
from frappe.utils import nowdate, add_to_date


@frappe.whitelist()
def get_average_cac(filters=None, from_date=None, to_date=None):
	if not to_date:
		to_date = nowdate()
	if not from_date:
		from_date = add_to_date(to_date, months=-1)

	result = frappe.db.sql("""
		SELECT
			COALESCE(SUM(spend), 0) as total_spend,
			COALESCE(SUM(conversions), 0) as total_conversions
		FROM `tabAnalytics Daily Log`
		WHERE log_date BETWEEN %(from_date)s AND %(to_date)s
	""", {"from_date": from_date, "to_date": to_date}, as_dict=1)

	row = result[0] if result else {"total_spend": 0, "total_conversions": 0}
	value = round(row.total_spend / row.total_conversions, 2) if row.total_conversions else 0

	# Previous period for comparison
	period_days = (frappe.utils.getdate(to_date) - frappe.utils.getdate(from_date)).days
	prev_to = add_to_date(from_date, days=-1)
	prev_from = add_to_date(prev_to, days=-period_days)

	prev_result = frappe.db.sql("""
		SELECT
			COALESCE(SUM(spend), 0) as total_spend,
			COALESCE(SUM(conversions), 0) as total_conversions
		FROM `tabAnalytics Daily Log`
		WHERE log_date BETWEEN %(from_date)s AND %(to_date)s
	""", {"from_date": prev_from, "to_date": prev_to}, as_dict=1)

	prev_row = prev_result[0] if prev_result else {"total_spend": 0, "total_conversions": 0}
	prev_value = round(prev_row.total_spend / prev_row.total_conversions, 2) if prev_row.total_conversions else 0

	return {
		"value": value,
		"fieldtype": "Currency",
		"route_options": {},
		"route": [],
	}
