"""Convert Content Asset file_size from human-readable string to integer bytes.

Existing records may have values like "5.20 KB" or "1.30 MB".
This patch converts them to raw byte integers and links orphan File records.
"""

import re
import frappe


UNIT_MULTIPLIERS = {
    "B": 1,
    "KB": 1024,
    "MB": 1024 ** 2,
    "GB": 1024 ** 3,
    "TB": 1024 ** 4,
}


def execute():
    if not frappe.db.table_exists("tabContent Asset"):
        return

    # 1. Convert string file_size → integer bytes
    assets = frappe.db.sql(
        """SELECT name, file_size, file_attachment
        FROM `tabContent Asset`
        WHERE file_size IS NOT NULL AND file_size != '' AND file_size != '0'""",
        as_dict=True,
    )

    for asset in assets:
        raw = str(asset.file_size).strip()
        byte_val = _parse_size_string(raw)

        if byte_val is None and asset.file_attachment:
            # Try reading from the linked File doc instead
            byte_val = frappe.db.get_value(
                "File", {"file_url": asset.file_attachment}, "file_size"
            )

        if byte_val is not None:
            frappe.db.set_value(
                "Content Asset", asset.name, "file_size", int(byte_val), update_modified=False
            )

    # 2. Link orphan File records to their Content Assets
    linked_assets = frappe.db.sql(
        """SELECT name, file_attachment, thumbnail
        FROM `tabContent Asset`
        WHERE file_attachment IS NOT NULL AND file_attachment != ''""",
        as_dict=True,
    )

    for asset in linked_assets:
        for field in ("file_attachment", "thumbnail"):
            url = asset.get(field)
            if not url:
                continue
            file_name = frappe.db.get_value(
                "File",
                {"file_url": url, "attached_to_name": ["in", ["", None]]},
                "name",
            )
            if file_name:
                frappe.db.set_value(
                    "File",
                    file_name,
                    {
                        "attached_to_doctype": "Content Asset",
                        "attached_to_name": asset.name,
                        "attached_to_field": field,
                    },
                    update_modified=False,
                )

    frappe.db.commit()


def _parse_size_string(raw):
    """Parse '5.20 KB' → 5324 (bytes). Returns None if not parseable."""
    match = re.match(r"^([\d.]+)\s*(B|KB|MB|GB|TB)$", raw, re.IGNORECASE)
    if not match:
        # Already an integer?
        try:
            return int(float(raw))
        except (ValueError, TypeError):
            return None
    value = float(match.group(1))
    unit = match.group(2).upper()
    return int(value * UNIT_MULTIPLIERS.get(unit, 1))
