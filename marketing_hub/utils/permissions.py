"""
Permission Handlers for Marketing Hub
Implements role-based and user-based access control for campaigns
"""

import frappe
from frappe import _


def get_campaign_permission_query_conditions(user):
	"""Filter campaigns based on user permissions"""
	if not user:
		user = frappe.session.user
	
	# System Manager and Marketing Manager see all campaigns
	if "System Manager" in frappe.get_roles(user) or "Marketing Manager" in frappe.get_roles(user):
		return ""
	
	# Sales Manager sees all campaigns (for now - can be restricted later)
	if "Sales Manager" in frappe.get_roles(user):
		return ""
	
	# Others see only campaigns they own or are assigned to
	escaped_user = frappe.db.escape(user)
	return (
		"(`tabMarketing Campaign`.owner = " + escaped_user +
		" OR `tabMarketing Campaign`.name IN ("
		"SELECT DISTINCT parent FROM `tabUser Permission` "
		"WHERE allow = 'Marketing Campaign' "
		"AND user = " + escaped_user +
		" AND applicable_for IN ('', NULL, 'Marketing Hub')"
		"))"
	)


def has_campaign_permission(doc, ptype, user):
	"""Check if user has specific permission on campaign"""
	if not user:
		user = frappe.session.user
	
	# System Manager has full access
	if "System Manager" in frappe.get_roles(user):
		return True
	
	# Marketing Manager has full access
	if "Marketing Manager" in frappe.get_roles(user):
		return True
	
	# Sales Manager has full access (can be restricted)
	if "Sales Manager" in frappe.get_roles(user):
		return True
	
	# Owner has full access to their campaigns
	if doc.owner == user:
		return True
	
	# Check User Permissions
	user_perms = frappe.get_all(
		"User Permission",
		filters={
			"user": user,
			"allow": "Marketing Campaign",
			"for_value": doc.name
		},
		limit=1
	)
	
	if user_perms:
		# User has permission via User Permission doctype
		if ptype == "read":
			return True
		elif ptype in ("write", "submit", "cancel"):
			# Check if they have write permission specifically
			return frappe.has_permission("Marketing Campaign", ptype, user=user)
		elif ptype == "delete":
			# Only owners, System Manager, Marketing Manager can delete
			return False
	
	return False


def get_campaign_activity_permission_query_conditions(user):
	"""Filter campaign activities based on parent campaign permissions"""
	if not user:
		user = frappe.session.user
	
	# System Manager and Marketing Manager see all
	if "System Manager" in frappe.get_roles(user) or "Marketing Manager" in frappe.get_roles(user):
		return ""
	
	# Sales Manager sees all
	if "Sales Manager" in frappe.get_roles(user):
		return ""
	
	# Others see activities from campaigns they can access
	escaped_user = frappe.db.escape(user)
	return (
		"(`tabCampaign Activity`.campaign IN ("
		"SELECT name FROM `tabMarketing Campaign` "
		"WHERE owner = " + escaped_user +
		" OR name IN ("
		"SELECT DISTINCT for_value FROM `tabUser Permission` "
		"WHERE allow = 'Marketing Campaign' "
		"AND user = " + escaped_user +
		"))"
	)


def has_campaign_activity_permission(doc, ptype, user):
	"""Check if user has permission on campaign activity"""
	if not user:
		user = frappe.session.user
	
	# Check parent campaign permission via campaign link field
	if doc.campaign:
		try:
			campaign = frappe.get_doc("Marketing Campaign", doc.campaign)
			return has_campaign_permission(campaign, ptype, user)
		except frappe.DoesNotExistError:
			return False
	
	return False


def get_marketing_segment_permission_query_conditions(user):
	"""Marketing segments visible to all marketing roles"""
	if not user:
		user = frappe.session.user
	
	# Marketing roles see all segments
	marketing_roles = ["System Manager", "Marketing Manager", "Marketing User",
					   "Marketing Executive", "Marketing Analyst"]
	
	user_roles = frappe.get_roles(user)
	if any(role in marketing_roles for role in user_roles):
		return ""
	
	# Others see only their own
	return "`tabMarketing Segment`.owner = " + frappe.db.escape(user)


def has_workspace_access(user=None):
	"""Check if user has access to Marketing Hub workspace"""
	if not user:
		user = frappe.session.user
	
	# Define roles that have workspace access
	allowed_roles = [
		"System Manager",
		"Sales Manager",
		"Sales User",
		"Marketing Manager",
		"Marketing Executive",
		"Marketing Analyst",
		"HR Manager",
		"HR User"
	]
	
	user_roles = frappe.get_roles(user)
	return any(role in allowed_roles for role in user_roles)


@frappe.whitelist()
def assign_user_to_campaign(campaign, user, role="Collaborator", can_edit=1, can_execute=1):
	"""Assign a user to a campaign via User Permission"""
	# Check if caller has permission to assign
	if not frappe.has_permission("Marketing Campaign", "write"):
		frappe.throw(_("You don't have permission to assign users to campaigns"))
	
	# Check if campaign exists
	if not frappe.db.exists("Marketing Campaign", campaign):
		frappe.throw(_("Campaign {0} not found").format(campaign))
	
	# Check if user exists
	if not frappe.db.exists("User", user):
		frappe.throw(_("User {0} not found").format(user))
	
	# Check if already assigned
	existing = frappe.db.exists("User Permission", {
		"user": user,
		"allow": "Marketing Campaign",
		"for_value": campaign
	})
	
	if existing:
		frappe.msgprint(_("User {0} is already assigned to this campaign").format(user))
		return existing
	
	# Create User Permission
	user_perm = frappe.new_doc("User Permission")
	user_perm.user = user
	user_perm.allow = "Marketing Campaign"
	user_perm.for_value = campaign
	user_perm.applicable_for = "Marketing Hub"
	user_perm.insert()
	
	# Log the assignment
	frappe.logger().info(f"Assigned user {user} to campaign {campaign} as {role}")
	
	return {
		"success": True,
		"message": _("User {0} assigned successfully").format(user),
		"permission": user_perm.name
	}


@frappe.whitelist()
def remove_user_from_campaign(campaign, user):
	"""Remove user assignment from campaign"""
	# Check if caller has permission
	if not frappe.has_permission("Marketing Campaign", "write"):
		frappe.throw(_("You don't have permission to modify campaign assignments"))
	
	# Find and delete User Permission
	user_perms = frappe.get_all(
		"User Permission",
		filters={
			"user": user,
			"allow": "Marketing Campaign",
			"for_value": campaign
		},
		pluck="name"
	)
	
	for perm in user_perms:
		frappe.delete_doc("User Permission", perm)
	
	frappe.logger().info(f"Removed user {user} from campaign {campaign}")
	
	return {
		"success": True,
		"message": _("User {0} removed from campaign").format(user)
	}


@frappe.whitelist()
def get_campaign_assigned_users(campaign):
	"""Get list of users assigned to a campaign"""
	if not frappe.has_permission("Marketing Campaign", "read"):
		frappe.throw(_("You don't have permission to view campaign assignments"))
	
	assigned_users = frappe.get_all(
		"User Permission",
		filters={
			"allow": "Marketing Campaign",
			"for_value": campaign
		},
		fields=["user", "creation", "modified"]
	)
	
	# Enrich with user details
	for assignment in assigned_users:
		user_doc = frappe.get_cached_doc("User", assignment.user)
		assignment.full_name = user_doc.full_name
		assignment.user_image = user_doc.user_image
		assignment.email = user_doc.email
	
	return assigned_users


def validate_campaign_limits(doc, method):
	"""Validate campaign limits for agency mode"""
	# Only check for agency mode
	if not doc.client:
		return
	
	# Import here to avoid circular dependency
	from marketing_hub.utils.agency_mode import check_client_subscription
	
	try:
		result = check_client_subscription(doc.client, doc.name)
		
		if not result.get("valid"):
			frappe.throw(_(result.get("message", "Campaign limit exceeded")))
	except (frappe.DoesNotExistError, frappe.ValidationError) as e:
		frappe.log_error(f"Campaign limit validation error: {str(e)}", "Marketing Hub Permissions")
