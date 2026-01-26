# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, add_days
from marketing_hub.utils.oauth_integration import make_api_request, get_platform_credentials


def sync_all_connectors():
    """Scheduler to sync all active analytics connectors based on interval"""
    
    settings = frappe.get_single("Marketing Hub Settings")
    if not settings.enable_analytics_sync:
        return

    # Check interval
    interval = settings.analytics_sync_interval or 3600
    last_sync = settings.last_analytics_sync_time
    
    if last_sync and frappe.utils.time_diff_in_seconds(frappe.utils.now(), last_sync) < interval:
        return

    # Update global last sync time immediately to prevent double-fire
    settings.last_analytics_sync_time = frappe.utils.now()
    settings.save(ignore_permissions=True)

    connectors = frappe.get_all(
        "Analytics Connector",
        filters={"status": "Active"},
        fields=["name"]
    )

    for connector_name in connectors:
        try:
            sync_connector(connector_name.name)
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(f"Analytics sync failed for {connector_name.name}", str(e))
            frappe.db.rollback()


@frappe.whitelist()
def sync_connector(connector):
    """Sync analytics data from a specific connector"""

    if isinstance(connector, str):
        connector = frappe.get_doc("Analytics Connector", connector)

    platform = connector.get("platform", "")

    try:
        if platform == "Google Ads":
            result = _sync_google_ads(connector)
        elif platform == "Meta Ads":
            result = _sync_meta_ads(connector)
        elif platform == "TikTok Ads":
            result = _sync_tiktok_ads(connector)
        elif platform == "Twitter Ads":
            result = _sync_twitter_ads(connector)
        elif platform == "LinkedIn Ads":
            result = _sync_linkedin_ads(connector)
        else:
            result = {"status": "Error", "message": f"Platform {platform} not supported"}

        # Update last sync time
        connector.last_sync = frappe.utils.now()
        connector.save()

        return result

    except Exception as e:
        frappe.log_error(f"Sync error for {connector.name}", str(e))
        raise


def _sync_google_ads(connector):
    """Sync Google Ads data using OAuth"""
    try:
        credentials = get_platform_credentials("Google Ads", connector.company)
        if not credentials:
            return {"status": "Error", "message": "No credentials configured"}

        # Get customer ID from connector
        customer_id = connector.account_id
        if not customer_id:
            return {"status": "Error", "message": "Customer ID not configured"}

        # Fetch campaigns
        campaigns_data = make_api_request(
            "Google Ads",
            f"{customer_id}/campaigns",
            company=connector.company
        )

        synced_campaigns = 0

        # For each campaign, fetch insights and create log
        for campaign in campaigns_data.get("results", []):
            campaign_id = campaign.get("campaign", {}).get("id")
            campaign_name = campaign.get("campaign", {}).get("name")

            # Fetch campaign metrics
            metrics_query = {
                "query": f"""
                    SELECT
                        campaign.id,
                        campaign.name,
                        metrics.impressions,
                        metrics.clicks,
                        metrics.cost_micros,
                        metrics.conversions
                    FROM campaign
                    WHERE campaign.id = {campaign_id}
                    AND segments.date = '{today()}'
                """
            }

            metrics_data = make_api_request(
                "Google Ads",
                f"{customer_id}/googleAds:searchStream",
                method="POST",
                data=metrics_query,
                company=connector.company
            )

            if metrics_data.get("results"):
                metrics = metrics_data["results"][0]["metrics"]

                _create_analytics_log({
                    "connector": connector.name,
                    "platform": "Google Ads",
                    "campaign": campaign_name,
                    "campaign_id": campaign_id,
                    "date": today(),
                    "impressions": metrics.get("impressions", 0),
                    "clicks": metrics.get("clicks", 0),
                    "cost": metrics.get("cost_micros", 0) / 1000000,  # Convert micros to currency
                    "conversions": metrics.get("conversions", 0)
                })

                synced_campaigns += 1

        return {
            "status": "Success",
            "synced_campaigns": synced_campaigns
        }
    except Exception as e:
        frappe.log_error(f"Google Ads sync error: {str(e)}", "Marketing Hub Analytics")
        return {"status": "Error", "error": str(e)}


def _sync_meta_ads(connector):
    """Sync Meta Ads data using OAuth"""
    try:
        credentials = get_platform_credentials("Meta Ads", connector.company)
        if not credentials:
            return {"status": "Error", "message": "No credentials configured"}

        # Get ad account ID from connector
        ad_account_id = connector.account_id
        if not ad_account_id:
            return {"status": "Error", "message": "Ad Account ID not configured"}

        # Fetch campaigns from Meta Ads
        campaigns_data = make_api_request(
            "Meta Ads",
            f"act_{ad_account_id}/campaigns",
            data={
                "fields": "id,name,status",
                "limit": 100
            },
            company=connector.company
        )

        synced_campaigns = 0

        # For each campaign, fetch insights
        for campaign in campaigns_data.get("data", []):
            campaign_id = campaign.get("id")
            campaign_name = campaign.get("name")

            # Fetch campaign insights
            insights_data = make_api_request(
                "Meta Ads",
                f"{campaign_id}/insights",
                data={
                    "fields": "impressions,clicks,spend,conversions",
                    "date_preset": "today",
                    "level": "campaign"
                },
                company=connector.company
            )

            if insights_data.get("data"):
                insights = insights_data["data"][0]

                _create_analytics_log({
                    "connector": connector.name,
                    "platform": "Meta Ads",
                    "campaign": campaign_name,
                    "campaign_id": campaign_id,
                    "date": today(),
                    "impressions": int(insights.get("impressions", 0)),
                    "clicks": int(insights.get("clicks", 0)),
                    "cost": float(insights.get("spend", 0)),
                    "conversions": int(insights.get("conversions", 0))
                })

                synced_campaigns += 1

        # Optionally: Support campaign creation/blast if requested (stub for now)
        # Example: create_campaign_data = make_api_request(
        #     "Meta Ads",
        #     f"act_{ad_account_id}/campaigns",
        #     method="POST",
        #     data={...},
        #     company=connector.company
        # )

        return {
            "status": "Success",
            "synced_campaigns": synced_campaigns
        }
    except Exception as e:
        frappe.log_error(f"Meta Ads sync error: {str(e)}", "Marketing Hub Analytics")
        return {"status": "Error", "error": str(e)}


def _sync_tiktok_ads(connector):
    """Sync TikTok Ads data - Implementation Ready Stub"""
    try:
        # 1. Attempt to get credentials
        # credentials = get_platform_credentials("TikTok Ads", connector.company)
        credentials = None # Placeholder for when implementation arrives
        
        synced_campaigns = 0
        
        if not credentials:
            # SIMULATION MODE: No credentials, so we log simulation
            # frappe.log_error("No TikTok Credentials, skipping live sync", "Analytics Sync")
            return {
                "status": "Skipped", 
                "message": "No Credentials Configured",
                "synced_campaigns": 0
            }
            
        # 2. If credentials existed, we would call API here:
        # campaigns = tiktok_api.get_campaigns(...)
        
        # 3. Process results
        
        return {
            "status": "Success",
            "synced_campaigns": synced_campaigns
        }
    except Exception as e:
        return {"status": "Error", "error": str(e)}


def _sync_twitter_ads(connector):
    """Sync Twitter Ads data - Implementation Ready Stub"""
    try:
        credentials = None # Placeholder
        
        if not credentials:
            return {
                "status": "Skipped", 
                "message": "No Credentials Configured",
                "synced_campaigns": 0
            }

        return {
            "status": "Success",
            "synced_campaigns": 0
        }
    except Exception as e:
        return {"status": "Error", "error": str(e)}


def _sync_linkedin_ads(connector):
    """Sync LinkedIn Ads data - Implementation Ready Stub"""
    try:
        credentials = None # Placeholder
        
        if not credentials:
            return {
                "status": "Skipped", 
                "message": "No Credentials Configured",
                "synced_campaigns": 0
            }

        return {
            "status": "Success",
            "synced_campaigns": 0
        }
    except Exception as e:
        return {"status": "Error", "error": str(e)}


def _create_analytics_log(data):
    """Create or update Analytics Daily Log entry"""

    # Check if log already exists for this date/campaign
    existing = frappe.db.exists(
        "Analytics Daily Log",
        {
            "connector": data["connector"],
            "campaign": data["campaign"],
            "date": data["date"]
        }
    )

    if existing:
        log = frappe.get_doc("Analytics Daily Log", existing)
    else:
        log = frappe.new_doc("Analytics Daily Log")
        log.connector = data["connector"]
        log.campaign = data["campaign"]
        log.date = data["date"]
        log.platform = data["platform"]

    # Update metrics
    log.impressions = data.get("impressions", 0)
    log.clicks = data.get("clicks", 0)
    log.cost = data.get("cost", 0)
    log.conversions = data.get("conversions", 0)

    # Calculate derived metrics
    if log.clicks > 0:
        log.ctr = (log.clicks / log.impressions * 100) if log.impressions > 0 else 0
        log.cpc = log.cost / log.clicks

    if log.conversions > 0:
        log.conversion_rate = (log.conversions / log.clicks * 100) if log.clicks > 0 else 0
        log.cost_per_conversion = log.cost / log.conversions

    log.save(ignore_permissions=True)

    return log.name


@frappe.whitelist()
def get_campaign_analytics(campaign, from_date=None, to_date=None):
    """Get aggregated analytics for a campaign"""

    filters = {"campaign": campaign}

    if from_date:
        filters["date"] = [">=", from_date]
    if to_date:
        if "date" in filters:
            filters["date"] = ["between", [from_date, to_date]]
        else:
            filters["date"] = ["<=", to_date]

    logs = frappe.get_all(
        "Analytics Daily Log",
        filters=filters,
        fields=[
            "date",
            "impressions",
            "clicks",
            "cost",
            "conversions",
            "platform"
        ],
        order_by="date"
    )

    # Aggregate totals
    total_impressions = sum(log.impressions or 0 for log in logs)
    total_clicks = sum(log.clicks or 0 for log in logs)
    total_cost = sum(log.cost or 0 for log in logs)
    total_conversions = sum(log.conversions or 0 for log in logs)

    return {
        "logs": logs,
        "totals": {
            "impressions": total_impressions,
            "clicks": total_clicks,
            "cost": total_cost,
            "conversions": total_conversions,
            "ctr": (total_clicks / total_impressions * 100) if total_impressions > 0 else 0,
            "conversion_rate": (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        }
    }
