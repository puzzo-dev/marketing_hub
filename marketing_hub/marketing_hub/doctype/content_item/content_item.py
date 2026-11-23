# Copyright (c) 2026, I-Varse Technologies NG and contributors
# License: MIT

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class ContentItem(Document):
	"""An approval covers one version. Editing the body adds a version and clears approval."""

	def validate(self):
		self.brand = frappe.db.get_value("Marketing Campaign", self.campaign, "brand") or self.brand

	def on_update(self):
		pass

	def add_version(self, body, asset=None):
		self.append("versions", {"version_no": len(self.versions) + 1, "body": body, "asset": asset})
		if self.status == "Approved":
			self.status = "In review"

	@frappe.whitelist()
	def approve_latest(self):
		"""Only the exercise's Brand Manager approves, and only the newest version."""
		manager = frappe.db.get_value("Marketing Campaign", self.campaign, "brand_manager")
		if frappe.session.user != manager and "System Manager" not in frappe.get_roles():
			frappe.throw(_("Only the exercise's Brand Manager can approve content."), frappe.PermissionError)
		if not self.versions:
			frappe.throw(_("There is no version to approve."))
		latest = self.versions[-1]
		latest.approved_by = frappe.session.user
		latest.approved_on = now_datetime()
		self.status = "Approved"
		self.save()
