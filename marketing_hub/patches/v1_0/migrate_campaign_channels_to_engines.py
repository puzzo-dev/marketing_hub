# -*- coding: utf-8 -*-
"""
Migrate Marketing Campaign Channel (Table MultiSelect)
to Campaign Engine (Table) child rows.

Old channels only referenced Social Media Network names.
New engines require actual engine documents (Newsletter, Social Post, etc).
This patch creates Campaign Engine placeholders and logs campaigns
that need manual engine document creation.
"""

import frappe
from frappe import _

NETWORK_TYPE_TO_ENGINE = {
	"Email": ("Email Blast", "Newsletter"),
	"Messaging": ("WhatsApp", "Bulk WhatsApp Message"),
	"SMS": ("SMS", "SMS Campaign"),
	"Social Media": ("Social Media", "Social Post"),
	"Out of Home (OOH)": ("OOH", "OOH Campaign"),
	"Advertising": ("Meta Ads", "Meta Ads Campaign"),
}


def execute():
	campaigns = frappe.get_all(
		"Marketing Campaign",
		filters={"docstatus": ["<", 2]},
		fields=["name", "campaign_name"],
	)

	migrated = 0
	needs_manual = 0

	for campaign in campaigns:
		# Old channels are stored in the `tabMarketing Campaign Channel` child table
		# The field on Marketing Campaign was called `channels`
		old_channels = frappe.get_all(
			"Marketing Campaign Channel",
			filters={"parent": campaign.name, "parenttype": "Marketing Campaign"},
			fields=["social_media_network"],
		)

		if not old_channels:
			continue

		campaign_doc = frappe.get_doc("Marketing Campaign", campaign.name)
		existing_engines = [e.engine_type for e in campaign_doc.get("campaign_engines", [])]

		for ch in old_channels:
			network = frappe.get_cached_doc("Social Media Network", ch.social_media_network)
			mapping = NETWORK_TYPE_TO_ENGINE.get(network.network_type)

			if not mapping:
				frappe.logger().warning(
					f"Marketing Campaign {campaign.name}: unknown network_type '{network.network_type}' for {network.name}"
				)
				continue

			engine_type, engine_doc_type = mapping

			if engine_type in existing_engines:
				continue

			campaign_doc.append(
				"campaign_engines",
				{
					"engine_type": engine_type,
					"engine_doc_type": engine_doc_type,
					"engine_doc": "",  # No existing engine document to link
					"status": "Draft",
					"sync_with_omni_blast": 1,
				},
			)
			existing_engines.append(engine_type)
			needs_manual += 1

		campaign_doc.save(ignore_permissions=True)
		migrated += 1

	frappe.db.commit()

	msg = _(
		"Migrated {0} campaigns. {1} engine rows created without linked engine documents — "
		"please review and create the corresponding engine documents manually."
	).format(migrated, needs_manual)
	frappe.logger().info(msg)
