# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and Contributors
# License: MIT

import frappe
import unittest

class TestCampaignFlow(unittest.TestCase):
	"""Integration test for Campaign -> Blast -> Analytics flow"""

	def setUp(self):
		"""Set up test data"""
		frappe.set_user("Administrator")
		
		# Ensure we have a default Marketing Hub Settings configured
		if not frappe.db.exists("Marketing Hub Settings", "Marketing Hub Settings"):
			settings = frappe.new_doc("Marketing Hub Settings")
			settings.enable_gl_entry = 0
			settings.insert(ignore_permissions=True)
			
		# Create test segment
		if frappe.db.exists("Marketing Segment", "Integration Test Segment"):
			frappe.delete_doc("Marketing Segment", "Integration Test Segment", ignore_permissions=True, force=True)
		self.segment = frappe.get_doc({
			"doctype": "Marketing Segment",
			"segment_name": "Integration Test Segment",
		})
		self.segment.insert(ignore_permissions=True)

		# Create test campaign
		if frappe.db.exists("Marketing Campaign", "Integration Test Campaign"):
			frappe.delete_doc("Marketing Campaign", "Integration Test Campaign", ignore_permissions=True, force=True)
		self.campaign = frappe.get_doc({
			"doctype": "Marketing Campaign",
			"campaign_name": "Integration Test Campaign",
			"description": "Integration test campaign",
			"status": "Active"
		})
		self.campaign.insert(ignore_permissions=True)
		
		# Create a Network
		if not frappe.db.exists("Social Media Network", "Meta Ads"):
			self.network = frappe.get_doc({
				"doctype": "Social Media Network",
				"network_name": "Meta Ads",
				"network_code": "meta_ads_test",
				"network_type": "Social Media",
				"is_active": 1
			})
			self.network.insert(ignore_permissions=True)

		# Create Blast Type
		if not frappe.db.exists("Blast Type", "Immediate"):
			frappe.get_doc({
				"doctype": "Blast Type",
				"blast_type": "Immediate"
			}).insert(ignore_permissions=True)

	def tearDown(self):
		"""Clean up test data"""
		frappe.db.rollback()

	def test_campaign_to_blast_to_analytics(self):
		"""Test the full flow from Campaign creation to Analytics logging"""
		
		# 1. Create Omni Blast linked to campaign
		blast = frappe.get_doc({
			"doctype": "Omni Blast",
			"blast_title": "Test Integration Blast",
			"campaign": self.campaign.name,
			"blast_type": "Immediate",
			"content": "Test integration content",
			"status": "Draft",
		})
		blast.append("networks", {"social_media_network": "Meta Ads"})
		blast.insert(ignore_permissions=True)
		
		# Generate posts
		blast.generate_posts()
		
		# Verify Social Post was created
		posts = frappe.get_all("Social Post", filters={"omni_blast": blast.name, "campaign": self.campaign.name})
		self.assertGreaterEqual(len(posts), 1, "Social post should be created for the blast")
		
		# Create test ad account
		ad_account = frappe.get_doc({
			"doctype": "Ad Account",
			"account_name": "Test Ad Account",
			"social_media_network": "Meta Ads",
			"account_id": "test-123",
			"is_active": 1
		})
		ad_account.insert(ignore_permissions=True)

		# Create test connector
		connector = frappe.get_doc({
			"doctype": "Analytics Connector",
			"connector_name": "Test Connector",
			"platform": "Meta Ads",
			"ad_account": ad_account.name
		})
		connector.insert(ignore_permissions=True)

		# 2. Simulate Analytics Sync for the campaign
		log = frappe.get_doc({
			"doctype": "Analytics Daily Log",
			"log_date": frappe.utils.today(),
			"campaign": self.campaign.name,
			"channel": "Meta Ads",
			"connector": connector.name,
			"ad_account": ad_account.name,
			"impressions": 1000,
			"clicks": 50,
			"spend": 100,
			"revenue": 500,
			"conversions": 5
		})
		log.insert(ignore_permissions=True)
		
		# Verify log calculation
		self.assertEqual(log.roas, 5.0)
		
		# 3. Verify Campaign shows linked Analytics
		logs_for_campaign = frappe.get_all("Analytics Daily Log", filters={"campaign": self.campaign.name})
		self.assertEqual(len(logs_for_campaign), 1, "Analytics Log should be linked to the campaign")
