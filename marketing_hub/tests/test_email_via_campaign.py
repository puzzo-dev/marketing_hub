# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies NG and Contributors
# License: MIT

import unittest
from unittest.mock import patch

import frappe

from marketing_hub.utils import omni_blast


class FakeActivity:
	name = "CA-TEST"
	activity_name = "Test blast"
	campaign = "MC-1"
	segment = "SEG-1"
	scheduled_date = None


class TestEmailViaCampaign(unittest.TestCase):
	def test_email_blast_does_not_call_sendmail(self):
		"""The app hands email to ERPNext; it must not send mail itself."""
		with patch.object(frappe, "sendmail") as sendmail:
			omni_blast._execute_email_blast(type("A", (), {"segment": None, "name": "x"})())
		sendmail.assert_not_called()

	def test_no_segment_is_an_error(self):
		result = omni_blast._execute_email_blast(type("A", (), {"segment": None, "name": "x"})())
		self.assertEqual(result["status"], "Error")

	def test_enrols_group_in_email_campaign(self):
		inserted = []

		class FakeDoc:
			def __init__(self, values):
				self.values = values
				self.name = values.get("campaign_name") or values.get("title") or "NAME"

			def insert(self, **kwargs):
				inserted.append(self.values["doctype"])
				return self

		class FakeExercise:
			email_campaigns = []

			def get(self, key):
				return self.email_campaigns

			def append(self, key, row):
				appended.append(row)

			def save(self, **kwargs):
				pass

		appended = []

		with patch.object(frappe, "get_doc", side_effect=lambda v, *a: FakeDoc(v) if isinstance(v, dict) else FakeExercise()), \
			patch.object(frappe.db, "get_value", return_value=None), \
			patch.object(frappe.db, "exists", return_value=False), \
			patch.object(omni_blast, "_get_segment_recipients", return_value=[{"email": "a@example.com"}]), \
			patch.object(omni_blast, "_get_template", return_value={"subject": "Hi", "content": "<p>Hello</p>"}):
			result = omni_blast._execute_email_blast(FakeActivity())
		self.assertEqual(result["status"], "Scheduled")
		self.assertEqual(result["via"], "ERPNext Email Campaign")
		for doctype in ("Email Template", "Campaign", "Email Group", "Email Group Member", "Email Campaign"):
			self.assertIn(doctype, inserted)
		self.assertEqual(len(appended), 1)
		self.assertEqual(appended[0]["activity"], "CA-TEST")
