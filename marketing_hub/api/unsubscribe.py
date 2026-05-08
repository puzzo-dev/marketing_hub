import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def handle_unsubscribe(contact_id, channel="Email", reason="Unsubscribed", campaign=None):
    """
    Handle unsubscribe requests from public links.
    Adds the contact to the Suppression List.
    """
    if not contact_id:
        frappe.throw(_("Contact ID (Email or Phone) is required"))
        
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
            doc.save(ignore_permissions=True)
    else:
        # Create new suppression entry
        doc = frappe.get_doc({
            "doctype": "Suppression List",
            "contact_id": contact_id,
            "channel": channel,
            "reason": reason,
            "campaign": campaign
        })
        doc.insert(ignore_permissions=True)
        
    frappe.db.commit()
    return {"status": "success", "message": _("You have been successfully unsubscribed.")}
