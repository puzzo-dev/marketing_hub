import os
import re

import frappe
from frappe import _


no_cache = 1


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    # Get Vite-built asset paths from the compiled index.html
    context.frontend_assets = _get_frontend_assets()

    # Pass installed apps to frontend for app switcher
    context.installed_apps = get_apps_for_user()
    
    # Pass boot data that can't be computed in Jinja sandbox
    context.user_fullname = frappe.utils.get_fullname(frappe.session.user)
    context.user_image = frappe.db.get_value("User", frappe.session.user, "user_image") or ""
    context.socketio_port = frappe.conf.get("socketio_port", 9000)
    context.sitename = frappe.local.site
    context.user_roles = frappe.get_roles(frappe.session.user)

    return context


def _get_frontend_assets():
    """Read the Vite-built public/frontend/index.html and extract asset paths."""
    app_path = frappe.get_app_path("marketing_hub")
    built_index = os.path.join(app_path, "public", "frontend", "index.html")

    assets = {
        "scripts": [],
        "modulepreloads": [],
        "stylesheets": [],
    }

    if not os.path.exists(built_index):
        return assets

    with open(built_index, "r") as f:
        html = f.read()

    # Extract <script type="module" ... src="...">
    for match in re.finditer(r'<script\s+type="module"\s+crossorigin\s+src="([^"]+)"', html):
        assets["scripts"].append(match.group(1))

    # Extract <link rel="modulepreload" ... href="...">
    for match in re.finditer(r'<link\s+rel="modulepreload"\s+crossorigin\s+href="([^"]+)"', html):
        assets["modulepreloads"].append(match.group(1))

    # Extract <link rel="stylesheet" ... href="...">
    for match in re.finditer(r'<link\s+rel="stylesheet"\s+crossorigin\s+href="([^"]+)"', html):
        assets["stylesheets"].append(match.group(1))

    return assets


def get_apps_for_user():
    """Get list of apps with their metadata (logo, title, route) for current user"""
    all_apps = []

    for app in frappe.get_installed_apps():
        hooks = frappe.get_hooks(app_name=app)
        apps_config = hooks.get("add_to_apps_screen", [])

        for app_config in apps_config:
            has_permission = app_config.get("has_permission")
            if has_permission:
                try:
                    if not frappe.get_attr(has_permission)():
                        continue
                except (frappe.ValidationError, frappe.DoesNotExistError, AttributeError):
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
        "installed_apps": get_apps_for_user(),
        "user_roles": frappe.get_roles(frappe.session.user),
    }


# API Methods are in marketing_hub.www.marketing.api
# They are already decorated with @frappe.whitelist() and accessible
# via their full dotted path from the frontend.
# No re-import needed here.
