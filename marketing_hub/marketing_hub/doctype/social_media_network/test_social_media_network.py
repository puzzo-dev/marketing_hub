# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and Contributors
# See license.txt

import unittest

import frappe


class TestSocialMediaNetwork(unittest.TestCase):
	def test_network_creation(self):
		"""Test creating a social media network"""
		network = frappe.get_doc({
			"doctype": "Social Media Network",
			"network_name": "Test Network",
			"network_code": "test",
			"network_type": "Social Media",
			"is_active": 1
		})
		network.insert()
		self.assertTrue(network.name)
		network.delete()
