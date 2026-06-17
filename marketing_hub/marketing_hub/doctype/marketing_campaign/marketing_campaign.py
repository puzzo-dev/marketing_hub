# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class MarketingCampaign(Document):
	def validate(self):
		self.validate_dates()
		self.validate_approval()
		self.validate_engines()

	def validate_dates(self):
		if self.start_date and self.end_date:
			if self.start_date > self.end_date:
				frappe.throw(_("End Date cannot be before Start Date"))

	def validate_approval(self):
		if self.is_new():
			return

		old_status = self.get_doc_before_save().status
		if self.status in ["Approved", "Active"] and old_status not in ["Approved", "Active", "Paused"]:
			roles = frappe.get_roles(frappe.session.user)
			if "Marketing Manager" not in roles and "System Manager" not in roles:
				frappe.throw(_("Only a Marketing Manager or System Manager can approve or activate campaigns."))

	def validate_engines(self):
		if not self.campaign_engines:
			return
		engine_types = [e.engine_type for e in self.campaign_engines]
		if len(engine_types) != len(set(engine_types)):
			frappe.throw(_("Duplicate engine types are not allowed in a single campaign."))

	def get_synced_engines(self):
		"""Return engines marked for Omni Blast orchestration."""
		return [e for e in self.campaign_engines if e.sync_with_omni_blast]

	@frappe.whitelist()
	def launch_omni_blast(self):
		"""Launch all synced engines via orchestrator."""
		from marketing_hub.utils.engine_registry import execute_engines_for_campaign
		return execute_engines_for_campaign(self.name)

	@frappe.whitelist()
	def launch_engine(self, engine_row_name):
		"""Launch a single engine by its child-table row name."""
		from marketing_hub.utils.engine_registry import execute_engine
		for engine in self.campaign_engines:
			if engine.name == engine_row_name:
				return execute_engine(engine)
		frappe.throw(_("Engine row '{0}' not found.").format(engine_row_name))
