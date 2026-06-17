# -*- coding: utf-8 -*-
"""
LinkedIn Platform Adapter

Handles LinkedIn API specifics:
- URN-based entity references
- X-Restli-Protocol-Version header
- UGC Post creation format
"""

import frappe
import requests
from marketing_hub.utils.social_adapters.base import BasePlatformAdapter
from marketing_hub.utils.social_adapters.generic import PlatformAPIError


class LinkedInAdapter(BasePlatformAdapter):
	"""
	Adapter for LinkedIn organization/company pages.
	
	Register in Social Media Network → custom_adapter_class:
	  marketing_hub.utils.social_adapters.linkedin.LinkedInAdapter
	"""
	
	RESTLI_HEADERS = {
		"Content-Type": "application/json",
		"X-Restli-Protocol-Version": "2.0.0",
		"LinkedIn-Version": "202405"
	}
	
	def __init__(self, network_doc, ad_account_doc=None):
		super().__init__(network_doc, ad_account_doc)
		self.api_base_url = network_doc.api_base_url or "https://api.linkedin.com/v2"
	
	def publish(self, post_doc):
		"""Publish a post to LinkedIn organization page via UGC Post API."""
		try:
			ad_account = self.get_ad_account(post_doc.company)
			oauth_token = self.get_oauth_token()
			
			org_urn = ad_account.account_urn
			if not org_urn:
				return {"success": False, "error": "No LinkedIn Organization URN configured"}
			
			# Build author URN
			if not org_urn.startswith("urn:li:"):
				org_urn = f"urn:li:organization:{org_urn}"
			
			# Build UGC Post payload
			payload = {
				"author": org_urn,
				"lifecycleState": "PUBLISHED",
				"specificContent": {
					"com.linkedin.ugc.ShareContent": {
						"shareCommentary": {
							"text": post_doc.content or ""
						},
						"shareMediaCategory": "NONE"
					}
				},
				"visibility": {
					"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
				}
			}
			
			# Handle media attachment
			if post_doc.media_attachment:
				media_url = self.get_public_url(post_doc.media_attachment)
				if media_url:
					share_content = payload["specificContent"]["com.linkedin.ugc.ShareContent"]
					share_content["shareMediaCategory"] = "IMAGE"
					share_content["media"] = [{
						"status": "READY",
						"originalUrl": media_url,
						"description": {
							"text": ""
						}
					}]
			
			# Handle link
			if hasattr(post_doc, 'link_url') and post_doc.link_url:
				share_content = payload["specificContent"]["com.linkedin.ugc.ShareContent"]
				if share_content["shareMediaCategory"] == "NONE":
					share_content["shareMediaCategory"] = "ARTICLE"
				share_content.setdefault("media", []).append({
					"status": "READY",
					"originalUrl": post_doc.link_url
				})
			
			# Make request
			url = f"{self.api_base_url}/ugcPosts"
			headers = {
				**self.RESTLI_HEADERS,
				"Authorization": f"Bearer {oauth_token.access_token}"
			}
			
			response = requests.post(url, headers=headers, json=payload, timeout=60)
			response.raise_for_status()
			
			# LinkedIn returns the post URN in the 'id' field
			post_id = response.json().get("id", "")
			
			# Extract activity ID from URN for URL
			activity_id = post_id.split(":")[-1] if ":" in post_id else post_id
			post_url = f"https://www.linkedin.com/feed/update/{post_id}" if post_id else None
			
			return {
				"success": True,
				"platform_post_id": post_id,
				"url": post_url,
				"message": "Published to LinkedIn"
			}
		
		except (requests.exceptions.RequestException, frappe.ValidationError) as e:
			frappe.log_error(f"LinkedIn publish error: {str(e)}", "LinkedIn Adapter")
			return {"success": False, "error": str(e)}
	
	def delete_post(self, platform_post_id):
		"""Delete a UGC post from LinkedIn."""
		try:
			oauth_token = self.get_oauth_token()
			
			# URL-encode the URN
			encoded_id = requests.utils.quote(platform_post_id, safe='')
			url = f"{self.api_base_url}/ugcPosts/{encoded_id}"
			
			headers = {
				**self.RESTLI_HEADERS,
				"Authorization": f"Bearer {oauth_token.access_token}"
			}
			
			response = requests.delete(url, headers=headers, timeout=30)
			response.raise_for_status()
			
			return {"success": True, "message": "Post deleted from LinkedIn"}
		
		except (requests.exceptions.RequestException, frappe.ValidationError) as e:
			return {"success": False, "error": str(e)}
	
	def get_post_analytics(self, platform_post_id):
		"""Fetch post analytics from LinkedIn."""
		try:
			oauth_token = self.get_oauth_token()
			
			encoded_id = requests.utils.quote(platform_post_id, safe='')
			url = f"{self.api_base_url}/socialActions/{encoded_id}"
			
			headers = {
				**self.RESTLI_HEADERS,
				"Authorization": f"Bearer {oauth_token.access_token}"
			}
			
			response = requests.get(url, headers=headers, timeout=30)
			response.raise_for_status()
			data = response.json()
			
			likes = data.get("likesSummary", {}).get("totalLikes", 0)
			comments = data.get("commentsSummary", {}).get("totalFirstLevelComments", 0)
			
			return {
				"impressions": 0,  # Requires Share Statistics API
				"clicks": 0,
				"likes": likes,
				"shares": 0,
				"comments": comments,
				"engagement_rate": 0
			}
		
		except (requests.exceptions.RequestException, frappe.ValidationError) as e:
			frappe.log_error(f"LinkedIn analytics error: {str(e)}", "LinkedIn Adapter")
			return {
				"impressions": 0, "clicks": 0, "likes": 0,
				"shares": 0, "comments": 0, "engagement_rate": 0,
				"error": str(e)
			}
