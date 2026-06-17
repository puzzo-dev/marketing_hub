# Copyright (c) 2026, Your Name and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from frappe import _


def _resolve_email_field(doctype):
	"""Dynamically find the email field name for a given DocType."""
	meta = frappe.get_meta(doctype)
	for field in meta.fields:
		if field.fieldtype == "Data" and field.options == "Email":
			return field.fieldname
	# Fallback to common patterns
	for candidate in ("email_id", "email", "mail_id", "e_mail"):
		if meta.has_field(candidate):
			return candidate
	return None


class MarketingSegment(Document):
	def validate(self):
		"""Validate filters and calculate segment size"""
		filters = self._get_filters_dict()
		if filters and not isinstance(filters, dict):
			frappe.throw(_("Filters must be a valid dict"))

	def before_save(self):
		"""Migrate legacy filters_json to child table and calculate segment size"""
		self._migrate_legacy_filters()
		if self.status == "Active" and self._get_filters_dict():
			self.calculate_segment_size()

	def _migrate_legacy_filters(self):
		"""Convert legacy filters_json to child table rows if present"""
		if not self.get("filters_json"):
			return
		if self.get("filters"):
			# Child table already populated; clear legacy JSON
			self.filters_json = None
			return

		try:
			legacy = json.loads(self.filters_json) if isinstance(self.filters_json, str) else self.filters_json
			if not isinstance(legacy, dict):
				return

			for fieldname, value in legacy.items():
				if isinstance(value, list) and len(value) == 2:
					operator, val = value
				else:
					operator, val = "=", value

				self.append("filters", {
					"fieldname": fieldname,
					"operator": operator,
					"value": str(val) if val is not None else ""
				})

			self.filters_json = None
		except (json.JSONDecodeError, TypeError) as e:
			frappe.log_error(f"Legacy filter migration failed for {self.name}: {str(e)}", "Marketing Segment")

	def calculate_segment_size(self):
		"""Calculate the size of the segment based on filters"""
		filters = self._get_filters_dict()
		if not filters:
			self.segment_size = 0
			return

		try:
			# Determine base doctype
			base_doctype = self.segment_type if self.segment_type != "Custom" else "Lead"

			# Build query with filters
			count = frappe.db.count(base_doctype, filters=filters)

			self.segment_size = count
			self.last_calculated = frappe.utils.now()

		except (json.JSONDecodeError, frappe.DatabaseError) as e:
			frappe.log_error(f"Error calculating segment size: {str(e)}", "Marketing Segment Error")
			self.segment_size = 0

	def get_segment_members(self, limit=100):
		"""Get list of members in this segment"""
		filters = self._get_filters_dict()
		if not filters:
			return []

		try:
			base_doctype = self.segment_type if self.segment_type != "Custom" else "Lead"

			email_field = _resolve_email_field(base_doctype)
			fields = ["name", email_field] if email_field else ["name"]
			members = frappe.get_all(
				base_doctype,
				filters=filters,
				fields=fields,
				limit_page_length=limit
			)

			return members

		except (frappe.ValidationError, frappe.DatabaseError) as e:
			frappe.log_error(f"Error getting segment members: {str(e)}", "Marketing Segment Error")
			return []

	def _get_filters_dict(self):
		"""Build filter dict from child table rows, with legacy fallback to filters_json."""
		# Prefer new child table structure
		if self.get("filters"):
			return self._build_filters_from_child_table()

		# Legacy fallback: parse JSON filters field
		if self.get("filters_json"):
			try:
				return json.loads(self.filters_json)
			except json.JSONDecodeError:
				frappe.log_error(f"Invalid JSON in filters_json for {self.name}", "Marketing Segment")
				return {}

		return {}

	def _build_filters_from_child_table(self):
		"""Convert Marketing Segment Filter child rows to frappe filter dict."""
		filters = {}
		for row in self.get("filters", []):
			if not row.fieldname:
				continue
			if row.operator == "=":
				filters[row.fieldname] = row.value
			else:
				filters[row.fieldname] = [row.operator, row.value]
		return filters


@frappe.whitelist()
def refresh_segment(segment_name):
	"""Manually refresh segment size calculation"""
	doc = frappe.get_doc("Marketing Segment", segment_name)
	if not frappe.has_permission("Marketing Segment", "write", doc=doc):
		frappe.throw(_("You do not have permission to refresh this segment."))

	doc.status = "Calculating"
	doc.save()

	try:
		doc.calculate_segment_size()
		doc.status = "Active"
		doc.save()

		return {
			"success": True,
			"segment_size": doc.segment_size,
			"last_calculated": doc.last_calculated
		}

	except (frappe.ValidationError, frappe.DatabaseError) as e:
		doc.status = "Inactive"
		doc.save()
		frappe.throw(_("Error refreshing segment: {0}").format(str(e)))


@frappe.whitelist()
def get_segment_preview(filters_json, segment_type="Lead", limit=10):
	"""Preview segment members before saving"""
	try:
		filters = json.loads(filters_json) if isinstance(filters_json, str) else filters_json
		base_doctype = segment_type if segment_type != "Custom" else "Lead"

		email_field = _resolve_email_field(base_doctype)
		fields = ["name", "company"]
		if email_field:
			fields.insert(1, email_field)
		members = frappe.get_all(
			base_doctype,
			filters=filters,
			fields=fields,
			limit=limit
		)

		count = frappe.db.count(base_doctype, filters=filters)

		return {
			"preview": members,
			"total_count": count
		}

	except (json.JSONDecodeError, frappe.ValidationError) as e:
		frappe.throw(_("Error generating preview: {0}").format(str(e)))


def refresh_all_auto_segments():
	"""Background job to refresh all segments with auto_refresh enabled"""
	segments = frappe.get_all(
		"Marketing Segment",
		filters={"status": "Active", "auto_refresh": 1},
		pluck="name"
	)

	for segment_name in segments:
		try:
			refresh_segment(segment_name)
		except (frappe.ValidationError, frappe.DatabaseError) as e:
			frappe.log_error(f"Error auto-refreshing segment {segment_name}: {str(e)}", "Segment Auto Refresh")
