"""Unit tests for concurrency and locking fixes in Marketing Hub."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from marketing_hub.marketing_hub.doctype.omni_blast.omni_blast import _claim_social_post


class TestOmniBlastClaiming(unittest.TestCase):

	@patch("marketing_hub.marketing_hub.doctype.omni_blast.omni_blast.frappe")
	def test_claim_returns_true_when_row_updated(self, mock_frappe):
		mock_frappe.utils.now.return_value = "2026-08-01 10:00:00"
		mock_frappe.db.get_value.return_value = "Publishing"

		result = _claim_social_post("POST-001")

		self.assertTrue(result)
		mock_frappe.db.sql.assert_called_once()
		args = mock_frappe.db.sql.call_args.args
		self.assertIn("UPDATE `tabSocial Post`", args[0])

	@patch("marketing_hub.marketing_hub.doctype.omni_blast.omni_blast.frappe")
	def test_claim_returns_false_when_already_claimed(self, mock_frappe):
		mock_frappe.utils.now.return_value = "2026-08-01 10:00:00"
		mock_frappe.db.get_value.return_value = "Published"

		result = _claim_social_post("POST-001")

		self.assertFalse(result)


class TestCampaignActivityConcurrency(unittest.TestCase):

	@patch("marketing_hub.marketing_hub.doctype.campaign_activity.campaign_activity.frappe")
	def test_execute_claims_status_atomically(self, mock_frappe):
		from marketing_hub.marketing_hub.doctype.campaign_activity.campaign_activity import CampaignActivity

		doc = MagicMock(spec=CampaignActivity)
		doc.name = "CA-001"
		doc.status = "Scheduled"
		doc.activity_type = "Email Blast"
		doc.execute_email_blast = MagicMock(return_value={"status": "Success"})

		mock_frappe.db.sql.return_value = None
		mock_frappe.db.get_value.return_value = "In Progress"

		result = CampaignActivity.execute(doc)

		self.assertEqual(result["status"], "Error")
		self.assertIn("already being executed", result["message"])
