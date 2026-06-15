"""
Content Assets & Templates API
"""

import re

import frappe
from frappe.utils import cint

_VALID_ORDER_BY_RE = re.compile(
	r"^[a-z_]+(\s+(asc|desc))?$",
	re.IGNORECASE,
)


def _sanitize_order_by(order_by, default="modified desc"):
	"""Validate order_by to prevent SQL injection."""
	if not order_by or not _VALID_ORDER_BY_RE.match(order_by.strip()):
		return default
	return order_by.strip()


@frappe.whitelist()
def get_assets(filters=None, limit_start=0, limit_page_length=20, order_by="modified desc"):
	"""Get list of content assets with filters"""
	order_by = _sanitize_order_by(order_by)
	filters = frappe.parse_json(filters) if filters else {}

	base_filters = {}
	or_filters = {}

	if filters.get("asset_type"):
		base_filters["asset_type"] = filters["asset_type"]
	if filters.get("channel"):
		base_filters["channel"] = filters["channel"]
	if filters.get("status"):
		base_filters["status"] = filters["status"]
	if filters.get("search"):
		search_term = f"%{filters['search']}%"
		or_filters = {
			"asset_name": ["like", search_term],
			"tags": ["like", search_term],
			"description": ["like", search_term],
		}

	assets = frappe.get_all(
		"Content Asset",
		filters=base_filters,
		or_filters=or_filters,
		fields=[
			"name", "asset_name", "asset_type", "channel", "status", "tags",
			"file_attachment", "thumbnail", "file_size", "dimensions",
			"usage_count", "modified", "owner",
		],
		order_by=order_by,
		limit_start=cint(limit_start),
		limit_page_length=cint(limit_page_length),
	)

	total_count = len(frappe.get_all(
		"Content Asset", filters=base_filters, or_filters=or_filters,
		fields=["name"], limit_page_length=0,
	))

	return {"assets": assets, "total_count": total_count}


@frappe.whitelist()
def get_asset(name):
	"""Get single asset details"""
	return frappe.get_doc("Content Asset", name).as_dict()


@frappe.whitelist()
def create_asset(data):
	"""Create new content asset"""
	data = frappe.parse_json(data)
	doc = frappe.get_doc({"doctype": "Content Asset", **data})
	doc.insert()
	return doc.as_dict()


@frappe.whitelist()
def update_asset(name, data):
	"""Update existing asset"""
	data = frappe.parse_json(data)
	doc = frappe.get_doc("Content Asset", name)
	doc.update(data)
	doc.save()
	return doc.as_dict()


@frappe.whitelist()
def delete_asset(name):
	"""Delete asset"""
	frappe.delete_doc("Content Asset", name)
	return {"message": "Asset deleted successfully"}


@frappe.whitelist()
def bulk_update_assets(names, data):
	"""Bulk update multiple assets"""
	names = frappe.parse_json(names)
	data = frappe.parse_json(data)
	for name in names:
		doc = frappe.get_doc("Content Asset", name)
		doc.update(data)
		doc.save()
	return {"message": f"Updated {len(names)} assets"}


@frappe.whitelist()
def get_content_details(name):
	"""Get full details for a content asset"""
	try:
		doc = frappe.get_doc("Content Asset", name)
		return {"success": True, "doc": doc}
	except (frappe.DoesNotExistError, frappe.PermissionError) as e:
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_templates(filters=None, limit_start=0, limit_page_length=20, order_by="modified desc"):
	"""Get list of marketing templates"""
	order_by = _sanitize_order_by(order_by)
	filters = frappe.parse_json(filters) if filters else {}

	base_filters = {}
	or_filters = {}

	if filters.get("channel"):
		base_filters["channel"] = filters["channel"]
	if filters.get("template_type"):
		base_filters["template_type"] = filters["template_type"]
	if filters.get("status"):
		base_filters["status"] = filters["status"]
	if filters.get("category"):
		base_filters["category"] = filters["category"]
	if filters.get("search"):
		search_term = f"%{filters['search']}%"
		or_filters = {
			"template_name": ["like", search_term],
			"category": ["like", search_term],
			"subject": ["like", search_term],
		}

	templates = frappe.get_all(
		"Marketing Template",
		filters=base_filters,
		or_filters=or_filters,
		fields=[
			"name", "template_name", "channel", "template_type", "status", "category",
			"subject", "headline", "primary_asset", "modified", "owner",
		],
		order_by=order_by,
		limit_start=cint(limit_start),
		limit_page_length=cint(limit_page_length),
	)

	total_count = len(frappe.get_all(
		"Marketing Template", filters=base_filters, or_filters=or_filters,
		fields=["name"], limit_page_length=0,
	))

	return {"templates": templates, "total_count": total_count}


@frappe.whitelist()
def get_template(name):
	"""Get single template details"""
	return frappe.get_doc("Marketing Template", name).as_dict()


@frappe.whitelist()
def create_template(data):
	"""Create new marketing template"""
	data = frappe.parse_json(data)
	doc = frappe.get_doc({"doctype": "Marketing Template", **data})
	doc.insert()
	return doc.as_dict()


@frappe.whitelist()
def update_template(name, data):
	"""Update existing template"""
	data = frappe.parse_json(data)
	doc = frappe.get_doc("Marketing Template", name)
	doc.update(data)
	doc.save()
	return doc.as_dict()


@frappe.whitelist()
def delete_template(name):
	"""Delete template"""
	frappe.delete_doc("Marketing Template", name)
	return {"message": "Template deleted successfully"}


@frappe.whitelist()
def upload_file(file, asset_name=None, asset_type=None, channel=None):
	"""Handle file upload and create asset"""
	file_doc = frappe.get_doc("File", {"file_url": file})

	asset = frappe.get_doc({
		"doctype": "Content Asset",
		"asset_name": asset_name or file_doc.file_name,
		"asset_type": asset_type or "Image",
		"channel": channel,
		"file_attachment": file,
		"file_size": file_doc.file_size,
		"status": "Draft"
	})

	if file_doc.is_image():
		asset.thumbnail = file

	asset.insert()
	return asset.as_dict()


@frappe.whitelist()
def get_asset_types():
	"""Get list of available asset types"""
	return frappe.get_all("Media Type", fields=["name"], order_by="name")


@frappe.whitelist()
def get_channels():
	"""Get list of available channels from Social Media Network doctype"""
	networks = frappe.get_all(
		"Social Media Network",
		filters={"is_active": 1},
		fields=["network_name"],
		order_by="network_name"
	)
	return [n.network_name for n in networks]


@frappe.whitelist()
def get_template_categories():
	"""Get list of template categories"""
	return frappe.get_all(
		"Marketing Template",
		filters={"category": ["is", "set"]},
		fields=["category"],
		distinct=True,
		order_by="category",
		pluck="category",
	)


@frappe.whitelist()
def get_asset_stats():
	"""Get asset library statistics"""
	stats = {
		"total_assets": frappe.db.count("Content Asset"),
		"by_type": frappe.db.sql("""
			SELECT asset_type, COUNT(*) as count
			FROM `tabContent Asset`
			GROUP BY asset_type
			ORDER BY count DESC
		""", as_dict=True),
		"by_channel": frappe.db.sql("""
			SELECT channel, COUNT(*) as count
			FROM `tabContent Asset`
			WHERE channel IS NOT NULL AND channel != ''
			GROUP BY channel
			ORDER BY count DESC
		""", as_dict=True),
		"by_status": frappe.db.sql("""
			SELECT status, COUNT(*) as count
			FROM `tabContent Asset`
			GROUP BY status
		""", as_dict=True),
		"total_size": frappe.db.sql("""
			SELECT SUM(CAST(REPLACE(REPLACE(file_size, 'KB', ''), 'MB', '') AS DECIMAL(10,2))) as total
			FROM `tabContent Asset`
			WHERE file_size IS NOT NULL
		""")[0][0] or 0
	}
	return stats
