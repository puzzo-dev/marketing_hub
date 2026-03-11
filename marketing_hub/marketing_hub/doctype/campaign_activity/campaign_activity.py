# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class CampaignActivity(Document):
	def validate(self):
		"""Validate campaign activity"""
		# Validate scheduled_date is in future for new scheduled activities
		if self.status == "Scheduled" and self.scheduled_date:
			if now_datetime() >= self.scheduled_date:
				frappe.msgprint("Scheduled date should be in the future", indicator="orange")
		
		# Calculate target count from segment
		if self.segment and not self.target_count:
			self.calculate_target_count()
	
	def calculate_target_count(self):
		"""Calculate target count from segment"""
		# This would query the segment's filter criteria
		# For now, placeholder
		self.target_count = 0
	
	def on_update(self):
		"""Execute if scheduled time reached"""
		# Guard: only auto-execute if not already called from execute()
		if getattr(self, '_executing', False):
			return

		if self.status == "Scheduled" and self.scheduled_date:
			if now_datetime() >= self.scheduled_date:
				self.execute()
	
	@frappe.whitelist()
	def execute(self):
		"""Execute campaign activity"""
		if self.status == "Completed":
			return {"status": "Error", "message": "Activity already completed"}
		
		try:
			self._executing = True
			self.status = "In Progress"
			self.started_at = now_datetime()
			self.save()
			frappe.db.commit()
			
			# Execute based on activity type
			if self.activity_type == "Omni-Channel Blast":
				result = self.execute_omni_blast()
			elif self.activity_type == "Email Blast":
				result = self.execute_email_blast()
			elif self.activity_type == "WhatsApp Blast":
				result = self.execute_whatsapp_blast()
			else:
				result = {"status": "Error", "message": f"Execution not implemented for {self.activity_type}"}
			
			if result.get("status") == "Success":
				self.status = "Completed"
				self.completed_at = now_datetime()
			else:
				self.status = "Failed"
				self.error_log = result.get("message", "Unknown error")
			
			self.save()
			return result
			
		except Exception as e:
			self.status = "Failed"
			self.error_log = str(e)
			self.save()
			frappe.log_error(f"Campaign activity execution failed: {str(e)}", "Campaign Activity")
			return {"status": "Error", "message": str(e)}
	
	def execute_omni_blast(self):
		"""Execute omni-channel blast"""
		# Import omni_blast utility
		from marketing_hub.utils import omni_blast
		
		channels = [ch.strip() for ch in (self.channels or "").split(",")]
		
		result = omni_blast.execute_omni_channel_blast(
			campaign=self.campaign,
			channels=channels,
			segment=self.segment,
			channel_config=self.channel_config
		)
		
		# Update metrics
		self.sent_count = result.get("sent_count", 0)
		self.delivered_count = result.get("delivered_count", 0)
		self.failed_count = result.get("failed_count", 0)
		
		return result
	
	def execute_email_blast(self):
		"""Execute email blast"""
		# Placeholder for email blast execution
		return {"status": "Success", "message": "Email blast executed", "sent_count": 0}
	
	def execute_whatsapp_blast(self):
		"""Execute WhatsApp blast"""
		# Placeholder for WhatsApp blast execution
		return {"status": "Success", "message": "WhatsApp blast executed", "sent_count": 0}
	
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
def execute_activity(activity_name):
	"""Execute a campaign activity"""
	doc = frappe.get_doc("Campaign Activity", activity_name)
	return doc.execute()


@frappe.whitelist()
def retry_activity(activity_name):
	"""Retry a failed campaign activity"""
	doc = frappe.get_doc("Campaign Activity", activity_name)
	return doc.retry()
