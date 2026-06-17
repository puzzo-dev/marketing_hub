# -*- coding: utf-8 -*-
"""
Social Media Platform Adapter

Configuration-driven adapter that reads ALL settings from Social Media Network doctype.
No hardcoded platform logic - add new platforms by just creating doctype records!
"""

import frappe
import requests
import json


# ============ CUSTOM EXCEPTIONS ============

class PlatformAPIError(Exception):
	"""Raised when platform API returns an error."""
	pass


class RateLimitError(PlatformAPIError):
	"""Raised when rate limit is hit."""
	pass


class AuthenticationError(PlatformAPIError):
	"""Raised when authentication fails."""
	pass


class GenericAdapter:
	"""
	Generic adapter that uses configuration from Social Media Network doctype.
	No hardcoded platform logic - everything driven by database configuration.
	"""
	
	def __init__(self, network_doc, ad_account_doc=None, network_account_doc=None):
		"""
		Initialize adapter with network configuration.

		Args:
			network_doc: Social Media Network document
			ad_account_doc: Ad Account document (optional, for ad-specific IDs)
			network_account_doc: Network Account document (optional, for auth)
		"""
		self.network = network_doc
		self.ad_account = ad_account_doc
		self.network_account = network_account_doc
		self.api_base_url = network_doc.api_base_url or ""
		self.network_code = network_doc.network_code
		
		# Load API configuration from network doctype
		self.auth_type = network_doc.auth_type or "OAuth 2.0"
		self.api_version = network_doc.api_version or ""
		self.publish_endpoint = network_doc.publish_endpoint or ""
		self.delete_endpoint = network_doc.delete_endpoint or ""
		self.analytics_endpoint = network_doc.analytics_endpoint or ""
		self.publish_method = network_doc.publish_method or "POST"
		self.request_content_field = network_doc.request_content_field or "content"
		self.request_media_field = network_doc.request_media_field or "media"
		self.response_id_field = network_doc.response_id_field or "id"
		self.response_url_template = network_doc.response_url_template or ""
	
	def publish(self, post_doc):
		"""
		Publish post using configuration from Social Media Network.
		"""
		# Validate content
		validation_errors = self.validate_post_content(post_doc)
		if validation_errors:
			return {"success": False, "error": "; ".join(validation_errors)}
		
		# Check if endpoints are configured
		if not self.publish_endpoint:
			return {
				"success": False,
				"error": f"No publish endpoint configured for {self.network.network_name}"
			}
		
		try:
			# Get Ad Account credentials
			ad_account = self.get_ad_account(post_doc.company)
			self.check_token_expiry()
			
			# Build endpoint URL with placeholders
			endpoint = self._replace_placeholders(
				self.publish_endpoint,
				{
					"account_id": ad_account.account_id,
					"ad_account_id": getattr(ad_account, 'ad_account_id', ''),
				}
			)
			
			# Build request payload dynamically
			payload = self._build_publish_payload(post_doc, ad_account)
			
			# Make API request
			response = self.make_request(
				endpoint,
				method=self.publish_method,
				data=payload
			)
			
			# Extract post ID from response
			post_id = self._extract_field(response, self.response_id_field)
			
			# Build post URL
			post_url = self._build_post_url(post_id) if post_id else None
			
			return {
				"success": True,
				"platform_post_id": post_id,
				"url": post_url,
				"message": f"Published successfully to {self.network.network_name}"
			}
			
		except (PlatformAPIError, requests.exceptions.RequestException, frappe.ValidationError) as e:
			frappe.log_error(f"{self.network.network_name} publish error: {str(e)}", "Generic Adapter")
			return {"success": False, "error": str(e)}
	
	def delete_post(self, platform_post_id):
		"""
		Delete post using configuration.
		"""
		if not self.delete_endpoint:
			return {
				"success": False,
				"error": f"No delete endpoint configured for {self.network.network_name}"
			}
		
		try:
			ad_account = self.get_ad_account()
			
			# Build endpoint with post ID
			endpoint = self._replace_placeholders(
				self.delete_endpoint,
				{"post_id": platform_post_id}
			)
			
			self.make_request(endpoint, method="DELETE")
			
			return {"success": True, "message": "Post deleted successfully"}
			
		except (PlatformAPIError, requests.exceptions.RequestException, frappe.ValidationError) as e:
			frappe.log_error(f"{self.network.network_name} delete error: {str(e)}", "Generic Adapter")
			return {"success": False, "error": str(e)}
	
	def get_post_analytics(self, platform_post_id):
		"""
		Fetch analytics using configuration.
		"""
		if not self.analytics_endpoint:
			return {
				"impressions": 0,
				"clicks": 0,
				"likes": 0,
				"shares": 0,
				"comments": 0,
				"engagement_rate": 0,
				"error": f"No analytics endpoint configured for {self.network.network_name}"
			}
		
		try:
			# Build endpoint with post ID
			endpoint = self._replace_placeholders(
				self.analytics_endpoint,
				{"post_id": platform_post_id}
			)
			
			response = self.make_request(endpoint, method="GET")
			
			# Parse metrics (basic implementation, can be enhanced)
			return {
				"impressions": response.get("impressions", response.get("impression_count", 0)),
				"clicks": response.get("clicks", response.get("click_count", 0)),
				"likes": response.get("likes", response.get("like_count", 0)),
				"shares": response.get("shares", response.get("share_count", 0)),
				"comments": response.get("comments", response.get("comment_count", 0)),
				"engagement_rate": response.get("engagement_rate", 0)
			}
			
		except (PlatformAPIError, requests.exceptions.RequestException, frappe.ValidationError) as e:
			frappe.log_error(f"{self.network.network_name} analytics error: {str(e)}", "Generic Adapter")
			return {
				"impressions": 0,
				"clicks": 0,
				"likes": 0,
				"shares": 0,
				"comments": 0,
				"engagement_rate": 0,
				"error": str(e)
			}
	
	def build_auth_headers(self):
		"""
		Build authentication headers based on auth_type.
		Uses Network Account -> Connected App -> Token Cache for tokens.
		"""
		network_account = self.get_network_account()
		if not network_account:
			return {}

		access_token = network_account.get_access_token()
		if not access_token:
			return {}

		if self.auth_type == "Bearer Token" or self.auth_type == "OAuth 2.0":
			return {
				"Authorization": f"Bearer {access_token}",
				"Content-Type": "application/json"
			}
		elif self.auth_type == "API Key":
			api_key_header = self.network.get("api_key_header") or "X-API-Key"
			return {
				api_key_header: access_token,
				"Content-Type": "application/json"
			}
		elif self.auth_type == "Basic Auth":
			import base64
			connected_app = frappe.get_doc("Connected App", network_account.connected_app)
			client_id = connected_app.client_id or ""
			client_secret = connected_app.get_password("client_secret") or ""
			credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
			return {
				"Authorization": f"Basic {credentials}",
				"Content-Type": "application/json"
			}
		else:
			return {
				"Authorization": f"Bearer {access_token}",
				"Content-Type": "application/json"
			}
	
	def refresh_access_token(self):
		"""
		Generic OAuth token refresh using Frappe's Connected App configuration.
		"""
		network_account = self.get_network_account()
		if not network_account or not network_account.connected_app:
			raise PlatformAPIError("No Connected App configured for token refresh")

		connected_app = frappe.get_doc("Connected App", network_account.connected_app)
		token_cache = connected_app.get_active_token(network_account.user)

		if not token_cache:
			raise PlatformAPIError("No active token cache for refresh")

		return token_cache.get_json()
	
	# ============ COMMON HELPER METHODS ============
	
	def make_request(self, endpoint, method="GET", data=None, files=None, headers=None):
		"""
		Generic HTTP request wrapper with error handling.
		
		Args:
			endpoint: API endpoint (relative to base URL)
			method: HTTP method (GET, POST, DELETE, etc.)
			data: Request payload (dict)
			files: Files to upload (dict)
			headers: Additional headers (dict)
		
		Returns:
			dict: Response JSON
		"""
		url = f"{self.api_base_url}/{endpoint.lstrip('/')}"
		
		# Build headers
		request_headers = self.build_auth_headers()
		if headers:
			request_headers.update(headers)
		
		try:
			if method == "GET":
				response = requests.get(url, headers=request_headers, params=data, timeout=30)
			elif method == "POST":
				if files:
					response = requests.post(url, headers=request_headers, data=data, files=files, timeout=60)
				else:
					if 'Content-Type' not in request_headers:
						request_headers['Content-Type'] = 'application/json'
					response = requests.post(url, headers=request_headers, json=data, timeout=60)
			elif method == "DELETE":
				response = requests.delete(url, headers=request_headers, timeout=30)
			elif method == "PUT":
				response = requests.put(url, headers=request_headers, json=data, timeout=60)
			else:
				raise ValueError(f"Unsupported HTTP method: {method}")
			
			# Log request for debugging
			self._log_request(method, url, response.status_code)
			
			# Handle rate limiting
			if response.status_code == 429:
				retry_after = int(response.headers.get('Retry-After', 60))
				raise RateLimitError(f"Rate limited. Retry after {retry_after} seconds")
			
			# Raise for HTTP errors
			response.raise_for_status()
			
			return response.json() if response.content else {}
			
		except requests.exceptions.RequestException as e:
			frappe.log_error(f"{self.network.network_name} API Error: {str(e)}", "Social Adapter")
			raise PlatformAPIError(f"API request failed: {str(e)}")
	
	def validate_post_content(self, post_doc):
		"""
		Validate post content against platform limits.
		
		Args:
			post_doc: Social Post document
		
		Returns:
			list: List of error messages (empty if valid)
		"""
		errors = []
		
		# Check text length
		if self.network.max_text_length:
			if len(post_doc.content or "") > self.network.max_text_length:
				errors.append(f"Content exceeds {self.network.max_text_length} character limit")
		
		# Check media count
		if post_doc.media_attachment and self.network.max_media_count:
			media_files = post_doc.media_attachment.split(',') if isinstance(post_doc.media_attachment, str) else [post_doc.media_attachment]
			if len(media_files) > self.network.max_media_count:
				errors.append(f"Too many media files (max {self.network.max_media_count})")
		
		# Check if platform supports media
		if post_doc.media_attachment and not self.network.supports_media:
			errors.append(f"{self.network.network_name} does not support media attachments")
		
		return errors
	
	def get_ad_account(self, company=None):
		"""
		Get Ad Account document for this network and company.
		
		Args:
			company: Company name (optional)
		
		Returns:
			Document: Ad Account document
		"""
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
	
	def get_network_account(self):
		"""
		Get Network Account for auth. Uses explicit network_account if set,
		otherwise looks up via Ad Account -> Network Account or directly by platform.
		"""
		if self.network_account:
			return self.network_account

		# If ad_account has network_account, use that
		if self.ad_account and self.ad_account.network_account:
			self.network_account = frappe.get_doc("Network Account", self.ad_account.network_account)
			return self.network_account

		# Fallback: find active Network Account for this platform
		if self.network:
			networks = frappe.get_all(
				"Network Account",
				filters={
					"platform": self.network.network_name,
					"is_active": 1,
				},
				fields=["name"],
				limit=1,
				order_by="modified desc",
			)
			if networks:
				self.network_account = frappe.get_doc("Network Account", networks[0].name)
				return self.network_account

		return None
	
	def _log_request(self, method, url, status_code):
		"""Log API request for debugging."""
		frappe.logger().debug(f"{self.network.network_name} API: {method} {url} -> {status_code}")
	
	def check_token_expiry(self):
		"""Check if OAuth token is expired and refresh if needed via Connected App."""
		network_account = self.get_network_account()
		if not network_account:
			return

		connected_app = frappe.get_doc("Connected App", network_account.connected_app)
		token_cache = connected_app.get_active_token(network_account.user)

		if not token_cache:
			raise AuthenticationError(f"No active token for {self.network.network_name}")
	
	def get_public_url(self, file_path):
		"""
		Get publicly accessible URL for media file.
		
		Args:
			file_path: Frappe file path
		
		Returns:
			str: Full public URL
		"""
		from frappe.utils import get_url
		
		if not file_path:
			return None
		
		# If already a full URL, return as is
		if file_path.startswith('http'):
			return file_path
		
		# Convert Frappe file path to full URL
		return get_url(file_path)
	
	def get_file_path(self, file_url):
		"""
		Get local file path from Frappe file URL.
		
		Args:
			file_url: File URL (e.g., /files/image.jpg)
		
		Returns:
			str: Absolute file path
		"""
		if not file_url:
			return None
		
		# Remove leading slash
		file_url = file_url.lstrip('/')
		
		# Get site path
		return frappe.get_site_path('public', file_url)
	
	def _build_publish_payload(self, post_doc, ad_account):
		"""
		Build request payload dynamically based on configuration.
		"""
		payload = {}
		
		# Add content field
		if self.request_content_field:
			payload[self.request_content_field] = post_doc.content or ""
		
		# Add media field if exists
		if post_doc.media_attachment and self.request_media_field:
			media_url = self.get_public_url(post_doc.media_attachment)
			payload[self.request_media_field] = media_url
		
		# Add access token if auth type requires it in body
		if self.auth_type == "OAuth 2.0" and "graph.facebook.com" in self.api_base_url:
			# Meta APIs use access_token in body
			oauth_token = self.get_oauth_token()
			payload["access_token"] = oauth_token.access_token
		
		# Add link if provided
		if hasattr(post_doc, 'link_url') and post_doc.link_url:
			payload["link"] = post_doc.link_url
		
		return payload
	
	def _replace_placeholders(self, template, values):
		"""
		Replace placeholders in template string.
		
		Args:
			template: String with {placeholders}
			values: Dict of placeholder values
		
		Returns:
			String with placeholders replaced
		"""
		result = template
		for key, value in values.items():
			result = result.replace(f"{{{key}}}", str(value))
		return result
	
	def _extract_field(self, data, field_path):
		"""
		Extract field from nested JSON using dot notation.
		
		Args:
			data: JSON response dict
			field_path: Path like "id" or "data.id" or "response.post.id"
		
		Returns:
			Field value or None
		"""
		if not field_path:
			return None
		
		parts = field_path.split('.')
		current = data
		
		for part in parts:
			if isinstance(current, dict) and part in current:
				current = current[part]
			else:
				return None
		
		return current
	
	def _build_post_url(self, post_id):
		"""
		Build post URL from template.
		"""
		if not self.response_url_template or not post_id:
			return None
		
		return self._replace_placeholders(
			self.response_url_template,
			{"post_id": post_id}
		)
