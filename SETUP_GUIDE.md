# Marketing Hub - Quick Start Guide

## What We've Built

✅ **Core Infrastructure Created:**
- Config & Desktop module
- Custom Fields for Campaign and Lead
- Attribution Engine
- Omni-Blast Engine
- Auto-Post Scheduler
- Analytics Sync System
- Agency Mode Manager
- Client-side scripts
- Event hooks and schedulers

## Next Steps: Create Doctypes

You need to create the following doctypes through Frappe Desk UI. Here are the exact specifications:

### 1. Marketing Segment
```
Module: Marketing Hub
Fields:
- segment_name (Data, mandatory)
- company (Link: Company, mandatory)
- description (Text Editor)
- customer_group (Link: Customer Group)
- territory (Link: Territory)
- lead_source (Link: Lead Source)
- segment_size (Int, read-only)
```

### 2. Marketing Template
```
Module: Marketing Hub
Fields:
- template_name (Data, mandatory)
- company (Link: Company, mandatory)
- campaign (Link: Campaign)
- channel (Select: Email, WhatsApp, SMS, Push Notification, mandatory)
- subject (Data)
- content (Text Editor, mandatory)
- media_url (Data)
```

### 3. Social Post
```
Module: Marketing Hub
Fields:
- company (Link: Company, mandatory)
- client (Link: Customer)
- platform (Select: Meta, Twitter, LinkedIn, Instagram, TikTok, YouTube, mandatory)
- content (Text Editor, mandatory)
- media_url (Data)
- scheduled_time (Datetime, mandatory)
- status (Select: Draft, Scheduled, Publishing, Published, Failed)
- published_time (Datetime, read-only)
- post_results (JSON, read-only)
```

### 4. Ad Account
```
Module: Marketing Hub
Fields:
- account_name (Data, mandatory)
- company (Link: Company, mandatory)
- platform (Select: Google Ads, Meta Ads, TikTok Ads, Twitter Ads, LinkedIn Ads, mandatory)
- account_id (Data, mandatory)
- access_token (Password)
- refresh_token (Password)
- status (Select: Active, Inactive, Expired)
```

### 5. Analytics Connector
```
Module: Marketing Hub
Fields:
- connector_name (Data, mandatory)
- company (Link: Company, mandatory)
- platform (Select: Google Ads, Meta Ads, TikTok Ads, Twitter Ads, LinkedIn Ads, mandatory)
- account_id (Data, mandatory)
- access_token (Password)
- refresh_token (Password)
- sync_frequency (Select: Daily, Weekly, Monthly)
- last_sync (Datetime, read-only)
- status (Select: Active, Inactive, Error)
```

### 6. Analytics Daily Log
```
Module: Marketing Hub
Fields:
- connector (Link: Analytics Connector, mandatory)
- platform (Data, read-only)
- campaign (Link: Campaign, mandatory)
- date (Date, mandatory)
- impressions (Int)
- clicks (Int)
- cost (Currency)
- conversions (Int)
- ctr (Percent, read-only)
- cpc (Currency, read-only)
- conversion_rate (Percent, read-only)
- cost_per_conversion (Currency, read-only)

Indexes:
- connector + campaign + date (unique)
```

### 7. Marketing Hub Setup (Single DocType)
```
Module: Marketing Hub
Is Single: Yes
Fields:
- mode (Select: Internal, Agency, mandatory, default: Internal)
- default_company (Link: Company)
- enable_multi_company (Check)
- agency_settings_section (Section Break)
- require_client_subscription (Check)
- default_billing_cycle (Int, default: 1)
```

### 8. Agency Package
```
Module: Marketing Hub
Fields:
- package_name (Data, mandatory)
- description (Text Editor)
- monthly_fee (Currency, mandatory)
- billing_cycle_months (Int, default: 1)
- campaign_limit (Int)
- included_channels (MultiSelect: [same as Campaign channels])
- features (Text Editor)
- is_active (Check, default: 1)
```

### 9. Client Subscription
```
Module: Marketing Hub
Fields:
- client (Link: Customer, mandatory)
- package (Link: Agency Package, mandatory)
- start_date (Date, mandatory)
- end_date (Date, mandatory)
- status (Select: Active, Expired, Cancelled, mandatory)
- monthly_fee (Currency, read-only)
- billing_details (Text Editor)
```

### 10. Campaign Activity (Child Table)
```
Module: Marketing Hub
Is Child Table: Yes
Fields:
- activity_type (MultiSelect: [same channels as Campaign])
- is_omni_blast (Check)
- target_all_companies (Check)
- segment (Link: Marketing Segment)
- status (Select: Draft, Scheduled, Running, Completed, Failed)
- scheduled_time (Datetime)
- results (JSON, read-only)
```

## Installation Commands

### 1. Build the App
```bash
cd /home/puxxo/CodeBase/erpNext/frappe-bench-v15
source env/bin/activate
bench build --app marketing_hub
```

### 2. Import Custom Fields
```bash
bench --site erpnext-v15.local import-fixtures
```

### 3. Clear Cache
```bash
bench --site erpnext-v15.local clear-cache
bench restart
```

### 4. Enable Scheduler
```bash
bench --site erpnext-v15.local enable-scheduler
```

## Testing the Installation

### 1. Check Custom Fields
```bash
bench --site erpnext-v15.local console
```
```python
frappe.get_meta("Campaign").get_field("channels_used")
frappe.get_meta("Lead").get_field("utm_campaign")
```

### 2. Test Attribution Engine
Create a new Lead with UTM parameters and check if attribution works.

### 3. Test Utils Modules
```python
from marketing_hub.utils import attribution_engine
from marketing_hub.utils import agency_mode

# Check agency mode
agency_mode.get_agency_mode()

# Test attribution (requires a lead)
# lead = frappe.get_doc("Lead", "LEAD-0001")
# attribution_engine.get_real_lead_source(lead, None)
```

## Usage Examples

### Creating a Segment
1. Go to Marketing Segment
2. Fill segment name and company
3. Add filters (customer group, territory, etc.)
4. Save

### Creating a Campaign with Omni-Channel
1. Go to Campaign doctype
2. Fill campaign details
3. Check "Omni-Channel Campaign"
4. Select multiple channels (Email, WhatsApp, Meta Ads, etc.)
5. Link to Client if in Agency mode
6. Save and Submit

### Scheduling a Social Post
1. Go to Social Post
2. Fill content and select platform
3. Set scheduled time
4. Status will auto-change to "Scheduled"
5. Scheduler will publish at scheduled time

### Running an Omni-Blast
1. Open a Campaign
2. Click "Execute Blast" button
3. Select target segment
4. Choose channels
5. Set schedule time
6. Execute

## Troubleshooting

### Custom Fields Not Showing
```bash
bench --site erpnext-v15.local migrate
bench --site erpnext-v15.local clear-cache
```

### Scheduler Not Running
```bash
bench --site erpnext-v15.local enable-scheduler
bench doctor  # Check for issues
```

### JS Files Not Loading
```bash
bench build --app marketing_hub
bench clear-cache
```

### Import Errors in Python
```bash
cd apps/marketing_hub
# Check for syntax errors
python -m py_compile marketing_hub/utils/*.py
```

## File Checklist

- [x] marketing_hub/config/desktop.py
- [x] marketing_hub/fixtures/custom_fields.json
- [x] marketing_hub/utils/attribution_engine.py
- [x] marketing_hub/utils/omni_blast.py
- [x] marketing_hub/utils/auto_post.py
- [x] marketing_hub/utils/analytics_sync.py
- [x] marketing_hub/utils/agency_mode.py
- [x] marketing_hub/public/js/marketing_hub.js
- [x] marketing_hub/public/js/campaign.js
- [x] hooks.py (updated with fixtures, events, schedulers)
- [ ] Doctypes (create via Desk UI)
- [ ] Dashboard page (optional - can create later)

## What's Working Now

✅ Custom fields will be added to Campaign and Lead
✅ Lead attribution engine will auto-tag leads
✅ Utils modules are ready for omni-blast, posting, analytics
✅ Agency mode helper functions available
✅ Scheduler hooks configured (will run once doctypes exist)
✅ Client-side scripts loaded for Campaign form

## What Needs Manual Creation

⚠️ All 10 doctypes listed above
⚠️ Dashboard page (optional Vue component)
⚠️ Reports (can create later)

## Next Immediate Action

1. Import custom fields:
```bash
cd /home/puxxo/CodeBase/erpNext/frappe-bench-v15
source env/bin/activate
bench --site erpnext-v15.local import-fixtures
bench --site erpnext-v15.local clear-cache
```

2. Build assets:
```bash
bench build --app marketing_hub
```

3. Restart:
```bash
bench restart
```

4. Then create the doctypes through Desk UI following the specs above.

That's it! The core infrastructure is ready. Once you create the doctypes, the entire system will be functional.
