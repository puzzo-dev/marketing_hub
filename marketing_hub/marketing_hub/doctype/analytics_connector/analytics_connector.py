# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, add_to_date, getdate
import requests
import json


class AnalyticsConnector(Document):
	def validate(self):
		"""Validate connector configuration"""
		# Validate ad_account is active
		if self.ad_account:
			ad_account = frappe.get_doc("Ad Account", self.ad_account)
			if not ad_account.is_active:
				frappe.throw(f"Ad Account {self.ad_account} is not active")
			
			# Ensure platform matches
			if ad_account.platform != self.platform:
				frappe.throw(f"Platform mismatch: Connector is {self.platform} but Ad Account is {ad_account.platform}")
		
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
		"""Fetch analytics data from platform and create Analytics Daily Log entries"""
		if not self.is_active:
			return {"status": "Error", "message": "Connector is not active"}
		
		if self.sync_status == "Paused":
			return {"status": "Error", "message": "Connector is paused"}
		
		try:
			# Get ad account credentials
			ad_account = frappe.get_doc("Ad Account", self.ad_account)
			
			# Fetch data based on platform
			data = self.sync_network_ads(ad_account)
			
			# Create Analytics Daily Log entries
			self.create_analytics_logs(data)
			
			# Update sync status
			self.last_sync_date = now_datetime()
			self.total_syncs = (self.total_syncs or 0) + 1
			self.sync_status = "Active"
			self.last_error = ""
			self.set_next_sync_date()
			self.save()
			
			return {"status": "Success", "message": f"Synced {len(data)} records", "records": len(data)}
			
		except Exception as e:
			self.sync_status = "Error"
			self.failed_syncs = (self.failed_syncs or 0) + 1
			self.last_error = str(e)
			self.save()
			frappe.log_error(f"Analytics sync failed: {str(e)}", "Analytics Connector Sync")
			return {"status": "Error", "message": str(e)}

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
			frappe.throw(f"Sync handler '{method_name}' not implemented for platform: {self.platform}")

	def _sync_meta_ads_ads(self, ad_account): 
		# Legacy naming fix or just route to _sync_meta_ads
		return self._sync_meta_ads(ad_account)

	def _sync_facebook_ads(self, ad_account):
		return self._sync_meta_ads(ad_account)

	def _sync_instagram_ads(self, ad_account):
		return self._sync_meta_ads(ad_account)

	def _sync_meta_ads(self, ad_account):
		"""Sync data from Meta Ads API"""
		url = f"https://graph.facebook.com/v18.0/{ad_account.ad_account_id}/insights"
		
		params = {
			"access_token": ad_account.get_password("access_token"),
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
		# Google Ads API v14
		url = f"https://googleads.googleapis.com/v14/customers/{ad_account.customer_id}/googleAds:searchStream"
		
		# Get developer token from settings or ad account (assuming stored in settings for now)
		developer_token = frappe.db.get_single_value("Marketing Hub Settings", "google_ads_developer_token")
		if not developer_token:
			# Fallback or error if critical
			pass 

		headers = {
			"Authorization": f"Bearer {ad_account.get_password('access_token')}",
			"developer-token": developer_token or "INSERT_DEV_TOKEN",
			"login-customer-id": ad_account.customer_id 
		}

		query = f"""
			SELECT
				campaign.id,
				campaign.name,
				metrics.impressions,
				metrics.clicks,
				metrics.cost_micros,
				metrics.conversions,
				metrics.conversions_value
			FROM campaign
			WHERE segments.date BETWEEN '{self.sync_start_date or getdate()}' AND '{getdate()}'
		"""

		response = requests.post(url, headers=headers, json={"query": query})
		
		try:
			response.raise_for_status()
		except Exception as e:
			if response.status_code == 400:
				frappe.log_error(f"Google Ads Query Error: {response.text}", "Google Ads Sync")
			raise e

		return self.parse_google_ads_response(response.json())
	
	def _sync_linkedin_ads_ads(self, ad_account):
		return self._sync_linkedin_ads(ad_account)

	def _sync_linkedin_ads(self, ad_account):
		"""Sync data from LinkedIn Ads API"""
		url = "https://api.linkedin.com/v2/adAnalyticsV2"
		
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
			"Authorization": f"Bearer {ad_account.get_password('access_token')}",
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
			
			log.save(ignore_permissions=True)
	
	def get_or_create_campaign(self, campaign_name, campaign_id_platform):
		"""Get or create Campaign record"""
		# Search for existing campaign
		existing = frappe.db.get_value("Campaign", {"campaign_name": campaign_name})
		if existing:
			return existing
		
		# Create new campaign
		try:
			campaign = frappe.new_doc("Campaign")
			campaign.campaign_name = campaign_name
			campaign.description = f"Auto-created from {self.platform} (ID: {campaign_id_platform})"
			campaign.save(ignore_permissions=True)
			return campaign.name
		except Exception as e:
			frappe.log_error(f"Failed to create campaign: {str(e)}", "Analytics Connector")
			return None
	
	@frappe.whitelist()
	def get_platform_campaigns(self):
		"""Fetch campaigns from platform for mapping"""
		try:
			ad_account = frappe.get_doc("Ad Account", self.ad_account)
			
			if self.platform == "Meta Ads":
				url = f"https://graph.facebook.com/v18.0/{ad_account.ad_account_id}/campaigns"
				params = {
					"access_token": ad_account.get_password("access_token"),
					"fields": "id,name,status,objective",
					"limit": 100
				}
				
				response = requests.get(url, params=params)
				response.raise_for_status()
				
				campaigns = response.json().get("data", [])
				return {"status": "Success", "campaigns": campaigns}
			
			else:
				return {"status": "Error", "message": f"Not implemented for {self.platform}"}
				
		except Exception as e:
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



