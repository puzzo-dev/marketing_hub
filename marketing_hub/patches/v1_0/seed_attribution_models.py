# -*- coding: utf-8 -*-
# Copyright (c) 2026, Puzzo and Contributors
# License: MIT

"""
Seed data for Attribution Models
Creates standard attribution model records
"""

import frappe
import json


def execute():
	"""Create seed data for Attribution Models"""
	
	models = [
		{
			"model_name": "First Touch",
			"model_code": "first_touch",
			"calculation_method": "First Touch",
			"description": "<p>Attributes 100% of the conversion credit to the first touchpoint in the customer journey.</p><p><strong>Use when:</strong> You want to focus on top-of-funnel awareness campaigns.</p>",
			"parameters": json.dumps({"weight": 1.0, "position": "first"}),
			"is_active": 1,
			"is_default": 0
		},
		{
			"model_name": "Last Touch",
			"model_code": "last_touch",
			"calculation_method": "Last Touch",
			"description": "<p>Attributes 100% of the conversion credit to the last touchpoint before conversion.</p><p><strong>Use when:</strong> You want to focus on bottom-of-funnel conversion campaigns.</p>",
			"parameters": json.dumps({"weight": 1.0, "position": "last"}),
			"is_active": 1,
			"is_default": 1  # Set as default
		},
		{
			"model_name": "Linear",
			"model_code": "linear",
			"calculation_method": "Linear",
			"description": "<p>Distributes conversion credit equally across all touchpoints in the customer journey.</p><p><strong>Use when:</strong> All touchpoints are considered equally important.</p>",
			"parameters": json.dumps({"distribution": "equal"}),
			"is_active": 1,
			"is_default": 0
		},
		{
			"model_name": "Time Decay",
			"model_code": "time_decay",
			"calculation_method": "Time Decay",
			"description": "<p>Gives more credit to touchpoints closer to the conversion, with exponential decay.</p><p><strong>Use when:</strong> Recent interactions are more influential than earlier ones.</p>",
			"parameters": json.dumps({"decay_rate": 0.5, "half_life_days": 7}),
			"is_active": 1,
			"is_default": 0
		},
		{
			"model_name": "Position Based (U-Shaped)",
			"model_code": "position_based",
			"calculation_method": "Position Based",
			"description": "<p>Gives 40% credit to first touch, 40% to last touch, and 20% distributed among middle touchpoints.</p><p><strong>Use when:</strong> Both awareness and conversion touchpoints are important.</p>",
			"parameters": json.dumps({"first_touch_weight": 0.4, "last_touch_weight": 0.4, "middle_weight": 0.2}),
			"is_active": 1,
			"is_default": 0
		}
	]
	
	for model_data in models:
		# Check if already exists
		if frappe.db.exists("Attribution Model", model_data["model_name"]):
			print(f"Model {model_data['model_name']} already exists, skipping")
			continue
		
		try:
			model = frappe.get_doc({
				"doctype": "Attribution Model",
				**model_data
			})
			model.insert(ignore_permissions=True)
			print(f"Created attribution model: {model_data['model_name']}")
		except Exception as e:
			print(f"Failed to create {model_data['model_name']}: {str(e)}")
			frappe.log_error(f"Failed to create attribution model seed data: {str(e)}")
	
	frappe.db.commit()
	print("Attribution Model seed data created successfully")
