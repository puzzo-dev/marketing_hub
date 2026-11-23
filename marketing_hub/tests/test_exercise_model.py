# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies NG and Contributors
# License: MIT
"""Needs a bench: `bench --site <site> run-tests --app marketing_hub --module marketing_hub.tests.test_exercise_model`.
Written against the exercise model; not yet run."""

import frappe
from frappe.tests import IntegrationTestCase


class TestExerciseModel(IntegrationTestCase):
	def setUp(self):
		from marketing_hub.setup_roles_workflows import run

		run()
		self.brand = self.make_brand()
		self.manager = self.make_user("bm1@example.com", "Brand Manager")
		self.other = self.make_user("bm2@example.com", "Brand Manager")
		self.planner = self.make_user("mp@example.com", "Media Planner")
		self.add_team(self.manager, "Brand Manager")
		self.add_team(self.other, "Brand Manager")
		self.exercise = self.make_exercise("Test exercise", self.manager)

	def make_user(self, email, role):
		if frappe.db.exists("User", email):
			return email
		frappe.get_doc({"doctype": "User", "email": email, "first_name": email.split("@")[0], "roles": [{"role": role}], "send_welcome_email": 0}).insert(ignore_permissions=True)
		return email

	def make_brand(self):
		if frappe.db.exists("Brand", "Test Brand"):
			return "Test Brand"
		return frappe.get_doc({"doctype": "Brand", "brand_name": "Test Brand"}).insert(ignore_permissions=True).name

	def add_team(self, user, role):
		brand = frappe.get_doc("Brand", self.brand)
		if not any(r.user == user for r in brand.team):
			brand.append("team", {"user": user, "brand_role": role})
			brand.save(ignore_permissions=True)

	def make_exercise(self, name, manager):
		return frappe.get_doc({"doctype": "Marketing Campaign", "campaign_name": name, "brand": self.brand, "brand_manager": manager}).insert(ignore_permissions=True)

	def test_exercise_gets_a_project(self):
		self.assertTrue(self.exercise.project)
		self.assertEqual(frappe.db.get_value("Project", self.exercise.project, "mkt_campaign"), self.exercise.name)

	def test_manager_must_be_on_the_brand_team(self):
		with self.assertRaises(frappe.ValidationError):
			self.make_exercise("Bad manager", self.planner)

	def test_manager_sees_only_own_exercises(self):
		frappe.set_user(self.other)
		try:
			self.assertEqual(frappe.get_list("Marketing Campaign", filters={"name": self.exercise.name}), [])
		finally:
			frappe.set_user("Administrator")

	def test_request_goes_to_assigned_manager(self):
		cr = frappe.get_doc(
			{"doctype": "Campaign Change Request", "brand": self.brand, "campaign": self.exercise.name, "reason": "More budget", "target_modified": self.exercise.modified, "items": [{"fieldname": "budget", "old_value": "0", "new_value": "500"}]}
		).insert(ignore_permissions=True)
		self.assertEqual(cr.approver, self.manager)

	def test_request_cannot_change_brand_manager(self):
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{"doctype": "Campaign Change Request", "brand": self.brand, "campaign": self.exercise.name, "reason": "x", "target_modified": self.exercise.modified, "items": [{"fieldname": "brand_manager", "new_value": self.other}]}
			).insert(ignore_permissions=True)

	def test_stale_request_is_refused(self):
		cr = frappe.get_doc(
			{"doctype": "Campaign Change Request", "brand": self.brand, "campaign": self.exercise.name, "reason": "x", "target_modified": "2000-01-01 00:00:00", "items": [{"fieldname": "budget", "new_value": "10"}]}
		).insert(ignore_permissions=True)
		with self.assertRaises(frappe.ValidationError):
			cr.apply()

	def test_overlapping_bookings_are_refused(self):
		vendor = frappe.get_doc({"doctype": "Supplier", "supplier_name": "Test Vendor", "supplier_group": frappe.db.get_value("Supplier Group", {}, "name")}).insert(ignore_permissions=True)
		site = frappe.get_doc({"doctype": "OOH Site", "site_name": "Test Site", "vendor": vendor.name}).insert(ignore_permissions=True)
		args = {"doctype": "OOH Booking", "brand": self.brand, "campaign": self.exercise.name, "site": site.name}
		frappe.get_doc({**args, "start_date": "2026-12-01", "end_date": "2026-12-31"}).insert(ignore_permissions=True)
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc({**args, "start_date": "2026-12-15", "end_date": "2027-01-15"}).insert(ignore_permissions=True)
