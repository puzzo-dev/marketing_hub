# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def get_real_lead_source(doc, method):
    """
    Attribution engine to determine the real lead source.

    Only runs when UTM params or a campaign_name are present — skips
    leads created without any marketing context to avoid unnecessary
    DB lookups on every Lead insert.
    """
    # 1. Check UTM parameters first (highest priority)
    utm_campaign = frappe.form_dict.get("utm_campaign") or doc.get("utm_campaign")
    utm_source = frappe.form_dict.get("utm_source") or doc.get("utm_source")
    utm_medium = frappe.form_dict.get("utm_medium") or doc.get("utm_medium")

    # Short-circuit: nothing to attribute
    if not utm_campaign and not doc.campaign_name:
        return

    sources = []

    if utm_campaign:
        # Store UTM data in lead
        doc.utm_campaign = utm_campaign
        if utm_source:
            doc.utm_source = utm_source
        if utm_medium:
            doc.utm_medium = utm_medium
        sources.append(utm_campaign)

    # 2. Check direct campaign link
    if doc.campaign_name and not sources:
        sources.append(doc.campaign_name)



    # 4. Apply attribution if sources found
    if sources:
        try:
            campaign_name = sources[0]
            # Try getting Marketing Campaign first
            if frappe.db.exists("Marketing Campaign", campaign_name):
                campaign = frappe.get_doc("Marketing Campaign", campaign_name)
                
                # Get primary channel
                if campaign.channels:
                    # Generic fallback since specific channel attribution is complex
                    primary_channel = "Marketing"
                else:
                    primary_channel = "Direct"

                # Set lead source with channel prefix
                doc.lead_source = f"{primary_channel}-{campaign.name}"
                
                # IMPORTANT: We store the marketing campaign reference in utm_campaign
                # We do NOT overwrite doc.campaign_name as that links to standard Campaign
                doc.utm_campaign = campaign.name
                
            elif frappe.db.exists("Campaign", campaign_name):
                # Fallback for standard campaigns
                campaign = frappe.get_doc("Campaign", campaign_name)
                doc.lead_source = f"Standard-{campaign.name}"

            # Log attribution
            frappe.logger().info(f"Lead {doc.name} attributed to {doc.lead_source}")

            # Sync with CRM if installed
            if frappe.db.exists("DocType", "CRM Lead"):
                from marketing_hub.utils.crm_integration import sync_lead_with_crm
                marketing_data = {
                    "campaign": campaign_name,
                    "utm_source": utm_source,
                    "utm_medium": utm_medium,
                    "utm_campaign": utm_campaign
                }
                frappe.enqueue(
                    sync_lead_with_crm,
                    lead_name=doc.name,
                    marketing_data=marketing_data,
                    queue="short"
                )

        except Exception as e:
            frappe.logger().error(f"Attribution error for lead {doc.name}: {str(e)}")


@frappe.whitelist()
def calculate_campaign_attribution(campaign):
    """Calculate attribution metrics for a campaign"""

    # Update to filter by UTM Campaign to support Marketing Campaign decoupling
    leads = frappe.get_all(
        "Lead",
        filters={"utm_campaign": campaign},
        fields=["name", "lead_source", "status", "utm_source", "utm_medium"]
    )

    conversions = frappe.get_all(
        "Lead",
        filters={"utm_campaign": campaign, "status": "Converted"},
        fields=["name"]
    )

    return {
        "total_leads": len(leads),
        "conversions": len(conversions),
        "conversion_rate": (len(conversions) / len(leads) * 100) if leads else 0,
        "channels": _get_channel_breakdown(leads)
    }


def _get_channel_breakdown(leads):
    """Get breakdown of leads by channel"""
    channels = {}
    for lead in leads:
        if lead.lead_source:
            channel = lead.lead_source.split("-")[0]
            channels[channel] = channels.get(channel, 0) + 1
    return channels
