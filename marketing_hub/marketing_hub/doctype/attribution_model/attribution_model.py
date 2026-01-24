# -*- coding: utf-8 -*-
# Copyright (c) 2026, Puzzo and Contributors
# License: MIT

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json


class AttributionModel(Document):
	"""Attribution Model master doctype"""
	
	def validate(self):
		"""Validate attribution model"""
		# Validate JSON parameters
		if self.parameters:
			try:
				json.loads(self.parameters)
			except json.JSONDecodeError:
				frappe.throw("Invalid JSON format in parameters field")
		
		# Only one model can be default
		if self.is_default:
			existing_default = frappe.db.get_value(
				"Attribution Model",
				{"is_default": 1, "name": ["!=", self.name]},
				"name"
			)
			if existing_default:
				frappe.throw(f"'{existing_default}' is already set as default. Please unset it first.")
	
	def before_save(self):
		"""Generate model code if not provided"""
		if not self.model_code:
			self.model_code = self.model_name.lower().replace(" ", "_")
