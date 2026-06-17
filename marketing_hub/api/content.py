"""
Content Assets & Templates API
"""

import frappe
from frappe import _
from frappe.utils import cint


# Allowlist of valid columns for ORDER BY in Content Asset queries
_VALID_ASSET_ORDER_COLUMNS = {
	"name", "asset_name", "asset_type", "channel", "status", "tags",
	"file_attachment", "thumbnail", "file_size", "dimensions",
	"usage_count", "modified", "owner", "creation"
}
_VALID_SORT_DIRECTIONS = {"asc", "desc"}


def _sanitize_order_by(order_by, valid_columns):
	"""Sanitize ORDER BY clause against SQL injection."""
	if not order_by:
		return "modified desc"
	parts = order_by.replace(",", " ").split()
	safe_parts = []
	for part in parts:
		part_lower = part.lower().strip()
		if not part_lower:
			continue
		# Check for column name only
		if part_lower in valid_columns:
			safe_parts.append(f"`{part_lower}` desc")
			continue
		# Check for column direction combo (e.g. modified desc)
		for col in valid_columns:
			if part_lower.startswith(col.lower() + " ") or part_lower == col.lower():
				remainder = part_lower[len(col):].strip()
				direction = "desc"
				if remainder in _VALID_SORT_DIRECTIONS:
					direction = remainder
				safe_parts.append(f"`{col}` {direction}")
				break
		else:
			# If no valid column matched, skip this part
			continue
	return ", ".join(safe_parts) if safe_parts else "modified desc"


@frappe.whitelist()
def get_assets(filters=None, limit_start=0, limit_page_length=20, order_by="modified desc"):
	"""Get list of content assets with filters"""
	filters = frappe.parse_json(filters) if filters else {}

	conditions = []
	values = {}

	if filters.get("asset_type"):
		conditions.append("asset_type = %(asset_type)s")
		values["asset_type"] = filters["asset_type"]
	if filters.get("channel"):
		conditions.append("channel = %(channel)s")
		values["channel"] = filters["channel"]
	if filters.get("status"):
		conditions.append("status = %(status)s")
		values["status"] = filters["status"]
	if filters.get("search"):
		conditions.append("(asset_name LIKE %(search)s OR tags LIKE %(search)s OR description LIKE %(search)s)")
		values["search"] = f"%{filters['search']}%"

	where_clause = " AND ".join(conditions) if conditions else "1=1"
	safe_order_by = _sanitize_order_by(order_by, _VALID_ASSET_ORDER_COLUMNS)

	assets = frappe.db.sql(f"""
		SELECT
			name, asset_name, asset_type, channel, status, tags,
			file_attachment, thumbnail, file_size, dimensions,
			usage_count, modified, owner
		FROM `tabContent Asset`
		WHERE {where_clause}
		ORDER BY {safe_order_by}
		LIMIT {cint(limit_start)}, {cint(limit_page_length)}
	""", values, as_dict=True)

	total_count = frappe.db.sql(f"""
		SELECT COUNT(*) as count
		FROM `tabContent Asset`
		WHERE {where_clause}
	""", values, as_dict=True)[0].count

	return {"assets": assets, "total_count": total_count}


@frappe.whitelist()
def get_asset(name):
	"""Get single asset details"""
	return frappe.get_doc("Content Asset", name).as_dict()


@frappe.whitelist()
def create_asset(data):
	"""Create new content asset"""
	frappe.has_permission("Content Asset", throw=True)
	data = frappe.parse_json(data)
	doc = frappe.get_doc({"doctype": "Content Asset", **data})
	doc.insert()
	frappe.db.commit()
	return doc.as_dict()


@frappe.whitelist()
def update_asset(name, data):
	"""Update existing asset"""
	data = frappe.parse_json(data)
	doc = frappe.get_doc("Content Asset", name)
	doc.check_permission("write")
	doc.update(data)
	doc.save()
	frappe.db.commit()
	return doc.as_dict()


@frappe.whitelist()
def delete_asset(name):
	"""Delete asset"""
	doc = frappe.get_doc("Content Asset", name)
	doc.check_permission("delete")
	frappe.delete_doc("Content Asset", name)
	frappe.db.commit()
	return {"message": "Asset deleted successfully"}


def _calculate_total_asset_size():
	"""Calculate total asset size in KB by properly handling KB and MB units."""
	rows = frappe.db.sql("""
		SELECT file_size
		FROM `tabContent Asset`
		WHERE file_size IS NOT NULL AND file_size != ''
	""", as_dict=False)
	total_kb = 0
	for row in rows:
		size_str = (row[0] or "").strip()
		if not size_str:
			continue
		try:
			if size_str.upper().endswith("MB"):
				value = float(size_str[:-2].strip())
				total_kb += value * 1024
			elif size_str.upper().endswith("KB"):
				value = float(size_str[:-2].strip())
				total_kb += value
			else:
				# Assume bytes if no unit
				value = float(size_str)
				total_kb += value / 1024
		except (ValueError, TypeError):
			continue
	return round(total_kb, 2)


@frappe.whitelist()
def bulk_update_assets(names, data):
	"""Bulk update multiple assets"""
	names = frappe.parse_json(names)
	data = frappe.parse_json(data)
	for name in names:
		doc = frappe.get_doc("Content Asset", name)
		doc.check_permission("write")
		doc.update(data)
		doc.save()
	frappe.db.commit()
	return {"message": f"Updated {len(names)} assets"}


@frappe.whitelist()
def get_content_details(name):
	"""Get full details for a content asset"""
	try:
		doc = frappe.get_doc("Content Asset", name)
		return {"success": True, "doc": doc}
	except (frappe.ValidationError, frappe.DoesNotExistError) as e:
		return {"success": False, "error": str(e)}


# Allowlist of valid columns for ORDER BY in Marketing Template queries
_VALID_TEMPLATE_ORDER_COLUMNS = {
	"name", "template_name", "channel", "template_type", "status", "category",
	"subject", "headline", "primary_asset", "modified", "owner", "creation"
}


@frappe.whitelist()
def get_templates(filters=None, limit_start=0, limit_page_length=20, order_by="modified desc"):
	"""Get list of marketing templates"""
	filters = frappe.parse_json(filters) if filters else {}

	conditions = []
	values = {}

	if filters.get("channel"):
		conditions.append("channel = %(channel)s")
		values["channel"] = filters["channel"]
	if filters.get("template_type"):
		conditions.append("template_type = %(template_type)s")
		values["template_type"] = filters["template_type"]
	if filters.get("status"):
		conditions.append("status = %(status)s")
		values["status"] = filters["status"]
	if filters.get("category"):
		conditions.append("category = %(category)s")
		values["category"] = filters["category"]
	if filters.get("search"):
		conditions.append("(template_name LIKE %(search)s OR category LIKE %(search)s OR subject LIKE %(search)s)")
		values["search"] = f"%{filters['search']}%"

	where_clause = " AND ".join(conditions) if conditions else "1=1"
	safe_order_by = _sanitize_order_by(order_by, _VALID_TEMPLATE_ORDER_COLUMNS)

	templates = frappe.db.sql(f"""
		SELECT
			name, template_name, channel, template_type, status, category,
			subject, headline, primary_asset, modified, owner
		FROM `tabMarketing Template`
		WHERE {where_clause}
		ORDER BY {safe_order_by}
		LIMIT {cint(limit_start)}, {cint(limit_page_length)}
	""", values, as_dict=True)

	total_count = frappe.db.sql(f"""
		SELECT COUNT(*) as count
		FROM `tabMarketing Template`
		WHERE {where_clause}
	""", values, as_dict=True)[0].count

	return {"templates": templates, "total_count": total_count}


@frappe.whitelist()
def get_template(name):
	"""Get single template details"""
	return frappe.get_doc("Marketing Template", name).as_dict()


@frappe.whitelist()
def create_template(data):
	"""Create new marketing template"""
	frappe.has_permission("Marketing Template", throw=True)
	data = frappe.parse_json(data)
	doc = frappe.get_doc({"doctype": "Marketing Template", **data})
	doc.insert()
	frappe.db.commit()
	return doc.as_dict()


@frappe.whitelist()
def update_template(name, data):
	"""Update existing template"""
	data = frappe.parse_json(data)
	doc = frappe.get_doc("Marketing Template", name)
	doc.check_permission("write")
	doc.update(data)
	doc.save()
	frappe.db.commit()
	return doc.as_dict()


@frappe.whitelist()
def delete_template(name):
	"""Delete template"""
	doc = frappe.get_doc("Marketing Template", name)
	doc.check_permission("delete")
	frappe.delete_doc("Marketing Template", name)
	frappe.db.commit()
	return {"message": "Template deleted successfully"}


@frappe.whitelist()
def upload_file(file, asset_name=None, asset_type=None, channel=None):
	"""Handle file upload and create asset"""
	frappe.has_permission("Content Asset", throw=True)
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
	frappe.db.commit()
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
	categories = frappe.db.sql("""
		SELECT DISTINCT category
		FROM `tabMarketing Template`
		WHERE category IS NOT NULL AND category != ''
		ORDER BY category
	""", as_dict=True)
	return [c.category for c in categories]


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
		"total_size": _calculate_total_asset_size(),
	}
	return stats
