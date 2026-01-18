"""
OAuth Integration for Marketing Hub
Leverages Frappe's Social Login Key for platform authentication
"""

import frappe
from frappe import _
import requests
import json


def get_platform_credentials(platform, company=None):
	"""Get OAuth credentials for advertising platform using Social Login Key"""
	try:
		# Check if we have a Social Login Key for this platform
		filters = {"provider_name": platform, "enable_social_login": 0}

		social_key = frappe.get_all(
			"Social Login Key",
			filters=filters,
			fields=["name", "client_id", "client_secret", "base_url", "authorize_url",
					"access_token_url", "api_endpoint"],
			limit=1
		)

		if not social_key:
			# Fallback to Ad Account doctype
			return get_ad_account_credentials(platform, company)

		return social_key[0]
	except Exception as e:
		frappe.log_error(f"Error getting platform credentials: {str(e)}", "Marketing Hub OAuth")
		return None


def get_ad_account_credentials(platform, company=None):
	"""Get credentials from Ad Account doctype"""
	try:
		filters = {"platform": platform, "status": "Active"}
		if company:
			filters["company"] = company

		ad_account = frappe.get_all(
			"Ad Account",
			filters=filters,
			fields=["name", "account_id", "access_token", "refresh_token",
					"token_expiry", "platform"],
			limit=1
		)

		if not ad_account:
			return None

		account = ad_account[0]

		# Check if token needs refresh
		if account.get("token_expiry"):
			from frappe.utils import now_datetime, get_datetime
			if get_datetime(account.token_expiry) <= now_datetime():
				# Token expired, try to refresh
				refreshed = refresh_access_token(account.name)
				if refreshed:
					return frappe.get_doc("Ad Account", account.name)

		return account
	except Exception as e:
		frappe.log_error(f"Error getting ad account: {str(e)}", "Marketing Hub OAuth")
		return None


def refresh_access_token(ad_account_name):
	"""Refresh OAuth access token for ad account"""
	try:
		account = frappe.get_doc("Ad Account", ad_account_name)

		if not account.refresh_token:
			frappe.log_error("No refresh token available", "Marketing Hub OAuth")
			return False

		# Get platform OAuth config
		platform_config = get_oauth_config(account.platform)
		if not platform_config:
			return False

		# Request new access token
		response = requests.post(
			platform_config.get("token_url"),
			data={
				"grant_type": "refresh_token",
				"refresh_token": account.refresh_token,
				"client_id": platform_config.get("client_id"),
				"client_secret": platform_config.get("client_secret")
			}
		)

		if response.status_code == 200:
			data = response.json()

			# Update account with new tokens
			account.access_token = data.get("access_token")
			if data.get("refresh_token"):
				account.refresh_token = data.get("refresh_token")

			# Calculate expiry
			if data.get("expires_in"):
				from frappe.utils import add_to_date, now_datetime
				account.token_expiry = add_to_date(
					now_datetime(),
					seconds=data.get("expires_in")
				)

			account.save(ignore_permissions=True)
			frappe.db.commit()

			return True
		else:
			frappe.log_error(
				f"Token refresh failed: {response.text}",
				"Marketing Hub OAuth"
			)
			return False
	except Exception as e:
		frappe.log_error(f"Error refreshing token: {str(e)}", "Marketing Hub OAuth")
		return False


def get_oauth_config(platform):
	"""Get OAuth configuration for platform"""
	configs = {
		"Google Ads": {
			"token_url": "https://oauth2.googleapis.com/token",
			"auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
			"api_base": "https://googleads.googleapis.com/v14/customers",
			"scopes": ["https://www.googleapis.com/auth/adwords"]
		},
		"Meta Ads": {
			"token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
			"auth_url": "https://www.facebook.com/v18.0/dialog/oauth",
			"api_base": "https://graph.facebook.com/v18.0",
			"scopes": ["ads_management", "ads_read", "business_management"]
		},
		"LinkedIn Ads": {
			"token_url": "https://www.linkedin.com/oauth/v2/accessToken",
			"auth_url": "https://www.linkedin.com/oauth/v2/authorization",
			"api_base": "https://api.linkedin.com/v2",
			"scopes": ["r_ads", "r_ads_reporting", "w_organization_social"]
		},
		"TikTok Ads": {
			"token_url": "https://business-api.tiktok.com/open_api/v1.3/oauth2/access_token/",
			"auth_url": "https://business-api.tiktok.com/portal/auth",
			"api_base": "https://business-api.tiktok.com/open_api/v1.3",
			"scopes": ["ad_management", "reporting"]
		},
		"Twitter Ads": {
			"token_url": "https://api.twitter.com/2/oauth2/token",
			"auth_url": "https://twitter.com/i/oauth2/authorize",
			"api_base": "https://ads-api.twitter.com/11",
			"scopes": ["tweet.read", "users.read", "offline.access"]
		}
	}

	config = configs.get(platform, {})

	# Try to get client credentials from Social Login Key
	social_key = frappe.db.get_value(
		"Social Login Key",
		{"provider_name": platform},
		["client_id", "client_secret"],
		as_dict=1
	)

	if social_key:
		config.update(social_key)

	return config


@frappe.whitelist()
def initiate_oauth_flow(platform, company=None, redirect_uri=None):
	"""Initiate OAuth flow for platform authentication"""
	try:
		config = get_oauth_config(platform)
		if not config:
			return {"error": "Platform not supported"}

		if not redirect_uri:
			redirect_uri = frappe.utils.get_url(
				"/api/method/marketing_hub.utils.oauth_integration.oauth_callback"
			)

		# Build authorization URL
		auth_params = {
			"client_id": config.get("client_id"),
			"redirect_uri": redirect_uri,
			"response_type": "code",
			"scope": " ".join(config.get("scopes", [])),
			"state": frappe.generate_hash(length=20)
		}

		# Store state for verification
		frappe.cache().set_value(
			f"oauth_state_{auth_params['state']}",
			{"platform": platform, "company": company},
			expires_in_sec=600
		)

		from urllib.parse import urlencode
		auth_url = f"{config.get('auth_url')}?{urlencode(auth_params)}"

		return {"auth_url": auth_url}
	except Exception as e:
		frappe.log_error(f"OAuth initiation error: {str(e)}", "Marketing Hub OAuth")
		return {"error": str(e)}


@frappe.whitelist(allow_guest=True)
def oauth_callback(code, state):
	"""Handle OAuth callback from platform"""
	try:
		# Verify state
		cached_data = frappe.cache().get_value(f"oauth_state_{state}")
		if not cached_data:
			return {"error": "Invalid state parameter"}

		platform = cached_data.get("platform")
		company = cached_data.get("company")

		config = get_oauth_config(platform)

		# Exchange code for access token
		redirect_uri = frappe.utils.get_url(
			"/api/method/marketing_hub.utils.oauth_integration.oauth_callback"
		)

		response = requests.post(
			config.get("token_url"),
			data={
				"grant_type": "authorization_code",
				"code": code,
				"redirect_uri": redirect_uri,
				"client_id": config.get("client_id"),
				"client_secret": config.get("client_secret")
			}
		)

		if response.status_code == 200:
			data = response.json()

			# Create or update Ad Account
			ad_account = frappe.new_doc("Ad Account")
			ad_account.platform = platform
			ad_account.company = company or frappe.defaults.get_user_default("Company")
			ad_account.access_token = data.get("access_token")
			ad_account.refresh_token = data.get("refresh_token")
			ad_account.status = "Active"

			# Calculate expiry
			if data.get("expires_in"):
				from frappe.utils import add_to_date, now_datetime
				ad_account.token_expiry = add_to_date(
					now_datetime(),
					seconds=data.get("expires_in")
				)

			ad_account.insert(ignore_permissions=True)
			frappe.db.commit()

			# Clear state from cache
			frappe.cache().delete_value(f"oauth_state_{state}")

			return {
				"success": True,
				"ad_account": ad_account.name,
				"message": _("Successfully connected {0}").format(platform)
			}
		else:
			frappe.log_error(f"Token exchange failed: {response.text}", "Marketing Hub OAuth")
			return {"error": "Failed to exchange authorization code"}
	except Exception as e:
		frappe.log_error(f"OAuth callback error: {str(e)}", "Marketing Hub OAuth")
		return {"error": str(e)}


def make_api_request(platform, endpoint, method="GET", data=None, company=None):
	"""Make authenticated API request to platform"""
	try:
		credentials = get_platform_credentials(platform, company)
		if not credentials:
			raise Exception(f"No credentials found for {platform}")

		config = get_oauth_config(platform)
		access_token = credentials.get("access_token")

		if not access_token:
			raise Exception("No access token available")

		headers = {
			"Authorization": f"Bearer {access_token}",
			"Content-Type": "application/json"
		}

		# Platform-specific header adjustments
		if platform == "Google Ads":
			headers["developer-token"] = credentials.get("developer_token", "")

		url = f"{config.get('api_base')}/{endpoint.lstrip('/')}"

		if method == "GET":
			response = requests.get(url, headers=headers, params=data)
		elif method == "POST":
			response = requests.post(url, headers=headers, json=data)
		elif method == "PUT":
			response = requests.put(url, headers=headers, json=data)
		elif method == "DELETE":
			response = requests.delete(url, headers=headers)

		response.raise_for_status()
		return response.json()
	except Exception as e:
		frappe.log_error(
			f"API request error for {platform}: {str(e)}",
			"Marketing Hub OAuth"
		)
		raise
