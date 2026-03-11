"""
Expenses & Budget API
"""

import frappe
from frappe import _
from frappe.utils import today, get_datetime, add_months
from frappe.utils.data import flt


@frappe.whitelist()
def get_expense_list(filters=None, limit=20, offset=0):
	"""Get marketing expenses list"""
	try:
		if filters and isinstance(filters, str):
			import json
			filters = json.loads(filters)

		filters = filters or {}
		base_filters = {}
		if filters.get("campaign"):
			base_filters["campaign"] = filters["campaign"]
		if filters.get("expense_type"):
			base_filters["expense_type"] = filters["expense_type"]

		expenses = frappe.get_all(
			"Marketing Expense",
			fields=[
				"name", "expense_title", "campaign", "amount",
				"expense_date", "expense_type", "vendor", "status"
			],
			filters=base_filters,
			order_by="expense_date desc",
			limit=limit,
			start=offset
		)

		for expense in expenses:
			if expense.campaign:
				expense["campaign_name"] = frappe.db.get_value("Marketing Campaign", expense.campaign, "campaign_name")

		total_count = frappe.db.count("Marketing Expense", base_filters)

		return {
			"expenses": expenses,
			"total_count": total_count,
			"has_more": (offset + limit) < total_count
		}
	except Exception as e:
		frappe.log_error(f"Error fetching expenses: {str(e)}", "Expense API Error")
		return {"error": str(e), "expenses": []}


@frappe.whitelist()
def get_budget_overview():
	"""Get budget vs actuals overview"""
	try:
		from frappe.utils import get_first_day, get_last_day

		total_budget = frappe.db.sql("""
			SELECT SUM(budget) FROM `tabMarketing Campaign` WHERE status != 'Completed'
		""")[0][0] or 0.0

		ad_spend = frappe.db.sql("""
			SELECT SUM(spend) FROM `tabAnalytics Daily Log`
		""")[0][0] or 0.0

		manual_spend = frappe.db.sql("""
			SELECT SUM(amount) FROM `tabMarketing Expense` WHERE status = 'Approved'
		""")[0][0] or 0.0

		total_spend = ad_spend + manual_spend

		# Monthly trend (last 6 months)
		trend_labels = []
		trend_budget = []
		trend_actual = []

		for i in range(5, -1, -1):
			month_start = add_months(today(), -i)
			month_start = get_first_day(month_start)
			month_end = get_last_day(month_start)

			trend_labels.append(get_datetime(month_start).strftime("%b %Y"))

			m_ad_spend = frappe.db.sql("""
				SELECT SUM(spend) FROM `tabAnalytics Daily Log`
				WHERE log_date BETWEEN %s AND %s
			""", (month_start, month_end))[0][0] or 0.0

			m_manual_spend = frappe.db.sql("""
				SELECT SUM(amount) FROM `tabMarketing Expense`
				WHERE expense_date BETWEEN %s AND %s AND status = 'Approved'
			""", (month_start, month_end))[0][0] or 0.0

			trend_actual.append(flt(m_ad_spend + m_manual_spend, 2))
			trend_budget.append(flt(total_budget / 12, 2))

		return {
			"total_budget": flt(total_budget, 2),
			"total_spend": flt(total_spend, 2),
			"remaining_budget": flt(total_budget - total_spend, 2),
			"utilization": flt((total_spend / total_budget * 100) if total_budget > 0 else 0, 2),
			"chart": {
				"labels": trend_labels,
				"budget": trend_budget,
				"actual": trend_actual
			}
		}
	except Exception as e:
		frappe.log_error(f"Error fetching budget overview: {str(e)}", "Budget API Error")
		return {"error": str(e)}


@frappe.whitelist()
def create_expense(data):
	"""Create a new marketing expense"""
	try:
		if isinstance(data, str):
			import json
			data = json.loads(data)

		expense = frappe.get_doc({
			"doctype": "Marketing Expense",
			"expense_title": data.get("title"),
			"campaign": data.get("campaign"),
			"amount": data.get("amount"),
			"expense_date": data.get("date") or today(),
			"expense_type": data.get("type"),
			"vendor": data.get("vendor"),
			"description": data.get("description"),
			"status": "Pending"
		})

		expense.insert()
		return {"success": True, "message": _("Expense logged successfully")}
	except Exception as e:
		frappe.log_error(f"Error creating expense: {str(e)}", "Expense Creation Error")
		return {"success": False, "error": str(e)}
