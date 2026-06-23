# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies NG and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AnalyticsDailyLog(Document):
	def validate(self):
		"""Validate and calculate derived metrics"""
		self.calculate_metrics()
		
		# Ensure unique constraint
		self.validate_unique()
	
	def calculate_metrics(self):
		"""Calculate derived metrics"""
		# ROAS = revenue / spend
		if self.spend and self.spend > 0:
			self.roas = self.revenue / self.spend if self.revenue else 0
		else:
			self.roas = 0
		
		# CPC = spend / clicks
		if self.clicks and self.clicks > 0:
			self.cpc = self.spend / self.clicks
		else:
			self.cpc = 0
		
		# CPM = (spend / impressions) * 1000
		if self.impressions and self.impressions > 0:
			self.cpm = (self.spend / self.impressions) * 1000
		else:
			self.cpm = 0
		
		# CTR = (clicks / impressions) * 100
		if self.impressions and self.impressions > 0:
			self.ctr = (self.clicks / self.impressions) * 100
		else:
			self.ctr = 0
		
		# Conversion Rate = (conversions / clicks) * 100
		if self.clicks and self.clicks > 0:
			self.conversion_rate = (self.conversions / self.clicks) * 100
		else:
			self.conversion_rate = 0
	
	def validate_unique(self):
		"""Ensure unique log per date + connector + campaign"""
		if not self.is_new():
			return
		
		existing = frappe.db.exists("Analytics Daily Log", {
			"log_date": self.log_date,
			"connector": self.connector,
			"campaign_id_platform": self.campaign_id_platform,
			"name": ["!=", self.name]
		})
		
		if existing:
			frappe.throw(f"Analytics log already exists for this date, connector, and campaign")
