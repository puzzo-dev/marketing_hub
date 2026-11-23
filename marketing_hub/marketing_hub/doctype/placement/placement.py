# Copyright (c) 2026, I-Varse Technologies NG and contributors
# License: MIT

import frappe
from frappe import _
from frappe.model.document import Document


class Placement(Document):
	"""A scheduled post. Every placement needs the Brand Manager's approval, the Publisher's too.

	`status` has one writer, the dispatcher. `approval_state` moves only through the workflow.
	"""

	def validate(self):
		campaign = frappe.db.get_value("Content Item", self.content_item, "campaign")
		if campaign and campaign != self.campaign:
			frappe.throw(_("The content belongs to a different exercise."))
		self.brand = frappe.db.get_value("Marketing Campaign", self.campaign, "brand") or self.brand
		self.approver = frappe.db.get_value("Marketing Campaign", self.campaign, "brand_manager")
		if not self.approver:
			frappe.throw(_("This exercise has no Brand Manager yet, so nobody can approve a placement."))
		if self.is_new():
			self.idempotency_key = f"{self.content_item}:{self.channel}:{self.scheduled_for}"
		else:
			before = self.get_doc_before_save()
			if before and before.status != self.status and not frappe.flags.in_dispatcher:
				frappe.throw(_("Only the dispatcher changes a placement's status."))
