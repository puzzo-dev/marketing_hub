# -*- coding: utf-8 -*-
# Copyright (c) 2026, Puzzo and Contributors
# License: MIT

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class MarketingExpenseCategory(Document):
	"""Marketing Expense Category master doctype"""
	
	def validate(self):
		"""Validate category"""
		if self.parent_category == self.name:
			frappe.throw("Parent category cannot be the same as category")
	
	def before_save(self):
		"""Generate category code if not provided"""
		if not self.category_code:
			self.category_code = self.category_name.upper().replace(" ", "_")[:10]
