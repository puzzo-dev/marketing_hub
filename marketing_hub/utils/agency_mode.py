# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies NG and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, add_months

def get_settings(company=None):
    """Get Marketing Hub Settings (single doctype)"""
    try:
        return frappe.get_single("Marketing Hub Settings")
    except Exception:
        return None


@frappe.whitelist()
def get_agency_mode(company=None):
    """Check if system is in agency mode for a company"""
    settings = get_settings(company)
    if settings:
        return settings.agency_mode

    # Fallback to old method
    try:
        setup = frappe.get_single("Marketing Hub Setup")
        return setup.get("mode") == "Agency"
    except Exception:
        return False


@frappe.whitelist()
def check_client_subscription(client, campaign=None):
    """Check if client has active subscription"""

    if not get_agency_mode():
        return {"valid": True, "message": "Internal mode - no subscription required"}

    # Get active subscription
    subscriptions = frappe.get_all(
        "Client Subscription",
        filters={
            "client": client,
            "status": "Active",
            "end_date": [">=", today()]
        },
        fields=["name", "package", "start_date", "end_date"],
        order_by="end_date desc",
        limit=1
    )

    if not subscriptions:
        return {
            "valid": False,
            "message": "No active subscription found for client"
        }

    subscription = subscriptions[0]

    # Get package details
    package = frappe.get_doc("Agency Package", subscription.package)

    # Check campaign limit if provided
    if campaign:
        client_campaigns = frappe.db.count(
            "Marketing Campaign",
            filters={"client": client}
        )

        if package.campaign_limit and client_campaigns >= package.campaign_limit:
            return {
                "valid": False,
                "message": f"Campaign limit reached ({package.campaign_limit})"
            }

    return {
        "valid": True,
        "subscription": subscription.name,
        "package": package.name,
        "expires": subscription.end_date
    }


@frappe.whitelist()
def check_channel_permission(client, channel):
    """Check if client's package allows a specific channel"""

    if not get_agency_mode():
        return {"allowed": True}

    # Get active subscription
    subscription_check = check_client_subscription(client)

    if not subscription_check["valid"]:
        return {"allowed": False, "message": subscription_check["message"]}

    # Get package
    subscriptions = frappe.get_all(
        "Client Subscription",
        filters={
            "client": client,
            "status": "Active",
            "end_date": [">=", today()]
        },
        fields=["package"],
        limit=1
    )

    if not subscriptions:
        return {"allowed": False, "message": "No active subscription"}

    package = frappe.get_doc("Agency Package", subscriptions[0].package)

    # Check if channel is in included channels
    included_channels = package.get("included_channels", "").split("\n")

    if channel in included_channels or "All Channels" in included_channels:
        return {"allowed": True}
    else:
        return {
            "allowed": False,
            "message": f"Channel {channel} not included in package"
        }


@frappe.whitelist()
def create_subscription(client, package, start_date=None):
    """Create new client subscription"""

    if not get_agency_mode():
        frappe.throw(_("System is not in Agency mode"))

    # Get package details
    pkg = frappe.get_doc("Agency Package", package)

    # Calculate dates
    if not start_date:
        start_date = today()

    end_date = add_months(start_date, pkg.get("billing_cycle_months", 1))

    # Create subscription
    subscription = frappe.new_doc("Client Subscription")
    subscription.client = client
    subscription.package = package
    subscription.start_date = start_date
    subscription.end_date = end_date
    subscription.status = "Active"
    subscription.monthly_fee = pkg.monthly_fee
    subscription.save()

    return subscription.name


@frappe.whitelist()
def renew_subscription(subscription):
    """Renew an existing subscription"""

    sub = frappe.get_doc("Client Subscription", subscription)
    pkg = frappe.get_doc("Agency Package", sub.package)

    # Extend end date
    new_end_date = add_months(sub.end_date, pkg.get("billing_cycle_months", 1))

    sub.end_date = new_end_date
    sub.status = "Active"
    sub.save()

    return sub.name


@frappe.whitelist()
def get_client_limits(client):
    """Get current usage vs limits for a client"""

    if not get_agency_mode():
        return {"mode": "internal", "limits": None}

    subscription_check = check_client_subscription(client)

    if not subscription_check["valid"]:
        return {"valid": False, "message": subscription_check["message"]}

    # Get subscription and package
    subscriptions = frappe.get_all(
        "Client Subscription",
        filters={
            "client": client,
            "status": "Active",
            "end_date": [">=", today()]
        },
        fields=["name", "package"],
        limit=1
    )

    package = frappe.get_doc("Agency Package", subscriptions[0].package)

    # Get current usage
    campaign_count = frappe.db.count("Campaign", filters={"client": client})

    return {
        "valid": True,
        "package": package.name,
        "limits": {
            "campaigns": {
                "used": campaign_count,
                "limit": package.campaign_limit or "Unlimited"
            },
            "channels": package.get("included_channels", "").split("\n")
        }
    }


@frappe.whitelist()
def get_agency_dashboard_data():
    """Get dashboard data for agency mode"""

    if not get_agency_mode():
        return {"mode": "internal"}

    # Count active subscriptions
    active_subs = frappe.db.count(
        "Client Subscription",
        filters={"status": "Active", "end_date": [">=", today()]}
    )

    # Count total clients
    total_clients = frappe.db.count(
        "Customer",
        filters={"customer_type": "Company"}
    )

    # Get expiring soon (next 30 days)
    expiring_soon = frappe.get_all(
        "Client Subscription",
        filters={
            "status": "Active",
            "end_date": ["between", [today(), add_months(today(), 1)]]
        },
        fields=["name", "client", "end_date"]
    )

    return {
        "mode": "agency",
        "active_subscriptions": active_subs,
        "total_clients": total_clients,
        "expiring_soon": len(expiring_soon),
        "expiring_list": expiring_soon
    }
