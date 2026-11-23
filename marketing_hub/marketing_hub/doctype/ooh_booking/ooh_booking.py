# Copyright (c) 2026, I-Varse Technologies NG and contributors
# License: MIT

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate

STEPS = ["Proposed", "Approved", "Production", "Live", "Ended"]


class OOHBooking(Document):
	"""Reserves a site for an exercise. Booking status is written by this controller only."""

	def validate(self):
		if getdate(self.start_date) > getdate(self.end_date):
			frappe.throw(_("End date cannot be before the start date."))
		self.brand = frappe.db.get_value("Marketing Campaign", self.campaign, "brand") or self.brand
		self.approver = frappe.db.get_value("Marketing Campaign", self.campaign, "brand_manager")
		self.check_overlap()

	def check_overlap(self):
		"""No two live bookings on a site may overlap. The site row is locked so two people
		booking at once cannot both pass the check."""
		frappe.db.sql("select name from `tabOOH Site` where name = %s for update", self.site)
		clash = frappe.db.sql(
			"""select name from `tabOOH Booking`
			where site = %(site)s and name != %(name)s and status not in ('Cancelled', 'Ended')
			and start_date <= %(end)s and end_date >= %(start)s limit 1""",
			{"site": self.site, "name": self.name or "", "start": self.start_date, "end": self.end_date},
		)
		if clash:
			frappe.throw(_("{0} is already booked on those dates ({1}).").format(self.site, clash[0][0]))

	@frappe.whitelist()
	def advance(self):
		"""Move to the next step. Approval is the Brand Manager's; the rest is the coordinator's."""
		i = STEPS.index(self.status)
		if i == len(STEPS) - 1:
			frappe.throw(_("This booking has ended."))
		nxt = STEPS[i + 1]
		if nxt == "Approved" and frappe.session.user != self.approver and "System Manager" not in frappe.get_roles():
			frappe.throw(_("Only the exercise's Brand Manager can approve a booking."), frappe.PermissionError)
		self.status = nxt
		self.save()
		if nxt == "Approved":
			self.create_purchase_order()

	def create_purchase_order(self):
		"""One purchase order per booking. The row lock and the empty-field check keep it to one."""
		frappe.db.sql("select name from `tabOOH Booking` where name = %s for update", self.name)
		self.reload()
		if self.purchase_order:
			return
		item = frappe.db.get_single_value("Marketing Hub Settings", "ooh_purchase_item")
		if not item:
			frappe.throw(_("Set the OOH purchase item in Marketing Hub Settings before approving bookings."))
		vendor = frappe.db.get_value("OOH Site", self.site, "vendor")
		po = frappe.get_doc(
			{
				"doctype": "Purchase Order",
				"supplier": vendor,
				"schedule_date": self.start_date,
				"mkt_booking": self.name,
				"items": [{"item_code": item, "qty": 1, "rate": flt(self.agreed_rate), "schedule_date": self.start_date}],
			}
		).insert(ignore_permissions=True)
		self.db_set("purchase_order", po.name)
