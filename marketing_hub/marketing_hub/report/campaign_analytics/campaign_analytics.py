# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "fieldname": "campaign",
            "label": _("Campaign"),
            "fieldtype": "Link",
            "options": "Campaign",
            "width": 200
        },
        {
            "fieldname": "channels_used",
            "label": _("Channels"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "leads",
            "label": _("Leads"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "opportunities",
            "label": _("Opportunities"),
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "quotations",
            "label": _("Quotations"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "sales_orders",
            "label": _("Sales Orders"),
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "revenue",
            "label": _("Revenue"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "spend",
            "label": _("Ad Spend"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "roas",
            "label": _("ROAS"),
            "fieldtype": "Float",
            "precision": 2,
            "width": 100
        },
        {
            "fieldname": "impressions",
            "label": _("Impressions"),
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "clicks",
            "label": _("Clicks"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "ctr",
            "label": _("CTR %"),
            "fieldtype": "Percent",
            "width": 100
        }
    ]


def get_data(filters):
    conditions = ""
    if filters.get("campaign"):
        conditions = f" AND c.name = '{filters.get('campaign')}'"

    # Get campaigns with basic info
    campaigns = frappe.db.sql(f"""
        SELECT
            c.name as campaign,
            c.channels_used,
            c.roas
        FROM `tabCampaign` c
        WHERE c.docstatus < 2
        {conditions}
        ORDER BY c.creation DESC
    """, as_dict=1)

    data = []
    for campaign in campaigns:
        # Get lead count
        leads = frappe.db.count("Lead", {"campaign_name": campaign.campaign})

        # Get opportunities
        opportunities = frappe.db.sql("""
            SELECT COUNT(*) as count
            FROM `tabOpportunity` o
            INNER JOIN `tabLead` l ON l.name = o.party_name
            WHERE l.campaign_name = %s
        """, campaign.campaign)[0][0] or 0

        # Get quotations
        quotations = frappe.db.sql("""
            SELECT COUNT(*) as count
            FROM `tabQuotation` q
            INNER JOIN `tabLead` l ON l.name = q.party_name
            WHERE l.campaign_name = %s
        """, campaign.campaign)[0][0] or 0

        # Get sales orders and revenue
        sales_data = frappe.db.sql("""
            SELECT
                COUNT(DISTINCT so.name) as count,
                SUM(so.grand_total) as revenue
            FROM `tabSales Order` so
            INNER JOIN `tabLead` l ON l.name = so.party_name
            WHERE l.campaign_name = %s
            AND so.docstatus = 1
        """, campaign.campaign, as_dict=1)

        sales_orders = sales_data[0].count if sales_data else 0
        revenue = sales_data[0].revenue if sales_data and sales_data[0].revenue else 0

        # Get analytics data (impressions, clicks, spend)
        analytics = frappe.db.sql("""
            SELECT
                SUM(impressions) as impressions,
                SUM(clicks) as clicks,
                SUM(spend) as spend
            FROM `tabAnalytics Daily Log`
            WHERE campaign = %s
        """, campaign.campaign, as_dict=1)

        impressions = analytics[0].impressions if analytics and analytics[0].impressions else 0
        clicks = analytics[0].clicks if analytics and analytics[0].clicks else 0
        spend = analytics[0].spend if analytics and analytics[0].spend else 0

        # Calculate CTR
        ctr = (flt(clicks) / flt(impressions) * 100) if impressions > 0 else 0

        data.append({
            "campaign": campaign.campaign,
            "channels_used": campaign.channels_used or "",
            "leads": leads,
            "opportunities": opportunities,
            "quotations": quotations,
            "sales_orders": sales_orders,
            "revenue": revenue,
            "spend": spend,
            "roas": campaign.roas or 0,
            "impressions": impressions,
            "clicks": clicks,
            "ctr": ctr
        })

    return data
