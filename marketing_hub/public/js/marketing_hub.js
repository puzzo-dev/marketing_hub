// Marketing Hub Global Client Scripts
frappe.provide("marketing_hub");

marketing_hub = {
    channels: [
        "Email",
        "WhatsApp",
        "SMS",
        "Push Notification",
        "Google Ads",
        "Meta Ads",
        "TikTok Ads",
        "Twitter/X Ads",
        "Reddit Ads",
        "LinkedIn Ads",
        "Trade Show",
        "TV",
        "Radio",
        "Telecalling",
        "Outdoor",
        "Print",
        "Event",
        "Omni-Channel"
    ],

    platforms: [
        "Meta",
        "Twitter",
        "LinkedIn",
        "Instagram",
        "TikTok",
        "YouTube"
    ],

    ad_platforms: [
        "Google Ads",
        "Meta Ads",
        "TikTok Ads",
        "Twitter Ads",
        "LinkedIn Ads",
        "Reddit Ads"
    ]
};

// Helper to check agency mode
marketing_hub.is_agency_mode = function() {
    return frappe.boot.marketing_hub_mode === "Agency";
};

// Helper to calculate ROAS
marketing_hub.calculate_roas = function(revenue, cost) {
    if (!cost || cost === 0) return 0;
    return (revenue / cost).toFixed(2);
};

// Helper to format currency
marketing_hub.format_currency = function(value) {
    return format_currency(value, frappe.defaults.get_default("currency"));
};
