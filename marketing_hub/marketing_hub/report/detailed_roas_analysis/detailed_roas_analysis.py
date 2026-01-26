import frappe
from frappe.utils import flt

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	return columns, data, None, chart

def get_columns():
	return [
		{"fieldname": "campaign", "label": "Campaign", "fieldtype": "Link", "options": "Campaign", "width": 150},
		{"fieldname": "platform", "label": "Platform", "fieldtype": "Data", "width": 100},
		{"fieldname": "spend", "label": "Spend", "fieldtype": "Currency", "width": 100},
		{"fieldname": "revenue", "label": "Revenue", "fieldtype": "Currency", "width": 100},
		{"fieldname": "roas", "label": "Actual ROAS", "fieldtype": "Float", "width": 100},
		{"fieldname": "roas_target", "label": "Target ROAS", "fieldtype": "Float", "width": 100},
		{"fieldname": "variance", "label": "Variance (%)", "fieldtype": "Percent", "width": 100},
	]

def get_data(filters):
	conditions = ""
	if filters.get("from_date") and filters.get("to_date"):
		conditions += f" AND a.date BETWEEN '{filters.get('from_date')}' AND '{filters.get('to_date')}'"
	
	if filters.get("campaign"):
		conditions += f" AND a.campaign = '{filters.get('campaign')}'"

	data = frappe.db.sql(f"""
		SELECT 
			a.campaign,
			a.platform,
			SUM(a.cost) as spend,
			SUM(a.conversion_value) as revenue,
			AVG(a.roas) as roas
		FROM `tabAnalytics Daily Log` a
		WHERE 1=1 {conditions}
		GROUP BY a.campaign, a.platform
		HAVING spend > 0
		ORDER BY roas DESC
	""", as_dict=True)

	for row in data:
		# Fetch campaign target ROAS if available, else default to 2.0
		# Assuming a custom field might exist or just a standard benchmark
		# If custom field doesn't exist, we use a heuristic or dummy value
		target_roas = 2.0 # Default business target
		
		# Try to fetch from campaign if field exists (graceful fallback)
		try:
			campaign_target = frappe.db.get_value("Campaign", row.campaign, "target_roas")
			if campaign_target:
				target_roas = flt(campaign_target)
		except:
			pass

		row.roas_target = target_roas
		
		# Variance calc
		if target_roas > 0:
			row.variance = flt((row.roas - target_roas) / target_roas * 100, 2)
		else:
			row.variance = 0

	return data

def get_chart(data):
	labels = [d.campaign[:20] for d in data[:10]]
	actual = [d.roas for d in data[:10]]
	target = [d.roas_target for d in data[:10]]

	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": "Actual ROAS", "values": actual},
				{"name": "Target ROAS", "values": target}
			]
		},
		"type": "line",
		"colors": ["#28a745", "#6c757d"]
	}
