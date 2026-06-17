# -*- coding: utf-8 -*-
"""
Twitter/X Platform Adapter

Handles Twitter API v2 specifics:
- OAuth 2.0 Bearer Token authentication
- Tweet creation with media upload
- Tweet metrics endpoint
"""

import frappe
import requests
from marketing_hub.utils.social_adapters.base import BasePlatformAdapter
from marketing_hub.utils.social_adapters.generic import PlatformAPIError


class TwitterAdapter(BasePlatformAdapter):
	"""
	Adapter for Twitter/X platform.
	
	Register in Social Media Network → custom_adapter_class:
	  marketing_hub.utils.social_adapters.twitter.TwitterAdapter
	"""
	
	API_V2_URL = "https://api.twitter.com/2"
	UPLOAD_URL = "https://upload.twitter.com/1.1"
	
	def __init__(self, network_doc, ad_account_doc=None):
		super().__init__(network_doc, ad_account_doc)
		self.api_base_url = network_doc.api_base_url or self.API_V2_URL
	
	def publish(self, post_doc):
		"""Publish a tweet via Twitter API v2."""
		try:
			ad_account = self.get_ad_account(post_doc.company)
			oauth_token = self.get_oauth_token()
			access_token = oauth_token.access_token
			
			headers = {
				"Authorization": f"Bearer {access_token}",
				"Content-Type": "application/json"
			}
			
			# Build tweet payload
			payload = {
				"text": post_doc.content or ""
			}
			
			# Handle media - Twitter requires pre-uploading
			if post_doc.media_attachment:
				media_id = self._upload_media(post_doc.media_attachment, access_token)
				if media_id:
					payload["media"] = {"media_ids": [media_id]}
			
			# Create tweet
			url = f"{self.api_base_url}/tweets"
			response = requests.post(url, headers=headers, json=payload, timeout=60)
			response.raise_for_status()
			
			data = response.json().get("data", {})
			tweet_id = data.get("id")
			tweet_url = f"https://twitter.com/i/web/status/{tweet_id}" if tweet_id else None
			
			return {
				"success": True,
				"platform_post_id": tweet_id,
				"url": tweet_url,
				"message": "Published to Twitter/X"
			}
		
		except (requests.exceptions.RequestException, frappe.ValidationError) as e:
			frappe.log_error(f"Twitter publish error: {str(e)}", "Twitter Adapter")
			return {"success": False, "error": str(e)}
	
	def _upload_media(self, file_path, access_token):
		"""Upload media to Twitter via v1.1 media upload endpoint."""
		try:
			local_path = frappe.get_site_path('public', file_path.lstrip('/'))
			
			import os
			if not os.path.exists(local_path):
				frappe.log_error(f"Media file not found: {local_path}", "Twitter Adapter")
				return None
			
			url = f"{self.UPLOAD_URL}/media/upload.json"
			headers = {"Authorization": f"Bearer {access_token}"}
			
			with open(local_path, 'rb') as f:
				files = {"media": f}
				response = requests.post(url, headers=headers, files=files, timeout=120)
				response.raise_for_status()
			
			return response.json().get("media_id_string")
		
		except (requests.exceptions.RequestException, frappe.ValidationError, OSError) as e:
			frappe.log_error(f"Twitter media upload error: {str(e)}", "Twitter Adapter")
			return None
	
	def delete_post(self, platform_post_id):
		"""Delete a tweet via Twitter API v2."""
		try:
			oauth_token = self.get_oauth_token()
			
			url = f"{self.api_base_url}/tweets/{platform_post_id}"
			headers = {
				"Authorization": f"Bearer {oauth_token.access_token}"
			}
			
			response = requests.delete(url, headers=headers, timeout=30)
			response.raise_for_status()
			
			return {"success": True, "message": "Tweet deleted"}
		
		except (requests.exceptions.RequestException, frappe.ValidationError) as e:
			return {"success": False, "error": str(e)}
	
	def get_post_analytics(self, platform_post_id):
		"""Fetch tweet metrics via Twitter API v2."""
		try:
			oauth_token = self.get_oauth_token()
			
			url = f"{self.api_base_url}/tweets/{platform_post_id}"
			headers = {
				"Authorization": f"Bearer {oauth_token.access_token}"
			}
			params = {
				"tweet.fields": "public_metrics"
			}
			
			response = requests.get(url, headers=headers, params=params, timeout=30)
			response.raise_for_status()
			
			data = response.json().get("data", {})
			metrics = data.get("public_metrics", {})
			
			impressions = metrics.get("impression_count", 0)
			likes = metrics.get("like_count", 0)
			retweets = metrics.get("retweet_count", 0)
			replies = metrics.get("reply_count", 0)
			
			total_engagement = likes + retweets + replies
			engagement_rate = (total_engagement / impressions * 100) if impressions > 0 else 0
			
			return {
				"impressions": impressions,
				"clicks": 0,  # Not available in public_metrics
				"likes": likes,
				"shares": retweets,
				"comments": replies,
				"engagement_rate": round(engagement_rate, 2)
			}
		
		except (requests.exceptions.RequestException, frappe.ValidationError) as e:
			frappe.log_error(f"Twitter analytics error: {str(e)}", "Twitter Adapter")
			return {
				"impressions": 0, "clicks": 0, "likes": 0,
				"shares": 0, "comments": 0, "engagement_rate": 0,
				"error": str(e)
			}
