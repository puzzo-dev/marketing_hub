# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

"""
Analytics Sync Scheduler

Scheduled job that syncs analytics data from all active connectors.
Referenced in hooks.py → scheduler_events → "all".
"""

import frappe
from frappe.utils import now_datetime


def sync_all_connectors():
	"""
	Scheduler function to enqueue analytics sync for all active connectors
	that are due for sync.

	Called by Frappe scheduler (hooks.py → scheduler_events → "hourly").
	Each connector is enqueued as a separate background job to avoid
	blocking the scheduler worker.
	"""
	connectors = frappe.get_all(
		"Analytics Connector",
		filters={
			"is_active": 1,
			"sync_status": ["not in", ["Paused", "Error"]],
			"next_sync_date": ["<=", now_datetime()]
		},
		pluck="name"
	)

	if not connectors:
		return

	enqueued = 0
	for connector_name in connectors:
		job_id = f"analytics_sync_{connector_name}"

		# Skip if a sync job is already running for this connector
		if frappe.utils.background_jobs.is_job_enqueued(job_id):
			continue

		frappe.enqueue(
			"marketing_hub.utils.analytics_sync._sync_single_connector",
			connector_name=connector_name,
			queue="default",
			timeout=300,
			job_id=job_id,
		)
		enqueued += 1

	if enqueued:
		frappe.logger().info(
			f"Analytics Sync: enqueued {enqueued} of {len(connectors)} connectors"
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
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(
			f"Background sync failed for {connector_name}: {str(e)}",
			"Analytics Sync Background"
		)
		raise
