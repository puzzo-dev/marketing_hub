# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, add_to_date, getdate
import requests
import json
import time


class AnalyticsConnector(Document):
	def validate(self):
		"""Validate connector configuration"""
		# Validate ad_account is active
		if self.ad_account:
			ad_account = frappe.get_doc("Ad Account", self.ad_account)
			if not ad_account.is_active:
				frappe.throw(_("Ad Account {0} is not active").format(self.ad_account))
			
			# Ensure platform matches
			if ad_account.platform != self.platform:
				frappe.throw(_("Platform mismatch: Connector is {0} but Ad Account is {1}").format(self.platform, ad_account.platform))
		
		# Set next sync date
		if not self.next_sync_date:
			self.set_next_sync_date()
	
	def set_next_sync_date(self):
		"""Calculate next sync date based on frequency"""
		if self.sync_frequency == "Hourly":
			self.next_sync_date = add_to_date(now_datetime(), hours=1)
		elif self.sync_frequency == "Daily":
			self.next_sync_date = add_to_date(now_datetime(), days=1)
		elif self.sync_frequency == "Weekly":
			self.next_sync_date = add_to_date(now_datetime(), weeks=1)
	
	@frappe.whitelist()
	def sync_analytics(self):
		"""Fetch analytics data from platform and create Analytics Daily Log entries.
		Includes retry logic with exponential backoff (max 3 retries).
		Prevents overlapping syncs via sync_in_progress flag.
		"""
		if not self.is_active:
			return {"status": "Error", "message": "Connector is not active"}
		
		if self.sync_status == "Paused":
			return {"status": "Error", "message": "Connector is paused"}
		
		# Prevent overlapping syncs
		if self.sync_in_progress:
			return {"status": "Error", "message": "Sync already in progress"}
		
		self.sync_in_progress = 1
		self.save()
		frappe.db.commit()
		
		max_retries = 3
		base_delay = 2  # seconds
		last_error = None
		
		for attempt in range(1, max_retries + 1):
			try:
				# Get ad account credentials
				ad_account = frappe.get_doc("Ad Account", self.ad_account)
				
				# Fetch data based on platform
				data = self.sync_network_ads(ad_account)
				
				# Create Analytics Daily Log entries
				self.create_analytics_logs(data)
				
				# Update sync status — success
				self.last_sync_date = now_datetime()
				self.total_syncs = (self.total_syncs or 0) + 1
				self.consecutive_failures = 0
				self.sync_status = "Active"
				self.last_error = ""
				self.sync_in_progress = 0
				self.set_next_sync_date()
				self.save()
				
				return {"status": "Success", "message": f"Synced {len(data)} records", "records": len(data)}
			
			except requests.exceptions.HTTPError as e:
				response = getattr(e, 'response', None)
				status_code = response.status_code if response is not None else 0
				
				# Rate limited — respect Retry-After header
				if status_code == 429:
					retry_after = int(response.headers.get('Retry-After', 60))
					frappe.logger().warning(
						f"Analytics sync rate limited for {self.name}, retrying after {retry_after}s"
					)
					if attempt < max_retries:
						time.sleep(min(retry_after, 120))  # Cap at 2 minutes
						continue
				
				# Auth errors — don't retry
				if status_code in (401, 403):
					last_error = f"Authentication failed (HTTP {status_code}): {str(e)}"
					break
				
				# Server errors — retry with backoff
				if status_code >= 500 and attempt < max_retries:
					delay = base_delay * (2 ** (attempt - 1))
					frappe.logger().warning(
						f"Analytics sync server error for {self.name} (attempt {attempt}), retrying in {delay}s"
					)
					time.sleep(delay)
					continue
				
				last_error = str(e)
				break
			
			except requests.exceptions.ConnectionError as e:
				# Network error — retry with backoff
				if attempt < max_retries:
					delay = base_delay * (2 ** (attempt - 1))
					time.sleep(delay)
					continue
				last_error = f"Connection error: {str(e)}"
				break
			
			except (frappe.ValidationError, frappe.DoesNotExistError, ValueError) as e:
				last_error = str(e)
				break
		
		# All retries exhausted — record failure
		self.failed_syncs = (self.failed_syncs or 0) + 1
		self.consecutive_failures = (self.consecutive_failures or 0) + 1
		self.last_error = last_error or "Unknown error"
		self.sync_in_progress = 0
		
		# Auto-pause after 5 consecutive failures
		if self.consecutive_failures >= 5:
			self.sync_status = "Paused"
			self.last_error += " [Auto-paused after 5 consecutive failures]"
		else:
			self.sync_status = "Error"
		
		self.save()
		frappe.log_error(f"Analytics sync failed: {last_error}", "Analytics Connector Sync")
		return {"status": "Error", "message": last_error}

	def sync_network_ads(self, ad_account):
		"""
		Generic sync method that dispatches to platform-specific implementation.
		The dispatching is based on the Linked Social Media Network's 'network_code' or name.
		"""
		# Normalize platform name to method name (e.g. "Google Ads" -> "google_ads")
		method_name = f"_sync_{frappe.scrub(self.platform)}_ads"
		
		# Check if method exists in this class
		if hasattr(self, method_name):
			return getattr(self, method_name)(ad_account)
		else:
			# Fallback: Check if there's a custom controller or hook
			# For now, throw error if not implemented
			frappe.throw(_("Sync handler '{0}' not implemented for platform: {1}").format(method_name, self.platform))

	def _sync_meta_ads_ads(self, ad_account): 
		# Legacy naming fix or just route to _sync_meta_ads
		return self._sync_meta_ads(ad_account)

	def _sync_facebook_ads(self, ad_account):
		return self._sync_meta_ads(ad_account)

	def _sync_instagram_ads(self, ad_account):
		return self._sync_meta_ads(ad_account)

	def _sync_meta_ads(self, ad_account):
		"""Sync data from Meta Ads API using Social Media Network configuration"""
		access_token = ad_account.get_access_token()

		# Get API endpoint from Social Media Network doctype
		network = frappe.get_cached_doc("Social Media Network", self.platform)
		base_url = network.api_base_url or "https://graph.facebook.com/v18.0"
		analytics_endpoint = network.analytics_endpoint or "{account_id}/insights"

		# Replace placeholders
		endpoint = analytics_endpoint.replace("{account_id}", ad_account.ad_account_id)
		url = f"{base_url}/{endpoint}"

		params = {
			"access_token": access_token,
			"fields": "campaign_id,campaign_name,impressions,clicks,spend,actions,action_values",
			"time_range": json.dumps({
				"since": str(self.sync_start_date or getdate()),
				"until": str(getdate())
			}),
			"level": "campaign",
			"limit": 100
		}

		response = requests.get(url, params=params)
		response.raise_for_status()

		return self.parse_meta_ads_response(response.json())
	
	def _sync_google_ads_ads(self, ad_account): # Handle redundancy from scrub("Google Ads") -> "google_ads" + "_ads"
		return self._sync_google_ads(ad_account)

	def _sync_google_ads(self, ad_account):
		"""Sync data from Google Ads API"""
		access_token = ad_account.get_access_token()
		# Google Ads API v17
		url = f"https://googleads.googleapis.com/v17/customers/{ad_account.customer_id}/googleAds:searchStream"
		
		# Get developer token from settings
		developer_token = frappe.db.get_single_value("Marketing Hub Settings", "google_ads_developer_token")
		if not developer_token:
			frappe.throw(_("Google Ads Developer Token is not configured in Marketing Hub Settings"))

		headers = {
			"Authorization": f"Bearer {access_token}",
			"developer-token": developer_token,
			"login-customer-id": ad_account.customer_id 
		}

		# Use parameterized date values to prevent injection
		sync_start = str(self.sync_start_date or getdate())
		sync_end = str(getdate())

		query = (
			"SELECT "
			"campaign.id, campaign.name, "
			"metrics.impressions, metrics.clicks, "
			"metrics.cost_micros, metrics.conversions, "
			"metrics.conversions_value "
			"FROM campaign "
			"WHERE segments.date BETWEEN %(sync_start)s AND %(sync_end)s"
		)
		params = {"sync_start": sync_start, "sync_end": sync_end}

		response = requests.post(url, headers=headers, json={"query": query, "params": params})
		response.raise_for_status()

		return self.parse_google_ads_response(response.json())
	
	def _sync_linkedin_ads_ads(self, ad_account):
		return self._sync_linkedin_ads(ad_account)

	def _sync_linkedin_ads(self, ad_account):
		"""Sync data from LinkedIn Ads API using Social Media Network configuration"""
		access_token = ad_account.get_access_token()
		
		# Get API endpoint from Social Media Network doctype
		network = frappe.get_cached_doc("Social Media Network", self.platform)
		base_url = network.api_base_url or "https://api.linkedin.com/v2"
		analytics_endpoint = network.analytics_endpoint or "adAnalyticsV2"
		url = f"{base_url}/{analytics_endpoint}"
		
		params = {
			"q": "analytics",
			"dateRange.start.day": (self.sync_start_date or getdate()).day,
			"dateRange.start.month": (self.sync_start_date or getdate()).month,
			"dateRange.start.year": (self.sync_start_date or getdate()).year,
			"dateRange.end.day": getdate().day,
			"dateRange.end.month": getdate().month,
			"dateRange.end.year": getdate().year,
			"timeGranularity": "DAILY",
			"pivot": "CAMPAIGN",
			"accounts": f"urn:li:sponsoredAccount:{ad_account.account_urn}"
		}

		headers = {
			"Authorization": f"Bearer {access_token}",
			"X-Restli-Protocol-Version": "2.0.0"
		}

		response = requests.get(url, headers=headers, params=params)
		response.raise_for_status()

		return self.parse_linkedin_ads_response(response.json())

	def parse_google_ads_response(self, response_data):
		"""Parse Google Ads API response"""
		parsed_data = []
		
		# searchStream returns a list of batches
		for batch in response_data:
			for row in batch.get("results", []):
				campaign = row.get("campaign", {})
				metrics = row.get("metrics", {})
				
				parsed_data.append({
					"campaign_id_platform": str(campaign.get("id")),
					"campaign_name": campaign.get("name"),
					"impressions": int(metrics.get("impressions", 0)),
					"clicks": int(metrics.get("clicks", 0)),
					"spend": float(metrics.get("costMicros", 0)) / 1000000, # Convert micros to currency
					"conversions": float(metrics.get("conversions", 0)),
					"revenue": float(metrics.get("conversionsValue", 0))
				})
				
		return parsed_data

	def parse_linkedin_ads_response(self, response_data):
		"""Parse LinkedIn Ads API response"""
		parsed_data = []
		
		for element in response_data.get("elements", []):
			# Pivot value contains the URN
			campaign_urn = element.get("pivotValue", "")
			# You might need another call to get Campaign Name if not cached/stored
			campaign_id = campaign_urn.split(":")[-1] if ":" in campaign_urn else campaign_urn
			
			parsed_data.append({
				"campaign_id_platform": campaign_id,
				"campaign_name": f"LinkedIn Campaign {campaign_id}", # optimize: fetch name
				"impressions": element.get("impressions", 0),
				"clicks": element.get("clicks", 0),
				"spend": float(element.get("costInLocalCurrency", 0)),
				"conversions": element.get("externalWebsiteConversions", 0),
				"revenue": float(element.get("conversionValueInLocalCurrency", 0))
			})
			
		return parsed_data
	
	def parse_meta_ads_response(self, response_data):
		"""Parse Meta Ads API response into standard format"""
		parsed_data = []
		
		for record in response_data.get("data", []):
			# Extract conversions and revenue from actions
			conversions = 0
			revenue = 0
			
			for action in record.get("actions", []):
				if action.get("action_type") in ["purchase", "complete_registration", "lead"]:
					conversions += int(action.get("value", 0))
			
			for action_value in record.get("action_values", []):
				if action_value.get("action_type") == "purchase":
					revenue += float(action_value.get("value", 0))
			
			parsed_data.append({
				"campaign_id_platform": record.get("campaign_id"),
				"campaign_name": record.get("campaign_name"),
				"impressions": int(record.get("impressions", 0)),
				"clicks": int(record.get("clicks", 0)),
				"spend": float(record.get("spend", 0)),
				"conversions": conversions,
				"revenue": revenue
			})
		
		return parsed_data
	
	def create_analytics_logs(self, data):
		"""Create Analytics Daily Log entries from synced data"""
		for record in data:
			# Check if log already exists
			existing = frappe.db.exists("Analytics Daily Log", {
				"log_date": getdate(),
				"connector": self.name,
				"campaign_id_platform": record.get("campaign_id_platform")
			})
			
			if existing:
				# Update existing log
				log = frappe.get_doc("Analytics Daily Log", existing)
			else:
				# Create new log
				log = frappe.new_doc("Analytics Daily Log")
				log.log_date = getdate()
				log.connector = self.name
				log.campaign_id_platform = record.get("campaign_id_platform")
				log.channel = self.platform
			
			# Update metrics
			log.impressions = record.get("impressions", 0)
			log.clicks = record.get("clicks", 0)
			log.conversions = record.get("conversions", 0)
			log.spend = record.get("spend", 0)
			log.revenue = record.get("revenue", 0)
			log.sync_timestamp = now_datetime()
			
			# Try to link to Campaign if auto_create_campaigns is enabled
			if self.auto_create_campaigns and record.get("campaign_name"):
				campaign = self.get_or_create_campaign(record.get("campaign_name"), record.get("campaign_id_platform"))
				if campaign:
					log.campaign = campaign
			
			log.save()
	
	def get_or_create_campaign(self, campaign_name, campaign_id_platform):
		"""Get or create Marketing Campaign record"""
		# Search for existing marketing campaign
		existing = frappe.db.get_value("Marketing Campaign", {"campaign_name": campaign_name})
		if existing:
			return existing

		# Create new marketing campaign
		try:
			campaign = frappe.new_doc("Marketing Campaign")
			campaign.campaign_name = campaign_name
			campaign.description = f"Auto-created from {self.platform} (ID: {campaign_id_platform})"
			campaign.save()
			return campaign.name
		except (frappe.ValidationError, frappe.DoesNotExistError) as e:
			frappe.log_error(f"Failed to create marketing campaign: {str(e)}", "Analytics Connector")
			return None
	
	@frappe.whitelist()
	def get_platform_campaigns(self):
		"""Fetch campaigns from platform using Social Media Network configuration"""
		try:
			ad_account = frappe.get_doc("Ad Account", self.ad_account)
			access_token = ad_account.get_access_token()
			
			# Get API configuration from Social Media Network doctype
			network = frappe.get_cached_doc("Social Media Network", self.platform)
			base_url = network.api_base_url
			
			if not base_url:
				return {"status": "Error", "message": f"No API configuration found for {self.platform}"}
			
			if self.platform in ("Meta Ads", "Facebook", "Instagram"):
				url = f"{base_url}/{ad_account.ad_account_id}/campaigns"
				params = {
					"access_token": access_token,
					"fields": "id,name,status,objective",
					"limit": 100
				}
				
				response = requests.get(url, params=params)
				response.raise_for_status()
				
				campaigns = response.json().get("data", [])
				return {"status": "Success", "campaigns": campaigns}
			
			elif self.platform == "Google Ads":
				developer_token = frappe.db.get_single_value("Marketing Hub Settings", "google_ads_developer_token")
				if not developer_token:
					return {"status": "Error", "message": "Google Ads Developer Token not configured"}
				
				url = f"https://googleads.googleapis.com/v17/customers/{ad_account.customer_id}/googleAds:searchStream"
				headers = {
					"Authorization": f"Bearer {oauth_token.access_token}",
					"developer-token": developer_token,
					"login-customer-id": ad_account.customer_id
				}
				query = "SELECT campaign.id, campaign.name, campaign.status FROM campaign ORDER BY campaign.name"
				
				response = requests.post(url, headers=headers, json={"query": query})
				response.raise_for_status()
				
				campaigns = []
				for batch in response.json():
					for row in batch.get("results", []):
						campaign = row.get("campaign", {})
						campaigns.append({
							"id": str(campaign.get("id")),
							"name": campaign.get("name"),
							"status": campaign.get("status")
						})
				
				return {"status": "Success", "campaigns": campaigns}
			
			elif self.platform == "LinkedIn Ads":
				url = f"{base_url}/adCampaignsV2"
				headers = {
					"Authorization": f"Bearer {oauth_token.access_token}",
					"X-Restli-Protocol-Version": "2.0.0"
				}
				params = {
					"q": "search",
					"search.account.values[0]": f"urn:li:sponsoredAccount:{ad_account.account_urn}",
					"count": 100
				}
				
				response = requests.get(url, headers=headers, params=params)
				response.raise_for_status()
				
				campaigns = []
				for element in response.json().get("elements", []):
					campaign_id = element.get("id", "")
					campaigns.append({
						"id": str(campaign_id),
						"name": element.get("name"),
						"status": element.get("status")
					})
				
				return {"status": "Success", "campaigns": campaigns}
			
			else:
				return {"status": "Error", "message": f"Campaign listing not implemented for {self.platform}"}
				
		except (frappe.ValidationError, requests.exceptions.RequestException) as e:
			return {"status": "Error", "message": str(e)}


@frappe.whitelist()
def sync_connector(connector_name):
	"""Sync a specific connector"""
	doc = frappe.get_doc("Analytics Connector", connector_name)
	return doc.sync_analytics()


@frappe.whitelist()
def get_campaigns_from_platform(connector_name):
	"""Get campaigns from platform"""
	doc = frappe.get_doc("Analytics Connector", connector_name)
	return doc.get_platform_campaigns()



