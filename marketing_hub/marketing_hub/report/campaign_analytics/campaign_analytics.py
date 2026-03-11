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
            "options": "Marketing Campaign",
            "width": 200
        },
        # ... (rest of columns) ...
    ]


def get_data(filters):
    conditions = ""
    values = {}
    if filters.get("campaign"):
        conditions = " AND c.name = %(campaign)s"
        values["campaign"] = filters.get("campaign")

    # Get campaigns - Marketing Campaign
    campaigns = frappe.db.sql(f"""
        SELECT
            c.name as campaign,
            (SELECT GROUP_CONCAT(social_media_network) FROM `tabMarketing Campaign Channel` WHERE parent=c.name) as channels_used,
            c.total_actual_cost as spend
        FROM `tabMarketing Campaign` c
        WHERE c.docstatus < 2
        {conditions}
        ORDER BY c.creation DESC
    """, values, as_dict=1)

    data = []
    for campaign in campaigns:
        # Get lead count via UTM
        leads = frappe.db.count("Lead", {"utm_campaign": campaign.campaign})

        # Get opportunities via Lead UTM
        opportunities = frappe.db.sql("""
            SELECT COUNT(*) as count
            FROM `tabOpportunity` o
            INNER JOIN `tabLead` l ON l.name = o.party_name
            WHERE l.utm_campaign = %s
        """, campaign.campaign)[0][0] or 0

        # Get quotations via Lead UTM
        quotations = frappe.db.sql("""
            SELECT COUNT(*) as count
            FROM `tabQuotation` q
            INNER JOIN `tabLead` l ON l.name = q.party_name
            WHERE l.utm_campaign = %s
        """, campaign.campaign)[0][0] or 0

        # Get sales orders and revenue via Lead UTM
        sales_data = frappe.db.sql("""
            SELECT
                COUNT(DISTINCT so.name) as count,
                SUM(so.grand_total) as revenue
            FROM `tabSales Order` so
            INNER JOIN `tabLead` l ON l.name = so.party_name
            WHERE l.utm_campaign = %s
            AND so.docstatus = 1
        """, campaign.campaign, as_dict=1)

        sales_orders = sales_data[0].count if sales_data else 0
        revenue = sales_data[0].revenue if sales_data and sales_data[0].revenue else 0

        # Get analytics data (impressions, clicks, spend override if available from logs)
        analytics = frappe.db.sql("""
            SELECT
                SUM(impressions) as impressions,
                SUM(clicks) as clicks,
                SUM(spend) as log_spend
            FROM `tabAnalytics Daily Log`
            WHERE campaign = %s
        """, campaign.campaign, as_dict=1)

        impressions = analytics[0].impressions if analytics and analytics[0].impressions else 0
        clicks = analytics[0].clicks if analytics and analytics[0].clicks else 0
        
        # Prefer logged spend if available, else budget/actual from doc
        spend = analytics[0].log_spend if analytics and analytics[0].log_spend else (campaign.spend or 0)

        # Calculate CTR
        ctr = (flt(clicks) / flt(impressions) * 100) if impressions > 0 else 0
        
        # Calculate ROAS
        roas = (revenue / spend) if spend > 0 else 0

        data.append({
            "campaign": campaign.campaign,
            "channels_used": campaign.channels_used or "",
            "leads": leads,
            "opportunities": opportunities,
            "quotations": quotations,
            "sales_orders": sales_orders,
            "revenue": revenue,
            "spend": spend,
            "roas": roas,
            "impressions": impressions,
            "clicks": clicks,
            "ctr": ctr
        })

    return data
