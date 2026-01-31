import frappe
from frappe import _
from frappe.utils import getdate, add_to_date

def get_context(context):
    context.no_cache = 1
    
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect
    
    return context

@frappe.whitelist()
def get_analytics_data():
    """Get analytics overview data"""
    try:
        return {
            "channel_performance": get_channel_performance(),
            "daily_metrics": get_daily_metrics(),
        }
    except Exception as e:
        frappe.log_error(f"Analytics data error: {str(e)}")
        return {
            "channel_performance": [],
            "daily_metrics": [],
        }

def get_channel_performance():
    """Get aggregated performance by channel"""
    today = getdate()
    last_30_days = add_to_date(today, days=-30)
    
    try:
        data = frappe.db.sql("""
            SELECT 
                channel,
                SUM(spend) as spend,
                SUM(revenue) as revenue,
                SUM(clicks) as clicks,
                SUM(impressions) as impressions,
                SUM(conversions) as conversions,
                CASE 
                    WHEN SUM(spend) > 0 THEN SUM(revenue) / SUM(spend)
                    ELSE 0
                END as roas,
                CASE
                    WHEN SUM(impressions) > 0 THEN (SUM(clicks) / SUM(impressions)) * 100
                    ELSE 0
                END as ctr
            FROM `tabAnalytics Daily Log`
            WHERE log_date >= %s
            GROUP BY channel
            ORDER BY spend DESC
        """, (last_30_days,), as_dict=1)
        
        return data
    except:
        return []

def get_daily_metrics():
    """Get daily metrics for charts (last 30 days)"""
    today = getdate()
    last_30_days = add_to_date(today, days=-30)
    
    try:
        data = frappe.db.sql("""
            SELECT 
                log_date as date,
                SUM(spend) as spend,
                SUM(revenue) as revenue,
                SUM(impressions) as impressions,
                SUM(clicks) as clicks
            FROM `tabAnalytics Daily Log`
            WHERE log_date >= %s
            GROUP BY log_date
            ORDER BY log_date ASC
        """, (last_30_days,), as_dict=1)
        
        return data
    except:
        return []
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
