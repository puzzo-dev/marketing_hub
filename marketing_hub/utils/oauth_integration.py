"""
OAuth Integration for Marketing Hub
Leverages Frappe's Social Login Key for platform authentication
"""

import json

import frappe
import requests
from frappe import _


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
			from frappe.utils import get_datetime, now_datetime
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
	"""Get OAuth configuration from Social Login Key and Social Media Network doctypes"""
	try:
		# Get Social Login Key (contains OAuth URLs and client credentials)
		social_key = frappe.get_all(
			"Social Login Key",
			filters={"provider_name": platform, "enable_social_login": 1},
			fields=["name", "client_id", "client_secret", "authorize_url", "access_token_url", "api_endpoint"],
			limit=1
		)
		
		if not social_key:
			frappe.log_error(f"No Social Login Key found for {platform}", "OAuth Config")
			return {}
		
		social_key = social_key[0]
		
		# Get Social Media Network (contains API endpoints and specifications)
		network = frappe.get_all(
			"Social Media Network",
			filters={"network_name": platform, "is_active": 1},
			fields=["name", "api_base_url", "publish_endpoint", "analytics_endpoint", "auth_type"],
			limit=1
		)
		
		if not network:
			frappe.log_error(f"No Social Media Network found for {platform}", "OAuth Config")
			return {}
		
		network = network[0]
		
		# Combine configuration
		config = {
			"client_id": social_key.get("client_id"),
			"client_secret": social_key.get("client_secret"),
			"auth_url": social_key.get("authorize_url"),
			"token_url": social_key.get("access_token_url"),
			"api_base": network.get("api_base_url"),
			"social_login_key": social_key.get("name")
		}
		
		return config
	except Exception as e:
		frappe.log_error(f"Error getting OAuth config for {platform}: {str(e)}", "OAuth Config")
		return {}


@frappe.whitelist()
def initiate_oauth_flow(platform, company=None, redirect_uri=None):
	"""Initiate OAuth flow for platform authentication using Frappe's OAuth system"""
	try:
		config = get_oauth_config(platform)
		if not config or not config.get("social_login_key"):
			return {"error": "Platform OAuth not configured. Please set up Social Login Key."}

		if not redirect_uri:
			redirect_uri = frappe.utils.get_url(
				"/api/method/marketing_hub.utils.oauth_integration.oauth_callback"
			)

		# Get scopes from Social Login Key
		social_login_key = frappe.get_doc("Social Login Key", config["social_login_key"])
		
		# Build authorization URL
		auth_params = {
			"client_id": config.get("client_id"),
			"redirect_uri": redirect_uri,
			"response_type": "code",
			"state": frappe.generate_hash(length=20)
		}
		
		# Add scopes if configured
		if social_login_key.get("scopes"):
			auth_params["scope"] = social_login_key.scopes

		# Store state for verification
		frappe.cache().set_value(
			f"oauth_state_{auth_params['state']}",
			{"platform": platform, "company": company, "social_login_key": config["social_login_key"]},
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
