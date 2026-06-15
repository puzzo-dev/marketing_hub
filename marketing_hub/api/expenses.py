"""
Expenses & Budget API
"""

import frappe
from frappe import _
from frappe.utils import add_months, get_datetime, today
from frappe.utils.data import flt


def _get_company(company=None):
	"""Get the active company - explicit param or user default"""
	if company:
		return company
	return frappe.defaults.get_user_default("Company")


@frappe.whitelist()
def get_expense_list(filters=None, limit=20, offset=0):
	"""Get marketing expenses list"""
	try:
		if filters and isinstance(filters, str):
			import json
			filters = json.loads(filters)

		filters = filters or {}
		base_filters = {}
		company = _get_company(filters.get("company"))
		if company:
			base_filters["company"] = company
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
def get_budget_overview(company=None):
	"""Get budget vs actuals overview"""
	try:
		from frappe.utils import get_first_day, get_last_day

		company = _get_company(company)
		campaign_cond = "AND company = %(company)s" if company else ""
		expense_cond = "AND company = %(company)s" if company else ""
		analytics_join = (
			"JOIN `tabMarketing Campaign` mc ON mc.name = a.campaign AND mc.company = %(company)s"
			if company else ""
		)
		params = {"company": company}

		total_budget = frappe.db.sql("""
			SELECT SUM(budget) FROM `tabMarketing Campaign`
			WHERE status != 'Completed' {campaign_cond}
		""".format(campaign_cond=campaign_cond), params)[0][0] or 0.0

		ad_spend = frappe.db.sql("""
			SELECT SUM(a.spend) FROM `tabAnalytics Daily Log` a
			{analytics_join}
			WHERE 1=1
		""".format(analytics_join=analytics_join), params)[0][0] or 0.0

		manual_spend = frappe.db.sql("""
			SELECT SUM(amount) FROM `tabMarketing Expense`
			WHERE status = 'Approved' {expense_cond}
		""".format(expense_cond=expense_cond), params)[0][0] or 0.0

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
			month_params = {"company": company, "month_start": month_start, "month_end": month_end}

			m_ad_spend = frappe.db.sql("""
				SELECT SUM(a.spend) FROM `tabAnalytics Daily Log` a
				{analytics_join}
				WHERE a.log_date BETWEEN %(month_start)s AND %(month_end)s
			""".format(analytics_join=analytics_join), month_params)[0][0] or 0.0

			m_manual_spend = frappe.db.sql("""
				SELECT SUM(amount) FROM `tabMarketing Expense`
				WHERE expense_date BETWEEN %(month_start)s AND %(month_end)s
				AND status = 'Approved' {expense_cond}
			""".format(expense_cond=expense_cond), month_params)[0][0] or 0.0

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
			"company": data.get("company") or _get_company(),
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
