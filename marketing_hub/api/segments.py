"""
Segments API
"""

import json

import frappe
from frappe import _
from frappe.utils import cint


def _get_company(company=None):
	"""Get the active company - explicit param or user default"""
	if company:
		return company
	return frappe.defaults.get_user_default("Company")


@frappe.whitelist()
def get_segment_list(filters=None, limit=20, offset=0):
	"""Get marketing segments list"""
	try:
		if filters and isinstance(filters, str):
			filters = json.loads(filters)

		filters = filters or {}
		base_filters = {}
		company = _get_company(filters.get("company"))
		if company:
			base_filters["company"] = company
		if filters.get("search"):
			base_filters["segment_name"] = ["like", f"%{filters['search']}%"]

		segments = frappe.get_all(
			"Marketing Segment",
			fields=["name", "segment_name", "segment_type", "description", "creation", "modified", "segment_size"],
			filters=base_filters,
			order_by="modified desc",
			limit_page_length=cint(limit),
			limit_start=cint(offset)
		)

		# Attach child table filters for frontend preview
		for seg in segments:
			filters_rows = frappe.get_all(
				"Marketing Segment Filter",
				filters={"parent": seg["name"], "parenttype": "Marketing Segment"},
				fields=["fieldname", "operator", "value"],
				order_by="idx"
			)
			seg["filters"] = filters_rows

		total_count = frappe.db.count("Marketing Segment", base_filters)
		return {
			"segments": segments,
			"total_count": total_count,
			"has_more": (cint(offset) + cint(limit)) < total_count
		}
	except (frappe.DatabaseError, frappe.ValidationError) as e:
		frappe.log_error(f"Error fetching segments: {str(e)}", "Segment API Error")
		return {"segments": [], "total_count": 0, "has_more": False}


@frappe.whitelist()
def create_segment(data):
	"""Create a new marketing segment"""
	try:
		if isinstance(data, str):
			data = json.loads(data)

		frappe.has_permission("Marketing Segment", throw=True)
		doc = frappe.get_doc({
			"doctype": "Marketing Segment",
			"segment_name": data.get("segment_name"),
			"company": data.get("company") or _get_company(),
			"segment_type": data.get("segment_type", "Lead"),
			"description": data.get("description"),
		})

		if data.get("filters"):
			for f in data["filters"]:
				doc.append("filters", {
					"fieldname": f.get("fieldname"),
					"operator": f.get("operator"),
					"value": f.get("value")
				})

		doc.insert()
		return {"success": True, "name": doc.name}
	except (frappe.DoesNotExistError, frappe.DuplicateEntryError, frappe.ValidationError) as e:
		frappe.log_error(f"Error creating segment: {str(e)}", "Segment Creation Error")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def update_segment(name, data):
	"""Update an existing marketing segment"""
	try:
		if isinstance(data, str):
			data = json.loads(data)

		doc = frappe.get_doc("Marketing Segment", name)
		doc.check_permission("write")
		for field in ["segment_name", "segment_type", "description"]:
			if field in data:
				doc.set(field, data[field])

		if "filters" in data:
			doc.set("filters", [])
			for f in data["filters"]:
				doc.append("filters", {
					"fieldname": f.get("fieldname"),
					"operator": f.get("operator"),
					"value": f.get("value")
				})

		doc.save()
		return {"success": True, "name": doc.name}
	except (frappe.DoesNotExistError, frappe.DuplicateEntryError, frappe.ValidationError) as e:
		frappe.log_error(f"Error updating segment: {str(e)}", "Segment Update Error")
		return {"success": False, "error": str(e)}
