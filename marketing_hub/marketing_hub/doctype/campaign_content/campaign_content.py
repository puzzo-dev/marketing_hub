# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CampaignContent(Document):
    def validate(self):
        # Auto-populate UTM parameters
        if not self.utm_campaign:
            self.utm_campaign = self.campaign
        if not self.utm_source:
            self.utm_source = self.channel.lower().replace(" ", "_")
        if not self.utm_medium:
            self.utm_medium = self.get_utm_medium()

    def get_utm_medium(self):
        """Determine UTM medium based on channel from Social Media Network doctype"""
        try:
            network = frappe.get_cached_doc("Social Media Network", self.channel)
            network_type = network.network_type or "Social Media"
            
            # Map network type to UTM medium
            utm_mapping = {
                "Advertising Platform": "paid_search" if "Google" in self.channel else "paid_social",
                "Social Media": "social",
                "Messaging": "messaging",
                "Email": "email",
                "Search Engine": "organic",
                "Out of Home (OOH)": "offline"
            }
            return utm_mapping.get(network_type, "referral")
        except:
            # Fallback logic
            if "Ads" in self.channel:
                return "paid_search" if "Google" in self.channel else "paid_social"
            elif self.channel == "Email":
                return "email"
            elif self.channel in ["WhatsApp", "SMS"]:
                return "messaging"
            else:
                return "organic"

    def before_save(self):
        self.generate_preview()

    def generate_preview(self):
        """Generate HTML preview of content"""
        content = self.get_rendered_content()

        preview_html = f"""
        <div class="campaign-content-preview" style="border: 1px solid #d1d8dd; padding: 15px; border-radius: 5px; background: #f9fafb;">
            <div class="channel-badge" style="display: inline-block; background: #3b82f6; color: white; padding: 4px 12px; border-radius: 4px; font-size: 12px; margin-bottom: 10px;">
                {self.channel}
            </div>
        """

        if content.get("subject"):
            preview_html += f'<h4 style="margin: 10px 0;">{content["subject"]}</h4>'

        if content.get("headline"):
            preview_html += f'<h5 style="margin: 10px 0; color: #374151;">{content["headline"]}</h5>'

        if content.get("body_text"):
            preview_html += f'<div style="margin: 10px 0;">{content["body_text"]}</div>'

        if content.get("call_to_action"):
            preview_html += f'<div style="margin-top: 15px;"><button style="background: #3b82f6; color: white; padding: 8px 20px; border: none; border-radius: 4px; cursor: pointer;">{content["call_to_action"]}</button></div>'

        if content.get("link_url"):
            preview_html += f'<div style="margin-top: 10px; font-size: 12px; color: #6b7280;">🔗 {content["link_url"]}</div>'

        preview_html += "</div>"

        self.preview_html = preview_html

    def get_rendered_content(self):
        """Get final rendered content (template + custom overrides)"""
        content = {
            "subject": self.custom_subject,
            "headline": self.custom_headline,
            "body_text": self.custom_body,
            "call_to_action": self.custom_cta,
            "link_url": self.custom_link_url
        }

        # If template is specified, use it as base
        if self.template:
            template = frappe.get_doc("Marketing Template", self.template)
            template_content = template.render()

            # Override with custom values if provided
            for key in content:
                if not content[key]:
                    content[key] = template_content.get(key)

        # Add UTM parameters to link
        if content["link_url"]:
            content["link_url"] = self.add_utm_params(content["link_url"])

        return content

    def add_utm_params(self, url):
        """Add UTM parameters to URL"""
        if not url:
            return url

        separator = "&" if "?" in url else "?"
        utm_params = []

        if self.utm_campaign:
            utm_params.append(f"utm_campaign={self.utm_campaign}")
        if self.utm_source:
            utm_params.append(f"utm_source={self.utm_source}")
        if self.utm_medium:
            utm_params.append(f"utm_medium={self.utm_medium}")

        if utm_params:
            return url + separator + "&".join(utm_params)

        return url
