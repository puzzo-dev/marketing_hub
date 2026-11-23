"""Numbers for the Home dashboard: by exercise, by channel and over time.

The rows come from Analytics Daily Log (one row per day, exercise and channel, filled by the
analytics connectors). Only exercises the caller may read are included, so a Brand Manager's
dashboard covers their own exercises and a Marketing Head's covers all of them.
"""

import frappe
from frappe import _
from frappe.utils import add_days, flt, getdate, today

PERIODS = {"7d": 7, "30d": 30, "90d": 90}
MEASURES = ("impressions", "clicks", "conversions", "spend")


def _visible_exercises(exercise=None):
	filters = {"name": exercise} if exercise else {}
	return frappe.get_list("Marketing Campaign", filters=filters, pluck="name", limit_page_length=0)


def _totals(exercises, start, end):
	row = frappe.db.sql(
		"""select coalesce(sum(impressions), 0) impressions, coalesce(sum(clicks), 0) clicks,
		coalesce(sum(conversions), 0) conversions, coalesce(sum(spend), 0) spend
		from `tabAnalytics Daily Log` where campaign in %(ex)s and log_date between %(s)s and %(e)s""",
		{"ex": exercises, "s": start, "e": end},
		as_dict=True,
	)[0]
	return {k: flt(row[k]) for k in MEASURES}


def _change(now, before):
	"""Percent change against the previous period; None when there is nothing to compare."""
	return None if not before else round((now - before) / before * 100, 1)


@frappe.whitelist()
def overview(period="30d", exercise=None):
	if period not in PERIODS:
		frappe.throw(_("Unknown period"))
	days = PERIODS[period]
	end = getdate(today())
	start = add_days(end, -(days - 1))
	prev_end = add_days(start, -1)
	prev_start = add_days(prev_end, -(days - 1))

	exercises = _visible_exercises(exercise)
	empty = {"kpis": {}, "by_exercise": [], "by_channel": [], "trend": [], "period": {"from": str(start), "to": str(end)}}
	if not exercises:
		return empty

	now = _totals(exercises, start, end)
	before = _totals(exercises, prev_start, prev_end)
	leads = frappe.db.count("Lead", {"mkt_campaign": ["in", exercises], "creation": ["between", [start, add_days(end, 1)]]})
	leads_before = frappe.db.count("Lead", {"mkt_campaign": ["in", exercises], "creation": ["between", [prev_start, start]]})

	kpis = {
		"spend": {"value": now["spend"], "change": _change(now["spend"], before["spend"])},
		"impressions": {"value": now["impressions"], "change": _change(now["impressions"], before["impressions"])},
		"clicks": {"value": now["clicks"], "change": _change(now["clicks"], before["clicks"])},
		"leads": {"value": leads, "change": _change(leads, leads_before)},
		"cost_per_lead": {"value": round(now["spend"] / leads, 2) if leads else None, "change": None},
	}

	params = {"ex": exercises, "s": start, "e": end}
	by_exercise = frappe.db.sql(
		"""select l.campaign exercise, c.campaign_name name, sum(l.spend) spend, sum(l.clicks) clicks,
		sum(l.impressions) impressions, sum(l.conversions) conversions
		from `tabAnalytics Daily Log` l join `tabMarketing Campaign` c on c.name = l.campaign
		where l.campaign in %(ex)s and l.log_date between %(s)s and %(e)s
		group by l.campaign, c.campaign_name order by spend desc limit 20""",
		params,
		as_dict=True,
	)
	by_channel = frappe.db.sql(
		"""select channel, sum(spend) spend, sum(clicks) clicks, sum(impressions) impressions, sum(conversions) conversions
		from `tabAnalytics Daily Log` where campaign in %(ex)s and log_date between %(s)s and %(e)s
		group by channel order by spend desc""",
		params,
		as_dict=True,
	)
	trend = frappe.db.sql(
		"""select log_date date, sum(spend) spend, sum(clicks) clicks, sum(impressions) impressions
		from `tabAnalytics Daily Log` where campaign in %(ex)s and log_date between %(s)s and %(e)s
		group by log_date order by log_date""",
		params,
		as_dict=True,
	)
	return {
		"kpis": kpis,
		"by_exercise": by_exercise,
		"by_channel": by_channel,
		"trend": [{**r, "date": str(r["date"])} for r in trend],
		"period": {"from": str(start), "to": str(end)},
	}
