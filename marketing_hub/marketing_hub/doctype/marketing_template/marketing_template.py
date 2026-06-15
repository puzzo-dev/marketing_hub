# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

import json
import re

import frappe
from frappe.model.document import Document


class MarketingTemplate(Document):
    def validate(self):
        # Set channel-specific specs
        self.set_channel_specifications()

        # Validate content against specs
        self.validate_content()

    def set_channel_specifications(self):
        """Set default specifications based on channel from Social Media Network doctype"""
        if not self.channel:
            return
        
        try:
            # Get channel configuration from Social Media Network doctype
            network = frappe.get_doc("Social Media Network", self.channel)
            
            # Set character limit
            if network.max_text_length:
                self.character_limit = network.max_text_length
            
            # Set image specs from JSON field
            if network.image_specifications:
                import json
                if isinstance(network.image_specifications, str):
                    image_specs = json.loads(network.image_specifications)
                else:
                    image_specs = network.image_specifications
                
                # Convert dict to formatted string
                self.image_specs = "\n".join([f"{k}: {v}" for k, v in image_specs.items()])
            
            # Set video specs from JSON field
            if network.video_specifications:
                import json
                if isinstance(network.video_specifications, str):
                    video_specs = json.loads(network.video_specifications)
                else:
                    video_specs = network.video_specifications
                
                # Convert dict to formatted string
                video_lines = []
                for k, v in video_specs.items():
                    if isinstance(v, list):
                        video_lines.append(f"{k.title()}: {', '.join(v)}")
                    else:
                        video_lines.append(f"{k.title()}: {v}")
                self.video_specs = "\n".join(video_lines)
        
        except Exception as e:
            frappe.log_error(f"Error setting channel specifications: {str(e)}", "Marketing Template")

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
