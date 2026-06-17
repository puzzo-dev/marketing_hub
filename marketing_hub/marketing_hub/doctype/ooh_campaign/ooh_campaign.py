# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class OOHCampaign(Document):
	def validate(self):
		if self.display_start_date and self.display_end_date:
			if self.display_start_date > self.display_end_date:
				frappe.throw(_("Display End Date cannot be before Display Start Date"))

	@frappe.whitelist()
	def execute(self):
		"""Execute OOH campaign: either via vendor API or mark as manual/tracked."""
		if self.status == "Running":
			return {"status": "Error", "message": "Campaign is already running"}

		self.status = "Running"
		self.save()
		frappe.db.commit()

		try:
			vendor = frappe.get_doc("OOH Vendor", self.ooh_vendor)

			if vendor.api_base_url:
				# Attempt API-based execution via GenericAdapter
				from marketing_hub.utils.social_adapter import get_platform_adapter
				adapter = get_platform_adapter(vendor)
				result = adapter.publish(self._as_post_doc())
				self.results_json = frappe.as_json(result)
				if result.get("success"):
					self.status = "Completed"
				else:
					self.status = "Failed"
					self.error_log = result.get("error", "Unknown error")
			else:
				# No API configured — manual/tracked campaign
				self.status = "Completed"
				self.results_json = frappe.as_json({
					"status": "Manual",
					"message": "No API configured for vendor. Campaign marked as tracked."
				})
		except Exception as e:
			frappe.log_error(f"OOH Campaign execution failed: {str(e)}", "OOH Campaign")
			self.status = "Failed"
			self.error_log = str(e)
			self.results_json = frappe.as_json({"error": str(e)})

		self.save()
		frappe.db.commit()
		return {"status": self.status, "results": frappe.parse_json(self.results_json or "{}")}

	def _as_post_doc(self):
		"""Return a pseudo-post object for the GenericAdapter."""
		class _PseudoPost:
			pass

		post = _PseudoPost()
		post.content = self.creative_brief
		post.media_attachment = self.design_asset
		post.platform = self.ooh_vendor
		post.status = "Draft"
		post.company = frappe.defaults.get_defaults().get("company")
		return post
