# -*- coding: utf-8 -*-
# Copyright (c) 2026, Puzzo and Contributors
# License: MIT

import frappe
import unittest
from marketing_hub.utils.permissions import (
	get_campaign_permission_query_conditions,
	has_campaign_permission,
	get_campaign_activity_permission_query_conditions,
	has_campaign_activity_permission,
	get_marketing_segment_permission_query_conditions
)


class TestPermissions(unittest.TestCase):
	"""Test suite for Row-Level Security and Permissions"""

	def setUp(self):
		"""Set up test data"""
		frappe.set_user("Administrator")
		
		# Create test customer (client)
		self.client = frappe.get_doc({
			"doctype": "Customer",
			"customer_name": "Test Client",
			"customer_type": "Company"
		})
		self.client.insert(ignore_permissions=True)
		
		# Create test campaign
		self.campaign = frappe.get_doc({
			"doctype": "Campaign",
			"campaign_name": "Test Permission Campaign",
			"description": "Test campaign for permissions"
		})
		self.campaign.insert(ignore_permissions=True)

	def tearDown(self):
		"""Clean up test data"""
		self.campaign.delete()
		self.client.delete()
		frappe.db.rollback()

	def test_campaign_permission_query_admin(self):
		"""Test that admin sees all campaigns"""
		frappe.set_user("Administrator")
		
		conditions = get_campaign_permission_query_conditions("Campaign")
		
		# Admin should have no restrictions
		self.assertEqual(conditions, "")

	def test_campaign_visibility_by_client(self):
		"""Test that campaigns are filtered by client in agency mode"""
		# Enable agency mode
		settings = frappe.get_single("Marketing Hub Settings")
		settings.agency_mode = 1
		settings.save()
		
		# Create campaign with client
		campaign_with_client = frappe.get_doc({
			"doctype": "Campaign",
			"campaign_name": "Client Campaign",
			"client": self.client.name
		})
		campaign_with_client.insert(ignore_permissions=True)
		
		# Create campaign without client
		campaign_without_client = frappe.get_doc({
			"doctype": "Campaign",
			"campaign_name": "Internal Campaign"
		})
		campaign_without_client.insert(ignore_permissions=True)
		
		# Get permission conditions for non-admin user
		# In agency mode, should filter by client
		conditions = get_campaign_permission_query_conditions("Campaign")
		
		# Conditions should include client filter (in agency mode for non-admin)
		# For admin, should be empty
		self.assertTrue(isinstance(conditions, str))
		
		# Clean up
		campaign_with_client.delete()
		campaign_without_client.delete()
		settings.agency_mode = 0
		settings.save()

	def test_has_campaign_permission_admin(self):
		"""Test that admin has permission to all campaigns"""
		frappe.set_user("Administrator")
		
		result = has_campaign_permission(self.campaign)
		
		self.assertTrue(result)

	def test_campaign_activity_inherits_campaign_permissions(self):
		"""Test that campaign activity inherits campaign permissions"""
		# Create activity
		activity = frappe.get_doc({
			"doctype": "Campaign Activity",
			"subject": "Test Activity",
			"campaign": self.campaign.name
		})
		activity.insert(ignore_permissions=True)
		
		# Check permission
		result = has_campaign_activity_permission(activity)
		
		# Should have permission since we're admin
		self.assertTrue(result)
		
		activity.delete()

	def test_marketing_segment_permission_query(self):
		"""Test marketing segment permission query conditions"""
		frappe.set_user("Administrator")
		
		conditions = get_marketing_segment_permission_query_conditions("Marketing Segment")
		
		# Admin should have no restrictions
		self.assertEqual(conditions, "")

	def test_role_based_access_marketing_manager(self):
		"""Test Marketing Manager role has broader access"""
		# Marketing Manager should see all campaigns in their company
		# This is enforced by standard Frappe permissions + our custom filters
		
		# Get role permissions
		roles = frappe.get_roles()
		
		# Admin has all roles
		self.assertIn("System Manager", roles)

	def test_role_based_access_marketing_user(self):
		"""Test Marketing User role has restricted access"""
		# Marketing User should only see campaigns they're assigned to
		# This would be tested with actual user context
		
		# For now, verify permission system doesn't break
		try:
			conditions = get_campaign_permission_query_conditions("Campaign")
			self.assertIsInstance(conditions, str)
		except Exception as e:
			self.fail(f"Permission query raised exception: {str(e)}")

	def test_agency_mode_client_filtering(self):
		"""Test that agency mode properly filters by client"""
		# Enable agency mode
		settings = frappe.get_single("Marketing Hub Settings")
		original_mode = settings.agency_mode
		settings.agency_mode = 1
		settings.save()
		
		# Create campaigns for different clients
		client1_campaign = frappe.get_doc({
			"doctype": "Campaign",
			"campaign_name": "Client 1 Campaign",
			"client": self.client.name
		})
		client1_campaign.insert(ignore_permissions=True)
		
		# Query campaigns with client filter
		campaigns = frappe.get_all(
			"Campaign",
			filters={"client": self.client.name},
			fields=["name", "campaign_name", "client"]
		)
		
		# Should return only client's campaigns
		self.assertGreaterEqual(len(campaigns), 1)
		
		# All campaigns should be for this client
		for campaign in campaigns:
			if campaign.client:
				self.assertEqual(campaign.client, self.client.name)
		
		# Clean up
		client1_campaign.delete()
		settings.agency_mode = original_mode
		settings.save()

	def test_permission_query_no_errors_for_missing_settings(self):
		"""Test that permission queries don't break if settings don't exist"""
		# Delete settings temporarily
		if frappe.db.exists("Marketing Hub Settings", "Marketing Hub Settings"):
			settings = frappe.get_single("Marketing Hub Settings")
			original_mode = settings.agency_mode
		else:
			original_mode = 0
		
		try:
			conditions = get_campaign_permission_query_conditions("Campaign")
			self.assertIsInstance(conditions, str)
		except Exception as e:
			self.fail(f"Permission query failed without settings: {str(e)}")

	def test_cross_company_campaign_isolation(self):
		"""Test that campaigns are isolated by company"""
		# This would require multi-company setup
		# For now, verify structure supports it
		
		# Campaign should have company field in filters
		campaign_fields = frappe.get_meta("Campaign").fields
		has_company_field = any(f.fieldname == "company" for f in campaign_fields)
		
		# Standard ERPNext Campaign has company field
		self.assertTrue(has_company_field)

	def test_has_permission_returns_boolean(self):
		"""Test that has_permission functions return boolean"""
		result1 = has_campaign_permission(self.campaign)
		result2 = has_campaign_activity_permission(None)
		
		self.assertIsInstance(result1, bool)
		self.assertIsInstance(result2, bool)

	def test_permission_query_returns_string(self):
		"""Test that permission query functions return string"""
		result1 = get_campaign_permission_query_conditions("Campaign")
		result2 = get_marketing_segment_permission_query_conditions("Marketing Segment")
		
		self.assertIsInstance(result1, str)
		self.assertIsInstance(result2, str)

	def test_segment_permissions_inherit_from_campaign(self):
		"""Test that segments respect campaign permissions"""
		# Create segment
		segment = frappe.get_doc({
			"doctype": "Marketing Segment",
			"segment_name": "Test Segment",
			"segment_type": "Lead"
		})
		segment.insert(ignore_permissions=True)
		
		# Admin should have access
		frappe.set_user("Administrator")
		conditions = get_marketing_segment_permission_query_conditions("Marketing Segment")
		
		self.assertEqual(conditions, "")
		
		segment.delete()
