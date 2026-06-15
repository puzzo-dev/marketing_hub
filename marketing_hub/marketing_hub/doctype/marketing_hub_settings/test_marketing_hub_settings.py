# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and Contributors
# See license.txt

import unittest

import frappe


class TestMarketingHubSettings(unittest.TestCase):
	def setUp(self):
		"""Setup test data"""
		self.company = "_Test Company"

		# Clean up any existing settings
		if frappe.db.exists("Marketing Hub Settings", {"company": self.company}):
			frappe.delete_doc("Marketing Hub Settings", {"company": self.company})

	def test_create_settings(self):
		"""Test creating settings"""
		settings = frappe.new_doc("Marketing Hub Settings")
		settings.company = self.company
		settings.agency_mode = 0
		settings.enable_auto_attribution = 1
		settings.insert()

		self.assertTrue(frappe.db.exists("Marketing Hub Settings", {"company": self.company}))

	def test_session_timeout_validation(self):
		"""Test session timeout validation"""
		settings = frappe.new_doc("Marketing Hub Settings")
		settings.company = self.company
		settings.session_timeout_days = 0

		with self.assertRaises(frappe.ValidationError):
			settings.insert()

	def test_auto_post_interval_validation(self):
		"""Test auto post interval validation"""
		settings = frappe.new_doc("Marketing Hub Settings")
		settings.company = self.company
		settings.auto_post_interval_minutes = 2

		with self.assertRaises(frappe.ValidationError):
			settings.insert()

	def tearDown(self):
		"""Clean up test data"""
		if frappe.db.exists("Marketing Hub Settings", {"company": self.company}):
			frappe.delete_doc("Marketing Hub Settings", {"company": self.company})
