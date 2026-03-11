# Marketing Hub — Portal & Desk Architecture

## Architecture Principle

| Layer | Purpose | Tech | URL | Actors |
|-------|---------|------|-----|--------|
| **Portal (Vue SPA)** | All operational workflows | Vue 3 + frappe-ui + Pinia | `/marketing/` | Marketing Manager, Marketing User, Agent |
| **Desk (Standard Frappe)** | Setup, Accounting, Analysis | Frappe Desk | `/app/` | System Manager, Marketing Manager |

---

## Feature Matrix

### Portal — Operations (Vue SPA at `/marketing/`)

| Feature | Page | Status | User Stories |
|---------|------|--------|--------------|
| **Dashboard** | `Dashboard.vue` | Complete | View KPIs (spend, campaigns, leads, ROAS), recent activities, top campaigns |
| **Campaign Management** | `Campaigns.vue`, `NewCampaign.vue`, `CampaignDetail.vue` | Complete | List/search/filter campaigns, create campaigns with channels/budget/schedule, view campaign detail with live metrics |
| **Social Media** | `Social.vue`, `NewSocialPost.vue`, `SocialPostDetail.vue` | Complete | List social posts, create posts with platform/scheduling/targeting, view engagement metrics, publish posts |
| **Omni Blast** | `OmniBlast.vue` | Complete | 5-step wizard: select campaign → channels → segments → compose → review & send |
| **Content Library** | `Content.vue`, `ContentEditor.vue` | Complete | Browse assets (grid/list), upload assets, create/edit text/image/video content, bulk actions |
| **Segments** | `Segments.vue` | Complete | List segments with contact counts, create/edit with filter builder, test/preview segments |
| **Expenses** | `Expenses.vue` | Complete | View budget overview (KPIs + trend chart), list expenses, add new expenses |
| **Analytics** | `Analytics.vue` | Complete | Performance trend chart, channel breakdown table, connector status cards |
| **Settings** | `Settings.vue` | Complete | 5 tabs: General, Channels, Analytics, Content, Notifications (link to Desk for advanced) |

### Desk — Setup, Accounting & Analysis (`/app/`)

| Feature | Doctype / Resource | Purpose |
|---------|-------------------|---------|
| **Full Settings** | Marketing Hub Settings | 8 tabs, 50+ fields: General, Omni-Channel, Social Media, Analytics, Agency, Content, Accounting, Notifications |
| **Ad Accounts** | Ad Account | OAuth credentials per platform account |
| **Analytics Connectors** | Analytics Connector | Platform API connections for data sync |
| **Social Networks** | Social Media Network | Platform config: character limits, supported media, API endpoints |
| **Attribution Models** | Attribution Model | Define attribution logic (First Touch, Last Touch, etc.) |
| **Accounting Setup** | Marketing Expense, Marketing Ledger Entry | GL entry config, expense accounts, cost centers, budget validation |
| **Reports** | 8 Script Reports | Campaign Performance, ROAS Analysis, Budget vs Actual, Channel Attribution, Detailed ROAS, Marketing Expense Analysis, Marketing Ledger, Campaign Analytics |
| **Dashboard Charts** | 4 Dashboard Charts | Campaign Performance Overview, Channel Distribution, Monthly Budget, Monthly ROAS Trend |
| **Workspaces** | 4 Workspaces | Marketing Hub, Social Connect, Marketing Operations, Marketing Settings |

---

## Actors & Roles

| Role | Portal Access | Desk Access | Scope |
|------|--------------|-------------|-------|
| **System Manager** | Full | Full | Everything including system settings |
| **Marketing Manager** | Full | Full | All operations + setup/accounting config |
| **Marketing User** | Full (read/create/update) | Limited (view-only for setup doctypes) | Day-to-day operations: campaigns, posts, blasts, content |
| **Agent** | Agent layout (simplified nav) | None | Simplified operational tasks |

---

## Workflows

### 1. Campaign Lifecycle
```
[Portal] Create Campaign (NewCampaign.vue)
    → Set name, company, budget, dates, channels
    → Status: Draft
[Portal] Activate Campaign (CampaignDetail.vue)
    → Change status to Active
[Portal] Create Content / Social Posts / Omni Blasts
    → Link to campaign
[Portal] Monitor Performance (CampaignDetail.vue, Analytics.vue)
    → Real-time metrics from Analytics Daily Log
[Portal] Complete Campaign
    → Status: Completed
[Desk] Review Reports
    → Campaign Performance, ROAS Analysis, Budget vs Actual
```

### 2. Social Post Publishing
```
[Portal] Create Post (NewSocialPost.vue)
    → Select platform, post type, content, schedule
    → Status: Draft or Scheduled
[Backend] Auto-publish (scheduler: publish_scheduled_posts)
    → Adapter pattern: BasePlatformAdapter → GenericAdapter → Platform-specific
    → Status: Published or Failed
[Portal] View Engagement (SocialPostDetail.vue)
    → Impressions, reach, clicks, likes, comments, shares
```

### 3. Omni Blast Execution
```
[Portal] Create Blast (OmniBlast.vue - 5-step wizard)
    1. Select Campaign
    2. Select Channels (Email, SMS, WhatsApp, Social)
    3. Select Target Segments
    4. Compose Message (with character count, templates)
    5. Review & Submit
[Backend] Generate posts per network (on_submit)
    → Adapts content per channel
    → Executes via channel-specific blast functions
```

### 4. Expense Tracking
```
[Portal] Log Expense (Expenses.vue)
    → Title, campaign, amount, date, type, vendor
[Desk] Accounting Integration
    → GL entries created if enable_gl_entry is on
    → Budget validation against campaign budget
    → Marketing Ledger Entry records
```

### 5. Analytics Sync
```
[Desk] Configure Connectors (Analytics Connector doctype)
    → Platform, credentials, sync schedule
[Backend] Hourly sync (scheduler: sync_all_connectors)
    → Fetches impressions, clicks, spend, revenue per day
    → Writes to Analytics Daily Log
[Portal] View Analytics (Analytics.vue, Dashboard.vue)
    → Charts and tables from aggregated Analytics Daily Log data
```

### 6. Lead Attribution
```
[Backend] Lead created/updated (doc_events → attribution_engine)
    → Check UTM parameters (utm_campaign, utm_source, utm_medium)
    → Match to Marketing Campaign
    → Set lead_source as "{Channel}-{CampaignName}"
    → Sync with CRM
[Portal] View Attributed Leads (CampaignDetail.vue)
[Desk] Attribution Reports (Channel Attribution report)
```

---

## API Layer

All portal API endpoints are in `marketing_hub/www/marketing/api.py`:

| Endpoint | Method | Portal Page |
|----------|--------|-------------|
| `get_dashboard_data` | GET | Dashboard.vue |
| `get_analytics_data` | GET | Analytics.vue |
| `get_campaign_list` | GET | Campaigns.vue |
| `get_campaign_metrics` | GET | CampaignDetail.vue |
| `create_campaign` | POST | NewCampaign.vue |
| `update_campaign` | POST | CampaignDetail.vue |
| `get_social_posts` | GET | Social.vue |
| `create_social_post` | POST | NewSocialPost.vue |
| `update_social_post` | POST | SocialPostDetail.vue |
| `publish_social_post` | POST | SocialPostDetail.vue |
| `get_content_list` | GET | Content.vue |
| `get_content_details` | GET | ContentEditor.vue |
| `update_content_status` | POST | Content.vue |
| `get_asset_stats` | GET | Content.vue |
| `get_segment_list` | GET | Segments.vue |
| `create_segment` | POST | Segments.vue |
| `update_segment` | POST | Segments.vue |
| `get_expense_list` | GET | Expenses.vue |
| `get_budget_overview` | GET | Expenses.vue |
| `create_expense` | POST | Expenses.vue |

Content-specific endpoints are in `marketing_hub/www/marketing/content.py`:

| Endpoint | Method | Portal Page |
|----------|--------|-------------|
| `get_assets` | GET | Content.vue |
| `get_asset` | GET | ContentEditor.vue |
| `create_asset` | POST | ContentEditor.vue |
| `get_templates` | GET | Content.vue |
| `get_channels` | GET | Content.vue |
| `get_asset_types` | GET | Content.vue |
| `get_asset_stats` | GET | Content.vue |
| `upload_file` | POST | Content.vue |
| `delete_asset` | POST | Content.vue |
| `bulk_update_assets` | POST | Content.vue |
| `create_template` | POST | Content.vue |
| `get_template_categories` | GET | Content.vue |

---

## Doctype Ownership

### Operational (Portal creates/manages)
- Marketing Campaign
- Social Post
- Omni Blast
- Campaign Activity
- Content Asset
- Marketing Segment
- Marketing Expense
- Marketing Template

### Configuration (Desk manages)
- Marketing Hub Settings (Single)
- Ad Account
- Analytics Connector
- Social Media Network
- Attribution Model
- Blast Type
- Post Type
- Media Type
- Marketing Expense Category
- Marketing Campaign Channel (child)
- Marketing Hub Social Platform (child)
- Marketing Hub Connection (child)
- Template Asset Item (child)

### System (Backend creates)
- Analytics Daily Log
- Marketing Ledger Entry

---

## File Structure

```
desk/src/                          # Vue SPA (Portal)
├── App.vue                        # Layout router (Admin vs Agent)
├── router.js                      # All /marketing/* routes
├── stores/
│   ├── user.js                    # Role detection, auth
│   ├── config.js                  # Settings cache
│   └── sidebar.js                 # UI state
├── layouts/
│   ├── AdminLayout.vue            # Sidebar + content
│   └── AgentLayout.vue            # Simple topbar + content
├── pages/                         # All operational pages
│   ├── Dashboard.vue
│   ├── Campaigns.vue / NewCampaign.vue / CampaignDetail.vue
│   ├── Social.vue / NewSocialPost.vue / SocialPostDetail.vue
│   ├── OmniBlast.vue
│   ├── Segments.vue
│   ├── Content.vue / ContentEditor.vue
│   ├── Expenses.vue
│   ├── Analytics.vue
│   └── Settings.vue
└── components/                    # Shared UI components

marketing_hub/www/marketing/       # Portal backend
├── api.py                         # Main API (20+ endpoints)
├── content.py                     # Content-specific API
├── index.py                       # Auth guard + Vite asset loader
└── index.html                     # Jinja template bootstraps Vue

marketing_hub/marketing_hub/       # Frappe module (Desk)
├── doctype/                       # 25 doctypes
├── report/                        # 8 script reports
├── workspace/                     # 4 workspaces
├── dashboard/                     # Dashboard definitions
├── dashboard_chart/               # 4 chart definitions
├── number_card/                   # KPI cards
└── utils/                         # Accounting utilities

marketing_hub/utils/               # Shared backend utilities
├── permissions.py                 # Role-based query conditions
├── attribution_engine.py          # Lead-to-campaign attribution
├── auto_post.py                   # Scheduler: publish posts
├── analytics_sync.py              # Scheduler: sync connectors
├── omni_blast.py                  # Blast execution engine
├── social_adapter.py              # Platform adapter factory
├── crm_integration.py             # CRM sync
├── content_orchestration.py       # Multi-channel content adaptation
├── agency_mode.py                 # Agency features
├── oauth_integration.py           # Platform OAuth handling
└── social_adapters/               # Platform-specific adapters
    ├── base.py                    # Abstract base
    ├── generic.py                 # Config-driven adapter
    ├── meta.py                    # Facebook/Instagram
    ├── linkedin.py
    └── twitter.py
```
