from frappe import _

def get_data():
    return {
        "Marketing Hub": {
            "color": "#3478F6",
            "icon": "octicon octicon-megaphone",
            "label": _("Marketing Hub"),
            "type": "module",
            "items": [
                {"type": "page", "name": "marketing-hub", "label": _("Dashboard"), "icon": "bar-chart"},
                {"type": "doctype", "name": "Campaign", "label": _("Campaigns")},
                {"type": "doctype", "name": "Social Post", "label": _("Social Posts")},
                {"type": "doctype", "name": "Marketing Segment", "label": _("Segments")},
                {"type": "doctype", "name": "Marketing Template", "label": _("Templates")},
                {"type": "doctype", "name": "Ad Account", "label": _("Ad Accounts")},
                {"type": "doctype", "name": "Analytics Connector", "label": _("Analytics")},
                {"type": "doctype", "name": "Marketing Hub Setup", "label": _("Setup")},
                {"type": "doctype", "name": "Agency Package", "label": _("Packages")},
                {"type": "doctype", "name": "Client Subscription", "label": _("Subscriptions")},
            ]
        }
    }
