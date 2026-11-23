# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies NG and Contributors
# License: MIT

import unittest
from unittest.mock import patch

import frappe

from marketing_hub.utils import omni_blast


class FakeActivity:
	def __init__(self, activity_type):
		self.activity_type = activity_type
		self.name = "CA-TEST"


class TestChannelRegistry(unittest.TestCase):
	def test_builtin_channels_are_registered(self):
		with patch.object(frappe, "get_hooks", return_value={}):
			senders = omni_blast.get_channel_senders()
		for name in ("Email", "SMS", "WhatsApp", "Push Notification", "Meta Ads", "Facebook", "Instagram", "LinkedIn", "Twitter", "X"):
			self.assertIn(name, senders)

	def test_app_can_register_a_channel(self):
		hooks = {"Telegram": ["marketing_hub.tests.test_channel_registry.fake_sender"]}
		with patch.object(frappe, "get_hooks", return_value=hooks):
			self.assertIn("Telegram", omni_blast.get_channel_senders())
			results = omni_blast.run_channels(FakeActivity("Telegram"))
		self.assertEqual(results["Telegram"], {"status": "Sent", "count": 3})

	def test_unknown_channel_is_not_implemented(self):
		with patch.object(frappe, "get_hooks", return_value={}):
			results = omni_blast.run_channels(FakeActivity("Carrier Pigeon"))
		self.assertEqual(results["Carrier Pigeon"], {"status": "Not Implemented", "count": 0})

	def test_one_failing_channel_does_not_stop_the_others(self):
		def boom(activity):
			raise RuntimeError("down")

		with patch.object(frappe, "get_hooks", return_value={}), \
			patch.object(omni_blast, "_builtin_senders", return_value={"A": boom, "B": lambda a: {"status": "Sent", "count": 1}}), \
			patch.object(frappe, "log_error"), patch.object(frappe, "get_traceback", return_value=""):
			results = omni_blast.run_channels(FakeActivity("A\nB"))
		self.assertEqual(results["A"]["status"], "Error")
		self.assertEqual(results["B"], {"status": "Sent", "count": 1})


def fake_sender(activity):
	return {"status": "Sent", "count": 3}
