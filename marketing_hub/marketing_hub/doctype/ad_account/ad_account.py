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
		"""Validate OAuth configuration and platform-specific fields"""
		# Validate OAuth configuration
		if not self.social_login_key:
			frappe.msgprint("Social Login Key is required for OAuth authentication", indicator="orange")
		
		if not self.oauth_user:
			frappe.msgprint("OAuth User is required to link to OAuth Bearer Token", indicator="orange")
		
		# Validate that at least one platform-specific identifier is provided
		platform_ids = [self.ad_account_id, self.pixel_id, self.customer_id, self.account_urn, self.business_id]
		if not any(platform_ids):
			frappe.msgprint(
				"Please provide at least one platform-specific identifier (Ad Account ID, Customer ID, Account URN, etc.)",
				indicator="orange"
			)
	
	def get_oauth_token(self):
		"""Get OAuth Bearer Token for the configured user."""
		if not self.oauth_user or not self.social_login_key:
			frappe.throw("OAuth User and Social Login Key must be configured")
		
		oauth_token = frappe.get_all(
			"OAuth Bearer Token",
			filters={
				"user": self.oauth_user,
				"client": self.social_login_key,
				"status": "Active"
			},
			fields=["name", "access_token", "refresh_token", "expiration_time"],
			limit=1
		)
		
		if not oauth_token:
			frappe.throw(f"No active OAuth Bearer Token found for user {self.oauth_user}")
		
		return frappe.get_doc("OAuth Bearer Token", oauth_token[0].name)
	
	@frappe.whitelist()
	def test_connection(self):
		"""Test API connection using OAuth Bearer Token"""
		try:
			oauth_token = self.get_oauth_token()
			access_token = oauth_token.access_token
		except Exception as e:
			return {"status": "Error", "message": str(e)}
		
		# Get Social Media Network configuration
		network = frappe.get_doc("Social Media Network", self.platform)
		
		if not network.api_base_url:
			return {"status": "Error", "message": f"No API configuration found for {self.platform}"}
		
		# Build test URL based on platform
		if self.ad_account_id:
			test_url = f"{network.api_base_url}/{self.ad_account_id}"
		elif self.customer_id:
			test_url = f"{network.api_base_url}/{self.customer_id}"
		else:
			test_url = f"{network.api_base_url}/me"
		
		# Use Bearer token auth for OAuth platforms
		headers = {"Authorization": f"Bearer {access_token}"}
		
		try:
			response = requests.get(test_url, headers=headers)
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
def test_account_connection(ad_account_name):
	"""Test connection for an ad account"""
	doc = frappe.get_doc("Ad Account", ad_account_name)
	return doc.test_connection()


@frappe.whitelist()
def get_authorization_url(platform, social_login_key, redirect_uri):
	"""Generate OAuth authorization URL from Social Login Key configuration"""
	# Get Social Login Key document (contains client_id and OAuth URLs)
	try:
		login_key = frappe.get_doc("Social Login Key", social_login_key)
	except Exception as e:
		return f"#error-social-login-key-not-found"
	
	if not login_key.client_id or not login_key.authorize_url:
		return f"#error-incomplete-social-login-key-config"
	
	# Get Social Media Network for additional config like scopes
	network = frappe.get_doc("Social Media Network", platform)
	
	# Build authorization URL
	auth_url = f"{login_key.authorize_url}?client_id={login_key.client_id}&redirect_uri={redirect_uri}&response_type=code"
	
	# Add platform-specific parameters
	if platform == "Google Ads":
		auth_url += "&scope=https://www.googleapis.com/auth/adwords&access_type=offline&prompt=consent"
	elif platform == "LinkedIn Ads":
		auth_url += "&scope=r_ads_reporting r_ads&state=linkedin_ads"
	elif platform == "Meta Ads":
		auth_url += "&state=meta_ads"
	
	return auth_url
