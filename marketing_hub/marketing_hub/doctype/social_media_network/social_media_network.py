# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class SocialMediaNetwork(Document):
	def validate(self):
		"""Validate Social Media Network"""
		# Ensure network code is lowercase and no spaces
		if self.network_code:
			self.network_code = self.network_code.lower().replace(" ", "_")
	
	def on_update(self):
		"""Update related records when network is updated"""
		pass
