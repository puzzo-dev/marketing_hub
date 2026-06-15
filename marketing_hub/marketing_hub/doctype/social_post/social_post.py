# Copyright (c) 2026, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_datetime, now

VALID_STATUS_TRANSITIONS = {
	"Draft": {"Scheduled", "Publishing", "Published", "Cancelled"},
	"Scheduled": {"Draft", "Publishing", "Published", "Cancelled"},
	"Publishing": {"Published", "Failed"},
	"Published": {"Deleted"},
	"Failed": {"Draft", "Scheduled", "Publishing"},
	"Cancelled": {"Draft"},
	"Deleted": set(),
}


class SocialPost(Document):
	def validate(self):
		"""Validate post data"""
		self.validate_status_transition()
		self.validate_content_length()
		self.validate_scheduled_time()
		self.calculate_engagement_rate()
		self.validate_approval_permissions()

	def validate_status_transition(self):
		"""Enforce valid status transitions via state machine."""
		if self.is_new():
			return

		old_status = self.get_doc_before_save()
		if not old_status:
			return

		old_status = old_status.status or "Draft"
		new_status = self.status or "Draft"

		if old_status == new_status:
			return

		allowed = VALID_STATUS_TRANSITIONS.get(old_status, set())
		if new_status not in allowed:
			frappe.throw(
				_("Cannot change status from {0} to {1}. Allowed: {2}").format(
					old_status, new_status, ", ".join(sorted(allowed)) or "none"
				)
			)

	def validate_approval_permissions(self):
		"""Check if user is authorized to publish based on settings"""
		if self.status in ["Scheduled", "Published"]:
			settings = frappe.get_cached_doc("Marketing Hub Settings")
			if settings.require_post_approval:
				if "Marketing Manager" not in frappe.get_roles() and "System Manager" not in frappe.get_roles():
					frappe.throw(_("Post Request Approval is enabled. Only Marketing Managers can Schedule or Publish posts."))

	def validate_content_length(self):
		"""Validate content length based on platform settings"""
		if not self.platform:
			return

		# Fetch network settings
		try:
			network = frappe.get_doc("Social Media Network", self.platform)
		except frappe.DoesNotExistError:
			return

		if network.max_text_length:
			# Strip HTML for character count if network doesn't support HTML
			import re
			clean_content = self.content
			if not network.supports_html:
				clean_content = re.sub(r'<[^>]+>', '', self.content or '')
			
			if len(clean_content) > network.max_text_length:
				frappe.msgprint(
					_("Content exceeds {0} character limit for {1}. Current: {2} characters").format(
						network.max_text_length, self.platform, len(clean_content)
					),
					indicator="orange",
					alert=True
				)

	def validate_scheduled_time(self):
		"""Ensure scheduled time is in the future"""
		if self.scheduled_time and self.status == "Scheduled":
			scheduled_dt = get_datetime(self.scheduled_time)
			now_dt = get_datetime(now())

			if scheduled_dt <= now_dt:
				frappe.throw(_("Scheduled time must be in the future"))

	def calculate_engagement_rate(self):
		"""Calculate engagement rate from metrics"""
		if self.impressions and self.impressions > 0:
			total_engagements = (
				(self.likes or 0) +
				(self.comments_count or 0) +
				(self.shares or 0) +
				(self.clicks or 0)
			)
			self.engagement_rate = (total_engagements / self.impressions) * 100
		else:
			self.engagement_rate = 0

	def before_insert(self):
		"""Set initial status"""
		if not self.status:
			self.status = "Draft"

	def on_update(self):
		"""Handle status changes"""
		if self.status == "Published" and not self.published_time:
			self.published_time = now()
			self.db_set("published_time", self.published_time, update_modified=False)


@frappe.whitelist()
def publish_post(post_name):
	"""Publish a social media post via the canonical auto_post.publish_post."""
	from marketing_hub.utils.auto_post import publish_post as _do_publish

	doc = frappe.get_doc("Social Post", post_name)
	frappe.has_permission("Social Post", "write", doc=doc, throw=True)

	result = _do_publish(doc)
	success = result.get("success", False)
	msg = _("Post published successfully") if success else result.get("error", _("Publishing failed"))
	return {"success": success, "message": msg}


@frappe.whitelist()
def schedule_post(post_name, scheduled_time):
	"""Schedule a post for future publishing"""
	doc = frappe.get_doc("Social Post", post_name)
	frappe.has_permission("Social Post", "write", doc=doc, throw=True)

	scheduled_dt = get_datetime(scheduled_time)
	now_dt = get_datetime(now())

	if scheduled_dt <= now_dt:
		frappe.throw(_("Scheduled time must be in the future"))

	doc.scheduled_time = scheduled_time
	doc.status = "Scheduled"
	doc.save()

	return {"success": True, "message": _("Post scheduled successfully")}


@frappe.whitelist()
def update_metrics(post_name, metrics):
	"""Update engagement metrics for a post"""
	doc = frappe.get_doc("Social Post", post_name)
	frappe.has_permission("Social Post", "write", doc=doc, throw=True)

	if isinstance(metrics, str):
		metrics = frappe.parse_json(metrics)

	metric_fields = {
		"impressions": "impressions",
		"reach": "reach",
		"clicks": "clicks",
		"likes": "likes",
		"comments": "comments_count",
		"shares": "shares",
	}
	for key, field in metric_fields.items():
		if key in metrics:
			doc.set(field, metrics[key])

	doc.calculate_engagement_rate()
	doc.save()

	return {"success": True, "engagement_rate": doc.engagement_rate}


@frappe.whitelist()
def get_platform_best_time(platform):
	"""Get best posting time recommendations for platform from Social Media Network doctype"""
	try:
		network = frappe.get_cached_doc("Social Media Network", platform)
		if network.best_practices:
			# Extract best times from best practices if mentioned
			practices = network.best_practices.split("\n") if isinstance(network.best_practices, str) else []
			for practice in practices:
				if "time" in practice.lower() or "post" in practice.lower():
					return practice
					
		# Check if there's a best_posting_times field in description
		if network.description and "best time" in network.description.lower():
			return network.description
	except:
		pass
	
	return "Best times vary by audience - analyze your specific audience engagement data"



