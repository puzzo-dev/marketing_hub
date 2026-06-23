"""Structured logging and optional Sentry integration helper.

Usage:
    from marketing_hub.utils.logger import capture_event, capture_exception

    capture_event("campaign_activity_executed", {"campaign": doc.campaign, "activity": doc.name})
    capture_exception("campaign_activity_failed", context={"activity": doc.name})

Sentry:
    Add `sentry_dsn` to your site_config.json and install `sentry-sdk`.
    The helper will initialise the Sentry SDK once per process and send events.
"""

from __future__ import annotations

import json
import traceback
import frappe


_sentry_client = None


def _get_sentry_client():
	global _sentry_client
	if _sentry_client is not None:
		return _sentry_client

	dsn = frappe.get_conf().get("sentry_dsn")
	if not dsn:
		return None

	try:
		import sentry_sdk
	except ImportError:
		frappe.logger().warning(
			"sentry_dsn is set but sentry-sdk is not installed. "
			"Run `pip install sentry-sdk` to enable Sentry."
		)
		return None

	sentry_sdk.init(dsn=dsn, environment=frappe.get_conf().get("sentry_environment", "production"))
	_sentry_client = sentry_sdk
	return _sentry_client


def capture_event(event: str, context: dict | None = None, level: str = "info"):
	"""Log a structured event to Frappe Error Log and optionally Sentry."""
	ctx = context or {}
	payload = {
		"event": event,
		"level": level,
		"context": ctx,
		"site": frappe.local.site,
	}
	frappe.logger().info(json.dumps(payload, default=str))

	client = _get_sentry_client()
	if client:
		with client.push_scope() as scope:
			for key, value in ctx.items():
				scope.set_extra(key, value)
			scope.set_tag("event", event)
			client.capture_message(event, level=level)


def capture_exception(
	event: str,
	exception: Exception | None = None,
	context: dict | None = None,
	message: str | None = None,
):
	"""Log an exception with structured context."""
	ctx = context or {}
	exc = exception or frappe.get_traceback()
	payload = {
		"event": event,
		"level": "error",
		"context": ctx,
		"traceback": exc if isinstance(exc, str) else traceback.format_exc(),
		"site": frappe.local.site,
	}
	frappe.log_error(
		title=event,
		message=json.dumps(payload, default=str) if not message else f"{message}\n\n{json.dumps(payload, default=str)}",
	)

	client = _get_sentry_client()
	if client:
		with client.push_scope() as scope:
			for key, value in ctx.items():
				scope.set_extra(key, value)
			scope.set_tag("event", event)
			client.capture_exception(error=exc if not isinstance(exc, str) else None)
