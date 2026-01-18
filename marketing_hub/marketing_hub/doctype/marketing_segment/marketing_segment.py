# Copyright (c) 2026, Your Name and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from frappe import _


class MarketingSegment(Document):
	def validate(self):
		"""Validate filters JSON and calculate segment size"""
		if self.filters_json:
			try:
				filters = json.loads(self.filters_json)
				if not isinstance(filters, dict):
					frappe.throw(_("Filters must be a valid JSON object"))
			except json.JSONDecodeError:
				frappe.throw(_("Invalid JSON format in filters"))

	def before_save(self):
		"""Calculate segment size before saving"""
		if self.status == "Active" and self.filters_json:
			self.calculate_segment_size()

	def calculate_segment_size(self):
		"""Calculate the size of the segment based on filters"""
		if not self.filters_json:
			self.segment_size = 0
			return

		try:
			filters = json.loads(self.filters_json)

			# Determine base doctype
			base_doctype = self.segment_type if self.segment_type != "Custom" else "Lead"

			# Build query with filters
			count = frappe.db.count(base_doctype, filters=filters)

			self.segment_size = count
			self.last_calculated = frappe.utils.now()

		except Exception as e:
			frappe.log_error(f"Error calculating segment size: {str(e)}", "Marketing Segment Error")
			self.segment_size = 0

	def get_segment_members(self, limit=None):
		"""Get list of members in this segment"""
		if not self.filters_json:
			return []

		try:
			filters = json.loads(self.filters_json)
			base_doctype = self.segment_type if self.segment_type != "Custom" else "Lead"

			members = frappe.get_all(
				base_doctype,
				filters=filters,
				fields=["name", "email_id" if base_doctype == "Lead" else "email"],
				limit=limit
			)

			return members

		except Exception as e:
			frappe.log_error(f"Error getting segment members: {str(e)}", "Marketing Segment Error")
			return []


@frappe.whitelist()
def refresh_segment(segment_name):
	"""Manually refresh segment size calculation"""
	doc = frappe.get_doc("Marketing Segment", segment_name)
	doc.status = "Calculating"
	doc.save(ignore_permissions=True)

	try:
		doc.calculate_segment_size()
		doc.status = "Active"
		doc.save(ignore_permissions=True)

		return {
			"success": True,
			"segment_size": doc.segment_size,
			"last_calculated": doc.last_calculated
		}

	except Exception as e:
		doc.status = "Inactive"
		doc.save(ignore_permissions=True)
		frappe.throw(_("Error refreshing segment: {0}").format(str(e)))


@frappe.whitelist()
def get_segment_preview(filters_json, segment_type="Lead", limit=10):
	"""Preview segment members before saving"""
	try:
		filters = json.loads(filters_json) if isinstance(filters_json, str) else filters_json
		base_doctype = segment_type if segment_type != "Custom" else "Lead"

		members = frappe.get_all(
			base_doctype,
			filters=filters,
			fields=["name", "email_id" if base_doctype == "Lead" else "email", "company"],
			limit=limit
		)

		count = frappe.db.count(base_doctype, filters=filters)

		return {
			"preview": members,
			"total_count": count
		}

	except Exception as e:
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
		except Exception as e:
			frappe.log_error(f"Error auto-refreshing segment {segment_name}: {str(e)}", "Segment Auto Refresh")
