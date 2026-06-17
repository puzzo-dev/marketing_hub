# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, add_to_date

STUCK_TIMEOUT_MINUTES = 30


class CampaignActivity(Document):
	def validate(self):
		"""Validate campaign activity"""
		# Validate scheduled_date is in future for new scheduled activities
		if self.status == "Scheduled" and self.scheduled_date:
			if now_datetime() >= self.scheduled_date:
				frappe.msgprint(_("Scheduled date should be in the future"), indicator="orange")

		# Calculate target count from segment
		if self.segment and not self.target_count:
			self.calculate_target_count()

	def calculate_target_count(self):
		"""Calculate target count from linked segment using its filters."""
		if not self.segment:
			self.target_count = 0
			return
		try:
			segment = frappe.get_doc("Marketing Segment", self.segment)
			filters = segment._get_filters_dict()
			base_doctype = segment.segment_type if segment.segment_type != "Custom" else "Lead"
			if filters:
				self.target_count = frappe.db.count(base_doctype, filters=filters)
			else:
				self.target_count = 0
		except (frappe.ValidationError, frappe.DoesNotExistError) as e:
			frappe.log_error(f"Error calculating target count for {self.name}: {str(e)}", "Campaign Activity")
			self.target_count = 0

	def is_stuck(self):
		"""Check if this activity has been In Progress beyond the timeout."""
		if self.status != "In Progress" or not self.started_at:
			return False
		cutoff = add_to_date(now_datetime(), minutes=-STUCK_TIMEOUT_MINUTES)
		return self.started_at < cutoff

	def on_update(self):
		"""Enqueue background execution if scheduled time reached"""
		# Guard: only auto-enqueue if not already called from execute()
		if getattr(self, '_executing', False):
			return

		if self.status == "Scheduled" and self.scheduled_date:
			if now_datetime() >= self.scheduled_date:
				self._enqueue_execution()

	def _enqueue_execution(self):
		"""Enqueue campaign activity execution as a background job"""
		self._executing = True
		self.status = "In Progress"
		self.started_at = now_datetime()
		self.save()
		frappe.db.commit()

		frappe.enqueue(
			"marketing_hub.marketing_hub.doctype.campaign_activity.campaign_activity._run_execution_job",
			campaign_activity=self.name,
			queue="default",
			timeout=600,
			job_id=f"campaign_activity_{self.name}"
		)

	@frappe.whitelist()
	def execute(self):
		"""Execute campaign activity via background job"""
		if self.status == "Completed":
			return {"status": "Error", "message": "Activity already completed"}

		if self.status == "In Progress" and not self.is_stuck():
			return {"status": "Error", "message": "Activity is already in progress"}

		self._enqueue_execution()
		return {"status": "Enqueued", "message": "Campaign activity execution queued"}

	def _run_execution(self):
		"""Synchronous execution wrapper for background job"""
		from marketing_hub.utils.engine_registry import execute_engines_for_campaign

		try:
			if not self.campaign:
				frappe.throw(_("No campaign linked to this activity"))

			result = execute_engines_for_campaign(self.campaign)

			# Aggregate metrics
			total_sent = 0
			total_failed = 0
			for engine_result in result.get("results", []):
				engine_results = engine_result.get("results", {})
				total_sent += engine_results.get("sent", 0) or engine_results.get("completed", 0) or 0
				total_failed += engine_results.get("failed", 0) or 0

			self.sent_count = total_sent
			self.failed_count = total_failed

			if result.get("status") == "Completed":
				self.status = "Completed"
				self.completed_at = now_datetime()
			elif result.get("status") == "Partially Failed":
				self.status = "Completed"
				self.completed_at = now_datetime()
				self.error_log = frappe.as_json(result)
			else:
				self.status = "Failed"
				self.error_log = frappe.as_json(result)

			self.save()

		except Exception as e:
			self.status = "Failed"
			self.error_log = str(e)
			self.save()
			frappe.log_error(f"Campaign activity execution failed: {str(e)}", "Campaign Activity")
			frappe.db.rollback()

	@frappe.whitelist()
	def retry(self):
		"""Retry failed activity"""
		if self.retry_count >= self.max_retries:
			return {"status": "Error", "message": f"Max retries ({self.max_retries}) reached"}

		self.retry_count += 1
		self.status = "Scheduled"
		self.error_log = ""
		self.save()

		return self.execute()


@frappe.whitelist()
def _run_execution_job(campaign_activity):
	"""Background entry point for campaign activity execution."""
	doc = frappe.get_doc("Campaign Activity", campaign_activity)
	if doc.status not in ("Scheduled", "In Progress"):
		return {"message": "Activity must be in Scheduled or In Progress status to execute"}

	doc.status = "In Progress"
	doc.started_at = now_datetime()
	doc.save()
	frappe.db.commit()

	doc._run_execution()
	return {"message": "Campaign activity execution finished", "status": doc.status}


@frappe.whitelist()
def execute_activity(activity_name):
	"""Execute a campaign activity"""
	doc = frappe.get_doc("Campaign Activity", activity_name)
	return doc.execute()


@frappe.whitelist()
def retry_activity(activity_name):
	"""Retry a failed campaign activity"""
	doc = frappe.get_doc("Campaign Activity", activity_name)
	return doc.retry()


@frappe.whitelist()
def recover_stuck_activities():
	"""Find activities stuck in In Progress and mark them as Failed so they can be retried."""
	cutoff = add_to_date(now_datetime(), minutes=-STUCK_TIMEOUT_MINUTES)
	stuck = frappe.get_all(
		"Campaign Activity",
		filters={
			"status": "In Progress",
			"started_at": ["<", cutoff]
		},
		fields=["name"]
	)
	recovered = 0
	for row in stuck:
		doc = frappe.get_doc("Campaign Activity", row.name)
		doc.status = "Failed"
		doc.error_log = _("Activity timed out after {0} minutes in progress and was marked as failed.").format(STUCK_TIMEOUT_MINUTES)
		doc.save()
		recovered += 1
	frappe.db.commit()
	return {"recovered": recovered, "message": _("Recovered {0} stuck activity(s)").format(recovered)}
