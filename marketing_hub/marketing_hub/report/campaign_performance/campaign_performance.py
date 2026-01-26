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
		{"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 100},
		{"fieldname": "start_date", "label": "Start Date", "fieldtype": "Date", "width": 100},
		{"fieldname": "cost", "label": "Spend", "fieldtype": "Currency", "width": 120},
		{"fieldname": "revenue", "label": "Revenue", "fieldtype": "Currency", "width": 120},
		{"fieldname": "roas", "label": "ROAS", "fieldtype": "Float", "width": 80},
		{"fieldname": "leads", "label": "Leads", "fieldtype": "Int", "width": 80},
		{"fieldname": "cpl", "label": "Cost Per Lead", "fieldtype": "Currency", "width": 120},
	]

def get_data(filters):
	data = []
	
	conditions = ""
	if filters.get("from_date") and filters.get("to_date"):
		conditions += f" AND a.date BETWEEN '{filters.get('from_date')}' AND '{filters.get('to_date')}'"
	
	if filters.get("status"):
		conditions += f" AND c.status = '{filters.get('status')}'"

	# Fetch aggregated data
	campaigns = frappe.db.sql(f"""
		SELECT 
			c.name as campaign,
			c.status,
			c.start_date,
			SUM(a.cost) as cost,
			SUM(a.conversion_value) as revenue,
			AVG(a.roas) as roas
		FROM `tabCampaign` c
		LEFT JOIN `tabAnalytics Daily Log` a ON a.campaign = c.name
		WHERE 1=1 {conditions}
		GROUP BY c.name
		ORDER BY revenue DESC
	""", as_dict=True)

	for row in campaigns:
		# Get lead count separately to ensure accuracy
		leads = frappe.db.count("Lead", {"campaign_name": row.campaign})
		row.leads = leads
		row.cpl = flt(row.cost / leads) if leads > 0 else 0
		data.append(row)

	return data

def get_chart(data):
	labels = [d.campaign for d in data[:10]] # Top 10
	spend = [d.cost for d in data[:10]]
	revenue = [d.revenue for d in data[:10]]

	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": "Spend", "values": spend},
				{"name": "Revenue", "values": revenue}
			]
		},
		"type": "bar",
		"colors": ["#fc8472", "#a8bbd9"]
	}
