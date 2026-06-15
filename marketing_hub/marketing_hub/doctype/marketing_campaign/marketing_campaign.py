# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MarketingCampaign(Document):
	def validate(self):
		self.validate_dates()

	def validate_dates(self):
		if self.start_date and self.end_date:
			if self.start_date > self.end_date:
				frappe.throw("End Date cannot be before Start Date")
