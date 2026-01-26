# Copyright (c) 2026, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime


class SocialPost(Document):
	def validate(self):
		"""Validate post data"""
		self.validate_content_length()
		self.validate_scheduled_time()
		self.calculate_engagement_rate()
		self.validate_approval_permissions()

	def validate_approval_permissions(self):
		"""Check if user is authorized to publish based on settings"""
		if self.status in ["Scheduled", "Published"]:
			settings = frappe.get_single("Marketing Hub Settings")
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
	"""Publish a social media post"""
	doc = frappe.get_doc("Social Post", post_name)

	if doc.status != "Draft":
		frappe.throw(_("Only draft posts can be published"))

	# Integrate with Social Media Adapter
	try:
		from marketing_hub.utils.social_adapter import publish_to_platform
		result = publish_to_platform(doc)
		
		if result.get("success"):
			doc.status = "Published"
			doc.published_time = now()
			doc.post_id = result.get("id")
			doc.save(ignore_permissions=True)
			return {"success": True, "message": _("Post published successfully via Adapter")}
		else:
			frappe.throw(_("Publishing failed: {0}").format(result.get("error", "Unknown error")))
			
	except Exception as e:
		frappe.log_error(f"Publishing Error: {str(e)}", "Social Post Publish")
		frappe.throw(_("Failed during publishing process: {0}").format(str(e)))


@frappe.whitelist()
def schedule_post(post_name, scheduled_time):
	"""Schedule a post for future publishing"""
	doc = frappe.get_doc("Social Post", post_name)

	scheduled_dt = get_datetime(scheduled_time)
	now_dt = get_datetime(now())

	if scheduled_dt <= now_dt:
		frappe.throw(_("Scheduled time must be in the future"))

	doc.scheduled_time = scheduled_time
	doc.status = "Scheduled"
	doc.save(ignore_permissions=True)

	return {"success": True, "message": _("Post scheduled successfully")}


@frappe.whitelist()
def update_metrics(post_name, metrics):
	"""Update engagement metrics for a post"""
	import json

	doc = frappe.get_doc("Social Post", post_name)

	if isinstance(metrics, str):
		metrics = json.loads(metrics)

	# Update metrics
	if "impressions" in metrics:
		doc.impressions = metrics["impressions"]
	if "reach" in metrics:
		doc.reach = metrics["reach"]
	if "clicks" in metrics:
		doc.clicks = metrics["clicks"]
	if "likes" in metrics:
		doc.likes = metrics["likes"]
	if "comments" in metrics:
		doc.comments_count = metrics["comments"]
	if "shares" in metrics:
		doc.shares = metrics["shares"]

	doc.calculate_engagement_rate()
	doc.save(ignore_permissions=True)

	return {"success": True, "engagement_rate": doc.engagement_rate}


@frappe.whitelist()
def get_platform_best_time(platform):
	"""Get best posting time recommendations for platform"""
	# Placeholder data - in production, this would use analytics
	best_times = {
		"Facebook": "1-3 PM on weekdays",
		"Instagram": "11 AM - 1 PM, Wednesday through Friday",
		"Twitter/X": "8-10 AM and 6-9 PM on weekdays",
		"LinkedIn": "10-11 AM on Tuesday, Wednesday, Thursday",
		"TikTok": "6-10 PM, Tuesday through Thursday",
		"YouTube": "2-4 PM on weekdays",
		"Pinterest": "8-11 PM on weekdays"
	}

	return best_times.get(platform, "Best times vary by audience")


def publish_scheduled_posts():
	"""Background job to publish scheduled posts"""
	settings = frappe.get_single("Marketing Hub Settings")
	if not settings.enable_auto_post:
		return

	scheduled_posts = frappe.get_all(
		"Social Post",
		filters={
			"status": "Scheduled",
			"scheduled_time": ["<=", now()]
		},
		pluck="name"
	)

	for post_name in scheduled_posts:
		try:
			publish_post(post_name)
			frappe.db.commit()
		except Exception as e:
			frappe.log_error(f"Error publishing scheduled post {post_name}: {str(e)}", "Social Post Publish Error")
			# Mark as failed
			frappe.db.set_value("Social Post", post_name, "status", "Failed")
			frappe.db.commit()
