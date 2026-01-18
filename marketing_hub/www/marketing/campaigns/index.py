import frappe
from frappe import _

def get_context(context):
    context.no_cache = 1
    
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect
    
    # Get all campaigns with stats
    context.campaigns = get_campaigns_list()

def get_campaigns_list():
    """Fetch campaigns with calculated ROI metrics"""
    campaigns = frappe.get_all("Campaign",
        fields=["name", "campaign_name", "status", "start_date", "end_date"],
        order_by="creation desc"
    )
    
    for campaign in campaigns:
        # Fetch stats for each campaign
        stats = frappe.db.sql("""
            SELECT 
                SUM(spend) as total_spend, 
                SUM(revenue) as total_revenue,
                SUM(clicks) as total_clicks,
                SUM(conversions) as total_conversions
            FROM `tabAnalytics Daily Log`
            WHERE campaign = %s
        """, (campaign.name,), as_dict=1)[0]
        
        campaign.spend = stats.get('total_spend') or 0
        campaign.revenue = stats.get('total_revenue') or 0
        campaign.roas = (campaign.revenue / campaign.spend) if campaign.spend > 0 else 0
        campaign.conversions = stats.get('total_conversions') or 0
        
    return campaigns
