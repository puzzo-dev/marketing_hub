# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
import re

class MarketingTemplate(Document):
    def validate(self):
        # Set channel-specific specs
        self.set_channel_specifications()

        # Validate content against specs
        self.validate_content()

    def set_channel_specifications(self):
        """Set default specifications based on channel"""
        specs = {
            "Meta Ads": {
                "character_limit": 125,
                "image_specs": "Primary: 1200x628\nSquare: 1080x1080\nStories: 1080x1920",
                "video_specs": "Format: MP4, MOV\nDuration: 1-241 seconds\nAspect: 16:9, 1:1, 9:16"
            },
            "Google Ads": {
                "character_limit": 90,
                "image_specs": "Landscape: 1200x628\nSquare: 1200x1200\nPortrait: 960x1200",
                "video_specs": "Format: MP4, AVI, WebM\nMax size: 1GB\nDuration: Up to 3 minutes"
            },
            "LinkedIn Ads": {
                "character_limit": 150,
                "image_specs": "Single: 1200x627\nCarousel: 1080x1080",
                "video_specs": "Format: MP4\nDuration: 3 seconds - 30 minutes\nAspect: 16:9, 1:1, 9:16"
            },
            "TikTok Ads": {
                "character_limit": 100,
                "image_specs": "1080x1920",
                "video_specs": "Format: MP4, MOV, MPEG, 3GP, AVI\nDuration: 5-60 seconds\nAspect: 9:16, 1:1, 16:9"
            },
            "Twitter/X Ads": {
                "character_limit": 280,
                "image_specs": "Single: 1200x675\nCarousel: 800x800",
                "video_specs": "Format: MP4, MOV\nDuration: Up to 2:20\nAspect: 16:9, 1:1"
            },
            "Reddit Ads": {
                "character_limit": 300,
                "image_specs": "1200x628",
                "video_specs": "Format: MP4, MOV\nDuration: Up to 15 minutes"
            },
            "WhatsApp": {
                "character_limit": 1024,
                "image_specs": "Any size, max 5MB",
                "video_specs": "Format: MP4, 3GP\nMax size: 16MB"
            },
            "SMS": {
                "character_limit": 160,
                "image_specs": "N/A",
                "video_specs": "N/A"
            },
            "Email": {
                "character_limit": None,
                "image_specs": "Max width: 600px",
                "video_specs": "Embedded or linked only"
            }
        }

        if self.channel in specs and not self.character_limit:
            spec = specs[self.channel]
            self.character_limit = spec["character_limit"]
            if not self.image_specs:
                self.image_specs = spec["image_specs"]
            if not self.video_specs:
                self.video_specs = spec["video_specs"]

    def validate_content(self):
        """Validate content against channel specifications"""
        if self.character_limit and self.body_text:
            # Strip HTML tags for counting
            text = re.sub(r'<[^>]+>', '', self.body_text or '')
            if len(text) > self.character_limit:
                frappe.msgprint(
                    f"Warning: Body text ({len(text)} chars) exceeds recommended limit ({self.character_limit} chars) for {self.channel}",
                    indicator="orange"
                )

    def render(self, context=None):
        """Render template with variables replaced"""
        context = context or {}

        # Load variables from template
        variables = {}
        if self.variables:
            try:
                variables = json.loads(self.variables)
            except:
                pass

        # Merge with provided context
        context = {**variables, **context}

        # Replace variables in all text fields
        rendered = {
            "subject": self.replace_variables(self.subject, context),
            "headline": self.replace_variables(self.headline, context),
            "body_text": self.replace_variables(self.body_text, context),
            "call_to_action": self.replace_variables(self.call_to_action, context),
            "link_url": self.replace_variables(self.link_url, context)
        }

        return rendered

    def replace_variables(self, text, context):
        """Replace {variable} placeholders with values"""
        if not text:
            return text

        for key, value in context.items():
            text = text.replace(f"{{{key}}}", str(value))

        return text
