# -*- coding: utf-8 -*-
"""
Hooks for Frappe OAuth / Connected App integration.
Auto-creates Network Account and fetches ad accounts on successful token exchange.
"""

import frappe
from frappe import _
import requests


def on_token_cache_update(doc, method):
	"""Triggered when Token Cache is updated (e.g., after OAuth callback).
	Creates Network Account and fetches platform ad accounts."""
	if not doc.access_token or not doc.connected_app:
		return

	connected_app = frappe.get_doc("Connected App", doc.connected_app)
	platform = connected_app.provider_name

	# Find Social Media Network linked to this Connected App
	networks = frappe.get_all(
		"Social Media Network",
		filters={"connected_app": doc.connected_app, "is_active": 1},
		fields=["name", "network_name", "api_base_url"],
		limit=1,
	)

	if not networks:
		frappe.log_error(
			f"No active Social Media Network linked to Connected App {doc.connected_app}",
			"Marketing Hub OAuth Hook",
		)
		return

	network = networks[0]

	# Create or update Network Account
	existing = frappe.get_all(
		"Network Account",
		filters={"connected_app": doc.connected_app, "user": doc.user},
		fields=["name"],
		limit=1,
	)

	if existing:
		network_account = frappe.get_doc("Network Account", existing[0].name)
		network_account.sync_status = "Success"
		network_account.last_sync = frappe.utils.now_datetime()
		network_account.save()
	else:
		network_account = frappe.new_doc("Network Account")
		network_account.account_name = f"{platform} - {doc.user}"
		network_account.social_media_network = network.name
		network_account.platform = network.network_name
		network_account.connected_app = doc.connected_app
		network_account.user = doc.user
		network_account.is_active = 1
		network_account.sync_status = "Success"
		network_account.last_sync = frappe.utils.now_datetime()
		network_account.insert()

	frappe.db.commit()

	# Fetch ad accounts from platform
	_fetch_ad_accounts(network_account, network, connected_app, doc)


def _fetch_ad_accounts(network_account, network, connected_app, token_cache):
	"""Fetch ad accounts from platform and create Ad Account records."""
	platform = network.network_name
	base_url = network.api_base_url or ""
	access_token = token_cache.get_password("access_token")

	if not access_token:
		return

	try:
		if platform == "Meta Ads" or platform == "Facebook" or platform == "Instagram":
			_fetch_meta_ad_accounts(network_account, network, base_url, access_token)
		elif platform == "Google Ads":
			_fetch_google_ad_accounts(network_account, network, base_url, access_token)
		elif platform == "LinkedIn Ads":
			_fetch_linkedin_ad_accounts(network_account, network, base_url, access_token)
	except Exception as e:
		frappe.log_error(
			f"Failed to fetch ad accounts for {platform}: {str(e)}",
			"Marketing Hub OAuth Hook",
		)
		network_account.sync_status = "Failed"
		network_account.error_log = str(e)
		network_account.save()
		frappe.db.commit()


def _fetch_meta_ad_accounts(network_account, network, base_url, access_token):
	"""Fetch Meta ad accounts via Graph API."""
	url = f"{base_url or 'https://graph.facebook.com/v18.0'}/me/adaccounts"
	params = {
		"access_token": access_token,
		"fields": "account_id,name,account_status,business_name",
	}
	response = requests.get(url, params=params, timeout=30)
	response.raise_for_status()
	data = response.json()

	for account in data.get("data", []):
		ad_account_id = account.get("account_id")
		if not ad_account_id:
			continue

		existing = frappe.get_all(
			"Ad Account",
			filters={
				"network_account": network_account.name,
				"ad_account_id": f"act_{ad_account_id}",
			},
			fields=["name"],
			limit=1,
		)

		if not existing:
			doc = frappe.new_doc("Ad Account")
			doc.account_name = account.get("name") or f"Meta Ad Account {ad_account_id}"
			doc.social_media_network = network.name
			doc.platform = network.network_name
			doc.network_account = network_account.name
			doc.ad_account_id = f"act_{ad_account_id}"
			doc.is_active = 1
			doc.insert()

	frappe.db.commit()


def _fetch_google_ad_accounts(network_account, network, base_url, access_token):
	"""Fetch Google Ads accessible customers."""
	url = "https://googleads.googleapis.com/v14/customers:listAccessibleCustomers"
	headers = {"Authorization": f"Bearer {access_token}"}
	response = requests.get(url, headers=headers, timeout=30)
	response.raise_for_status()
	data = response.json()

	for customer_id in data.get("resourceNames", []):
		cid = customer_id.replace("customers/", "")
		existing = frappe.get_all(
			"Ad Account",
			filters={
				"network_account": network_account.name,
				"customer_id": cid,
			},
			fields=["name"],
			limit=1,
		)

		if not existing:
			doc = frappe.new_doc("Ad Account")
			doc.account_name = f"Google Ads Customer {cid}"
			doc.social_media_network = network.name
			doc.platform = network.network_name
			doc.network_account = network_account.name
			doc.customer_id = cid
			doc.is_active = 1
			doc.insert()

	frappe.db.commit()


def _fetch_linkedin_ad_accounts(network_account, network, base_url, access_token):
	"""Fetch LinkedIn ad accounts."""
	url = f"{base_url or 'https://api.linkedin.com/v2'}/adAccountsV2"
	headers = {"Authorization": f"Bearer {access_token}", "X-Restli-Protocol-Version": "2.0.0"}
	params = {"q": "search", "start": 0, "count": 100}
	response = requests.get(url, headers=headers, params=params, timeout=30)
	response.raise_for_status()
	data = response.json()

	for account in data.get("elements", []):
		account_urn = account.get("id")
		if not account_urn:
			continue

		existing = frappe.get_all(
			"Ad Account",
			filters={
				"network_account": network_account.name,
				"account_urn": account_urn,
			},
			fields=["name"],
			limit=1,
		)

		if not existing:
			doc = frappe.new_doc("Ad Account")
			doc.account_name = account.get("name") or f"LinkedIn Ad Account {account_urn}"
			doc.social_media_network = network.name
			doc.platform = network.network_name
			doc.network_account = network_account.name
			doc.account_urn = account_urn
			doc.is_active = 1
			doc.insert()

	frappe.db.commit()
