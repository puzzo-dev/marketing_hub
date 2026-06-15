"""
Tracking Links API - Create, manage, and track links with QR codes for OOH ads
"""

import base64
import hashlib
import io
import ipaddress

import frappe
from frappe import _
from frappe.utils import cint, get_url, now


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


@frappe.whitelist()
def create_tracking_link(data):
	"""Create a new tracking link with optional QR code generation"""
	data = frappe.parse_json(data)

	link_name = data.get("link_name")
	destination_url = data.get("destination_url")

	if not link_name or not destination_url:
		frappe.throw(_("Link Name and Destination URL are required"))

	doc = frappe.get_doc({
		"doctype": "Tracking Link",
		"link_name": link_name,
		"destination_url": destination_url,
		"campaign": data.get("campaign"),
		"channel": data.get("channel", "QR Code"),
		"utm_source": data.get("utm_source", "qr"),
		"utm_medium": data.get("utm_medium", "offline"),
		"utm_campaign": data.get("utm_campaign", ""),
		"utm_term": data.get("utm_term", ""),
		"utm_content": data.get("utm_content", ""),
	})
	doc.insert()

	# Generate QR code
	generate_qr_for_link(doc)

	return {
		"name": doc.name,
		"short_code": doc.short_code,
		"tracking_url": doc.get_tracking_url(),
		"destination_url": doc.get_destination_with_utm(),
		"qr_code": doc.qr_code,
	}


@frappe.whitelist()
def get_tracking_links(campaign=None, limit=50):
	"""Get list of tracking links, optionally filtered by campaign"""
	filters = {}
	if campaign:
		filters["campaign"] = campaign

	links = frappe.get_all(
		"Tracking Link",
		filters=filters,
		fields=[
			"name", "link_name", "destination_url", "short_code",
			"campaign", "channel", "status",
			"total_clicks", "unique_clicks", "last_clicked",
			"utm_source", "utm_medium", "utm_campaign",
			"qr_code", "creation",
		],
		order_by="creation desc",
		limit_page_length=cint(limit),
	)

	site_url = get_url()
	for link in links:
		link["tracking_url"] = f"{site_url}/t/{link['short_code']}"

	return links


@frappe.whitelist()
def get_tracking_link_detail(name):
	"""Get detailed info about a tracking link including click history"""
	doc = frappe.get_doc("Tracking Link", name)

	# Get recent clicks
	clicks = frappe.get_all(
		"Tracking Link Click",
		filters={"tracking_link": name},
		fields=["clicked_at", "ip_address", "referrer"],
		order_by="clicked_at desc",
		limit_page_length=50,
	)

	# Clicks per day for the last 30 days
	clicks_by_day = frappe.db.sql("""
		SELECT DATE(clicked_at) as date, COUNT(*) as clicks
		FROM `tabTracking Link Click`
		WHERE tracking_link = %(name)s
		AND clicked_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
		GROUP BY DATE(clicked_at)
		ORDER BY date ASC
	""", {"name": name}, as_dict=True)

	return {
		"name": doc.name,
		"link_name": doc.link_name,
		"destination_url": doc.destination_url,
		"short_code": doc.short_code,
		"tracking_url": doc.get_tracking_url(),
		"full_url": doc.get_destination_with_utm(),
		"campaign": doc.campaign,
		"channel": doc.channel,
		"status": doc.status,
		"total_clicks": doc.total_clicks,
		"unique_clicks": doc.unique_clicks,
		"last_clicked": doc.last_clicked,
		"utm_source": doc.utm_source,
		"utm_medium": doc.utm_medium,
		"utm_campaign": doc.utm_campaign,
		"utm_term": doc.utm_term,
		"utm_content": doc.utm_content,
		"qr_code": doc.qr_code,
		"creation": doc.creation,
		"clicks_by_day": clicks_by_day,
		"recent_clicks": clicks,
	}


@frappe.whitelist(allow_guest=True)
def handle_redirect(short_code):
	"""Handle tracking link redirect - increments click count"""
	if not short_code:
		frappe.throw(_("Invalid tracking link"), frappe.DoesNotExistError)

	# Basic rate limiting: max 30 clicks per IP per minute
	ip_address = frappe.local.request.remote_addr if frappe.local.request else ""
	if ip_address:
		cache_key = f"tracking_redirect:{ip_address}"
		click_count = frappe.cache.get_value(cache_key) or 0
		if click_count >= 30:
			frappe.throw(_("Too many requests"), frappe.TooManyRequestsError)
		frappe.cache.set_value(cache_key, click_count + 1, expires_in_sec=60)

	link = frappe.db.get_value(
		"Tracking Link",
		{"short_code": short_code, "status": "Active"},
		["name", "destination_url", "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"],
		as_dict=True,
	)

	if not link:
		frappe.throw(_("Tracking link not found or inactive"), frappe.DoesNotExistError)

	# Get the doc and record click
	doc = frappe.get_doc("Tracking Link", link.name)
	raw_ip = frappe.local.request.remote_addr if frappe.local.request else ""
	ip_address = _anonymize_ip(raw_ip)
	user_agent = (frappe.local.request.headers.get("User-Agent", "") if frappe.local.request else "")[:500]
	referrer = (frappe.local.request.headers.get("Referer", "") if frappe.local.request else "")[:500]

	# Record click
	doc.total_clicks = (doc.total_clicks or 0) + 1
	doc.last_clicked = now()

	# Check unique by IP
	if ip_address:
		existing = frappe.db.exists("Tracking Link Click", {
			"tracking_link": doc.name,
			"ip_address": ip_address,
		})
		if not existing:
			doc.unique_clicks = (doc.unique_clicks or 0) + 1

	doc.save(ignore_permissions=True)

	# Log click
	frappe.get_doc({
		"doctype": "Tracking Link Click",
		"tracking_link": doc.name,
		"ip_address": ip_address,
		"clicked_at": now(),
		"user_agent": user_agent,
		"referrer": referrer,
	}).insert(ignore_permissions=True)

	frappe.db.commit()

	# Build redirect URL with UTM params
	redirect_url = doc.get_destination_with_utm()
	frappe.local.flags.redirect_location = redirect_url
	raise frappe.Redirect


@frappe.whitelist()
def regenerate_qr(name):
	"""Regenerate QR code for an existing tracking link"""
	doc = frappe.get_doc("Tracking Link", name)
	generate_qr_for_link(doc)
	return {"qr_code": doc.qr_code}


def generate_qr_for_link(doc):
	"""Generate QR code image and attach to tracking link"""
	try:
		import qrcode
	except ImportError:
		# Fall back: no QR generation if library not installed
		frappe.msgprint(_("QR code generation requires the 'qrcode' Python package. Install with: pip install qrcode[pil]"))
		return

	tracking_url = doc.get_tracking_url()

	qr = qrcode.QRCode(version=1, box_size=10, border=4, error_correction=qrcode.constants.ERROR_CORRECT_H)
	qr.add_data(tracking_url)
	qr.make(fit=True)
	img = qr.make_image(fill_color="black", back_color="white")

	buffer = io.BytesIO()
	img.save(buffer, format="PNG")
	buffer.seek(0)

	filename = f"qr_{doc.short_code}.png"
	file_doc = frappe.get_doc({
		"doctype": "File",
		"file_name": filename,
		"content": buffer.read(),
		"attached_to_doctype": "Tracking Link",
		"attached_to_name": doc.name,
		"attached_to_field": "qr_code",
		"is_private": 0,
	})
	file_doc.save(ignore_permissions=True)

	doc.qr_code = file_doc.file_url
	doc.save(ignore_permissions=True)
