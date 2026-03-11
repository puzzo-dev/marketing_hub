# Copyright (c) 2026, Marketing Hub and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ClientSubscription(Document):
	def validate(self):
		self.validate_dates()
		self.validate_active_subscription()

	def validate_dates(self):
		if self.end_date and self.start_date and self.end_date < self.start_date:
			frappe.throw("End Date cannot be before Start Date")

	def validate_active_subscription(self):
		if self.status == "Active" and not self.is_new():
			existing = frappe.db.exists(
				"Client Subscription",
				{
					"client": self.client,
					"status": "Active",
					"name": ("!=", self.name),
				},
			)
			if existing:
				frappe.throw(
					f"Client {self.client} already has an active subscription: {existing}"
				)
