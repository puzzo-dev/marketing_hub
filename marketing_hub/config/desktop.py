from frappe import _

def get_data():
    return {
        "Marketing Hub": {
            "color": "#DC2626",
            "icon": "fa fa-bullhorn",
            "label": _("Marketing Hub"),
            "type": "module",
            "items": [
                {"type": "doctype", "name": "Marketing Hub Settings", "label": _("Settings")},
                {"type": "doctype", "name": "Marketing Campaign", "label": _("Campaigns")},
                {"type": "doctype", "name": "Social Post", "label": _("Social Posts")},
                {"type": "doctype", "name": "Marketing Segment", "label": _("Segments")},
                {"type": "doctype", "name": "Marketing Template", "label": _("Templates")},
                {"type": "doctype", "name": "Ad Account", "label": _("Ad Accounts")},
                {"type": "doctype", "name": "Analytics Connector", "label": _("Analytics Connectors")},
                {"type": "doctype", "name": "Analytics Daily Log", "label": _("Analytics Logs")},
                {"type": "doctype", "name": "Social Media Network", "label": _("Social Networks")},
                {"type": "doctype", "name": "Attribution Model", "label": _("Attribution Models")},
                {"type": "doctype", "name": "Marketing Expense", "label": _("Expenses")},
                {"type": "doctype", "name": "Marketing Ledger Entry", "label": _("Ledger")},
            ]
        }
    }
