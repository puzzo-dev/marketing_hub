# Copyright (c) 2026, Puzzo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class OmniBlast(Document):
	def validate(self):
		"""Validate the Omni Blast document"""
		if not self.networks:
			frappe.throw("Please add at least one network to blast to")
		
		# Validate scheduled time for scheduled blasts
		if self.blast_type == "Scheduled" and not self.scheduled_time:
			frappe.throw("Scheduled time is required for scheduled blasts")

	def on_submit(self):
		"""Create draft Social Posts when blast is submitted"""
		if self.status != "Draft":
			return
		
		self.generate_posts()
		self.status = "Scheduled" if self.blast_type == "Scheduled" else "Published"
		self.save()

	@frappe.whitelist()
	def generate_posts(self):
		"""Generate Social Post for each selected network"""
		# Table MultiSelect stores child rows with link field
		network_list = [row.social_media_network for row in self.networks if row.social_media_network]
		if not network_list:
			frappe.throw("No networks selected")

		created_post_links = []

		for network_name in network_list:
			# Get network details
			network = frappe.get_doc("Social Media Network", network_name)
			
			# Check settings for channel permissions
			settings = frappe.get_single("Marketing Hub Settings")
			
			if network.network_type == "SMS" and not settings.enable_sms_blast:
				frappe.throw(f"SMS Blast is disabled in Marketing Hub Settings. Cannot post to {network_name}.")
				
			if network.network_type == "Messaging" and "WhatsApp" in network_name and not settings.enable_whatsapp_blast:
				frappe.throw(f"WhatsApp Blast is disabled in Marketing Hub Settings. Cannot post to {network_name}.")
				
			if network.network_type == "Email" and not settings.enable_email_blast:
				frappe.throw(f"Email Blast is disabled in Marketing Hub Settings. Cannot post to {network_name}.")
			
			# Adapt content based on network type
			adapted_content = self.content
			if network.network_type == "Out of Home (OOH)":
				# For OOH, content is the billboard/poster design description
				adapted_content = f"OOH Design: {self.content}"
			elif network.network_type == "SMS":
				# Truncate for SMS (160 chars)
				adapted_content = self.content[:157] + "..." if len(self.content) > 160 else self.content
			
			# Create Social Post for this network
			social_post = frappe.get_doc({
				"doctype": "Social Post",
				"post_title": f"{self.blast_title} - {network_name}",
				"campaign": self.campaign,
				"platform": network_name,  # Link to Social Media Network
				"post_type": "Image" if self.media_attachment else "Text",
				"status": "Draft",
				"scheduled_time": self.scheduled_time if self.blast_type == "Scheduled" else None,
				"content": adapted_content,
				"media_attachment": self.media_attachment,
				"media_type": self.media_type,
				"hashtags": self.hashtags,
				"mentions": self.mentions,
				"target_audience": self.target_audience,
				"enable_comments": self.enable_comments if network.network_type not in ["SMS", "Email", "Out of Home (OOH)"] else 0,
				"enable_sharing": self.enable_sharing if network.network_type not in ["SMS", "Email"] else 0,
				"omni_blast": self.name  # Link back to Omni Blast
			})
			
			try:
				social_post.insert()
				created_post_links.append(social_post.name)
				
			except Exception as e:
				frappe.log_error(f"Failed to create social post for {network_name}: {str(e)}")
				frappe.msgprint(f"Failed to create post for {network_name}: {str(e)}", indicator="orange")
		
		# Store created posts as JSON links
		self.created_posts = "\n".join(created_post_links)
		self.save()
		frappe.msgprint(f"Created {len(created_post_links)} social posts", indicator="green")

	@frappe.whitelist()
	def execute_blast(self):
		"""Execute the blast by publishing all created posts via the social adapter."""
		if not self.created_posts:
			frappe.throw("No posts to publish. Generate posts first.")
		
		# Parse created posts (newline-separated list of post names)
		post_list = [p.strip() for p in self.created_posts.split('\n') if p.strip()]

		# Always publish in the background. _execute_blast_posts performs external
		# API calls and commits per post to persist progress; running it inside the
		# web-request transaction would violate Frappe's transaction management.
		self.status = "Publishing"
		self.save()
		frappe.enqueue(
			"marketing_hub.marketing_hub.doctype.omni_blast.omni_blast._execute_blast_posts",
			blast_name=self.name,
			post_list=post_list,
			queue="default",
			timeout=600,
			job_id=f"omni_blast_{self.name}"
		)
		frappe.msgprint(f"Publishing {len(post_list)} posts in background...")
		return {"published": 0, "failed": 0, "status": "enqueued"}


def _execute_blast_posts(blast_name, post_list=None):
	"""Execute publishing for a list of Social Post names.
	Runs as a background job. Uses atomic row-level status claiming to prevent
	concurrent workers from publishing the same post twice.
	"""
	from marketing_hub.utils.social_adapter import publish_to_platform

	blast = frappe.get_doc("Omni Blast", blast_name)

	# If another worker already finished this blast, exit immediately.
	if blast.status in ("Published", "Partially Published", "Failed"):
		return {"published": 0, "failed": 0, "status": "skipped"}

	# Re-query the post list if not provided (idempotent retries).
	if post_list is None:
		post_list = frappe.get_all(
			"Social Post",
			filters={"omni_blast": blast_name, "status": ["in", ["Draft", "Scheduled"]]},
			pluck="name",
		)

	published_count = 0
	failed_count = 0
	errors = []

	for post_name in post_list:
		try:
			# Atomically claim the post: only a row still in Draft/Scheduled can be claimed.
			claimed = _claim_social_post(post_name)
			if not claimed:
				continue

			social_post = frappe.get_doc("Social Post", post_name)

			# For scheduled blasts, just mark as Scheduled
			if blast.blast_type == "Scheduled":
				social_post.status = "Scheduled"
				social_post.save()
				published_count += 1
				continue

			# Get the network to determine channel type
			network = frappe.get_cached_doc("Social Media Network", social_post.platform)

			# Non-social channels are handled elsewhere (Email/WhatsApp/SMS)
			if network.network_type in ("Email", "Messaging", "SMS"):
				social_post.status = "Published"
				social_post.published_time = frappe.utils.now_datetime()
				social_post.save()
				published_count += 1
				continue

			# Social media channels — publish via GenericAdapter
			result = publish_to_platform(social_post)

			if result.get("success"):
				published_count += 1
			else:
				failed_count += 1
				errors.append(f"{post_name}: {result.get('error', 'Unknown error')}")

		except Exception as e:
			frappe.log_error(
				title=f"Failed to publish post {post_name}",
				message=frappe.get_traceback(),
			)
			failed_count += 1
			errors.append(f"{post_name}: {str(e)}")
		finally:
			# Commit each post's result so progress is not lost if a later post fails.
			frappe.db.commit()

	# Update blast status based on results
	if failed_count > 0 and published_count == 0:
		blast.status = "Failed"
	elif failed_count > 0:
		blast.status = "Partially Published"
	else:
		blast.status = "Published"

	if errors:
		blast.error_log = "\n".join(errors[:20])

	blast.save()
	frappe.db.commit()

	result = {"published": published_count, "failed": failed_count}

	if not frappe.flags.in_test:
		frappe.msgprint(f"Published {published_count} posts. Failed: {failed_count}")

	return result


def _claim_social_post(post_name: str) -> bool:
	"""Atomically claim a Social Post row for publishing.

	Returns True only if this worker successfully moved the post from
	Draft/Scheduled into Publishing. This is equivalent to row-level locking
	for concurrent blast workers.
	"""
	frappe.db.sql(
		"""
		UPDATE `tabSocial Post`
		SET status = 'Publishing', modified = %s
		WHERE name = %s AND status IN ('Draft', 'Scheduled')
		""",
		(frappe.utils.now(), post_name),
	)
	frappe.db.commit()
	current_status = frappe.db.get_value("Social Post", post_name, "status")
	return current_status == "Publishing"
