import frappe
from frappe.model.document import Document
import hashlib
import time


class TrackingLink(Document):
	def before_insert(self):
		if not self.short_code:
			self.short_code = self._generate_short_code()
		if not self.created_by:
			self.created_by = frappe.session.user

	def _generate_short_code(self):
		"""Generate a unique short code for the link"""
		raw = f"{self.destination_url}{time.time()}{frappe.session.user}"
		hash_val = hashlib.sha256(raw.encode()).hexdigest()[:8]
		# Ensure uniqueness
		while frappe.db.exists("Tracking Link", {"short_code": hash_val}):
			raw += "x"
			hash_val = hashlib.sha256(raw.encode()).hexdigest()[:8]
		return hash_val

	def get_tracking_url(self):
		"""Get the full tracking URL"""
		site_url = frappe.utils.get_url()
		return f"{site_url}/t/{self.short_code}"

	def get_destination_with_utm(self):
		"""Build destination URL with UTM parameters appended"""
		from urllib.parse import urlparse, urlencode, parse_qs, urlunparse

		parsed = urlparse(self.destination_url)
		params = parse_qs(parsed.query)

		utm_fields = {
			"utm_source": self.utm_source,
			"utm_medium": self.utm_medium,
			"utm_campaign": self.utm_campaign,
			"utm_term": self.utm_term,
			"utm_content": self.utm_content,
		}
		for key, val in utm_fields.items():
			if val:
				params[key] = [val]

		new_query = urlencode(params, doseq=True)
		return urlunparse(parsed._replace(query=new_query))

	def record_click(self, ip_address=None):
		"""Record a click on this tracking link"""
		self.total_clicks = (self.total_clicks or 0) + 1
		self.last_clicked = frappe.utils.now()

		# Track unique clicks by IP (simple approach)
		if ip_address:
			existing = frappe.db.exists("Tracking Link Click", {
				"tracking_link": self.name,
				"ip_address": ip_address,
			})
			if not existing:
				self.unique_clicks = (self.unique_clicks or 0) + 1

		self.save(ignore_permissions=True)

		# Log the click
		frappe.get_doc({
			"doctype": "Tracking Link Click",
			"tracking_link": self.name,
			"ip_address": ip_address or "",
			"clicked_at": frappe.utils.now(),
		}).insert(ignore_permissions=True)
