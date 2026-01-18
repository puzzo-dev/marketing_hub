# Marketing Hub Settings Guide

## Overview

Marketing Hub Settings is a company-specific configuration doctype that allows you to customize the behavior and features of the Marketing Hub app for each company in your ERPNext installation.

## Key Features

### 1. **Per-Company Configuration**
- Each company can have its own Marketing Hub settings
- Settings are automatically created when you access the doctype for a new company
- Autonamed by company for easy identification

### 2. **General Settings**
- **Default Campaign Naming Series**: Set the naming convention for campaigns
- **Default Lead Source**: Pre-fill lead source for new leads
- **Enable Auto Attribution**: Automatically attribute leads to campaigns based on UTM parameters
- **Enable UTM Tracking**: Track UTM parameters for campaign attribution
- **Enable Session Tracking**: Track user sessions for better attribution
- **Session Timeout (Days)**: How long to keep session data (1-365 days)

### 3. **Omni-Channel Settings**
- **Enable Email Blast**: Allow email campaigns
- **Default Email Sender**: Set default sender for marketing emails
- **Enable WhatsApp Blast**: Enable WhatsApp campaigns (requires frappe_whatsapp)
- **Enable SMS Blast**: Enable SMS campaigns (requires gateway integration)

### 4. **Social Media Settings**
- **Enable Auto Post**: Automatically publish scheduled social posts
- **Auto Post Interval**: How often to check for scheduled posts (5-1440 minutes)
- **Default Social Platforms**: Pre-select platforms for new posts
- **Require Post Approval**: Enforce approval workflow before publishing

### 5. **Advertising Platform Settings**
- **Enable Google Ads**: Activate Google Ads integration
- **Enable Meta Ads**: Activate Facebook/Instagram Ads integration
- **Enable LinkedIn Ads**: Activate LinkedIn Ads integration
- **Enable TikTok Ads**: Activate TikTok Ads integration
- **Enable Twitter/X Ads**: Activate Twitter/X Ads integration
- **Analytics Sync Frequency**: How often to sync data (Hourly/Daily/Weekly)

### 6. **Analytics Settings**
- **Enable Analytics Sync**: Sync data from advertising platforms
- **Analytics Sync Schedule**: Cron expression for sync timing (default: 2 AM daily)
- **Default Attribution Model**: Choose attribution model (First Touch, Last Touch, Linear, Time Decay, Position Based)
- **Track Conversions**: Monitor conversion events from campaigns

### 7. **Agency Settings** (Only visible when Agency Mode is enabled)
- **Max Campaigns per Client**: Limit active campaigns per client
- **Enable Client Portal**: Allow clients to access their campaign data
- **Enable White Label**: Hide agency branding from client reports
- **Client Approval Required**: Require client sign-off before campaign execution

### 8. **Content Management Settings**
- **Enable Content Library**: Use centralized content asset library
- **Enable Version Control**: Track content versions and revisions
- **Enable Brand Guidelines**: Enforce brand guidelines for content
- **Default Content Approval Workflow**: Set workflow for content approval

### 9. **Notification Settings**
- **Notify Campaign Completion**: Send alerts when campaigns complete
- **Notify Blast Execution**: Alert on blast execution
- **Notify Analytics Sync**: Alert on analytics sync completion
- **Notification Recipients**: Comma-separated email addresses for notifications

## Setup Instructions

### Initial Setup

1. Navigate to: **Marketing Hub > Settings > Marketing Hub Settings**
2. Click **New** or select your company from the list
3. Configure settings according to your needs
4. Save the document

### Testing Integrations

The form includes helpful action buttons:

1. **Test Email Configuration**: Verify email settings work
2. **Test WhatsApp Integration**: Check WhatsApp integration status
3. **Sync Analytics Now**: Trigger immediate analytics sync

### OAuth Setup

When enabling advertising platforms:
- The system will prompt you to configure OAuth credentials
- Go to **Social Login Key** or **Ad Account** to set up platform access
- Follow the platform-specific setup guides in the Integration Guide

### Migration from Old Setup

If you previously used "Marketing Hub Setup" (single doctype), your settings will be automatically migrated when you run:

```bash
bench --site your-site migrate
```

The migration patch will:
- Create Marketing Hub Settings for all companies
- Copy agency mode settings from old setup
- Set sensible defaults for all options

## API Usage

### Get Settings Programmatically

```python
from marketing_hub.utils.agency_mode import get_settings

# Get settings for current company
settings = get_settings()

# Get settings for specific company
settings = get_settings(company="My Company")

# Access settings
if settings.enable_auto_attribution:
    # Do attribution logic
    pass
```

### Check Agency Mode

```python
from marketing_hub.utils.agency_mode import get_agency_mode

is_agency = get_agency_mode()  # Current company
is_agency = get_agency_mode(company="My Company")  # Specific company
```

### Create Default Settings

```python
from marketing_hub.marketing_hub.doctype.marketing_hub_settings.marketing_hub_settings import create_default_settings

settings = create_default_settings("My Company")
```

## Validation Rules

The doctype includes validation to ensure:
- Session timeout is between 1-365 days
- Auto post interval is between 5-1440 minutes
- Max campaigns per client is at least 1 (if agency mode is enabled)

## Permissions

- **System Manager**: Full access (create, read, write, delete)
- **Marketing Manager**: Read and write access

## Best Practices

1. **Start Conservative**: Enable features gradually as you test them
2. **Test Before Production**: Use the test buttons to verify integrations
3. **Monitor Notifications**: Set up notification recipients for important events
4. **Review Periodically**: Audit settings quarterly to ensure they match your workflow
5. **Document Custom Settings**: Keep notes on why specific settings are enabled/disabled

## Troubleshooting

### Email Blast Not Working
- Check "Enable Email Blast" is checked
- Verify "Default Email Sender" is configured
- Use "Test Email Configuration" button
- Check Email Account settings in ERPNext

### WhatsApp Blast Failing
- Ensure frappe_whatsapp app is installed
- Verify WhatsApp Settings has a default outgoing account
- Use "Test WhatsApp Integration" button

### Analytics Not Syncing
- Check "Enable Analytics Sync" is enabled
- Verify advertising platforms are enabled (Google Ads, Meta Ads, etc.)
- Check Analytics Connector has valid OAuth credentials
- Review Analytics Daily Log for errors
- Use "Sync Analytics Now" button for immediate sync

### Agency Mode Not Working
- Ensure "Agency Mode" checkbox is enabled
- Verify Agency Package and Client Subscription doctypes exist
- Check client has an active subscription

## Related Documentation

- [Integration Guide](../INTEGRATION_GUIDE.md)
- [Setup Guide](../SETUP_GUIDE.md)
- [Implementation Summary](../IMPLEMENTATION_SUMMARY.md)
- [Workspace Permissions](../WORKSPACE_PERMISSIONS.md)
