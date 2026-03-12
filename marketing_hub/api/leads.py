"""
Leads API - View and manage leads attributed to marketing campaigns
"""

import frappe
from frappe import _
from frappe.utils import add_days, today, cint
from frappe.utils.data import flt


@frappe.whitelist()
def get_leads_overview(company=None):
	"""Get overview stats for marketing-attributed leads"""
	company = _get_company(company)
	from_date = add_days(today(), -30)
	params = {"company": company, "from_date": from_date}
	company_cond = "AND company = %(company)s" if company else ""

	# Total marketing leads (have UTM campaign set)
	total = frappe.db.sql("""
		SELECT COUNT(*) FROM `tabLead`
		WHERE utm_campaign IS NOT NULL AND utm_campaign != ''
		{company_cond}
	""".format(company_cond=company_cond), params)[0][0] or 0

	# Last 30 days
	recent = frappe.db.sql("""
		SELECT COUNT(*) FROM `tabLead`
		WHERE utm_campaign IS NOT NULL AND utm_campaign != ''
		AND creation >= %(from_date)s
		{company_cond}
	""".format(company_cond=company_cond), params)[0][0] or 0

	# Converted
	converted = frappe.db.sql("""
		SELECT COUNT(*) FROM `tabLead`
		WHERE utm_campaign IS NOT NULL AND utm_campaign != ''
		AND status = 'Converted'
		{company_cond}
	""".format(company_cond=company_cond), params)[0][0] or 0

	# By status
	by_status = frappe.db.sql("""
		SELECT status, COUNT(*) as count FROM `tabLead`
		WHERE utm_campaign IS NOT NULL AND utm_campaign != ''
		{company_cond}
		GROUP BY status ORDER BY count DESC
	""".format(company_cond=company_cond), params, as_dict=True)

	# Top campaigns by lead count
	by_campaign = frappe.db.sql("""
		SELECT utm_campaign as campaign, COUNT(*) as count FROM `tabLead`
		WHERE utm_campaign IS NOT NULL AND utm_campaign != ''
		{company_cond}
		GROUP BY utm_campaign ORDER BY count DESC LIMIT 10
	""".format(company_cond=company_cond), params, as_dict=True)

	# Top sources
	by_source = frappe.db.sql("""
		SELECT utm_source as source, COUNT(*) as count FROM `tabLead`
		WHERE utm_source IS NOT NULL AND utm_source != ''
		{company_cond}
		GROUP BY utm_source ORDER BY count DESC LIMIT 10
	""".format(company_cond=company_cond), params, as_dict=True)

	conversion_rate = (converted / total * 100) if total > 0 else 0

	return {
		"total_leads": total,
		"recent_leads": recent,
		"converted": converted,
		"conversion_rate": flt(conversion_rate, 1),
		"by_status": by_status,
		"by_campaign": by_campaign,
		"by_source": by_source,
	}


@frappe.whitelist()
def get_leads_list(campaign=None, source=None, status=None, limit=50, offset=0):
	"""Get list of marketing-attributed leads"""
	filters = [
		["utm_campaign", "is", "set"],
	]

	if campaign:
		filters.append(["utm_campaign", "=", campaign])
	if source:
		filters.append(["utm_source", "=", source])
	if status:
		filters.append(["status", "=", status])

	leads = frappe.get_all(
		"Lead",
		filters=filters,
		fields=[
			"name", "lead_name", "email_id", "mobile_no",
			"status", "source", "lead_source",
			"utm_campaign", "utm_source", "utm_medium",
			"creation", "company",
		],
		order_by="creation desc",
		limit_page_length=cint(limit),
		limit_start=cint(offset),
	)

	total_count = frappe.db.count("Lead", filters=filters)

	return {
		"leads": leads,
		"total": total_count,
	}


def _get_company(company=None):
	if company:
		return company
	return frappe.defaults.get_user_default("Company")
