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

# API Methods for Vue.js Frontend
@frappe.whitelist()
def get_dashboard_data():
    """Get dashboard data with error handling for missing doctypes"""
    try:
        return {
            "stats": get_dashboard_stats(),
            "active_campaigns": get_active_campaigns(),
        }
    except Exception as e:
        frappe.log_error(f"Dashboard data error: {str(e)}")
        # Return default data structure
        return {
            "stats": {
                "spend": 0,
                "revenue": 0,
                "roas": 0,
                "leads": 0,
                "month_name": format_date(getdate(), "MMMM")
            },
            "active_campaigns": []
        }

def get_dashboard_stats():
    """Calculate high-level dashboard metrics"""
    today = getdate()
    month_start = today.replace(day=1)

    try:
        # Calculate Total Spend & Revenue (This Month) from Analytics Daily Log
        financials = frappe.db.sql("""
            SELECT
                SUM(spend) as total_spend,
                SUM(revenue) as total_revenue
            FROM `tabAnalytics Daily Log`
            WHERE log_date >= %s
        """, (month_start,), as_dict=1)
        
        total_spend = financials[0].get('total_spend') if financials else 0
        total_revenue = financials[0].get('total_revenue') if financials else 0
        total_spend = total_spend or 0
        total_revenue = total_revenue or 0
        roas = (total_revenue / total_spend) if total_spend > 0 else 0
    except Exception:
        total_spend = 0
        total_revenue = 0
        roas = 0

    # Count Total Leads - check if Lead doctype exists (from ERPNext/CRM)
    try:
        if frappe.db.exists("DocType", "Lead"):
            total_leads = frappe.db.count("Lead", filters={
                "creation": (">=", month_start)
            })
        else:
            total_leads = 0
    except Exception:
        total_leads = 0

    return {
        "spend": total_spend,
        "revenue": total_revenue,
        "roas": roas,
        "leads": total_leads,
        "month_name": format_date(today, "MMMM")
    }

def get_active_campaigns():
    """Fetch recent campaigns - check if Campaign doctype exists"""
    try:
        if frappe.db.exists("DocType", "Campaign"):
            return frappe.get_all("Campaign",
                filters={"docstatus": ["<", 2]},  # Not cancelled
                fields=["name", "campaign_name", "description", "creation"],
                limit=5,
                order_by="modified desc"
            )
        else:
            return []
    except Exception:
        return []

def get_recent_activities():
    """Fetch recent campaign activities"""
    return frappe.get_all("Campaign Activity",
        fields=["name", "activity_name", "status", "scheduled_date", "activity_type"],
        limit=5,
        order_by="modified desc"
    )
