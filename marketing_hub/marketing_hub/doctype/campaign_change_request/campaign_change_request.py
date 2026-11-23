# Copyright (c) 2026, I-Varse Technologies NG and contributors
# License: MIT

import frappe
from frappe.model.document import Document

from marketing_hub.utils.change_requests import ChangeRequestMixin


class CampaignChangeRequest(ChangeRequestMixin, Document):
	def target(self):
		return frappe.get_doc("Marketing Campaign", self.campaign)
