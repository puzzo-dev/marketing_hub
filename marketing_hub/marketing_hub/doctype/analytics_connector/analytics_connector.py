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
			if self.platform == "Meta Ads":
				data = self.sync_meta_ads(ad_account)
			elif self.platform == "Google Ads":
				data = self.sync_google_ads(ad_account)
			elif self.platform == "LinkedIn Ads":
				data = self.sync_linkedin_ads(ad_account)
			else:
				frappe.throw(f"Sync not implemented for {self.platform}")
			
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
	
	def sync_meta_ads(self, ad_account):
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
	
	def sync_google_ads(self, ad_account):
		"""Sync data from Google Ads API"""
		# Placeholder - implement Google Ads API integration
		frappe.throw("Google Ads sync not yet implemented")
	
	def sync_linkedin_ads(self, ad_account):
		"""Sync data from LinkedIn Ads API"""
		# Placeholder - implement LinkedIn Ads API integration
		frappe.throw("LinkedIn Ads sync not yet implemented")
	
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



