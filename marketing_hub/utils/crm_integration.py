"""
CRM Integration for Marketing Hub
Extends CRM app functionality with marketing-specific features
"""

import frappe
from frappe import _


def sync_lead_with_crm(lead_name, marketing_data=None):
	"""Sync Lead data with CRM app if installed"""
	try:
		if not frappe.db.exists("DocType", "CRM Lead"):
			return False

		lead = frappe.get_doc("Lead", lead_name)

		# Check if CRM Lead already exists
		crm_lead = frappe.db.get_value(
			"CRM Lead",
			{"email_id": lead.email_id},
			"name"
		)

		if not crm_lead:
			# Create new CRM Lead
			crm_lead_doc = frappe.new_doc("CRM Lead")
			crm_lead_doc.first_name = lead.first_name
			crm_lead_doc.last_name = lead.last_name or ""
			crm_lead_doc.email_id = lead.email_id
			crm_lead_doc.mobile_no = lead.mobile_no
			crm_lead_doc.organization = lead.company_name
			crm_lead_doc.lead_owner = lead.lead_owner

			# Add marketing attribution data
			if marketing_data:
				crm_lead_doc.source = marketing_data.get("utm_source", lead.source)
				# Ensure we don't break CRM Campaign link if it expects standard Campaign
				# We put the string name, let CRM handle it (or fail gracefully)
				crm_lead_doc.campaign = marketing_data.get("campaign")

			crm_lead_doc.insert()

			# Link ERPNext Lead to CRM Lead
			lead.crm_lead = crm_lead_doc.name
			lead.save()

			return crm_lead_doc.name
		else:
			# Update existing CRM Lead with marketing data
			if marketing_data:
				frappe.db.set_value("CRM Lead", crm_lead, {
					"source": marketing_data.get("utm_source"),
					"campaign": marketing_data.get("campaign")
				})

			return crm_lead
	except (frappe.ValidationError, frappe.DoesNotExistError) as e:
		frappe.log_error(f"CRM sync error: {str(e)}", "Marketing Hub CRM Integration")
		return False


def get_crm_deal_value(lead_name):
	"""Get deal value from CRM if lead was converted"""
	try:
		if not frappe.db.exists("DocType", "CRM Deal"):
			return 0

		lead = frappe.get_doc("Lead", lead_name)

		# Find CRM Deal linked to this lead
		deals = frappe.get_all(
			"CRM Deal",
			filters={"lead": lead.crm_lead if hasattr(lead, "crm_lead") else None},
			fields=["name", "deal_value", "status"],
			limit=1
		)

		if deals and deals[0].status == "Won":
			return deals[0].deal_value or 0

		return 0
	except (frappe.ValidationError, frappe.DoesNotExistError):
		return 0


def create_crm_activity_from_campaign(campaign_name, lead_name, activity_type="Email"):
	"""Create CRM activity when marketing campaign interacts with lead"""
	try:
		if not frappe.db.exists("DocType", "CRM Lead"):
			return False

		lead = frappe.get_doc("Lead", lead_name)
		crm_lead = lead.crm_lead if hasattr(lead, "crm_lead") else None

		if not crm_lead:
			# Try to sync first
			crm_lead = sync_lead_with_crm(lead_name)

		if not crm_lead:
			return False

		# Check if CRM activities exist
		if frappe.db.exists("DocType", "CRM Activities"):
			activity = frappe.new_doc("CRM Activities")
			activity.lead = crm_lead
			activity.activity_type = activity_type
			activity.reference_doctype = "Marketing Campaign"
			activity.reference_docname = campaign_name
			activity.insert()
			return activity.name

		return False
	except (frappe.ValidationError, frappe.DoesNotExistError) as e:
		frappe.log_error(f"CRM activity creation error: {str(e)}", "Marketing Hub CRM Integration")
		return False


def get_lead_engagement_score(lead_name, crm_lead=None):
	"""Calculate lead engagement score based on CRM interactions and behavioral data"""
	try:
		if not crm_lead and frappe.db.exists("DocType", "CRM Lead"):
			crm_lead = frappe.db.get_value("Lead", lead_name, "crm_lead")

		score = 0

		# Count email opens from standard Frappe Email Tracker
		if frappe.db.exists("DocType", "Email Tracker"):
			opens = frappe.db.count("Email Tracker", {
				"reference_doctype": "Lead",
				"reference_name": lead_name,
				"status": "Opened"
			})
			score += opens * 5

		# Count communications (emails sent/received)
		email_count = frappe.db.count("Communication", {
			"reference_doctype": "Lead",
			"reference_name": lead_name,
			"communication_type": "Communication"
		})
		score += email_count * 2

		if crm_lead:
			# Count calls
			if frappe.db.exists("DocType", "CRM Call Log"):
				call_count = frappe.db.count("CRM Call Log", {"lead": crm_lead})
				score += call_count * 10

			# Count WhatsApp messages
			if frappe.db.exists("DocType", "WhatsApp Message"):
				wa_count = frappe.db.count("WhatsApp Message", {
					"reference_doctype": "CRM Lead",
					"reference_name": crm_lead,
					"type": "Incoming"
				})
				score += wa_count * 8

			# Count CRM Activities
			if frappe.db.exists("DocType", "CRM Activities"):
				activity_count = frappe.db.count("CRM Activities", {"lead": crm_lead})
				score += activity_count * 5

		return score
	except (frappe.ValidationError, frappe.DoesNotExistError) as e:
		frappe.log_error(f"Engagement score error: {str(e)}", "Marketing Hub CRM Integration")
		return 0

def batch_update_engagement_scores():
	"""Nightly job to calculate and cache engagement scores on Lead doctype"""
	try:
		# Process in batches to avoid memory issues
		batch_size = 500
		offset = 0
		while True:
			leads = frappe.get_all(
				"Lead",
				fields=["name", "crm_lead"],
				limit_page_length=batch_size,
				limit_start=offset
			)
			if not leads:
				break
			for lead in leads:
				score = get_lead_engagement_score(lead.name, lead.crm_lead)
				frappe.db.set_value("Lead", lead.name, "engagement_score", score, update_modified=False)
			frappe.db.commit()
			offset += batch_size
	except (frappe.ValidationError, frappe.DatabaseError) as e:
		frappe.log_error(f"Batch engagement score error: {str(e)}", "Marketing Hub CRM Integration")


@frappe.whitelist()
def get_crm_dashboard_data(campaign=None):
	"""Get CRM-integrated dashboard data for marketing"""
	try:
		if not frappe.db.exists("DocType", "CRM Lead"):
			return {"error": "CRM app not installed"}

		data = {}

		# Get leads from campaign
		# Use utm_campaign to find leads linked to Marketing Campaign
		if campaign:
			leads = frappe.get_all(
				"Lead",
				filters={"utm_campaign": campaign},
				fields=["name", "crm_lead", "status", "email_id"]
			)

			data["total_leads"] = len(leads)

			# Count converted leads
			converted = 0
			total_deal_value = 0

			crm_leads = [lead.crm_lead for lead in leads if lead.crm_lead]
			if crm_leads:
				deals = frappe.get_all(
					"CRM Deal",
					filters={"lead": ["in", crm_leads]},
					fields=["lead", "status", "deal_value"]
				)
				converted_leads = set()
				for deal in deals:
					converted_leads.add(deal.lead)
					if deal.status == "Won":
						total_deal_value += deal.deal_value or 0
				converted = len(converted_leads)

			data["converted_leads"] = converted
			data["conversion_rate"] = (converted / len(leads) * 100) if leads else 0
			data["total_revenue"] = total_deal_value
		else:
			# Overall stats
			data["total_leads"] = frappe.db.count("CRM Lead")
			data["total_deals"] = frappe.db.count("CRM Deal")
			data["won_deals"] = frappe.db.count("CRM Deal", {"status": "Won"})

		return data
	except (frappe.ValidationError, frappe.DatabaseError) as e:
		frappe.log_error(f"CRM dashboard error: {str(e)}", "Marketing Hub CRM Integration")
		return {"error": str(e)}


def link_whatsapp_to_campaign(whatsapp_message_name, campaign_name):
	"""Link WhatsApp message to campaign for tracking"""
	try:
		if not frappe.db.exists("DocType", "WhatsApp Message"):
			return False

		wa_message = frappe.get_doc("WhatsApp Message", whatsapp_message_name)

		# Add campaign reference
		frappe.db.set_value(
			"WhatsApp Message",
			wa_message.name,
			"campaign_reference",
			campaign_name
		)

		# If there's a CRM Lead linked, create activity
		if wa_message.reference_doctype == "CRM Lead":
			create_crm_activity_from_campaign(
				campaign_name,
				wa_message.reference_name,
				"WhatsApp"
			)

		return True
	except (frappe.ValidationError, frappe.DoesNotExistError) as e:
		frappe.log_error(f"WhatsApp campaign link error: {str(e)}", "Marketing Hub CRM Integration")
		return False


def get_campaign_performance_with_crm(campaign_name):
	"""Get detailed campaign performance including CRM metrics"""
	try:
		performance = {
			"campaign": campaign_name,
			"leads": 0,
			"crm_leads": 0,
			"deals": 0,
			"won_deals": 0,
			"total_revenue": 0,
			"avg_deal_size": 0,
			"conversion_to_deal": 0,
			"win_rate": 0
		}

		# Get all leads from campaign using UTM filter
		leads = frappe.get_all(
			"Lead",
			filters={"utm_campaign": campaign_name},
			fields=["name", "crm_lead"]
		)

		performance["leads"] = len(leads)

		if not frappe.db.exists("DocType", "CRM Lead"):
			return performance

		# Get CRM metrics
		crm_leads = [l.crm_lead for l in leads if l.crm_lead]
		performance["crm_leads"] = len(crm_leads)

		if crm_leads:
			deals = frappe.get_all(
				"CRM Deal",
				filters={"lead": ["in", crm_leads]},
				fields=["name", "status", "deal_value"]
			)

			performance["deals"] = len(deals)

			won_deals = [d for d in deals if d.status == "Won"]
			performance["won_deals"] = len(won_deals)

			total_revenue = sum(d.deal_value or 0 for d in won_deals)
			performance["total_revenue"] = total_revenue

			if won_deals:
				performance["avg_deal_size"] = total_revenue / len(won_deals)

			if performance["leads"] > 0:
				performance["conversion_to_deal"] = (performance["deals"] / performance["leads"]) * 100

			if performance["deals"] > 0:
				performance["win_rate"] = (performance["won_deals"] / performance["deals"]) * 100

		return performance
	except (frappe.ValidationError, frappe.DatabaseError) as e:
		frappe.log_error(f"Campaign performance error: {str(e)}", "Marketing Hub CRM Integration")
		return {"error": str(e)}
