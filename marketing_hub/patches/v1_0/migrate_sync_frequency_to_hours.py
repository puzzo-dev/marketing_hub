# Copyright (c) 2026, Puxxo and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""Migrate sync_frequency from text values to hours (Int)"""
	
	# Mapping of text values to hours
	frequency_mapping = {
		"Hourly": 1,
		"Daily": 24,
		"Weekly": 168,  # 7 days * 24 hours
		"Monthly": 720  # 30 days * 24 hours (approximate)
	}
	
	# Get all Marketing Hub Settings records
	settings_records = frappe.db.sql("""
		SELECT name, sync_frequency 
		FROM `tabMarketing Hub Settings`
	""", as_dict=True)
	
	for record in settings_records:
		old_value = record.get("sync_frequency")
		
		# Convert text value to hours
		if old_value in frequency_mapping:
			new_value = frequency_mapping[old_value]
			frappe.db.set_value(
				"Marketing Hub Settings",
				record["name"],
				"sync_frequency",
				new_value,
				update_modified=False
			)
			print(f"Converted sync_frequency: {old_value} -> {new_value} hours")
		elif old_value and isinstance(old_value, int):
			# Already numeric, keep it
			print(f"Keeping numeric value: {old_value} hours")
		elif old_value and str(old_value).isdigit():
			# Numeric string, keep it
			print(f"Keeping numeric value: {old_value} hours")
		else:
			# Set default 24 hours (daily)
			frappe.db.set_value(
				"Marketing Hub Settings",
				record["name"],
				"sync_frequency",
				24,
				update_modified=False
			)
			print(f"Set default: 24 hours (was: {old_value})")
	
	frappe.db.commit()
