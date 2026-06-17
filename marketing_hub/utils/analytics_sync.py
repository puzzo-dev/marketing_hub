# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

"""
Analytics Sync Scheduler

Scheduled job that syncs analytics data from all active connectors.
Referenced in hooks.py → scheduler_events → "all".
"""

import requests

import frappe
from frappe.utils import now_datetime


def sync_all_connectors():
	"""
	Scheduler function to sync analytics from all active connectors
	that are due for sync.

	Called by Frappe scheduler (hooks.py → scheduler_events → "all").
	Runs every minute, but only processes connectors whose next_sync_date
	has passed.
	"""
	connectors = frappe.get_all(
		"Analytics Connector",
		filters={
			"is_active": 1,
			"sync_status": ["not in", ["Paused", "Error"]],
			"sync_in_progress": 0,
			"next_sync_date": ["<=", now_datetime()]
		},
		pluck="name"
	)

	if not connectors:
		return

	synced = 0
	failed = 0

	for connector_name in connectors:
		try:
			doc = frappe.get_doc("Analytics Connector", connector_name)
			result = doc.sync_analytics()

			if result.get("status") == "Success":
				synced += 1
			else:
				failed += 1

			frappe.db.commit()

		except (frappe.ValidationError, frappe.DoesNotExistError, requests.exceptions.RequestException) as e:
			frappe.db.rollback()
			failed += 1
			frappe.log_error(
				f"Analytics sync failed for connector {connector_name}: {str(e)}",
				"Analytics Sync Scheduler"
			)

	if synced or failed:
		frappe.logger().info(
			f"Analytics Sync: {synced} succeeded, {failed} failed out of {len(connectors)} connectors"
		)


@frappe.whitelist()
def sync_connector_in_background(connector_name):
	"""
	Enqueue a single connector sync as a background job.
	Useful for manual sync triggers from the UI.

	Args:
		connector_name: Analytics Connector document name
	"""
	frappe.has_permission("Analytics Connector", doc=connector_name, throw=True)

	frappe.enqueue(
		"marketing_hub.utils.analytics_sync._sync_single_connector",
		connector_name=connector_name,
		queue="default",
		timeout=300,
		job_id=f"analytics_sync_{connector_name}"
	)

	return {"message": f"Sync enqueued for {connector_name}"}


def _sync_single_connector(connector_name):
	"""Background job wrapper for single connector sync."""
	try:
		doc = frappe.get_doc("Analytics Connector", connector_name)
		result = doc.sync_analytics()
		frappe.db.commit()
		return result
	except (frappe.ValidationError, frappe.DoesNotExistError, requests.exceptions.RequestException) as e:
		frappe.db.rollback()
		frappe.log_error(
			f"Background sync failed for {connector_name}: {str(e)}",
			"Analytics Sync Background"
		)
		raise
