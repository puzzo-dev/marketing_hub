"""
Anonymize existing IP addresses in Tracking Link Click records
and recalculate unique_clicks for all Tracking Links.

This patch must run after the code change that introduced _anonymize_ip()
to ensure deduplication queries work correctly against historical data.
"""

import ipaddress

import frappe


def _anonymize_ip(ip_str):
	"""Anonymize IP by zeroing the last octet (IPv4) or last 80 bits (IPv6)."""
	if not ip_str:
		return ""
	try:
		addr = ipaddress.ip_address(ip_str)
		if isinstance(addr, ipaddress.IPv4Address):
			return str(ipaddress.IPv4Network(f"{ip_str}/24", strict=False).network_address)
		return str(ipaddress.IPv6Network(f"{ip_str}/48", strict=False).network_address)
	except ValueError:
		return ""


def execute():
	if not frappe.db.table_exists("tabTracking Link Click"):
		return

	# Anonymize all existing IP addresses in click records
	clicks = frappe.db.sql(
		"SELECT name, ip_address FROM `tabTracking Link Click` WHERE ip_address IS NOT NULL AND ip_address != ''",
		as_dict=True,
	)

	for click in clicks:
		anon_ip = _anonymize_ip(click.ip_address)
		if anon_ip != click.ip_address:
			frappe.db.set_value("Tracking Link Click", click.name, "ip_address", anon_ip, update_modified=False)

	# Recalculate unique_clicks for all Tracking Links
	links = frappe.db.sql(
		"SELECT name FROM `tabTracking Link`",
		as_dict=True,
	)

	for link in links:
		unique_count = frappe.db.sql(
			"""SELECT COUNT(DISTINCT ip_address) FROM `tabTracking Link Click`
			WHERE tracking_link = %s AND ip_address IS NOT NULL AND ip_address != ''""",
			(link.name,),
		)[0][0] or 0
		frappe.db.set_value("Tracking Link", link.name, "unique_clicks", unique_count, update_modified=False)

	frappe.db.commit()
