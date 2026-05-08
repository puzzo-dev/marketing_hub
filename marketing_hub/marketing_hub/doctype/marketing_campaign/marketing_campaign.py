# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class MarketingCampaign(Document):
	def validate(self):
		self.validate_dates()
		self.validate_approval()

	def validate_dates(self):
		if self.start_date and self.end_date:
			if self.start_date > self.end_date:
				frappe.throw("End Date cannot be before Start Date")

	def validate_approval(self):
		if self.is_new():
			return
		
		old_status = self.get_doc_before_save().status
		if self.status in ["Approved", "Active"] and old_status not in ["Approved", "Active", "Paused"]:
			roles = frappe.get_roles(frappe.session.user)
			if "Marketing Manager" not in roles and "System Manager" not in roles:
				frappe.throw("Only a Marketing Manager or System Manager can approve or activate campaigns.")
