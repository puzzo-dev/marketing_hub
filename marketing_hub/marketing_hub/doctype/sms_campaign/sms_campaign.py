# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class SMSCampaign(Document):
	def validate(self):
		if self.message and len(self.message) > 1600:
			frappe.msgprint(
				_("Message exceeds 1600 characters. Some gateways may reject or split this into multiple SMS."),
				indicator="orange"
			)

	@frappe.whitelist()
	def execute(self):
		"""Execute SMS blast using Frappe's SMS gateway."""
		from frappe.core.doctype.sms_settings.sms_settings import send_sms

		if self.status == "Running":
			return {"status": "Error", "message": "Campaign is already running"}

		self.status = "Running"
		self.save()
		frappe.db.commit()

		recipients = self._get_recipients()
		if not recipients:
			self.status = "Failed"
			self.error_log = "No recipients found"
			self.save()
			return {"status": "Failed", "message": "No recipients found"}

		try:
			# Frappe send_sms handles the gateway and logging internally
			send_sms(
				receiver_list=recipients,
				msg=self.message,
				sender_name=self.sender_id or "",
				success_msg=False
			)
			self.sent_count = len(recipients)
			self.failed_count = 0
			self.status = "Completed"
			self.results_json = frappe.as_json({
				"recipients": len(recipients),
				"sent": len(recipients),
				"failed": 0
			})
		except Exception as e:
			frappe.log_error(f"SMS Campaign execution failed: {str(e)}", "SMS Campaign")
			self.status = "Failed"
			self.error_log = str(e)
			self.failed_count = len(recipients)
			self.results_json = frappe.as_json({
				"recipients": len(recipients),
				"sent": 0,
				"failed": len(recipients),
				"error": str(e)
			})

		self.save()
		frappe.db.commit()
		return {"status": self.status, "results": frappe.parse_json(self.results_json or "{}")}

	def _get_recipients(self):
		recipients = []

		if self.segment:
			segment = frappe.get_doc("Marketing Segment", self.segment)
			members = segment.get_segment_members() if hasattr(segment, "get_segment_members") else []
			for member in members:
				mobile = getattr(member, "mobile_no", None) or getattr(member, "phone", None)
				if mobile:
					recipients.append(mobile)

		# Deduplicate and clean
		seen = set()
		cleaned = []
		for number in recipients:
			clean = str(number).replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
			if clean and clean not in seen:
				seen.add(clean)
				cleaned.append(clean)

		return cleaned
