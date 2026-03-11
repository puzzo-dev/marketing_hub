---
description: Marketing Hub domain knowledge including app architecture, doctype map, role hierarchy, hooks patterns, and platform integrations
---

# Marketing Hub — Domain & Architecture Skills

## App Architecture

Marketing Hub is a Frappe v15 app providing omni-channel marketing management. It integrates with ERPNext for accounting, CRM for lead attribution, and external platforms for social media and advertising.

### Module Structure

```
marketing_hub/
├── marketing_hub/               # Frappe module
│   ├── doctype/                 # 20+ doctypes
│   ├── report/                  # Script reports
│   ├── dashboard_chart/         # Dashboard charts
│   └── workspace/               # Desk workspaces
├── utils/                       # Shared utilities
│   ├── accounting.py            # GL entry, budget checks
│   ├── permissions.py           # Role-based access
│   ├── attribution_engine.py    # Lead source attribution
│   └── crm_integration.py      # CRM app sync
├── www/marketing/               # Vue SPA portal
│   ├── index.html
│   └── api.py                   # Portal API endpoints
├── fixtures/                    # Fixture data
│   └── social_media_network.json
└── hooks.py                     # App hooks config
```

### Key Doctypes

| Doctype | Type | Purpose |
|---------|------|---------|
| Marketing Hub Settings | Single | Global app configuration |
| Marketing Campaign | Regular | Campaign management with budget, channels, status |
| Campaign Activity | Regular | Individual campaign tasks/actions |
| Campaign Content | Regular | Channel-specific content per campaign |
| Social Post | Regular | Scheduled social media posts |
| Omni Blast | Submittable | Multi-channel message blasts |
| Social Media Network | Regular | Static platform definitions (fixtures) |
| Ad Account | Regular | Platform OAuth credentials |
| Analytics Connector | Regular | Daily sync configuration |
| Analytics Daily Log | Regular | Time-series ad metrics |
| Marketing Expense | Submittable | Manual expense tracking |
| Marketing Ledger Entry | Regular | Double-entry marketing accounting |
| Marketing Segment | Regular | Audience segment definitions |
| Marketing Template | Regular | Channel-specific message templates |
| Content Asset | Regular | Creative asset library |
| Agency Package | Regular | Client subscription tiers |
| Client Subscription | Regular | Active client subscriptions |
| Attribution Model | Regular | Attribution configuration |

### Role Hierarchy

| Role | Access Level |
|------|-------------|
| System Manager | Full access to all doctypes |
| Marketing Manager | Full CRUD + submit on all marketing doctypes |
| Marketing User | Create/read/write on most doctypes, no delete |

### Hooks Pattern

```python
# hooks.py key patterns
fixtures = [
    {"dt": "Workspace", "filters": [["module", "=", "Marketing Hub"]]},
    {"dt": "Social Media Network", "filters": [["is_active", "=", 1]]},
    "Attribution Model",
]

doc_events = {
    "Lead": {
        "before_insert": "marketing_hub.utils.attribution_engine.get_real_lead_source"
    },
}

scheduler_events = {
    "daily": ["marketing_hub.tasks.sync_analytics"],
    "hourly": ["marketing_hub.tasks.process_scheduled_posts"],
}
```

## Campaign vs Marketing Campaign

> **CRITICAL**: ERPNext has a built-in `Campaign` doctype (CRM module). Marketing Hub uses `Marketing Campaign` to avoid conflicts.

- All SQL queries must use `tabMarketing Campaign`, never `tabCampaign`
- All `frappe.get_doc()` calls should use `"Marketing Campaign"`
- Link fields should point to `"Marketing Campaign"` (except `email_campaign` which intentionally links to ERPNext's CRM Campaign)
- The attribution engine falls back to standard `Campaign` if no Marketing Campaign is found

## Supported Platforms (16 static)

### Social Media (7)
Facebook, Instagram, LinkedIn, Twitter/X, TikTok, YouTube, Snapchat

### Advertising (5)
Meta Ads, Google Ads, LinkedIn Ads, TikTok Ads, Twitter/X Ads

### Messaging (3)
WhatsApp, SMS, Email

### Other (1)
Out of Home (OOH)

## Analytics & Reporting

### Built-in Reports
1. **Campaign Performance** — Spend, impressions, clicks, conversions by campaign
2. **ROAS Analysis** — Revenue vs spend with monthly trends
3. **Campaign Budget vs Actual** — Budget utilization tracking

### Key Metrics
- CTR (Click-Through Rate) = Clicks / Impressions × 100
- CPC (Cost Per Click) = Spend / Clicks
- ROAS (Return on Ad Spend) = Revenue / Spend
- CPL (Cost Per Lead) = Spend / Leads
- ROI = (Revenue - Spend) / Spend × 100

## Attribution Engine

Priority-based attribution for lead sources:
1. **UTM parameters** (highest) — `utm_campaign`, `utm_source`, `utm_medium`
2. **Campaign direct link** — `campaign_name` field on Lead
3. **Fallback** — Standard Campaign lookup

Lead source is set as `{Channel}-{CampaignName}` format.

## Workspace Structure

- **Marketing Hub** (parent) — Main dashboard with overview shortcuts
  - **Social Connect** — Social media management
  - **Marketing Operations** — Campaigns, blasts, expenses
  - **Marketing Settings** — Configuration, connectors, platforms
