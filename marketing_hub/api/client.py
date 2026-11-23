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
