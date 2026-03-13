# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


MARKETING_HUB_FOLDER = "Home/Marketing Hub"


class ContentAsset(Document):
    def before_save(self):
        if self.file_attachment:
            self._sync_file_metadata()

    def after_insert(self):
        if self.file_attachment:
            self._link_file_to_asset("file_attachment")
        if self.thumbnail and self.thumbnail != self.file_attachment:
            self._link_file_to_asset("thumbnail")

    def on_trash(self):
        """Delete attached File records when Content Asset is deleted."""
        files = frappe.get_all(
            "File",
            filters={
                "attached_to_doctype": "Content Asset",
                "attached_to_name": self.name,
            },
            pluck="name",
        )
        for fname in files:
            frappe.delete_doc("File", fname, ignore_permissions=True)

    def _sync_file_metadata(self):
        """Read file_size from the linked Frappe File doctype (bytes)."""
        file_doc = frappe.db.get_value(
            "File",
            {"file_url": self.file_attachment},
            ["file_size"],
            as_dict=True,
        )
        if file_doc and file_doc.file_size:
            self.file_size = file_doc.file_size

    def _link_file_to_asset(self, fieldname):
        """Set attached_to_* on the Frappe File doc so Drive can find it."""
        file_url = self.get(fieldname)
        if not file_url:
            return

        file_name = frappe.db.get_value("File", {"file_url": file_url}, "name")
        if not file_name:
            return

        frappe.db.set_value(
            "File",
            file_name,
            {
                "attached_to_doctype": "Content Asset",
                "attached_to_name": self.name,
                "attached_to_field": fieldname,
            },
            update_modified=False,
        )

    def increment_usage(self):
        """Increment usage count when asset is used."""
        self.usage_count = (self.usage_count or 0) + 1
        self.last_used = frappe.utils.now()
        self.save(ignore_permissions=True)

    @staticmethod
    def ensure_folder(folder_path=MARKETING_HUB_FOLDER):
        """Ensure the Marketing Hub folder exists in File Manager."""
        parts = folder_path.split("/")
        current = parts[0]  # "Home"
        for part in parts[1:]:
            parent = current
            current = f"{current}/{part}"
            if not frappe.db.exists("File", {"file_name": part, "is_folder": 1, "folder": parent}):
                folder = frappe.get_doc({
                    "doctype": "File",
                    "file_name": part,
                    "is_folder": 1,
                    "folder": parent,
                })
                folder.insert(ignore_permissions=True)
        return current
