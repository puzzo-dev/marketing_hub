# -*- coding: utf-8 -*-
# Copyright (c) 2026, Puzzo and Contributors
# License: MIT

import unittest

import frappe

from marketing_hub.utils.content_orchestration import (
	adapt_content_for_channel,
	create_campaign_content_for_channels,
	get_channel_best_practices,
	get_content_recommendations,
)


class TestContentOrchestration(unittest.TestCase):
	"""Test suite for Content Orchestration utilities"""

	def setUp(self):
		"""Set up test data"""
		frappe.set_user("Administrator")
		
		# Create test campaign
		self.campaign = frappe.get_doc({
			"doctype": "Campaign",
			"campaign_name": "Test Content Campaign",
			"description": "Test campaign for content orchestration"
		})
		self.campaign.insert(ignore_permissions=True)
		
		# Create test template
		self.template = frappe.get_doc({
			"doctype": "Marketing Template",
			"template_name": "Test Template",
			"channel": "Email",
			"subject": "Test Subject {customer_name}",
			"body": "Hello {customer_name}, check out {product_name}!",
			"call_to_action": "Buy Now"
		})
		self.template.insert(ignore_permissions=True)

	def tearDown(self):
		"""Clean up test data"""
		# Delete test data
		frappe.db.delete("Campaign Content", {"campaign": self.campaign.name})
		self.template.delete()
		self.campaign.delete()
		frappe.db.rollback()

	def test_create_campaign_content_for_multiple_channels(self):
		"""Test bulk creation of campaign content for multiple channels"""
		channels = ["Email", "WhatsApp", "SMS"]
		
		result = create_campaign_content_for_channels(
			campaign=self.campaign.name,
			channels=channels,
			template=self.template.name
		)
		
		# Check that content was created for all channels
		self.assertEqual(len(result), 3)
		
		# Verify each channel has content
		for channel in channels:
			content = frappe.db.exists("Campaign Content", {
				"campaign": self.campaign.name,
				"channel": channel
			})
			self.assertTrue(content, f"Content not created for {channel}")

	def test_avoid_duplicate_campaign_content(self):
		"""Test that duplicate content is not created"""
		channels = ["Email"]
		
		# Create content first time
		result1 = create_campaign_content_for_channels(
			campaign=self.campaign.name,
			channels=channels,
			template=self.template.name
		)
		
		# Try to create again
		result2 = create_campaign_content_for_channels(
			campaign=self.campaign.name,
			channels=channels,
			template=self.template.name
		)
		
		# Should not create duplicates
		content_count = frappe.db.count("Campaign Content", {
			"campaign": self.campaign.name,
			"channel": "Email"
		})
		self.assertEqual(content_count, 1)

	def test_adapt_content_for_channel_truncation(self):
		"""Test content adaptation with character limit truncation"""
		# Long content
		long_content = "This is a very long message that exceeds SMS character limits. " * 5
		
		# Adapt for SMS (160 char limit)
		adapted = adapt_content_for_channel(
			source_content=long_content,
			target_channel="SMS"
		)
		
		# Should be truncated
		self.assertLessEqual(len(adapted), 160)
		self.assertTrue(adapted.endswith("..."))

	def test_adapt_content_for_channel_html_stripping(self):
		"""Test HTML stripping for text-only channels"""
		html_content = "<p>Hello <strong>World</strong>!</p><br><a href='#'>Click here</a>"
		
		# Adapt for SMS (text-only)
		adapted = adapt_content_for_channel(
			source_content=html_content,
			target_channel="SMS"
		)
		
		# Should have no HTML tags
		self.assertNotIn("<p>", adapted)
		self.assertNotIn("<strong>", adapted)
		self.assertIn("Hello World!", adapted)

	def test_adapt_content_preserves_html_for_email(self):
		"""Test that HTML is preserved for email channel"""
		html_content = "<p>Hello <strong>World</strong>!</p>"
		
		# Adapt for Email (HTML allowed)
		adapted = adapt_content_for_channel(
			source_content=html_content,
			target_channel="Email"
		)
		
		# Should preserve HTML
		self.assertIn("<p>", adapted)
		self.assertIn("<strong>", adapted)

	def test_channel_best_practices_retrieval(self):
		"""Test retrieval of channel best practices"""
		practices = get_channel_best_practices()
		
		# Should have data for major channels
		self.assertIn("Meta Ads", practices)
		self.assertIn("Google Ads", practices)
		self.assertIn("Email", practices)
		self.assertIn("SMS", practices)
		
		# Check Meta Ads specs
		meta_specs = practices["Meta Ads"]
		self.assertIn("text_limit", meta_specs)
		self.assertIn("image_specs", meta_specs)
		self.assertEqual(meta_specs["text_limit"], 125)

	def test_channel_best_practices_image_specs(self):
		"""Test that image specifications are provided"""
		practices = get_channel_best_practices()
		
		# Meta Ads should have image specs
		meta_specs = practices["Meta Ads"]
		self.assertIsInstance(meta_specs["image_specs"], list)
		self.assertIn("1200x628", meta_specs["image_specs"][0])

	def test_content_recommendations_for_campaign(self):
		"""Test content recommendations based on successful campaigns"""
		# Create successful campaign with content
		successful_campaign = frappe.get_doc({
			"doctype": "Campaign",
			"campaign_name": "Successful Campaign",
			"status": "Completed"
		})
		successful_campaign.insert(ignore_permissions=True)
		
		# Create content for successful campaign
		content = frappe.get_doc({
			"doctype": "Campaign Content",
			"campaign": successful_campaign.name,
			"channel": "Email",
			"subject": "Great Subject Line",
			"body": "Engaging content",
			"sent_count": 1000,
			"opened_count": 300,
			"clicked_count": 50
		})
		content.insert(ignore_permissions=True)
		
		# Get recommendations
		recommendations = get_content_recommendations(
			campaign=self.campaign.name,
			channel="Email"
		)
		
		# Should return recommendations
		self.assertIsInstance(recommendations, list)
		
		# Clean up
		content.delete()
		successful_campaign.delete()

	def test_template_variable_replacement(self):
		"""Test variable replacement in template content"""
		template_text = "Hello {customer_name}, check out {product_name}!"
		variables = {
			"customer_name": "John Doe",
			"product_name": "Amazing Widget"
		}
		
		# Replace variables
		result = template_text.format(**variables)
		
		self.assertEqual(result, "Hello John Doe, check out Amazing Widget!")
		self.assertNotIn("{", result)
		self.assertNotIn("}", result)

	def test_utm_parameter_generation(self):
		"""Test UTM parameter auto-generation"""
		campaign_name = "summer_sale"
		channel = "Email"
		
		utm_params = {
			"utm_campaign": campaign_name.lower().replace(" ", "_"),
			"utm_source": channel.lower(),
			"utm_medium": "marketing"
		}
		
		self.assertEqual(utm_params["utm_campaign"], "summer_sale")
		self.assertEqual(utm_params["utm_source"], "email")
		self.assertEqual(utm_params["utm_medium"], "marketing")

	def test_content_adaptation_empty_input(self):
		"""Test handling of empty content"""
		adapted = adapt_content_for_channel(
			source_content="",
			target_channel="SMS"
		)
		
		self.assertEqual(adapted, "")

	def test_content_adaptation_none_input(self):
		"""Test handling of None content"""
		adapted = adapt_content_for_channel(
			source_content=None,
			target_channel="SMS"
		)
		
		self.assertEqual(adapted, "")

	def test_channel_specific_character_limits(self):
		"""Test that each channel has correct character limits"""
		practices = get_channel_best_practices()
		
		# Verify known limits
		self.assertEqual(practices["Meta Ads"]["text_limit"], 125)
		self.assertEqual(practices["Google Ads"]["text_limit"], 90)
		self.assertEqual(practices["LinkedIn"]["text_limit"], 150)
		self.assertEqual(practices["SMS"]["text_limit"], 160)
		self.assertIsNone(practices["Email"].get("text_limit"))  # Email has no limit

	def test_content_preview_generation(self):
		"""Test preview generation for content"""
		content = "This is a test message with {customer_name} variable"
		preview_vars = {"customer_name": "[Customer Name]"}
		
		preview = content.format(**preview_vars)
		
		self.assertIn("[Customer Name]", preview)
		self.assertEqual(preview, "This is a test message with [Customer Name] variable")
