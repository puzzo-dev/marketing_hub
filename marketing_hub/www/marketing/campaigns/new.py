import frappe

def get_context(context):
    context.no_cache = 1
    
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

@frappe.whitelist()
def create_campaign(campaign_name, start_date, end_date=None, description=None):
    """Create a new campaign from the portal wizard"""
    try:
        doc = frappe.new_doc("Campaign")
        doc.campaign_name = campaign_name
        doc.start_date = start_date
        doc.end_date = end_date
        doc.description = description
        doc.save()
        
        return {"status": "Success", "message": "Campaign created successfully", "name": doc.name}
    except Exception as e:
        return {"status": "Error", "message": str(e)}
