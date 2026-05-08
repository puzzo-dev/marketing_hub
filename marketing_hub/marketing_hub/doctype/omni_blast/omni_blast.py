# Copyright (c) 2026, Puzzo and contributors
# For license information, please see license.txt

import frappe
from frappe import _
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
				frappe.throw(_("SMS Blast is disabled in Marketing Hub Settings. Cannot post to {0}.").format(network_name))
				
			if network.network_type == "Messaging" and "WhatsApp" in network_name and not settings.enable_whatsapp_blast:
				frappe.throw(_("WhatsApp Blast is disabled in Marketing Hub Settings. Cannot post to {0}.").format(network_name))
				
			if network.network_type == "Email" and not settings.enable_email_blast:
				frappe.throw(_("Email Blast is disabled in Marketing Hub Settings. Cannot post to {0}.").format(network_name))
			
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
				frappe.msgprint(_("Failed to create post for {0}: {1}").format(network_name, str(e)), indicator="orange")
		
		# Store created posts as JSON links
		self.created_posts = "\n".join(created_post_links)
		self.save()
		frappe.msgprint(_("Created {0} social posts").format(len(created_post_links)), indicator="green")

	@frappe.whitelist()
	def execute_blast(self):
		"""Execute the blast by publishing all created posts via the social adapter."""
		if not self.created_posts:
			frappe.throw("No posts to publish. Generate posts first.")
		
		# Parse created posts (newline-separated list of post names)
		post_list = [p.strip() for p in self.created_posts.split('\n') if p.strip()]
		
		# For large blasts (>5 posts), run in background
		if len(post_list) > 5:
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
			frappe.msgprint(_("Publishing {0} posts in background...").format(len(post_list)))
			return {"published": 0, "failed": 0, "status": "enqueued"}
		
		return _execute_blast_posts(self.name, post_list)


def _execute_blast_posts(blast_name, post_list):
	"""Execute publishing for a list of Social Post names.
	Can run synchronously or as a background job.
	"""
	from marketing_hub.utils.social_adapter import publish_to_platform
	
	blast = frappe.get_doc("Omni Blast", blast_name)
	blast.status = "Publishing"
	blast.save()
	frappe.db.commit()
	
	published_count = 0
	failed_count = 0
	errors = []
	
	for post_name in post_list:
		try:
			if not frappe.db.exists("Social Post", post_name):
				failed_count += 1
				errors.append(f"{post_name}: Post not found")
				continue
			
			social_post = frappe.get_doc("Social Post", post_name)
			
			# Skip already-published or deleted posts
			if social_post.status in ("Published", "Deleted"):
				published_count += 1
				continue
			
			# For scheduled blasts, just mark as Scheduled
			if blast.blast_type == "Scheduled":
				social_post.status = "Scheduled"
				social_post.save()
				published_count += 1
				continue
			
			# Get the network to determine channel type
			network = frappe.get_cached_doc("Social Media Network", social_post.social_media_network)
			
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
			
			frappe.db.commit()
			
		except Exception as e:
			frappe.log_error(f"Failed to publish post {post_name}: {str(e)}", "Omni Blast Publish")
			failed_count += 1
			errors.append(f"{post_name}: {str(e)}")
			frappe.db.rollback()
	
	# Update blast status
	if failed_count > 0 and published_count == 0:
		blast.status = "Failed"
	elif failed_count > 0:
		blast.status = "Partially Published"
	else:
		blast.status = "Published"
	
	if errors:
		blast.error_log = "\n".join(errors[:20])  # Cap at 20 errors
	
	blast.save()
	frappe.db.commit()
	
	result = {"published": published_count, "failed": failed_count}
	
	if not frappe.flags.in_test:
		frappe.msgprint(_("Published {0} posts. Failed: {1}").format(published_count, failed_count))
	
	return result
