import frappe
from frappe import _


def after_install():
    """Seed attribution models, set the default, and run base setup on fresh install."""
    from marketing_hub.patches.v1_0.seed_attribution_models import execute as seed_attribution_models

    seed_attribution_models()
    set_default_attribution_model()
    setup_file_folder()
    setup_notifications()


def set_default_attribution_model():
    """Set Last Touch as the default attribution model in Marketing Hub Settings."""
    if not frappe.db.exists("Attribution Model", "Last Touch"):
        return

    settings = frappe.get_single("Marketing Hub Settings")
    if not settings.default_attribution_model:
        settings.default_attribution_model = "Last Touch"
        settings.save(ignore_permissions=True)


def setup_file_folder():
    """Create Marketing Hub folder in Frappe Files for uploaded assets."""
    if not frappe.db.exists("File", {"file_name": "Marketing Hub", "is_folder": 1}):
        folder = frappe.get_doc({
            "doctype": "File",
            "file_name": "Marketing Hub",
            "is_folder": 1,
            "folder": "Home"
        })
        folder.insert(ignore_permissions=True)
        frappe.db.commit()

def setup_notifications():
    """
    Create default Notification records for Marketing Hub events.
    Uses Standard Frappe Notification System.
    """
    notifications = [
        {
            "name": "Campaign Completion Alert",
            "subject": "Campaign Completed: {{ doc.name }}",
            "document_type": "Marketing Campaign",
            "event": "Save",
            "condition": "doc.status == 'Completed'",
            "channel": "Email",
            "recipients": [
                {"receiver_by_document_field": "owner"}
            ],
            "message": """
<h3>Campaign Completed</h3>
<p>The campaign <b>{{ doc.campaign_name }}</b> has been marked as Completed.</p>
<p>View details: <a href="{{ frappe.utils.get_url_to_form(doc.doctype, doc.name) }}">{{ doc.name }}</a></p>
            """
        },
        {
            "name": "Omni Blast Published",
            "subject": "Blast Published: {{ doc.blast_title }}",
            "document_type": "Omni Blast",
            "event": "Save",
            "condition": "doc.status == 'Published'",
            "channel": "Email",
            "recipients": [
                {"receiver_by_document_field": "owner"}
            ],
            "message": """
<h3>Omni Blast Published</h3>
<p>The blast <b>{{ doc.blast_title }}</b> has been successfully published to the following networks:</p>
<p>{{ doc.networks }}</p>
<p>View details: <a href="{{ frappe.utils.get_url_to_form(doc.doctype, doc.name) }}">{{ doc.name }}</a></p>
            """
        }
    ]

    count = 0
    for notif in notifications:
        if not frappe.db.exists("Notification", notif["name"]):
            doc = frappe.new_doc("Notification")
            doc.update(notif)
            # Add System Manager as receiver if owner query fails (fallback)
            doc.append("recipients", {
                 "receiver_by_role": "System Manager"
            })
            doc.insert(ignore_permissions=True)
            count += 1
            
    frappe.db.commit()
    return f"Created {count} default notifications."
