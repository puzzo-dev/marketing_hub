# -*- coding: utf-8 -*-
"""
Campaign Engine Registry & Orchestrator

Pure orchestration layer. Dispatches to engine-specific DocTypes.
Zero channel-specific logic lives here.
"""

import frappe
from frappe import _

# Engine type -> expected DocType name
ENGINE_DOC_TYPES = {
	"Email Blast": "Newsletter",
	"Email Sequence": "Email Campaign",
	"WhatsApp": "Bulk WhatsApp Message",
	"SMS": "SMS Campaign",
	"Social Media": "Social Post",
	"Meta Ads": "Meta Ads Campaign",
	"OOH": "OOH Campaign",
}

# Engine type -> method name on the engine doc to call for execution
_EXECUTE_METHOD = "execute"


def get_doctype_for_engine_type(engine_type):
	"""Return the expected DocType name for a given engine type."""
	return ENGINE_DOC_TYPES.get(engine_type)


def validate_engine(engine_row):
	"""Validate that an engine row references an existing document of the correct type."""
	doctype = get_doctype_for_engine_type(engine_row.engine_type)
	if doctype and engine_row.engine_doc_type != doctype:
		frappe.throw(
			_(
				"Engine Type '{0}' must reference DocType '{1}' (row references '{2}')"
			).format(engine_row.engine_type, doctype, engine_row.engine_doc_type)
		)

	if engine_row.engine_doc and not frappe.db.exists(engine_row.engine_doc_type, engine_row.engine_doc):
		frappe.throw(
			_(
				"{0} '{1}' does not exist"
			).format(engine_row.engine_doc_type, engine_row.engine_doc)
		)


@frappe.whitelist()
def execute_engine(engine_row):
	"""
	Execute a single engine by dispatching to its document's execute() method.

	Args:
		engine_row: CampaignEngine Document row (or dict with engine_type, engine_doc_type, engine_doc)

	Returns:
		dict: execution result with status and engine details
	"""
	validate_engine(engine_row)

	engine_doc = frappe.get_doc(engine_row.engine_doc_type, engine_row.engine_doc)

	# Update engine row status before execution
	if hasattr(engine_row, "name") and engine_row.name:
		frappe.db.set_value(
			"Campaign Engine",
			engine_row.name,
			{"status": "Running", "results_json": "{}"},
		)

	try:
		# Dispatch to the engine document's execute() method
		if hasattr(engine_doc, _EXECUTE_METHOD):
			result = getattr(engine_doc, _EXECUTE_METHOD)()
		else:
			# Fallback for external DocTypes without execute()
			result = _execute_external_engine(engine_row, engine_doc)
	except Exception as e:
		frappe.log_error(
			title=_("Engine Execution Failed"),
			message=f"Engine {engine_row.engine_type} ({engine_row.engine_doc}) failed: {str(e)}",
		)
		result = {"status": "Failed", "error": str(e)}

	# Update engine row with result
	if hasattr(engine_row, "name") and engine_row.name:
		status = result.get("status", "Failed")
		frappe.db.set_value(
			"Campaign Engine",
			engine_row.name,
			{
				"status": status,
				"results_json": frappe.as_json(result),
			},
		)

	return {
		"engine_type": engine_row.engine_type,
		"engine_doc": engine_row.engine_doc,
		"status": result.get("status", "Failed"),
		"results": result,
	}


def _execute_external_engine(engine_row, engine_doc):
	"""
	Handle execution for external DocTypes that don't have an execute() method.
	"""
	engine_type = engine_row.engine_type

	if engine_type == "Email Blast":
		return _execute_newsletter(engine_doc)
	elif engine_type == "Email Sequence":
		return _execute_email_campaign(engine_doc)
	elif engine_type == "WhatsApp":
		return _execute_whatsapp(engine_doc)
	elif engine_type == "Social Media":
		return _execute_social_media(engine_doc)
	else:
		return {
			"status": "Failed",
			"error": f"No execute() method found on {engine_row.engine_doc_type} and no external handler for {engine_type}",
		}


def _execute_newsletter(newsletter):
	"""Trigger Newsletter send."""
	try:
		if hasattr(newsletter, "send_emails"):
			newsletter.send_emails()
			return {"status": "Completed", "message": "Newsletter queued for sending"}
		else:
			return {"status": "Failed", "error": "Newsletter does not have send_emails method"}
	except Exception as e:
		return {"status": "Failed", "error": str(e)}


def _execute_email_campaign(email_campaign):
	"""Email Campaign is hook-driven; we just mark it active."""
	try:
		email_campaign.status = "In Progress"
		email_campaign.save()
		return {
			"status": "Completed",
			"message": "Email Campaign is now active. Emails will be sent according to schedule.",
		}
	except Exception as e:
		return {"status": "Failed", "error": str(e)}


def _execute_whatsapp(bulk_message):
	"""Submit BulkWhatsAppMessage to trigger its queue."""
	try:
		if bulk_message.docstatus != 1:
			bulk_message.submit()
		return {"status": "Completed", "message": "WhatsApp bulk message queued"}
	except Exception as e:
		return {"status": "Failed", "error": str(e)}


def _execute_social_media(social_post):
	"""Publish Social Post via the social adapter."""
	from marketing_hub.utils.social_adapter import publish_to_platform
	try:
		result = publish_to_platform(social_post)
		return {"status": "Completed" if result.get("success") else "Failed", "result": result}
	except Exception as e:
		return {"status": "Failed", "error": str(e)}


@frappe.whitelist()
def execute_engines_for_campaign(campaign_name):
	"""
	Execute all Campaign Engine rows for a Marketing Campaign where sync_with_omni_blast = 1.

	Args:
		campaign_name: Name of Marketing Campaign document

	Returns:
		dict: summary of all engine executions
	"""
	campaign = frappe.get_doc("Marketing Campaign", campaign_name)
	engines = campaign.get_synced_engines()

	if not engines:
		return {"status": "No Action", "message": "No engines marked for Omni Blast"}

	results = []
	failed = []

	for engine_row in engines:
		result = execute_engine(engine_row)
		results.append(result)
		if result.get("status") in ("Failed", "Error"):
			failed.append(result)

	summary = {
		"campaign": campaign_name,
		"total_engines": len(engines),
		"completed": len(engines) - len(failed),
		"failed": len(failed),
		"results": results,
	}

	if failed:
		summary["status"] = "Partially Failed" if len(failed) < len(engines) else "Failed"
		frappe.log_error(
			title=_("Omni Blast Partially Failed"),
			message=frappe.as_json(summary),
		)
	else:
		summary["status"] = "Completed"

	return summary
