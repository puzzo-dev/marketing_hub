"""Roles, custom fields and workflows the redesign needs. Each function is safe to run again,
so it is called on install and on every migrate."""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

ROLES = ["Marketing Head", "Brand Manager", "Media Planner", "Content Lead", "Publisher", "OOH Coordinator", "Marketing Client"]

CUSTOM_FIELDS = {
	"Project": [
		{"fieldname": "mkt_campaign", "label": "Marketing exercise", "fieldtype": "Link", "options": "Marketing Campaign", "read_only": 1, "insert_after": "project_name", "unique": 1},
		{"fieldname": "mkt_brand_manager", "label": "Exercise Brand Manager", "fieldtype": "Link", "options": "User", "read_only": 1, "insert_after": "mkt_campaign"},
	],
	"Lead": [{"fieldname": "mkt_campaign", "label": "Marketing exercise", "fieldtype": "Link", "options": "Marketing Campaign", "insert_after": "source"}],
	"Purchase Order": [{"fieldname": "mkt_booking", "label": "OOH booking", "fieldtype": "Link", "options": "OOH Booking", "read_only": 1, "insert_after": "supplier"}],
}

CHANGE_REQUESTS = ["Campaign Change Request", "Content Change Request", "OOH Booking Change Request"]


def run():
	ensure_roles()
	create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
	ensure_workflows()


def ensure_roles():
	for role in ROLES:
		if not frappe.db.exists("Role", role):
			frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": int(role != "Marketing Client")}).insert(ignore_permissions=True)


def _master(doctype, field, value):
	if not frappe.db.exists(doctype, value):
		frappe.get_doc({"doctype": doctype, field: value}).insert(ignore_permissions=True)


def ensure_workflows():
	for state in ("Pending", "Approved", "Rejected"):
		_master("Workflow State", "workflow_state_name", state)
	for action in ("Approve", "Reject"):
		_master("Workflow Action Master", "workflow_action_name", action)
	for doctype in CHANGE_REQUESTS:
		_workflow(f"{doctype} approval", doctype, "workflow_state")
	_workflow("Placement approval", "Placement", "approval_state")


def _workflow(name, doctype, state_field):
	if frappe.db.exists("Workflow", name):
		return
	approver = "doc.approver == frappe.session.user"
	frappe.get_doc(
		{
			"doctype": "Workflow",
			"workflow_name": name,
			"document_type": doctype,
			"is_active": 1,
			"workflow_state_field": state_field,
			"states": [
				{"state": "Pending", "doc_status": 0, "allow_edit": "All"},
				{"state": "Approved", "doc_status": 0, "allow_edit": "Brand Manager"},
				{"state": "Rejected", "doc_status": 0, "allow_edit": "Brand Manager"},
			],
			# The assigned Brand Manager approves; a Marketing Head can too, to cover absence.
			"transitions": [
				{"state": "Pending", "action": "Approve", "next_state": "Approved", "allowed": "Brand Manager", "condition": approver, "allow_self_approval": 1},
				{"state": "Pending", "action": "Reject", "next_state": "Rejected", "allowed": "Brand Manager", "condition": approver, "allow_self_approval": 1},
				{"state": "Pending", "action": "Approve", "next_state": "Approved", "allowed": "Marketing Head", "allow_self_approval": 1},
				{"state": "Pending", "action": "Reject", "next_state": "Rejected", "allowed": "Marketing Head", "allow_self_approval": 1},
			],
		}
	).insert(ignore_permissions=True)
