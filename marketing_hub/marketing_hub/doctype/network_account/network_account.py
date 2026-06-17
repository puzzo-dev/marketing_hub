# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class NetworkAccount(Document):
	def validate(self):
		if not self.connected_app:
			frappe.msgprint(
				_("Connected App is required for OAuth authentication"),
				indicator="orange",
			)
		if not self.user:
			frappe.msgprint(
				_("User is required to link to Token Cache"),
				indicator="orange",
			)

	def get_access_token(self):
		"""Get valid access token from Frappe Token Cache, refreshing if necessary."""
		if not self.connected_app or not self.user:
			frappe.throw(_("Connected App and User must be configured"))

		connected_app = frappe.get_doc("Connected App", self.connected_app)
		token_cache = connected_app.get_active_token(self.user)

		if not token_cache:
			frappe.throw(
				_("No active token found for user {0} in Connected App {1}").format(
					self.user, self.connected_app
				)
			)

		return token_cache.get_password("access_token")

	def get_auth_header(self):
		"""Get Authorization header dict for API calls."""
		return {"Authorization": f"Bearer {self.get_access_token()}"}
