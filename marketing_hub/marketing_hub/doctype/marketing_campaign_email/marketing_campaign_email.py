# Copyright (c) 2026, I-Varse Technologies NG and Contributors
# License: MIT

from frappe.model.document import Document


class MarketingCampaignEmail(Document):
	"""One ERPNext Email Campaign started for an exercise. Brand access to the
	ERPNext records goes through the exercise that lists them, because ERPNext's
	own Campaign doctypes have no brand field."""

	pass
