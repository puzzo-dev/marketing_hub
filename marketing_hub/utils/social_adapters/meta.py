# -*- coding: utf-8 -*-
"""
Meta Platform Adapter (Facebook & Instagram)

Handles Meta Graph API specifics:
- Page access token in body (not just header)
- Instagram media container creation flow
- Facebook page post vs user post distinction
"""

import frappe
import requests
from marketing_hub.utils.social_adapters.base import BasePlatformAdapter
from marketing_hub.utils.social_adapters.generic import PlatformAPIError


class MetaAdapter(BasePlatformAdapter):
	"""
	Adapter for Meta platforms (Facebook & Instagram).
	
	Register in Social Media Network → custom_adapter_class:
	  marketing_hub.utils.social_adapters.meta.MetaAdapter
	"""
	
	def __init__(self, network_doc, ad_account_doc=None):
		super().__init__(network_doc, ad_account_doc)
		self.api_version = network_doc.api_version or "v21.0"
		self.graph_url = f"https://graph.facebook.com/{self.api_version}"
	
	def publish(self, post_doc):
		"""Publish to Facebook Page or Instagram Business account."""
		try:
			ad_account = self.get_ad_account(post_doc.company)
			oauth_token = self.get_oauth_token()
			access_token = oauth_token.access_token
			
			# Determine if Facebook or Instagram
			if self.network_code in ("instagram", "ig"):
				return self._publish_instagram(post_doc, ad_account, access_token)
			else:
				return self._publish_facebook(post_doc, ad_account, access_token)
		
		except Exception as e:
			frappe.log_error(f"Meta publish error: {str(e)}", "Meta Adapter")
			return {"success": False, "error": str(e)}
	
	def _publish_facebook(self, post_doc, ad_account, access_token):
		"""Publish a post to Facebook Page."""
		page_id = ad_account.account_id or ad_account.ad_account_id
		
		if not page_id:
			return {"success": False, "error": "No Facebook Page ID configured"}
		
		url = f"{self.graph_url}/{page_id}/feed"
		
		payload = {
			"message": post_doc.content or "",
			"access_token": access_token  # Meta requires token in body
		}
		
		# Add link if provided
		if hasattr(post_doc, 'link_url') and post_doc.link_url:
			payload["link"] = post_doc.link_url
		
		# Handle media attachment
		if post_doc.media_attachment:
			media_url = self.get_public_url(post_doc.media_attachment)
			if media_url:
				# Use photos endpoint for image posts
				url = f"{self.graph_url}/{page_id}/photos"
				payload["url"] = media_url
		
		response = requests.post(url, data=payload, timeout=60)
		response.raise_for_status()
		data = response.json()
		
		post_id = data.get("id") or data.get("post_id")
		post_url = f"https://www.facebook.com/{post_id}" if post_id else None
		
		return {
			"success": True,
			"platform_post_id": post_id,
			"url": post_url,
			"message": "Published to Facebook"
		}
	
	def _publish_instagram(self, post_doc, ad_account, access_token):
		"""
		Publish to Instagram Business account (two-step container flow).
		Step 1: Create media container
		Step 2: Publish the container
		"""
		ig_user_id = ad_account.account_id or ad_account.ad_account_id
		
		if not ig_user_id:
			return {"success": False, "error": "No Instagram Business Account ID configured"}
		
		if not post_doc.media_attachment:
			return {"success": False, "error": "Instagram requires a media attachment"}
		
		media_url = self.get_public_url(post_doc.media_attachment)
		
		# Step 1: Create media container
		container_url = f"{self.graph_url}/{ig_user_id}/media"
		container_payload = {
			"image_url": media_url,
			"caption": post_doc.content or "",
			"access_token": access_token
		}
		
		container_response = requests.post(container_url, data=container_payload, timeout=60)
		container_response.raise_for_status()
		container_id = container_response.json().get("id")
		
		if not container_id:
			return {"success": False, "error": "Failed to create Instagram media container"}
		
		# Step 2: Publish the container
		publish_url = f"{self.graph_url}/{ig_user_id}/media_publish"
		publish_payload = {
			"creation_id": container_id,
			"access_token": access_token
		}
		
		publish_response = requests.post(publish_url, data=publish_payload, timeout=60)
		publish_response.raise_for_status()
		
		post_id = publish_response.json().get("id")
		post_url = f"https://www.instagram.com/p/{post_id}/" if post_id else None
		
		return {
			"success": True,
			"platform_post_id": post_id,
			"url": post_url,
			"message": "Published to Instagram"
		}
	
	def delete_post(self, platform_post_id):
		"""Delete a post from Facebook/Instagram."""
		try:
			oauth_token = self.get_oauth_token()
			
			url = f"{self.graph_url}/{platform_post_id}"
			params = {"access_token": oauth_token.access_token}
			
			response = requests.delete(url, params=params, timeout=30)
			response.raise_for_status()
			
			return {"success": True, "message": "Post deleted from Meta"}
		
		except Exception as e:
			return {"success": False, "error": str(e)}
	
	def get_post_analytics(self, platform_post_id):
		"""Fetch post insights from Meta Graph API."""
		try:
			oauth_token = self.get_oauth_token()
			
			url = f"{self.graph_url}/{platform_post_id}/insights"
			params = {
				"metric": "post_impressions,post_clicks,post_reactions_by_type_total",
				"access_token": oauth_token.access_token
			}
			
			response = requests.get(url, params=params, timeout=30)
			response.raise_for_status()
			
			insights = response.json().get("data", [])
			
			# Parse insights into standard format
			metrics = {}
			for insight in insights:
				name = insight.get("name", "")
				values = insight.get("values", [{}])
				value = values[0].get("value", 0) if values else 0
				
				if name == "post_impressions":
					metrics["impressions"] = value
				elif name == "post_clicks":
					metrics["clicks"] = value
				elif name == "post_reactions_by_type_total":
					metrics["likes"] = value.get("like", 0) if isinstance(value, dict) else value
			
			return {
				"impressions": metrics.get("impressions", 0),
				"clicks": metrics.get("clicks", 0),
				"likes": metrics.get("likes", 0),
				"shares": 0,  # Requires separate API call
				"comments": 0,  # Requires separate API call
				"engagement_rate": 0
			}
		
		except Exception as e:
			frappe.log_error(f"Meta analytics error: {str(e)}", "Meta Adapter")
			return {
				"impressions": 0, "clicks": 0, "likes": 0,
				"shares": 0, "comments": 0, "engagement_rate": 0,
				"error": str(e)
			}
