"""Change requests: the way anyone but the exercise's Brand Manager changes something.

A request names a target, lists the fields to change (Change Request Item rows) and records the
target's `modified` time. It goes to the exercise's Brand Manager through the workflow. When the
request reaches Approved, apply() writes the new values, but only if the target has not moved
since the request was raised.
"""

import frappe
from frappe import _
from frappe.utils import now_datetime

# Fields a request may never change, whatever the requester types.
BLOCKED = {"name", "owner", "creation", "modified", "modified_by", "docstatus", "brand", "brand_manager", "project", "status", "approval_state", "approver"}


class ChangeRequestMixin:
	"""Shared behaviour for the three change request doctypes."""

	def target(self):
		raise NotImplementedError

	def before_insert(self):
		self.set_approver()
		self.workflow_state = self.workflow_state or "Pending"

	def validate(self):
		self.set_approver()
		for row in self.items:
			if row.fieldname in BLOCKED:
				frappe.throw(_("{0} cannot be changed through a request").format(row.fieldname))

	def set_approver(self):
		"""Set from the server, never from the form: the exercise's assigned Brand Manager."""
		self.approver = frappe.db.get_value("Marketing Campaign", self.campaign, "brand_manager")
		if not self.approver:
			frappe.throw(_("This exercise has no Brand Manager yet, so nobody can approve a request."))

	def on_update(self):
		if self.workflow_state == "Approved" and not self.applied_on:
			self.apply()

	def apply(self):
		target = self.target()
		if str(target.modified) != str(self.target_modified):
			frappe.throw(_("{0} changed after this request was raised. Raise it again against the current version.").format(target.name))
		for row in self.items:
			target.set(row.fieldname, row.new_value)
		frappe.flags.in_change_request_apply = True
		try:
			target.save(ignore_permissions=True)
		finally:
			frappe.flags.in_change_request_apply = False
		self.db_set("applied_on", now_datetime())
