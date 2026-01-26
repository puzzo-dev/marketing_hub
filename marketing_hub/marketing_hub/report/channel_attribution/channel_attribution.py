import frappe
from frappe.utils import flt

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	return columns, data, None, chart

def get_columns():
	return [
		{"fieldname": "channel", "label": "Channel", "fieldtype": "Data", "width": 150},
		{"fieldname": "impressions", "label": "Impressions", "fieldtype": "Int", "width": 120},
		{"fieldname": "clicks", "label": "Clicks", "fieldtype": "Int", "width": 120},
		{"fieldname": "ctr", "label": "CTR (%)", "fieldtype": "Float", "width": 100},
		{"fieldname": "conversions", "label": "Conversions", "fieldtype": "Int", "width": 100},
		{"fieldname": "cost", "label": "Spend", "fieldtype": "Currency", "width": 120},
		{"fieldname": "cpa", "label": "CPA", "fieldtype": "Currency", "width": 120},
	]

def get_data(filters):
	conditions = ""
	if filters.get("from_date") and filters.get("to_date"):
		conditions += f" AND date BETWEEN '{filters.get('from_date')}' AND '{filters.get('to_date')}'"

	data = frappe.db.sql(f"""
		SELECT 
			platform as channel,
			SUM(impressions) as impressions,
			SUM(clicks) as clicks,
			SUM(conversions) as conversions,
			SUM(cost) as cost
		FROM `tabAnalytics Daily Log`
		WHERE 1=1 {conditions}
		GROUP BY platform
		ORDER BY conversions DESC
	""", as_dict=True)

	for row in data:
		row.ctr = flt(row.clicks / row.impressions * 100, 2) if row.impressions > 0 else 0
		row.cpa = flt(row.cost / row.conversions, 2) if row.conversions > 0 else 0

	return data

def get_chart(data):
	labels = [d.channel for d in data]
	values = [d.conversions for d in data]

	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": "Conversions", "values": values}]
		},
		"type": "donut",
		"colors": ["#7b93db", "#b3a2c7", "#f8d7da", "#d4edda"]
	}
