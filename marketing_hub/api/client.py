"""What a client sees. Clients never read the doctypes: they call these methods, which check
that the caller is a Client on the exercise's brand and return only client-safe fields
(no rates, no vendor, no internal notes, no approver)."""

import frappe
from frappe import _
from frappe.utils import flt


def _exercise_for_client(name):
	brand = frappe.db.get_value("Marketing Campaign", name, "brand")
	if not brand:
		frappe.throw(_("Not found"), frappe.DoesNotExistError)
	is_client = frappe.db.exists("Brand Team Member", {"parent": brand, "parenttype": "Brand", "user": frappe.session.user, "brand_role": "Client"})
	if not is_client and "System Manager" not in frappe.get_roles():
		frappe.throw(_("You do not have access to this."), frappe.PermissionError)
	return frappe.db.get_value("Marketing Campaign", name, ["name", "campaign_name", "status", "start_date", "end_date", "budget", "project", "objective"], as_dict=True)


@frappe.whitelist()
def exercises():
	"""The exercises on brands where the caller is a Client."""
	brands = frappe.get_all("Brand Team Member", filters={"user": frappe.session.user, "brand_role": "Client", "parenttype": "Brand"}, pluck="parent")
	if not brands:
		return []
	return frappe.get_all("Marketing Campaign", filters={"brand": ["in", brands]}, fields=["name", "campaign_name", "status", "start_date", "end_date"], order_by="start_date desc")


@frappe.whitelist()
def exercise(name):
	return _exercise_for_client(name)


@frappe.whitelist()
def spend(name):
	"""Spend is read from the ledger against the exercise's Project."""
	ex = _exercise_for_client(name)
	spent = 0
	if ex.project:
		spent = flt(frappe.db.sql("select sum(debit - credit) from `tabGL Entry` where project = %s and is_cancelled = 0", ex.project)[0][0])
	return {"budget": flt(ex.budget), "spent": spent}


@frappe.whitelist()
def posted_content(name):
	_exercise_for_client(name)
	return frappe.get_all("Content Item", filters={"campaign": name, "status": "Posted"}, fields=["name", "title", "type", "modified"])


@frappe.whitelist()
def out_of_home(name):
	_exercise_for_client(name)
	rows = frappe.get_all("OOH Booking", filters={"campaign": name, "status": ["in", ["Live", "Ended"]]}, fields=["site", "start_date", "end_date", "status"])
	for r in rows:
		r["latitude"], r["longitude"] = frappe.db.get_value("OOH Site", r["site"], ["latitude", "longitude"])
	return rows


@frappe.whitelist()
def results(name):
	_exercise_for_client(name)
	leads = frappe.db.count("Lead", {"mkt_campaign": name})
	return {"leads": leads}


# ---- across every exercise the client can see (the sidebar pages) ----
def _my_exercise_names():
	return [e.name for e in exercises()] if "System Manager" not in frappe.get_roles() else frappe.get_all("Marketing Campaign", pluck="name")


@frappe.whitelist()
def all_posted_content():
	names = _my_exercise_names()
	if not names:
		return []
	rows = frappe.get_all("Content Item", filters={"campaign": ["in", names], "status": "Posted"}, fields=["name", "title", "type", "campaign", "modified"], order_by="modified desc")
	titles = dict(frappe.get_all("Marketing Campaign", filters={"name": ["in", names]}, fields=["name", "campaign_name"], as_list=True))
	for r in rows:
		r["exercise"] = titles.get(r["campaign"])
	return rows


@frappe.whitelist()
def all_out_of_home():
	names = _my_exercise_names()
	if not names:
		return []
	rows = frappe.get_all("OOH Booking", filters={"campaign": ["in", names], "status": ["in", ["Live", "Ended"]]}, fields=["name", "site", "campaign", "start_date", "end_date", "status"], order_by="start_date desc")
	titles = dict(frappe.get_all("Marketing Campaign", filters={"name": ["in", names]}, fields=["name", "campaign_name"], as_list=True))
	for r in rows:
		r["exercise"] = titles.get(r["campaign"])
	return rows


@frappe.whitelist()
def all_results():
	"""Leads per exercise. No cost per lead and no channel spend: clients see outcomes only."""
	names = _my_exercise_names()
	titles = dict(frappe.get_all("Marketing Campaign", filters={"name": ["in", names]}, fields=["name", "campaign_name"], as_list=True)) if names else {}
	return [{"name": n, "exercise": titles.get(n), "leads": frappe.db.count("Lead", {"mkt_campaign": n})} for n in names]


@frappe.whitelist()
def all_spend():
	names = _my_exercise_names()
	return [dict(spend(n), name=n, exercise=frappe.db.get_value("Marketing Campaign", n, "campaign_name")) for n in names]
