# Copyright (c) 2026, Marketing Hub and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import add_to_date, formatdate, getdate, nowdate
from frappe.utils.dashboard import cache_source
from frappe.utils.dateutils import get_from_date_from_timespan, get_period_ending


@frappe.whitelist()
@cache_source
def get(
	chart_name=None,
	chart=None,
	no_cache=None,
	filters=None,
	from_date=None,
	to_date=None,
	timespan=None,
	time_interval=None,
	heatmap_year=None,
):
	if chart_name:
		chart = frappe.get_doc("Dashboard Chart", chart_name)
	else:
		chart = frappe._dict(frappe.parse_json(chart))

	timespan = chart.timespan or "Last 3 Months"
	timegrain = chart.time_interval or "Weekly"

	if not to_date:
		to_date = nowdate()
	if not from_date:
		from_date = get_from_date_from_timespan(to_date, timespan)

	dates = get_dates_from_timegrain(from_date, to_date, timegrain)

	labels = []
	values = []

	for i, period_end in enumerate(dates):
		period_start = dates[i - 1] if i > 0 else from_date

		result = frappe.db.sql("""
			SELECT
				COALESCE(SUM(spend), 0) as total_spend,
				COALESCE(SUM(conversions), 0) as total_conversions
			FROM `tabAnalytics Daily Log`
			WHERE log_date > %(start)s AND log_date <= %(end)s
		""", {"start": period_start, "end": period_end}, as_dict=1)

		row = result[0] if result else {"total_spend": 0, "total_conversions": 0}
		cac = row.total_spend / row.total_conversions if row.total_conversions else 0

		labels.append(formatdate(period_end))
		values.append(round(cac, 2))

	return {
		"labels": labels,
		"datasets": [{"name": "CAC", "values": values}],
	}


def get_dates_from_timegrain(from_date, to_date, timegrain):
	days = months = 0
	if timegrain == "Daily":
		days = 1
	elif timegrain == "Weekly":
		days = 7
	elif timegrain == "Monthly":
		months = 1
	elif timegrain == "Quarterly":
		months = 3

	dates = [get_period_ending(from_date, timegrain)]
	while getdate(dates[-1]) < getdate(to_date):
		date = get_period_ending(
			add_to_date(dates[-1], months=months, days=days), timegrain
		)
		dates.append(date)
	return dates
