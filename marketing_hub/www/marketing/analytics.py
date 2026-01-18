import frappe
from frappe.utils import getdate, add_to_date

def get_context(context):
    context.no_cache = 1
    
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect
    
    # Get date range (default last 30 days)
    to_date = getdate()
    from_date = add_to_date(to_date, days=-30)
    
    context.analytics = get_analytics_data(from_date, to_date)
    context.connectors = frappe.get_all("Analytics Connector", fields=["name", "connector_name", "platform", "sync_status", "last_sync_date"])

def get_analytics_data(from_date, to_date):
    """Fetch aggregated analytics data"""
    data = frappe.db.sql("""
        SELECT 
            channel,
            SUM(impressions) as impressions,
            SUM(clicks) as clicks,
            SUM(conversions) as conversions,
            SUM(spend) as spend,
            SUM(revenue) as revenue
        FROM `tabAnalytics Daily Log`
        WHERE log_date BETWEEN %s AND %s
        GROUP BY channel
    """, (from_date, to_date), as_dict=1)
    
    # Calculate derived metrics
    for row in data:
        row.spend = row.spend or 0
        row.revenue = row.revenue or 0
        row.roas = (row.revenue / row.spend) if row.spend > 0 else 0
        row.ctr = (row.clicks / row.impressions * 100) if row.impressions > 0 else 0
        row.cpc = (row.spend / row.clicks) if row.clicks > 0 else 0
        
    return data
