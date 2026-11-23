"""The Home screen for the roles that do not get the analytics dashboard.

Everything here goes through frappe.get_list, so each person only sees what their
permissions already allow. Brand Managers keep the analytics Home; clients have their own API."""

import frappe
from frappe import _
from frappe.utils import add_days, today


def _count(doctype, filters):
	return len(frappe.get_list(doctype, filters=filters, pluck="name", limit=1000))


def _rows(doctype, filters, fields, order_by, route, params_field="name", limit=5, title_field=None, sub=None, status=None):
	out = []
	for r in frappe.get_list(doctype, filters=filters, fields=list(set(fields + [params_field])), order_by=order_by, limit=limit):
		out.append({"title": r.get(title_field or fields[0]), "sub": sub(r) if sub else "", "status": r.get(status) if status else None, "route": route, "param": r.get(params_field)})
	return out


@frappe.whitelist()
def get(role):
	fn = {"Marketing Head": _head, "Content Lead": _lead, "Media Planner": _lead, "Publisher": _publisher, "OOH Coordinator": _ooh}.get(role)
	if not fn:
		frappe.throw(_("No home screen for this role"), frappe.PermissionError)
	return fn()


def _head():
	waiting = _count("Workflow Action", {"status": "Open"})
	return {
		"alert": {"text": _("{0} requests are waiting for you").format(waiting), "route": "Approvals"} if waiting else None,
		"figures": [
			{"label": _("Exercises"), "value": _count("Marketing Campaign", {"status": ["in", ["Draft", "Active"]]})},
			{"label": _("Running"), "value": _count("Marketing Campaign", {"status": "Active"})},
			{"label": _("Planning"), "value": _count("Marketing Campaign", {"status": "Draft"})},
		],
		"lists": [{"title": _("Exercises"), "rows": _rows("Marketing Campaign", {"status": ["in", ["Draft", "Active"]]}, ["campaign_name", "brand", "end_date", "status"], "end_date asc", "Exercise", sub=lambda r: f"{r.brand} · ends {r.end_date}", status="status", title_field="campaign_name")}],
	}


def _lead():
	end = add_days(today(), 7)
	return {
		"alert": None,
		"figures": [
			{"label": _("In review"), "value": _count("Content Item", {"status": "In review"})},
			{"label": _("Drafts"), "value": _count("Content Item", {"status": "Draft"})},
			{"label": _("Due this week"), "value": _count("Content Item", {"status": ["in", ["Draft", "In review"]], "due_date": ["between", [today(), end]]})},
			{"label": _("Approved"), "value": _count("Content Item", {"status": "Approved"})},
		],
		"lists": [{"title": _("Due soon"), "rows": _rows("Content Item", {"status": ["in", ["Draft", "In review"]]}, ["title", "campaign", "due_date", "status"], "due_date asc", "ContentDetail", sub=lambda r: f"{r.campaign} · due {r.due_date or '—'}", status="status")}],
	}


def _publisher():
	failed = _count("Placement", {"status": "Failed"})
	return {
		"alert": {"text": _("{0} placements failed to send").format(failed), "route": "Placements"} if failed else None,
		"figures": [
			{"label": _("Waiting for approval"), "value": _count("Placement", {"approval_state": "Pending"})},
			{"label": _("Scheduled"), "value": _count("Placement", {"status": "Scheduled", "approval_state": "Approved"})},
			{"label": _("Posted"), "value": _count("Placement", {"status": "Posted"})},
			{"label": _("Failed"), "value": failed},
		],
		"lists": [{"title": _("Needs your attention"), "rows": _rows("Placement", {"status": "Failed"}, ["content_item", "channel", "scheduled_for", "status"], "scheduled_for desc", "Placement", sub=lambda r: f"{r.channel} · {r.scheduled_for}", status="status")}],
	}


def _ooh():
	return {
		"alert": None,
		"figures": [
			{"label": _("Proposed"), "value": _count("OOH Booking", {"status": "Proposed"})},
			{"label": _("In production"), "value": _count("OOH Booking", {"status": "Production"})},
			{"label": _("Live"), "value": _count("OOH Booking", {"status": "Live"})},
		],
		"lists": [{"title": _("Needs action"), "rows": _rows("OOH Booking", {"status": ["in", ["Proposed", "Approved", "Production"]]}, ["site", "campaign", "start_date", "status"], "start_date asc", "OOHBooking", sub=lambda r: f"{r.campaign} · starts {r.start_date}", status="status")}],
	}
