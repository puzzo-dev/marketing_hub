# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class AgencyPackage(Document):
	def validate(self):
		if self.billing_cycle_months and self.billing_cycle_months < 1:
			frappe.throw(_("Billing Cycle must be at least 1 month"))

		if self.monthly_fee and self.monthly_fee < 0:
			frappe.throw(_("Monthly Fee cannot be negative"))
