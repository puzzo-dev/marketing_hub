# Copyright (c) 2026, Puxxo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MediaType(Document):
	def validate(self):
		"""Validate the Media Type document."""
		pass
	
	def before_save(self):
		"""Auto-generate type code from type name."""
		if not self.type_code:
			self.type_code = self.type_name.upper().replace(" ", "_")[:20]
