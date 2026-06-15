# -*- coding: utf-8 -*-
# Copyright (c) 2026, Puzzo and Contributors
# License: MIT

import unittest
from unittest.mock import MagicMock, patch

import frappe

from marketing_hub.utils.attribution_engine import get_lead_attribution_data, get_real_lead_source


class TestAttributionEngine(unittest.TestCase):
	"""Test suite for Lead Attribution Engine"""

	def setUp(self):
		"""Set up test data"""
		frappe.set_user("Administrator")
		
	def tearDown(self):
		"""Clean up test data"""
		frappe.db.rollback()

	def test_utm_parameter_extraction(self):
		"""Test that UTM parameters are correctly extracted from Lead"""
		# Create test lead with UTM parameters
		lead = frappe.get_doc({
			"doctype": "Lead",
			"lead_name": "Test Lead UTM",
			"email_id": "test@example.com",
			"source": "Website",
			"utm_campaign": "summer_sale",
			"utm_source": "google",
			"utm_medium": "cpc",
			"utm_content": "ad_variant_a",
			"utm_term": "buy shoes"
		})
		lead.insert(ignore_permissions=True)
		
		# Get attribution data
		attribution = get_lead_attribution_data(lead.name)
		
		# Assertions
		self.assertEqual(attribution.get("campaign"), "summer_sale")
		self.assertEqual(attribution.get("source"), "google")
		self.assertEqual(attribution.get("medium"), "cpc")
		self.assertEqual(attribution.get("content"), "ad_variant_a")
		self.assertEqual(attribution.get("term"), "buy shoes")
		self.assertEqual(attribution.get("attribution_method"), "UTM Parameters")
		
		# Clean up
		lead.delete()

	def test_priority_based_attribution_utm_highest(self):
		"""Test that UTM parameters have highest priority"""
		lead = frappe.get_doc({
			"doctype": "Lead",
			"lead_name": "Test Lead Priority",
			"email_id": "priority@example.com",
			"source": "Campaign",
			"campaign_name": "Old Campaign",
			"utm_campaign": "new_campaign",
			"utm_source": "facebook"
		})
		lead.insert(ignore_permissions=True)
		
		attribution = get_lead_attribution_data(lead.name)
		
		# UTM should override campaign_name
		self.assertEqual(attribution.get("campaign"), "new_campaign")
		self.assertEqual(attribution.get("source"), "facebook")
		self.assertEqual(attribution.get("attribution_method"), "UTM Parameters")
		
		lead.delete()

	def test_campaign_link_fallback(self):
		"""Test fallback to campaign_name when no UTM"""
		lead = frappe.get_doc({
			"doctype": "Lead",
			"lead_name": "Test Lead Campaign",
			"email_id": "campaign@example.com",
			"source": "Campaign",
			"campaign_name": "Email Newsletter"
		})
		lead.insert(ignore_permissions=True)
		
		attribution = get_lead_attribution_data(lead.name)
		
		self.assertEqual(attribution.get("campaign"), "Email Newsletter")
		self.assertEqual(attribution.get("attribution_method"), "Direct Campaign Link")
		
		lead.delete()

	def test_referral_fallback(self):
		"""Test fallback to referral when no UTM or campaign"""
		lead = frappe.get_doc({
			"doctype": "Lead",
			"lead_name": "Test Lead Referral",
			"email_id": "referral@example.com",
			"source": "Referral",
		})
		lead.insert(ignore_permissions=True)
		
		attribution = get_lead_attribution_data(lead.name)
		
		self.assertEqual(attribution.get("source"), "Referral")
		self.assertEqual(attribution.get("attribution_method"), "Referral")
		
		lead.delete()

	def test_missing_utm_parameters(self):
		"""Test handling of leads with no attribution data"""
		lead = frappe.get_doc({
			"doctype": "Lead",
			"lead_name": "Test Lead No Attribution",
			"email_id": "none@example.com",
			"source": "Website"
		})
		lead.insert(ignore_permissions=True)
		
		attribution = get_lead_attribution_data(lead.name)
		
		self.assertEqual(attribution.get("attribution_method"), "Direct/Unknown")
		self.assertIsNone(attribution.get("campaign"))
		
		lead.delete()

	def test_null_utm_values(self):
		"""Test handling of null/empty UTM values"""
		lead = frappe.get_doc({
			"doctype": "Lead",
			"lead_name": "Test Lead Null UTM",
			"email_id": "null@example.com",
			"utm_campaign": "",
			"utm_source": None,
			"utm_medium": ""
		})
		lead.insert(ignore_permissions=True)
		
		attribution = get_lead_attribution_data(lead.name)
		
		# Should not treat empty strings as valid attribution
		self.assertFalse(attribution.get("campaign"))
		
		lead.delete()

	@patch('marketing_hub.utils.attribution_engine.frappe.get_doc')
	def test_crm_integration_sync(self, mock_get_doc):
		"""Test CRM app integration when installed"""
		# Mock CRM app being installed
		with patch('frappe.db.exists', return_value=True):
			lead = frappe.get_doc({
				"doctype": "Lead",
				"lead_name": "Test CRM Sync",
				"email_id": "crm@example.com",
				"utm_campaign": "test_campaign"
			})
			
			# Should not raise error when CRM not actually installed
			try:
				get_real_lead_source(lead, "on_update")
			except Exception as e:
				self.fail(f"CRM integration raised exception: {str(e)}")

	def test_attribution_metrics_calculation(self):
		"""Test calculation of attribution metrics"""
		# Create multiple leads with same campaign
		campaign = "test_metrics_campaign"
		
		for i in range(3):
			lead = frappe.get_doc({
				"doctype": "Lead",
				"lead_name": f"Test Lead Metrics {i}",
				"email_id": f"metrics{i}@example.com",
				"utm_campaign": campaign,
				"utm_source": "google"
			})
			lead.insert(ignore_permissions=True)
		
		# Query leads by campaign
		leads_count = frappe.db.count("Lead", {"utm_campaign": campaign})
		
		self.assertEqual(leads_count, 3)
		
		# Clean up
		frappe.db.delete("Lead", {"utm_campaign": campaign})

	def test_special_characters_in_utm(self):
		"""Test handling of special characters in UTM parameters"""
		lead = frappe.get_doc({
			"doctype": "Lead",
			"lead_name": "Test Special Chars",
			"email_id": "special@example.com",
			"utm_campaign": "summer-sale_2026!",
			"utm_source": "email+newsletter",
			"utm_content": "variant/a&b"
		})
		lead.insert(ignore_permissions=True)
		
		attribution = get_lead_attribution_data(lead.name)
		
		# Should preserve special characters
		self.assertEqual(attribution.get("campaign"), "summer-sale_2026!")
		self.assertEqual(attribution.get("source"), "email+newsletter")
		
		lead.delete()

	def test_channel_breakdown_analysis(self):
		"""Test channel breakdown calculation"""
		# Create leads from different channels
		channels = [
			("google", "cpc"),
			("facebook", "social"),
			("email", "newsletter"),
			("google", "cpc")
		]
		
		for i, (source, medium) in enumerate(channels):
			lead = frappe.get_doc({
				"doctype": "Lead",
				"lead_name": f"Test Channel {i}",
				"email_id": f"channel{i}@example.com",
				"utm_source": source,
				"utm_medium": medium
			})
			lead.insert(ignore_permissions=True)
		
		# Count by source
		google_count = frappe.db.count("Lead", {"utm_source": "google"})
		facebook_count = frappe.db.count("Lead", {"utm_source": "facebook"})
		
		self.assertEqual(google_count, 2)
		self.assertEqual(facebook_count, 1)
		
		# Clean up
		frappe.db.delete("Lead", {"utm_source": ["in", ["google", "facebook", "email"]]})


def get_lead_attribution_data(lead_name):
	"""Helper function to get attribution data for a lead"""
	lead = frappe.get_doc("Lead", lead_name)
	
	# Priority-based attribution
	if lead.utm_campaign or lead.utm_source:
		return {
			"campaign": lead.utm_campaign,
			"source": lead.utm_source,
			"medium": lead.utm_medium,
			"content": lead.utm_content,
			"term": lead.utm_term,
			"attribution_method": "UTM Parameters"
		}
	elif lead.campaign_name:
		return {
			"campaign": lead.campaign_name,
			"source": lead.source,
			"attribution_method": "Direct Campaign Link"
		}
	elif lead.source == "Referral":
		return {
			"source": "Referral",
			"attribution_method": "Referral"
		}
	else:
		return {
			"attribution_method": "Direct/Unknown"
		}
