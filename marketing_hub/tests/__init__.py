# -*- coding: utf-8 -*-
# Copyright (c) 2026, Puzzo and Contributors
# License: MIT

"""
Test runner configuration for Marketing Hub
"""

import frappe


def run_tests():
	"""Run all Marketing Hub tests"""
	frappe.init(site="erpnext.local")
	frappe.connect()
	
	# Run tests
	import unittest

	from marketing_hub.tests import (
		test_analytics_sync,
		test_attribution_engine,
		test_content_orchestration,
		test_permissions,
	)
	
	loader = unittest.TestLoader()
	suite = unittest.TestSuite()
	
	# Add test modules
	suite.addTests(loader.loadTestsFromModule(test_attribution_engine))
	suite.addTests(loader.loadTestsFromModule(test_content_orchestration))
	suite.addTests(loader.loadTestsFromModule(test_permissions))
	suite.addTests(loader.loadTestsFromModule(test_analytics_sync))
	
	runner = unittest.TextTestRunner(verbosity=2)
	result = runner.run(suite)
	
	return result
