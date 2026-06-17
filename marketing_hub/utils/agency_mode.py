# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, add_months

def get_settings(company=None):
    """Get Marketing Hub Settings (single doctype)"""
    try:
        return frappe.get_single("Marketing Hub Settings")
    except (frappe.ValidationError, frappe.DoesNotExistError):
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
    except (frappe.ValidationError, frappe.DoesNotExistError):
        return False


@frappe.whitelist()
def check_client_subscription(client, campaign=None):
    """Check if client has active ERPNext Subscription linked to an Agency Package."""

    if not get_agency_mode():
        return {"valid": True, "message": "Internal mode - no subscription required"}

    # Get active Subscription for customer
    subscriptions = frappe.get_all(
        "Subscription",
        filters={
            "party_type": "Customer",
            "party": client,
            "status": ["in", ["Active", "Trialling"]],
            "end_date": [">=", today()]
        },
        fields=["name", "start_date", "end_date"],
        order_by="end_date desc",
        limit=1
    )

    if not subscriptions:
        return {
            "valid": False,
            "message": "No active subscription found for client"
        }

    subscription = subscriptions[0]

    # Resolve Agency Package from Subscription Plan linked in Subscription
    package = _get_agency_package_from_subscription(subscription.name)
    if not package:
        return {
            "valid": False,
            "message": "No agency package linked to subscription"
        }

    # Check campaign limit if provided
    if campaign:
        client_campaigns = frappe.db.count(
            "Marketing Campaign",
            filters={"customer": client}
        )

        if package.campaign_limit and client_campaigns >= package.campaign_limit:
            return {
                "valid": False,
                "message": _("Campaign limit reached ({0})").format(package.campaign_limit)
            }

    return {
        "valid": True,
        "subscription": subscription.name,
        "package": package.name,
        "expires": subscription.end_date
    }


def _get_agency_package_from_subscription(subscription_name):
    """Find Agency Package linked to a Subscription via Subscription Plan."""
    sub = frappe.get_doc("Subscription", subscription_name)
    for plan_row in sub.get("plans", []):
        if plan_row.plan:
            packages = frappe.get_all(
                "Agency Package",
                filters={"subscription_plan": plan_row.plan, "is_active": 1},
                limit=1
            )
            if packages:
                return frappe.get_doc("Agency Package", packages[0].name)
    return None


@frappe.whitelist()
def check_channel_permission(client, channel):
    """Check if client's package allows a specific channel"""

    if not get_agency_mode():
        return {"allowed": True}

    subscription_check = check_client_subscription(client)

    if not subscription_check["valid"]:
        return {"allowed": False, "message": subscription_check["message"]}

    package = frappe.get_doc("Agency Package", subscription_check["package"])

    # Check if channel is in included channels
    included_channels = package.get("included_channels", "").split("\n")

    if channel in included_channels or "All Channels" in included_channels:
        return {"allowed": True}
    else:
        return {
            "allowed": False,
            "message": _("Channel {0} not included in package").format(channel)
        }


@frappe.whitelist()
def create_subscription(client, package, start_date=None):
    """Create new client subscription using ERPNext Subscription."""

    frappe.has_permission("Subscription", throw=True)
    if not get_agency_mode():
        frappe.throw(_("System is not in Agency mode"))

    pkg = frappe.get_doc("Agency Package", package)

    if not pkg.subscription_plan:
        frappe.throw(_("Agency Package {0} has no linked Subscription Plan. Please link one first.").format(package))

    if not start_date:
        start_date = today()

    end_date = add_months(start_date, pkg.get("billing_cycle_months", 1))

    subscription = frappe.new_doc("Subscription")
    subscription.party_type = "Customer"
    subscription.party = client
    subscription.start_date = start_date
    subscription.end_date = end_date
    subscription.status = "Active"
    subscription.company = frappe.defaults.get_defaults().get("company")
    subscription.append("plans", {"plan": pkg.subscription_plan})
    subscription.save()

    return subscription.name


@frappe.whitelist()
def renew_subscription(subscription_name):
    """Renew an existing ERPNext Subscription."""

    frappe.has_permission("Subscription", throw=True)
    sub = frappe.get_doc("Subscription", subscription_name)

    # Resolve Agency Package from Subscription
    package = _get_agency_package_from_subscription(subscription_name)
    if not package:
        frappe.throw(_("No agency package linked to this subscription"))

    # Extend end date
    new_end_date = add_months(sub.end_date, package.get("billing_cycle_months", 1))
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

    package = frappe.get_doc("Agency Package", subscription_check["package"])

    # Get current usage
    campaign_count = frappe.db.count("Marketing Campaign", filters={"customer": client})

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
        "Subscription",
        filters={
            "party_type": "Customer",
            "status": ["in", ["Active", "Trialling"]],
            "end_date": [">=", today()]
        }
    )

    # Count total clients
    total_clients = frappe.db.count(
        "Customer",
        filters={"customer_type": "Company"}
    )

    # Get expiring soon (next 30 days)
    expiring_soon = frappe.get_all(
        "Subscription",
        filters={
            "party_type": "Customer",
            "status": ["in", ["Active", "Trialling"]],
            "end_date": ["between", [today(), add_months(today(), 1)]]
        },
        fields=["name", "party as client", "end_date"],
        order_by="end_date asc"
    )

    return {
        "mode": "agency",
        "active_subscriptions": active_subs,
        "total_clients": total_clients,
        "expiring_soon": len(expiring_soon),
        "expiring_list": expiring_soon
    }
