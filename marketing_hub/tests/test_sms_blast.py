# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and Contributors
# License: MIT

import unittest
from unittest.mock import MagicMock, patch

import frappe

from marketing_hub.utils.omni_blast import _execute_sms_blast


class TestSMSBlast(unittest.TestCase):
	"""Test suite for SMS Blast functionality"""

	def setUp(self):
		"""Set up test data"""
		frappe.set_user("Administrator")
		
		# Create test campaign
		self.campaign = frappe.get_doc({
			"doctype": "Campaign",
			"campaign_name": "Test SMS Campaign",
			"description": "Test campaign for SMS blasts"
		})
		self.campaign.insert(ignore_permissions=True)
		
		# Create test segment with contacts
		self.segment = frappe.get_doc({
			"doctype": "Marketing Segment",
			"segment_name": "Test SMS Segment",
			"filter_json": frappe.as_json({"doctype": "Lead", "status": "Open"})
		})
		self.segment.insert(ignore_permissions=True)
		
		# Create test contacts with mobile numbers
		self.contacts = []
		for i in range(3):
			contact = frappe.get_doc({
				"doctype": "Contact",
				"first_name": f"Test Contact {i}",
				"mobile_no": f"+1234567890{i}"
			})
			contact.insert(ignore_permissions=True)
			self.contacts.append(contact)
		
		# Create test campaign activity
		self.activity = frappe.get_doc({
			"doctype": "Campaign Activity",
			"campaign": self.campaign.name,
			"activity_name": "Test SMS Activity",
			"activity_type": "SMS",
			"segment": self.segment.name,
			"message": "Test SMS message for blast",
			"status": "Scheduled"
		})
		self.activity.insert(ignore_permissions=True)

	def tearDown(self):
		"""Clean up test data"""
		# Delete test data in reverse order
		self.activity.delete()
		for contact in self.contacts:
			contact.delete()
		self.segment.delete()
		self.campaign.delete()
		frappe.db.rollback()

	@patch('frappe.db.get_single_value')
	def test_sms_blast_no_gateway_configured(self, mock_get_single_value):
		"""Test SMS blast when no gateway is configured"""
		mock_get_single_value.return_value = None
		
		result = _execute_sms_blast(self.activity)
		
		self.assertEqual(result["status"], "Error")
		self.assertIn("SMS gateway not configured", result["message"])
		self.assertEqual(result["count"], 0)

	def test_sms_blast_no_segment(self):
		"""Test SMS blast with no segment defined"""
		# Clear segment
		self.activity.segment = None
		
		result = _execute_sms_blast(self.activity)
		
		self.assertEqual(result["status"], "Error")
		self.assertIn("No segment defined", result["message"])

	def test_sms_blast_no_message(self):
		"""Test SMS blast with no message content"""
		# Clear message
		self.activity.message = None
		self.activity.content_html = None
		
		with patch('frappe.db.get_single_value') as mock_gateway:
			mock_gateway.return_value = "http://sms-gateway.com/api"
			
			with patch('marketing_hub.utils.omni_blast._get_segment_recipients') as mock_recipients:
				mock_recipients.return_value = [{"mobile_no": "+1234567890"}]
				
				result = _execute_sms_blast(self.activity)
				
				self.assertEqual(result["status"], "Error")
				self.assertIn("No message content", result["message"])

	@patch('frappe.db.get_single_value')
	@patch('marketing_hub.utils.omni_blast._get_segment_recipients')
	def test_sms_blast_no_recipients(self, mock_recipients, mock_gateway):
		"""Test SMS blast with no recipients in segment"""
		mock_gateway.return_value = "http://sms-gateway.com/api"
		mock_recipients.return_value = []
		
		result = _execute_sms_blast(self.activity)
		
		self.assertEqual(result["status"], "Error")
		self.assertIn("No recipients found", result["message"])

	@patch('frappe.db.get_single_value')
	@patch('marketing_hub.utils.omni_blast._get_segment_recipients')
	def test_sms_blast_no_mobile_numbers(self, mock_recipients, mock_gateway):
		"""Test SMS blast when recipients have no mobile numbers"""
		mock_gateway.return_value = "http://sms-gateway.com/api"
		mock_recipients.return_value = [
			{"email": "test@example.com"},  # No mobile
			{"name": "Test"}  # No mobile
		]
		
		result = _execute_sms_blast(self.activity)
		
		self.assertEqual(result["status"], "Error")
		self.assertIn("No valid mobile numbers", result["message"])

	@patch('frappe.db.get_single_value')
	@patch('marketing_hub.utils.omni_blast._get_segment_recipients')
	@patch('frappe.core.doctype.sms_settings.sms_settings.send_sms')
	def test_sms_blast_success(self, mock_send_sms, mock_recipients, mock_gateway):
		"""Test successful SMS blast execution"""
		mock_gateway.return_value = "http://sms-gateway.com/api"
		mock_recipients.return_value = [
			{"mobile_no": "+1234567890"},
			{"phone": "+0987654321"},
			{"mobile_no": "+1122334455"}
		]
		mock_send_sms.return_value = None  # Success
		
		result = _execute_sms_blast(self.activity)
		
		self.assertEqual(result["status"], "Success")
		self.assertEqual(result["count"], 3)
		self.assertEqual(result["channel"], "SMS")
		
		# Verify send_sms was called with correct parameters
		mock_send_sms.assert_called_once()
		call_args = mock_send_sms.call_args
		self.assertEqual(len(call_args[0][0]), 3)  # 3 mobile numbers
		self.assertIn("Test SMS message", call_args[0][1])  # Message content

	@patch('frappe.db.get_single_value')
	@patch('marketing_hub.utils.omni_blast._get_segment_recipients')
	@patch('frappe.core.doctype.sms_settings.sms_settings.send_sms')
	def test_sms_blast_truncates_long_message(self, mock_send_sms, mock_recipients, mock_gateway):
		"""Test that long messages are truncated to 160 characters"""
		mock_gateway.return_value = "http://sms-gateway.com/api"
		mock_recipients.return_value = [{"mobile_no": "+1234567890"}]
		
		# Set a very long message
		long_message = "This is a very long SMS message that exceeds 160 characters. " * 5
		self.activity.message = long_message
		
		result = _execute_sms_blast(self.activity)
		
		# Check that message was truncated
		call_args = mock_send_sms.call_args
		sent_message = call_args[0][1]
		self.assertLessEqual(len(sent_message), 160)
		self.assertTrue(sent_message.endswith("..."))

	@patch('frappe.db.get_single_value')
	@patch('marketing_hub.utils.omni_blast._get_segment_recipients')
	@patch('frappe.core.doctype.sms_settings.sms_settings.send_sms')
	def test_sms_blast_strips_html(self, mock_send_sms, mock_recipients, mock_gateway):
		"""Test that HTML tags are stripped from SMS content"""
		mock_gateway.return_value = "http://sms-gateway.com/api"
		mock_recipients.return_value = [{"mobile_no": "+1234567890"}]
		
		# Set HTML message
		html_message = "<h1>Hello</h1><p>This is a <strong>test</strong> message.</p>"
		self.activity.message = html_message
		
		result = _execute_sms_blast(self.activity)
		
		# Check that HTML was stripped
		call_args = mock_send_sms.call_args
		sent_message = call_args[0][1]
		self.assertNotIn("<", sent_message)
		self.assertNotIn(">", sent_message)
		self.assertIn("Hello", sent_message)
		self.assertIn("test", sent_message)

	@patch('frappe.db.get_single_value')
	@patch('marketing_hub.utils.omni_blast._get_segment_recipients')
	@patch('frappe.core.doctype.sms_settings.sms_settings.send_sms')
	def test_sms_blast_handles_gateway_error(self, mock_send_sms, mock_recipients, mock_gateway):
		"""Test SMS blast handles gateway errors gracefully"""
		mock_gateway.return_value = "http://sms-gateway.com/api"
		mock_recipients.return_value = [{"mobile_no": "+1234567890"}]
		mock_send_sms.side_effect = Exception("Gateway connection failed")
		
		result = _execute_sms_blast(self.activity)
		
		self.assertEqual(result["status"], "Error")
		self.assertIn("SMS sending failed", result["message"])
		self.assertIn("Gateway connection failed", result["message"])

	@patch('frappe.db.get_single_value')
	@patch('marketing_hub.utils.omni_blast._get_segment_recipients')
	@patch('frappe.core.doctype.sms_settings.sms_settings.send_sms')
	def test_sms_blast_collects_mobile_from_both_fields(self, mock_send_sms, mock_recipients, mock_gateway):
		"""Test that mobile numbers are collected from both mobile_no and phone fields"""
		mock_gateway.return_value = "http://sms-gateway.com/api"
		mock_recipients.return_value = [
			{"mobile_no": "+1111111111"},  # From mobile_no
			{"phone": "+2222222222"},  # From phone
			{"mobile_no": "+3333333333", "phone": "+4444444444"},  # mobile_no takes priority
		]
		
		result = _execute_sms_blast(self.activity)
		
		# Should collect 3 numbers
		call_args = mock_send_sms.call_args
		mobile_numbers = call_args[0][0]
		self.assertEqual(len(mobile_numbers), 3)
		self.assertIn("+1111111111", mobile_numbers)
		self.assertIn("+2222222222", mobile_numbers)
		self.assertIn("+3333333333", mobile_numbers)  # mobile_no preferred


def suite():
	"""Return test suite"""
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(TestSMSBlast))
	return suite


if __name__ == "__main__":
	unittest.main()
