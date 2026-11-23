# Copyright (c) 2026, I-Varse Technologies NG and contributors
# License: MIT

import frappe
from frappe import _
from frappe.model.document import Document

# Fields only the exercise's Brand Manager (or a Marketing Head) may change directly.
# Anyone else raises a Campaign Change Request.
MANAGER_FIELDS = ("campaign_name", "brand", "campaign_type", "objective", "start_date", "end_date", "budget", "brand_manager", "status", "customer", "company")
FULL_ACCESS = {"System Manager", "Marketing Head", "Marketing Manager"}


class MarketingCampaign(Document):
	def validate(self):
		self.validate_dates()
		self.validate_brand_manager()
		self.validate_who_may_change()

	def validate_dates(self):
		if self.start_date and self.end_date and self.start_date > self.end_date:
			frappe.throw(_("End Date cannot be before Start Date"))

	def validate_brand_manager(self):
		"""The assigned manager must be a Brand Manager on this exercise's brand."""
		if not self.brand_manager or not self.brand:
			return
		rows = frappe.get_all(
			"Brand Team Member",
			filters={"parent": self.brand, "parenttype": "Brand", "user": self.brand_manager, "brand_role": "Brand Manager"},
			limit=1,
		)
		if not rows:
			frappe.throw(_("{0} is not a Brand Manager of {1}.").format(self.brand_manager, self.brand))

	def validate_who_may_change(self):
		if self.is_new() or frappe.flags.in_change_request_apply or frappe.flags.in_install or frappe.flags.in_migrate or frappe.flags.in_import:
			return
		user = frappe.session.user
		if user == "Administrator" or FULL_ACCESS & set(frappe.get_roles(user)):
			return
		if self.get_doc_before_save() and self.brand_manager_before() == user:
			return
		before = self.get_doc_before_save()
		if before and any(self.get(f) != before.get(f) for f in MANAGER_FIELDS):
			frappe.throw(_("Only the exercise's Brand Manager can change this. Raise a change request instead."), frappe.PermissionError)

	def brand_manager_before(self):
		before = self.get_doc_before_save()
		return before.brand_manager if before else None

	def after_insert(self):
		self.create_project()

	def on_update(self):
		self.sync_project()

	def create_project(self):
		"""Every exercise has one ERPNext Project; the Project and its Tasks carry the work."""
		if self.project:
			return
		project = frappe.get_doc(
			{
				"doctype": "Project",
				"project_name": self.campaign_name,
				"company": self.company or frappe.defaults.get_user_default("Company"),
				"customer": self.customer,
				"expected_start_date": self.start_date,
				"expected_end_date": self.end_date,
				"estimated_costing": self.budget,
				"mkt_campaign": self.name,
				"mkt_brand_manager": self.brand_manager,
			}
		).insert(ignore_permissions=True)
		self.db_set("project", project.name)

	def sync_project(self):
		"""Keep the Project's manager and dates in step. Reassigning the manager moves the
		Project's permissions and the approvals with it, because both read brand_manager."""
		if not self.project:
			return
		values = {"mkt_brand_manager": self.brand_manager, "expected_start_date": self.start_date, "expected_end_date": self.end_date}
		frappe.db.set_value("Project", self.project, values, update_modified=False)
