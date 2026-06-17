# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class MetaAdsCampaign(Document):
	def validate(self):
		if self.daily_budget and self.lifetime_budget:
			frappe.throw(_("Specify either Daily Budget or Lifetime Budget, not both."))
		if self.budget_type == "Daily" and not self.daily_budget:
			frappe.throw(_("Daily Budget is required when Budget Type is Daily."))
		if self.budget_type == "Lifetime" and not self.lifetime_budget:
			frappe.throw(_("Lifetime Budget is required when Budget Type is Lifetime."))

	@frappe.whitelist()
	def execute(self):
		"""Create campaign via Meta Marketing API using GenericAdapter."""
		from marketing_hub.utils.social_adapter import get_platform_adapter

		if self.status == "Running":
			return {"status": "Error", "message": "Campaign is already running"}

		self.status = "Running"
		self.save()
		frappe.db.commit()

		try:
			# Resolve the Social Media Network for Meta
			network = frappe.get_doc("Social Media Network", "Meta Ads")

			# Resolve Network Account for auth
			network_account_doc = None
			if self.ad_account:
				ad_account = frappe.get_doc("Ad Account", self.ad_account)
				if ad_account.network_account:
					network_account_doc = frappe.get_doc("Network Account", ad_account.network_account)

			adapter = get_platform_adapter(network, ad_account_doc=self.ad_account, network_account_doc=network_account_doc)

			# Build ad creative payload
			payload = self._build_campaign_payload()
			result = adapter.publish(payload)

			if result.get("success"):
				self.platform_campaign_id = result.get("platform_post_id")
				self.status = "Completed"
			else:
				self.status = "Failed"
				self.error_log = result.get("error", "Unknown error")

			self.results_json = frappe.as_json(result)
		except Exception as e:
			frappe.log_error(f"Meta Ads Campaign execution failed: {str(e)}", "Meta Ads Campaign")
			self.status = "Failed"
			self.error_log = str(e)
			self.results_json = frappe.as_json({"error": str(e)})

		self.save()
		frappe.db.commit()
		return {"status": self.status, "results": frappe.parse_json(self.results_json or "{}")}

	def _build_campaign_payload(self):
		"""Return a dict that mimics a Social Post doc for the GenericAdapter."""
		# The GenericAdapter expects fields like content, media_attachment, etc.
		# We map Meta Ads campaign fields to the adapter's expected shape.
		class _PseudoPost:
			pass

		post = _PseudoPost()
		post.content = self.primary_text
		post.media_attachment = self.media_attachment
		post.link_url = self.link_url
		post.platform = "Meta Ads"
		post.status = "Draft"
		post.company = frappe.defaults.get_defaults().get("company")
		return post
