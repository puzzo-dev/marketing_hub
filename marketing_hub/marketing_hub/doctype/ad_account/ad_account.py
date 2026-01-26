# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, add_to_date
import requests
import json


class AdAccount(Document):
	def validate(self):
		"""Validate platform-specific fields"""
		if self.platform == "Meta Ads":
			if not self.ad_account_id:
				frappe.msgprint("Ad Account ID is required for Meta Ads", indicator="orange")
		
		elif self.platform == "Google Ads":
			if not self.customer_id:
				frappe.msgprint("Customer ID is required for Google Ads", indicator="orange")
		
		elif self.platform == "LinkedIn Ads":
			if not self.account_urn:
				frappe.msgprint("Account URN is required for LinkedIn Ads", indicator="orange")
	
	def before_save(self):
		"""Check if token needs refresh"""
		if self.token_expiry and self.refresh_token:
			if now_datetime() >= self.token_expiry:
				try:
					self.refresh_access_token()
				except Exception as e:
					frappe.log_error(f"Token refresh failed: {str(e)}", "Ad Account Token Refresh")
	
	def refresh_access_token(self):
		"""Refresh OAuth access token using refresh token"""
		if not self.refresh_token:
			frappe.throw("Refresh token not available")
		
		platform_configs = {
			"Meta Ads": {
				"url": "https://graph.facebook.com/v18.0/oauth/access_token",
				"params": {
					"grant_type": "fb_exchange_token",
					"client_id": self.client_id,
					"client_secret": self.get_password("client_secret"),
					"fb_exchange_token": self.get_password("access_token")
				}
			},
			"Google Ads": {
				"url": "https://oauth2.googleapis.com/token",
				"data": {
					"client_id": self.client_id,
					"client_secret": self.get_password("client_secret"),
					"refresh_token": self.get_password("refresh_token"),
					"grant_type": "refresh_token"
				}
			},
			"LinkedIn Ads": {
				"url": "https://www.linkedin.com/oauth/v2/accessToken",
				"data": {
					"grant_type": "refresh_token",
					"refresh_token": self.get_password("refresh_token"),
					"client_id": self.client_id,
					"client_secret": self.get_password("client_secret")
				}
			}
		}
		
		config = platform_configs.get(self.platform)
		if not config:
			frappe.throw(f"Token refresh not implemented for {self.platform}")
		
		try:
			if "params" in config:
				response = requests.get(config["url"], params=config["params"])
			else:
				response = requests.post(config["url"], data=config["data"])
			
			response.raise_for_status()
			data = response.json()
			
			# Update access token
			self.access_token = data.get("access_token")
			
			# Update expiry
			expires_in = data.get("expires_in", 3600)  # Default 1 hour
			self.token_expiry = add_to_date(now_datetime(), seconds=expires_in)
			
			# Update refresh token if provided
			if data.get("refresh_token"):
				self.refresh_token = data.get("refresh_token")
			
			self.sync_status = "Success"
			self.last_sync = now_datetime()
			
			frappe.msgprint(f"Access token refreshed successfully for {self.account_name}", indicator="green")
			
		except Exception as e:
			self.sync_status = "Failed"
			self.error_log = str(e)
			frappe.log_error(f"Token refresh failed: {str(e)}", "Ad Account Token Refresh")
			frappe.throw(f"Failed to refresh token: {str(e)}")
	
	@frappe.whitelist()
	def test_connection(self):
		"""Test API connection with current credentials"""
		if not self.access_token:
			return {"status": "Error", "message": "Access token not configured"}
		
		platform_tests = {
			"Meta Ads": {
				"url": f"https://graph.facebook.com/v18.0/{self.ad_account_id or 'me'}",
				"params": {"access_token": self.get_password("access_token")}
			},
			"Google Ads": {
				"url": f"https://googleads.googleapis.com/v14/customers/{self.customer_id}",
				"headers": {"Authorization": f"Bearer {self.get_password('access_token')}"}
			},
			"LinkedIn Ads": {
				"url": "https://api.linkedin.com/v2/me",
				"headers": {"Authorization": f"Bearer {self.get_password('access_token')}"}
			}
		}
		
		test_config = platform_tests.get(self.platform)
		if not test_config:
			return {"status": "Error", "message": f"Connection test not implemented for {self.platform}"}
		
		try:
			if "params" in test_config:
				response = requests.get(test_config["url"], params=test_config["params"])
			else:
				response = requests.get(test_config["url"], headers=test_config["headers"])
			
			response.raise_for_status()
			
			self.sync_status = "Success"
			self.last_sync = now_datetime()
			self.error_log = ""
			self.save()
			
			return {
				"status": "Success",
				"message": f"Successfully connected to {self.platform}",
				"data": response.json()
			}
			
		except Exception as e:
			self.sync_status = "Failed"
			self.error_log = str(e)
			self.save()
			
			return {
				"status": "Error",
				"message": f"Connection failed: {str(e)}"
			}


@frappe.whitelist()
def refresh_token(ad_account_name):
	"""Refresh access token for an ad account"""
	doc = frappe.get_doc("Ad Account", ad_account_name)
	doc.refresh_access_token()
	doc.save()
	return {"status": "Success", "message": "Token refreshed successfully"}


@frappe.whitelist()
def test_account_connection(ad_account_name):
	"""Test connection for an ad account"""
	doc = frappe.get_doc("Ad Account", ad_account_name)
	return doc.test_connection()


@frappe.whitelist()
def get_authorization_url(platform, client_id, redirect_uri):
	"""Generate OAuth authorization URL"""
	if platform == "Google Ads":
		return f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=https://www.googleapis.com/auth/adwords&access_type=offline&prompt=consent"
	
	elif platform == "Meta Ads":
		return f"https://www.facebook.com/v18.0/dialog/oauth?client_id={client_id}&redirect_uri={redirect_uri}&state=meta_ads"
	
	elif platform == "LinkedIn Ads":
		return f"https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope=r_ads_reporting r_ads&state=linkedin_ads"
	
	return "#"
