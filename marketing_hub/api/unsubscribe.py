import hmac
import hashlib

import frappe
from frappe import _


def _get_unsubscribe_secret():
    """Get the site secret used for unsubscribe token signing."""
    return frappe.local.conf.get("secret_key", frappe.local.site)


def generate_unsubscribe_token(contact_id, campaign=None):
    """Generate a signed HMAC token for unsubscribe links."""
    secret = _get_unsubscribe_secret()
    payload = f"{contact_id}:{campaign or ''}"
    return hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()[:32]


@frappe.whitelist(allow_guest=True)
def handle_unsubscribe(contact_id, token, channel="Email", reason="Unsubscribed", campaign=None):
    """
    Handle unsubscribe requests from public links.
    Adds the contact to the Suppression List.
    Requires a valid HMAC token to prevent abuse.
    """
    if not contact_id:
        frappe.throw(_("Contact ID (Email or Phone) is required"))

    if not token:
        frappe.throw(_("Unsubscribe token is required"), frappe.AuthenticationError)

    expected_token = generate_unsubscribe_token(contact_id, campaign)
    if not hmac.compare_digest(expected_token, token):
        frappe.throw(_("Invalid unsubscribe token"), frappe.AuthenticationError)

    # Check if already suppressed
    existing = frappe.get_all(
        "Suppression List",
        filters={"contact_id": contact_id},
        fields=["name", "channel"]
    )

    if existing:
        doc = frappe.get_doc("Suppression List", existing[0].name)
        if doc.channel != "All" and channel == "All":
            doc.channel = "All"
            doc.save()
    else:
        # Create new suppression entry
        doc = frappe.get_doc({
            "doctype": "Suppression List",
            "contact_id": contact_id,
            "channel": channel,
            "reason": reason,
            "campaign": campaign
        })
        doc.insert()

    frappe.db.commit()
    return {"status": "success", "message": _("You have been successfully unsubscribed.")}
