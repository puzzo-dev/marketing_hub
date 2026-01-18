import frappe
from frappe import _
from frappe.utils import add_to_date, getdate, format_date

def get_context(context):
    context.no_cache = 1
    
    # Basic access check
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect
    
    # Get Dashboard Stats
    context.stats = get_dashboard_stats()
    
    # Get Active Campaigns
    context.active_campaigns = get_active_campaigns()
    
    # Get Recent Activities
    context.recent_activities = get_recent_activities()

def get_dashboard_stats():
    """Calculate high-level dashboard metrics"""
    today = getdate()
    month_start = today.replace(day=1)
    
    # Calculate Total Spend & Revenue (This Month)
    financials = frappe.db.sql("""
        SELECT 
            SUM(spend) as total_spend, 
            SUM(revenue) as total_revenue
        FROM `tabAnalytics Daily Log`
        WHERE log_date >= %s
    """, (month_start,), as_dict=1)[0]
    
    total_spend = financials.get('total_spend') or 0
    total_revenue = financials.get('total_revenue') or 0
    roas = (total_revenue / total_spend) if total_spend > 0 else 0
    
    # Count Total Leads
    total_leads = frappe.db.count("Lead", filters={
        "creation": (">=", month_start)
    })
    
    return {
        "spend": total_spend,
        "revenue": total_revenue,
        "roas": roas,
        "leads": total_leads,
        "month_name": format_date(today, "MMMM")
    }

def get_active_campaigns():
    """Fetch campaigns that are currently active"""
    return frappe.get_all("Campaign", 
        filters={"status": "In Progress"},
        fields=["name", "campaign_name", "start_date", "end_date"],
        limit=5,
        order_by="creation desc"
    )

def get_recent_activities():
    """Fetch recent campaign activities"""
    return frappe.get_all("Campaign Activity",
        fields=["name", "activity_name", "status", "scheduled_date", "activity_type"],
        limit=5,
        order_by="modified desc"
    )
