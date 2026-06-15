# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

import os

import frappe
from frappe.model.document import Document


class ContentAsset(Document):
    def before_save(self):
        # Calculate file size if file is attached
        if self.file_attachment:
            file_doc = frappe.get_doc("File", {"file_url": self.file_attachment})
            if file_doc and file_doc.file_size:
                self.file_size = self.format_file_size(file_doc.file_size)

    def format_file_size(self, size_bytes):
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

    def increment_usage(self):
        """Increment usage count when asset is used"""
        self.usage_count = (self.usage_count or 0) + 1
        self.last_used = frappe.utils.now()
        self.save(ignore_permissions=True)
