# -*- coding: utf-8 -*-
"""
Base Platform Adapter

Abstract base class defining the interface for all platform-specific adapters.
Platform adapters should extend this class and implement the abstract methods.
"""

import frappe
from abc import ABC, abstractmethod


class BasePlatformAdapter(ABC):
	"""
	Abstract base adapter that defines the contract for platform-specific implementations.
	
	All adapters must implement:
	- publish(post_doc) -> dict
	- delete_post(platform_post_id) -> dict
	- get_post_analytics(platform_post_id) -> dict
	
	The GenericAdapter handles the common case (configuration-driven).
	Platform-specific adapters override behavior for platform quirks.
	"""
	
	def __init__(self, network_doc, ad_account_doc=None):
		"""
		Initialize adapter with network configuration.
		
		Args:
			network_doc: Social Media Network document
			ad_account_doc: Ad Account document (optional)
		"""
		self.network = network_doc
		self.ad_account = ad_account_doc
		self.api_base_url = network_doc.api_base_url or ""
		self.network_code = network_doc.network_code
	
	@abstractmethod
	def publish(self, post_doc):
		"""
		Publish a post to the platform.
		
		Args:
			post_doc: Social Post document
		
		Returns:
			dict: {"success": bool, "platform_post_id": str, "url": str, "error": str}
		"""
		pass
	
	@abstractmethod
	def delete_post(self, platform_post_id):
		"""
		Delete a post from the platform.
		
		Args:
			platform_post_id: Platform-specific post identifier
		
		Returns:
			dict: {"success": bool, "error": str}
		"""
		pass
	
	@abstractmethod
	def get_post_analytics(self, platform_post_id):
		"""
		Fetch analytics for a published post.
		
		Args:
			platform_post_id: Platform-specific post identifier
		
		Returns:
			dict: {"impressions": int, "clicks": int, "likes": int, 
			       "shares": int, "comments": int, "engagement_rate": float}
		"""
		pass
	
	def get_ad_account(self, company=None):
		"""Get Ad Account document for this network and company."""
		if self.ad_account:
			return self.ad_account
		
		filters = {
			"social_media_network": self.network.name,
			"is_active": 1
		}
		
		if company:
			filters["company"] = company
		
		accounts = frappe.get_all("Ad Account",
			filters=filters,
			fields=["name"],
			limit=1)
		
		if not accounts:
			raise frappe.ValidationError(
				f"No active Ad Account found for {self.network.network_name}"
			)
		
		self.ad_account = frappe.get_doc("Ad Account", accounts[0].name)
		return self.ad_account
	
	def get_oauth_token(self):
		"""Get OAuth Bearer Token for the configured user."""
		if not self.ad_account:
			self.get_ad_account()
		return self.ad_account.get_oauth_token()
	
	def get_public_url(self, file_path):
		"""Get publicly accessible URL for a Frappe file path."""
		from frappe.utils import get_url
		
		if not file_path:
			return None
		if file_path.startswith('http'):
			return file_path
		return get_url(file_path)
