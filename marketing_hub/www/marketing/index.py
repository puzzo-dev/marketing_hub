import frappe
from frappe import _
from frappe.utils import add_to_date, getdate, format_date

def get_context(context):
    context.no_cache = 1

    # Basic access check
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    # Pass installed apps to frontend - get full app data with logos
    context.installed_apps = get_apps_for_user()

    return context

def get_apps_for_user():
    """Get list of apps with their metadata (logo, title, route) for current user"""
    from frappe.config import get_modules_from_all_apps_for_user
    
    all_apps = []
    
    # Get apps from hooks
    for app in frappe.get_installed_apps():
        hooks = frappe.get_hooks(app_name=app)
        apps_config = hooks.get("add_to_apps_screen", [])
        
        for app_config in apps_config:
            # Check permission if specified
            has_permission = app_config.get("has_permission")
            if has_permission:
                try:
                    if not frappe.get_attr(has_permission)():
                        continue
                except:
                    continue
            
            all_apps.append({
                "name": app_config.get("name"),
                "logo": app_config.get("logo"),
                "title": app_config.get("title"),
                "route": app_config.get("route")
            })
    
    return all_apps

@frappe.whitelist()
def get_context_for_dev():
    return {
        "session": frappe.session,
    }

# API Methods - Import from api.py module
from marketing_hub.www.marketing.api import (
    get_dashboard_data,
    get_analytics_data,
    get_campaign_list,
    get_social_posts,
    create_campaign,
    create_social_post
)

# Re-export with whitelist decorator
get_dashboard_data = frappe.whitelist()(get_dashboard_data)
get_analytics_data = frappe.whitelist()(get_analytics_data)
get_campaign_list = frappe.whitelist()(get_campaign_list)
get_social_posts = frappe.whitelist()(get_social_posts)
create_campaign = frappe.whitelist()(create_campaign)
create_social_post = frappe.whitelist()(create_social_post)
