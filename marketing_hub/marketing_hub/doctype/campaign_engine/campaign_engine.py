# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CampaignEngine(Document):
	def validate(self):
		if self.engine_type and self.engine_doc_type:
			self._validate_engine_doc_type()

	def _validate_engine_doc_type(self):
		expected = _get_doctype_for_engine_type(self.engine_type)
		if expected and self.engine_doc_type != expected:
			frappe.throw(
				frappe._("Engine Type '{0}' must use DocType '{1}' (got '{2}')").format(
					self.engine_type, expected, self.engine_doc_type
				)
			)


def _get_doctype_for_engine_type(engine_type):
	mapping = {
		"Email Blast": "Newsletter",
		"Email Sequence": "Email Campaign",
		"WhatsApp": "Bulk WhatsApp Message",
		"SMS": "SMS Campaign",
		"Social Media": "Social Post",
		"Meta Ads": "Meta Ads Campaign",
		"OOH": "OOH Campaign",
	}
	return mapping.get(engine_type)
