# Copyright (c) 2026, Puzzo and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class OmniBlast(Document):
	"""
	Pure orchestrator for multi-channel campaign launches.
	Contains zero channel-specific logic — all dispatch goes through engine_registry.
	"""

	def validate(self):
		if not self.campaign:
			frappe.throw(_("Please link a Marketing Campaign"))
		if self.blast_type == "Scheduled" and not self.scheduled_time:
			frappe.throw(_("Scheduled time is required for scheduled blasts"))

	def on_submit(self):
		"""On submit, optionally enqueue execution if not scheduled."""
		if self.status != "Draft":
			return

		if self.blast_type == "Scheduled":
			self.status = "Scheduled"
		else:
			self.status = "Queued"
			self.execute_blast()

		self.save()

	@frappe.whitelist()
	def execute_blast(self):
		"""
		Execute the Omni Blast by delegating to the engine registry.
		Finds all synced Campaign Engines for the linked Marketing Campaign
		and dispatches them via execute_engines_for_campaign().
		"""
		from marketing_hub.utils.engine_registry import execute_engines_for_campaign

		if not self.campaign:
			frappe.throw(_("No Marketing Campaign linked to this blast"))

		self.status = "Running"
		self.save()
		frappe.db.commit()

		# Delegate entirely to the orchestrator
		summary = execute_engines_for_campaign(self.campaign)

		# Store aggregated results
		self.results_json = frappe.as_json(summary)
		self.error_log = "\n".join(
			[f"{r['engine_type']}: {r.get('results', {}).get('error', '')}"
			 for r in summary.get("results", [])
			 if r.get("status") in ("Failed", "Error")]
		) or ""

		# Determine final status
		if summary.get("status") == "Completed":
			self.status = "Completed"
		elif summary.get("status") == "Partially Failed":
			self.status = "Partially Completed"
		else:
			self.status = "Failed"

		self.save()
		frappe.db.commit()

		if not frappe.flags.in_test:
			frappe.msgprint(
				_("Omni Blast finished: {0} completed, {1} failed out of {2} engines").format(
					summary.get("completed", 0),
					summary.get("failed", 0),
					summary.get("total_engines", 0),
				)
			)

		return summary
