"""
Segments API
"""

import frappe
from frappe import _


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
			import json
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
			fields=["name", "segment_name", "base_doctype", "description", "creation", "modified"],
			filters=base_filters,
			order_by="modified desc",
			limit=limit,
			start=offset
		)

		for seg in segments:
			try:
				doc = frappe.get_doc("Marketing Segment", seg.name)
				seg["filter_count"] = len(doc.get("filters") or [])
				if doc.base_doctype and doc.get("filters"):
					seg["contact_count"] = frappe.db.count(doc.base_doctype, doc.get_segment_filters())
				else:
					seg["contact_count"] = 0
			except Exception:
				seg["filter_count"] = 0
				seg["contact_count"] = 0

		total_count = frappe.db.count("Marketing Segment", base_filters)
		return {
			"segments": segments,
			"total_count": total_count,
			"has_more": (offset + limit) < total_count
		}
	except Exception as e:
		frappe.log_error(f"Error fetching segments: {str(e)}", "Segment API Error")
		return {"segments": [], "total_count": 0, "has_more": False}


@frappe.whitelist()
def create_segment(data):
	"""Create a new marketing segment"""
	try:
		if isinstance(data, str):
			import json
			data = json.loads(data)

		doc = frappe.get_doc({
			"doctype": "Marketing Segment",
			"segment_name": data.get("segment_name"),
			"company": data.get("company") or _get_company(),
			"base_doctype": data.get("base_doctype", "Lead"),
			"description": data.get("description"),
		})

		if data.get("filters"):
			for f in data["filters"]:
				doc.append("filters", {
					"field": f.get("field"),
					"condition": f.get("condition"),
					"value": f.get("value")
				})

		doc.insert()
		return {"success": True, "name": doc.name}
	except Exception as e:
		frappe.log_error(f"Error creating segment: {str(e)}", "Segment Creation Error")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def update_segment(name, data):
	"""Update an existing marketing segment"""
	try:
		if isinstance(data, str):
			import json
			data = json.loads(data)

		doc = frappe.get_doc("Marketing Segment", name)
		for field in ["segment_name", "base_doctype", "description"]:
			if field in data:
				doc.set(field, data[field])

		if "filters" in data:
			doc.set("filters", [])
			for f in data["filters"]:
				doc.append("filters", {
					"field": f.get("field"),
					"condition": f.get("condition"),
					"value": f.get("value")
				})

		doc.save()
		return {"success": True, "name": doc.name}
	except Exception as e:
		frappe.log_error(f"Error updating segment: {str(e)}", "Segment Update Error")
		return {"success": False, "error": str(e)}
