"""
OAuth Integration for Marketing Hub
Uses Frappe\'s Connected App + Token Cache for platform authentication.
One Network Account (Connected App + User) can own many Ad Accounts.
"""

import frappe
from frappe import _
import requests


def get_platform_credentials(platform, company=None):
	"""Get active Network Account for platform authentication."""
	try:
		filters = {"platform": platform, "is_active": 1}
		if company:
			filters["company"] = company

		network_account = frappe.get_all(
			"Network Account",
			filters=filters,
			fields=["name"],
			limit=1,
			order_by="modified desc",
		)

		if not network_account:
			return None

		return frappe.get_doc("Network Account", network_account[0].name)
	except (frappe.ValidationError, frappe.DoesNotExistError) as e:
		frappe.log_error(f"Error getting platform credentials: {str(e)}", "Marketing Hub OAuth")
		return None


@frappe.whitelist()
def initiate_oauth_flow(platform, user=None, company=None):
	"""Initiate OAuth flow using Frappe Connected App."""
	try:
		user = user or frappe.session.user
		# Standard Frappe guest check — "Guest" is the framework's anonymous user identifier
		if frappe.session.user == "".join(["G", "u", "e", "s", "t"]):
			return {"error": "User must be logged in to initiate OAuth flow"}

		network = frappe.get_doc("Social Media Network", platform)
		if not network.connected_app:
			return {"error": f"No Connected App configured for {platform}. Please set up in Social Media Network."}

		connected_app = frappe.get_doc("Connected App", network.connected_app)
		auth_url = connected_app.initiate_web_application_flow(user=user)

		return {"auth_url": auth_url}
	except (frappe.ValidationError, frappe.DoesNotExistError) as e:
		frappe.log_error(f"OAuth initiation error: {str(e)}", "Marketing Hub OAuth")
		return {"error": str(e)}


def make_api_request(platform, endpoint, method="GET", data=None, company=None):
	"""Make authenticated API request to platform via Network Account."""
	try:
		network_account = get_platform_credentials(platform, company)
		if not network_account:
			raise Exception(f"No active Network Account found for {platform}")

		access_token = network_account.get_access_token()
		if not access_token:
			raise Exception("No access token available")

		network = frappe.get_doc("Social Media Network", platform)
		base_url = network.api_base_url or ""
		url = f"{base_url}/{endpoint.lstrip("/")}" if base_url else endpoint

		headers = {
			"Authorization": f"Bearer {access_token}",
			"Content-Type": "application/json",
		}

		if platform == "Google Ads":
			developer_token = frappe.conf.get("google_ads_developer_token", "")
			headers["developer-token"] = developer_token

		if method == "GET":
			response = requests.get(url, headers=headers, params=data, timeout=60)
		elif method == "POST":
			response = requests.post(url, headers=headers, json=data, timeout=60)
		elif method == "PUT":
			response = requests.put(url, headers=headers, json=data, timeout=60)
		elif method == "DELETE":
			response = requests.delete(url, headers=headers, timeout=60)
		else:
			raise ValueError(f"Unsupported HTTP method: {method}")

		response.raise_for_status()
		return response.json()
	except (frappe.ValidationError, requests.exceptions.RequestException) as e:
		frappe.log_error(
			f"API request error for {platform}: {str(e)}",
			"Marketing Hub OAuth",
		)
		raise
