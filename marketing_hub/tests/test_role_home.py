import frappe
from frappe.tests.utils import FrappeTestCase

from marketing_hub.api import client, role_home


class TestRoleHome(FrappeTestCase):
	def test_unknown_role_is_refused(self):
		with self.assertRaises(frappe.PermissionError):
			role_home.get("Brand Manager")

	def test_each_home_returns_figures_and_lists(self):
		for role in ("Marketing Head", "Content Lead", "Media Planner", "Publisher", "OOH Coordinator"):
			data = role_home.get(role)
			self.assertTrue(data["figures"], role)
			self.assertIn("lists", data)

	def test_client_pages_return_lists_for_a_user_with_no_brands(self):
		frappe.set_user("Guest")
		try:
			self.assertEqual(client.all_posted_content(), [])
			self.assertEqual(client.all_out_of_home(), [])
			self.assertEqual(client.all_results(), [])
			self.assertEqual(client.all_spend(), [])
		finally:
			frappe.set_user("Administrator")
