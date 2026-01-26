app_name = "marketing_hub"
app_title = "Marketing Hub"
app_publisher = "I-Varse Technologies"
app_description = "Frappe Framework based Marketing App for managing marketing operations of an organization"
app_email = "support@itechnologies.ng"
app_license = "mit"

# Apps
# ------------------

required_apps = ["frappe_whatsapp"]

add_to_apps_screen = [
    {
        "name": "marketing_hub",
        "logo": "/assets/marketing_hub/desk/logo.svg",
        "title": "Marketing Hub",
        "route": "/app/marketing-hub",
        "has_permission": "marketing_hub.api.permission.has_app_permission"
    }
]

desk_pages = [
    {
        "module": "Marketing Hub",
        "label": "Marketing Dashboard",
        "route": "/marketing_hub",
        "_route": "/marketing_hub",
        "_static": True,
        "icon": "broadcast",
    }
]

website_route_rules = [
    {
        "from_route": "/marketing/<path:app_path>",
        "to_route": "marketing",
    },
    {
        "from_route": "/marketing_hub/<path:app_path>",
        "to_route": "marketing_hub",
    },
]

# Fixtures
# --------
fixtures = [
    {
        "dt": "Custom Field",
        "filters": [
            [
                "name",
                "in",
                [

                    "Lead-utm_campaign",
                    "Lead-utm_source",
                    "Lead-utm_medium"
                ]
            ]
        ]
    },
    {
        "dt": "Workspace",
        "filters": [
            [
                "name",
                "in",
                [
                    "Marketing Hub"
                ]
            ]
        ]
    }
]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "marketing_hub",
# 		"logo": "/assets/marketing_hub/logo.png",
# 		"title": "Marketing Hub",
# 		"route": "/marketing_hub",
# 		"has_permission": "marketing_hub.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/marketing_hub/css/marketing_hub.css"
app_include_js = "/assets/marketing_hub/js/marketing_hub.js"

# include js, css files in header of web template
web_include_css = "/assets/marketing_hub/css/portal.css"
# web_include_js = "/assets/marketing_hub/js/marketing_hub.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "marketing_hub/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views

# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "marketing_hub/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "marketing_hub.utils.jinja_methods",
# 	"filters": "marketing_hub.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "marketing_hub.install.before_install"
# after_install = "marketing_hub.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "marketing_hub.uninstall.before_uninstall"
# after_uninstall = "marketing_hub.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "marketing_hub.utils.before_app_install"
# after_app_install = "marketing_hub.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "marketing_hub.utils.before_app_uninstall"
# after_app_uninstall = "marketing_hub.utils.after_app_uninstall"

after_migrate = "marketing_hub.setup.setup_notifications"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "marketing_hub.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
	"Campaign": "marketing_hub.utils.permissions.get_campaign_permission_query_conditions",
	"Campaign Activity": "marketing_hub.utils.permissions.get_campaign_activity_permission_query_conditions",
	"Marketing Segment": "marketing_hub.utils.permissions.get_marketing_segment_permission_query_conditions",
}

has_permission = {
	"Campaign": "marketing_hub.utils.permissions.has_campaign_permission",
	"Campaign Activity": "marketing_hub.utils.permissions.has_campaign_activity_permission",
}

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Lead": {
        "on_update": "marketing_hub.utils.attribution_engine.get_real_lead_source"
    },
    "Campaign Activity": {
        "on_update": "marketing_hub.utils.omni_blast.execute_if_scheduled"
    }
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    "daily": [],
    "all": [
        "marketing_hub.utils.auto_post.publish_scheduled_posts",
        "marketing_hub.utils.analytics_sync.sync_all_connectors"
    ]
}

# Testing
# -------

# before_tests = "marketing_hub.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "marketing_hub.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "marketing_hub.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["marketing_hub.utils.before_request"]
# after_request = ["marketing_hub.utils.after_request"]

# Job Events
# ----------
# before_job = ["marketing_hub.utils.before_job"]
# after_job = ["marketing_hub.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"marketing_hub.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

