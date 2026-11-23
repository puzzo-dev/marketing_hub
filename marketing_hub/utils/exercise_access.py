"""Who may see and change what, by exercise.

Marketing Campaign is the exercise. A Brand Manager works only on exercises where they are
the assigned brand_manager; a Marketing Head, a System Manager and the old Marketing Manager
role see all of them. Everything that hangs off an exercise (content, placements, bookings,
change requests, the ERPNext Project and its Tasks) follows the same rule, so a manager with
no assigned exercise sees none of it. This works from brand_manager directly and does not
depend on User Permission rows.
"""

import frappe

SEES_ALL = {"System Manager", "Marketing Head", "Marketing Manager"}


def _roles(user):
	return set(frappe.get_roles(user))


def is_scoped_manager(user=None):
	"""True for a Brand Manager who does not also hold a see-everything role."""
	user = user or frappe.session.user
	roles = _roles(user)
	return "Brand Manager" in roles and not (roles & SEES_ALL)


def managed_exercises(user=None):
	user = user or frappe.session.user
	return frappe.get_all("Marketing Campaign", filters={"brand_manager": user}, pluck="name")


def exercise_conditions(doctype, field):
	"""A permission_query_conditions function for a doctype whose `field` links an exercise."""

	def conditions(user=None):
		user = user or frappe.session.user
		if not is_scoped_manager(user):
			return ""
		escaped = frappe.db.escape(user)
		return (
			f"`tab{doctype}`.`{field}` in (select name from `tabMarketing Campaign` "
			f"where brand_manager = {escaped})"
		)

	return conditions


def exercise_permission(field):
	"""A has_permission function for the same doctypes."""

	def has_permission(doc, ptype=None, user=None):
		user = user or frappe.session.user
		if not is_scoped_manager(user):
			return None  # fall through to the normal role check
		return doc.get(field) in managed_exercises(user)

	return has_permission


def project_conditions(user=None):
	"""A Project without mkt_campaign is not an exercise's and is left alone."""
	user = user or frappe.session.user
	if not is_scoped_manager(user):
		return ""
	escaped = frappe.db.escape(user)
	return (
		"(ifnull(`tabProject`.`mkt_campaign`, '') = '' "
		f"or `tabProject`.`mkt_brand_manager` = {escaped})"
	)


def task_conditions(user=None):
	user = user or frappe.session.user
	if not is_scoped_manager(user):
		return ""
	escaped = frappe.db.escape(user)
	return (
		"(ifnull(`tabTask`.`project`, '') = '' or `tabTask`.`project` not in "
		"(select name from `tabProject` where ifnull(mkt_campaign, '') != '') "
		"or `tabTask`.`project` in (select name from `tabProject` "
		f"where mkt_brand_manager = {escaped}))"
	)


def project_permission(doc, ptype=None, user=None):
	user = user or frappe.session.user
	if not is_scoped_manager(user) or not doc.get("mkt_campaign"):
		return None
	return doc.get("mkt_brand_manager") == user


campaign_conditions = exercise_conditions("Marketing Campaign", "name")
content_conditions = exercise_conditions("Content Item", "campaign")
placement_conditions = exercise_conditions("Placement", "campaign")
booking_conditions = exercise_conditions("OOH Booking", "campaign")
campaign_cr_conditions = exercise_conditions("Campaign Change Request", "campaign")
content_cr_conditions = exercise_conditions("Content Change Request", "campaign")
booking_cr_conditions = exercise_conditions("OOH Booking Change Request", "campaign")

content_permission = exercise_permission("campaign")
campaign_permission = exercise_permission("name")
