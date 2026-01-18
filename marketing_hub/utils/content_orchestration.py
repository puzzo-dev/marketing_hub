# -*- coding: utf-8 -*-
# Copyright (c) 2026, I-Varse Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _

@frappe.whitelist()
def create_campaign_content_for_channels(campaign, channels, template=None):
    """
    Create Campaign Content entries for multiple channels at once

    Args:
        campaign: Campaign name
        channels: Comma-separated list of channels or list
        template: Optional base template to use

    Returns:
        List of created Campaign Content names
    """
    if isinstance(channels, str):
        channels = [c.strip() for c in channels.split(",")]

    created_content = []

    for channel in channels:
        # Check if content already exists
        existing = frappe.db.exists("Campaign Content", {
            "campaign": campaign,
            "channel": channel
        })

        if existing:
            frappe.msgprint(_(f"Content for {channel} already exists"))
            continue

        # Find appropriate template for channel
        channel_template = template
        if not channel_template:
            templates = frappe.get_all(
                "Marketing Template",
                filters={"channel": channel, "status": "Active"},
                order_by="modified desc",
                limit=1
            )
            if templates:
                channel_template = templates[0].name

        # Create Campaign Content
        content = frappe.new_doc("Campaign Content")
        content.campaign = campaign
        content.channel = channel
        if channel_template:
            content.template = channel_template
        content.insert()

        created_content.append(content.name)

    frappe.msgprint(_(f"Created content for {len(created_content)} channels"))

    return created_content


@frappe.whitelist()
def adapt_content_for_channel(source_content, target_channel):
    """
    Adapt existing content for a different channel

    Args:
        source_content: Source Campaign Content name
        target_channel: Target channel to adapt for

    Returns:
        New Campaign Content name
    """
    source = frappe.get_doc("Campaign Content", source_content)

    # Get rendered content from source
    rendered = source.get_rendered_content()

    # Create new content for target channel
    new_content = frappe.new_doc("Campaign Content")
    new_content.campaign = source.campaign
    new_content.channel = target_channel

    # Adapt content based on channel specs
    adapted = adapt_content_to_specs(rendered, target_channel)

    new_content.custom_subject = adapted.get("subject")
    new_content.custom_headline = adapted.get("headline")
    new_content.custom_body = adapted.get("body_text")
    new_content.custom_cta = adapted.get("call_to_action")
    new_content.custom_link_url = adapted.get("link_url")

    new_content.insert()

    return new_content.name


def adapt_content_to_specs(content, channel):
    """
    Adapt content to fit channel specifications

    Args:
        content: Dict with content fields
        channel: Target channel

    Returns:
        Adapted content dict
    """
    channel_specs = {
        "SMS": {"max_chars": 160, "no_html": True},
        "WhatsApp": {"max_chars": 1024, "no_html": False},
        "Twitter/X Ads": {"max_chars": 280, "no_html": False},
        "Meta Ads": {"max_chars": 125, "no_html": False},
        "Google Ads": {"max_chars": 90, "no_html": True},
        "LinkedIn Ads": {"max_chars": 150, "no_html": False},
        "TikTok Ads": {"max_chars": 100, "no_html": True},
        "Reddit Ads": {"max_chars": 300, "no_html": False}
    }

    specs = channel_specs.get(channel, {})
    adapted = content.copy()

    # Strip HTML if needed
    if specs.get("no_html"):
        import re
        for key in ["body_text", "subject", "headline"]:
            if adapted.get(key):
                adapted[key] = re.sub(r'<[^>]+>', '', adapted[key])

    # Truncate if exceeds limit
    if specs.get("max_chars") and adapted.get("body_text"):
        body = adapted["body_text"]
        if len(body) > specs["max_chars"]:
            adapted["body_text"] = body[:specs["max_chars"]-3] + "..."
            frappe.msgprint(
                _(f"Body text truncated to {specs['max_chars']} characters for {channel}"),
                indicator="orange"
            )

    return adapted


@frappe.whitelist()
def get_content_recommendations(campaign, channel):
    """
    Get AI/rule-based content recommendations for a channel

    Args:
        campaign: Campaign name
        channel: Channel to get recommendations for

    Returns:
        Dict with recommendations
    """
    campaign_doc = frappe.get_doc("Campaign", campaign)

    recommendations = {
        "suggested_templates": [],
        "content_tips": [],
        "spec_warnings": []
    }

    # Find similar successful campaigns
    similar_campaigns = frappe.get_all(
        "Campaign",
        filters={
            "name": ["!=", campaign],
            "channels_used": ["like", f"%{channel}%"]
        },
        fields=["name", "roas"],
        order_by="roas desc",
        limit=3
    )

    if similar_campaigns:
        # Get their templates
        for camp in similar_campaigns:
            templates = frappe.get_all(
                "Campaign Content",
                filters={"campaign": camp.name, "channel": channel},
                fields=["template"]
            )
            for t in templates:
                if t.template:
                    recommendations["suggested_templates"].append(t.template)

    # Channel-specific tips
    tips = {
        "Meta Ads": [
            "Use eye-catching images (1200x628 or 1080x1080)",
            "Lead with value proposition in first 125 characters",
            "Include clear CTA button text",
            "Test multiple ad variants (A/B testing)"
        ],
        "Google Ads": [
            "Include keywords in headline",
            "Highlight unique selling proposition",
            "Use ad extensions (sitelinks, callouts)",
            "Match landing page to ad message"
        ],
        "LinkedIn Ads": [
            "Professional tone and B2B focus",
            "Use company/role targeting effectively",
            "Include social proof or credentials",
            "Optimize for lead generation"
        ],
        "TikTok Ads": [
            "Vertical video format (9:16)",
            "Hook viewers in first 3 seconds",
            "Native, authentic content style",
            "Use trending sounds and effects"
        ],
        "Email": [
            "Personalize subject line",
            "Mobile-responsive design",
            "Single clear CTA",
            "Test send times"
        ]
    }

    recommendations["content_tips"] = tips.get(channel, [])

    return recommendations


@frappe.whitelist()
def bulk_schedule_content(campaign, schedule_plan):
    """
    Schedule multiple channel content according to plan

    Args:
        campaign: Campaign name
        schedule_plan: List of dicts with channel and datetime

    Returns:
        Success message
    """
    import json
    if isinstance(schedule_plan, str):
        schedule_plan = json.loads(schedule_plan)

    for item in schedule_plan:
        content_list = frappe.get_all(
            "Campaign Content",
            filters={
                "campaign": campaign,
                "channel": item["channel"]
            }
        )

        for content in content_list:
            doc = frappe.get_doc("Campaign Content", content.name)
            doc.scheduled_date = item["scheduled_date"]
            doc.status = "Scheduled"
            doc.save()

    return f"Scheduled {len(schedule_plan)} channel content items"


def get_channel_best_practices():
    """Return best practices and specifications for all channels"""
    return {
        "Meta Ads": {
            "image_sizes": {
                "Feed": "1200x628",
                "Square": "1080x1080",
                "Stories": "1080x1920"
            },
            "video_specs": {
                "format": ["MP4", "MOV"],
                "duration": "1-241 seconds",
                "aspect_ratios": ["16:9", "1:1", "9:16", "4:5"]
            },
            "text_limits": {
                "primary_text": 125,
                "headline": 40,
                "description": 30
            },
            "best_practices": [
                "Use high-quality visuals",
                "Test multiple ad formats",
                "Include clear CTA",
                "Target specific audiences"
            ]
        },
        "Google Ads": {
            "image_sizes": {
                "Landscape": "1200x628",
                "Square": "1200x1200",
                "Portrait": "960x1200"
            },
            "text_limits": {
                "headline": 30,
                "description": 90,
                "display_path": 15
            },
            "best_practices": [
                "Use keywords in headlines",
                "Highlight unique value",
                "Include pricing if competitive",
                "Use ad extensions"
            ]
        },
        "LinkedIn Ads": {
            "image_sizes": {
                "Single Image": "1200x627",
                "Carousel": "1080x1080"
            },
            "text_limits": {
                "intro_text": 150,
                "headline": 70,
                "description": 100
            },
            "best_practices": [
                "Professional B2B messaging",
                "Use social proof",
                "Target by job title/industry",
                "Focus on business outcomes"
            ]
        },
        "TikTok Ads": {
            "video_specs": {
                "aspect_ratio": "9:16 (recommended)",
                "duration": "5-60 seconds",
                "format": ["MP4", "MOV", "MPEG", "3GP", "AVI"]
            },
            "text_limits": {
                "ad_text": 100
            },
            "best_practices": [
                "Native, authentic content",
                "Hook in first 3 seconds",
                "Use trending sounds",
                "Show product in action"
            ]
        },
        "Email": {
            "design_specs": {
                "max_width": "600px",
                "mobile_responsive": True
            },
            "text_limits": {
                "subject_line": 50,
                "preheader": 100
            },
            "best_practices": [
                "Personalize content",
                "Clear hierarchy",
                "Single primary CTA",
                "Test across email clients"
            ]
        }
    }
