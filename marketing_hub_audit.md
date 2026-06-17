# Marketing Hub — Technical Due Diligence Report

**Date**: 2026-06-13  
**Version Audited**: 1.0.0-beta.1  
**Repo**: `puzzo-dev/marketing_hub`  
**Framework**: Frappe v15, ERPNext integration  
**Frontend**: Vue 3 SPA (Frappe UI + Pinia + Tailwind)  
**Codebase**: ~13,100 lines Python · ~8,400 lines Vue/JS · 29 DocTypes · 103 whitelisted APIs

---

## 1. SYSTEM OVERVIEW

### 1.1 Business Purpose

Marketing Hub is a Frappe app designed to **run and manage marketing campaigns across indoor, outdoor, social media, and digital channels** — functioning as a unified marketing operations center that integrates with ERPNext's financial infrastructure.

It solves three core problems:
1. **Campaign orchestration** — plan, schedule, and execute multi-channel campaigns (email, SMS, WhatsApp, social media, OOH/billboards) from a single interface
2. **Marketing finance** — track expenses against campaign budgets via proper GL entries tied to ERPNext's Chart of Accounts, with dedicated marketing cost centers
3. **Attribution & analytics** — sync platform analytics (Google Ads, Meta, LinkedIn, etc.), attribute leads back to campaigns, and calculate ROI/ROAS

It also has a **dual-mode architecture**: standard operations mode for internal marketing teams, and an **agency mode** for marketing agencies managing multiple clients with subscription-based billing.

### 1.2 Functional Scope

| Category | Assets |
|---|---|
| **DocTypes (standalone)** | 21 — Marketing Campaign, Social Post, Omni Blast, Marketing Expense, Marketing Segment, Content Asset, Marketing Template, Campaign Activity, Campaign Content, Tracking Link, Tracking Link Click, Analytics Connector, Analytics Daily Log, Ad Account, Social Media Network, Attribution Model, Blast Type, Media Type, Post Type, Marketing Ledger Entry, Agency Package, Client Subscription, Marketing Expense Category, Marketing Hub Settings |
| **DocTypes (child)** | 5 — Marketing Campaign Channel, Marketing Hub Company Settings, Marketing Hub Connection, Marketing Hub Social Platform, Template Asset Item |
| **Submittable DocTypes** | 2 — Marketing Expense, Omni Blast |
| **Single DocType** | 1 — Marketing Hub Settings (66 fields, global configuration) |
| **API modules** | 10 — agency.py, campaigns.py, content.py, dashboard.py, expenses.py, leads.py, permission.py, segments.py, social.py, tracking.py |
| **Utility modules** | 13 — accounting.py, agency_mode.py, analytics_sync.py, attribution_engine.py, auto_post.py, content_orchestration.py, crm_integration.py, dashboard.py, oauth_integration.py, omni_blast.py, permissions.py, social_adapter.py, social_adapters/ |
| **Social Adapters** | 5 — base.py (ABC), generic.py (config-driven), meta.py, linkedin.py, twitter.py |
| **Reports** | 1 — ROAS Analysis (Script Report with chart) |
| **Patches** | 14 — seed data, migrations, chart of accounts setup |
| **Scheduled Jobs** | 2 — `publish_scheduled_posts` (every minute via `all`), `sync_all_connectors` (hourly) |
| **Frontend pages** | 16 — Dashboard, Campaigns, Social, Analytics, OmniBlast, Segments, Content, Expenses, TrackingLinks, Leads, Clients, Settings, + detail/creation views |
| **Workspaces** | 4 — Marketing Hub, Social Connect, Marketing Operations, Marketing Settings |
| **Website routes** | 3 — `/marketing/*` (SPA), `/t/<short_code>` (tracking redirect), `/marketing_hub/*` |
| **Notifications** | 2 — Campaign Completion Alert, Omni Blast Published |
| **Fixtures** | 4 — Custom Fields (Lead UTM), Workspaces, Social Media Networks, Attribution Models |

### 1.3 User Journey Mapping

**Primary workflow (Campaign Manager)**:
```
Settings → Create Campaign → Define Channels → Create Content/Templates
    → Build Segment (audience) → Schedule Omni Blast → Submit Blast
    → Auto-generate Social Posts per network → Publish (manual or scheduled)
    → Track clicks via Tracking Links → Sync analytics from platforms
    → View Dashboard (spend, leads, ROI, ROAS) → Record Expenses (GL entries)
```

**Agency workflow**:
```
Enable Agency Mode → Create Agency Packages → Onboard Clients
    → Create Client Subscriptions → Manage per-client campaigns
    → Enforce campaign limits per subscription tier
    → Track per-client billing and channel permissions
```

**Lead attribution flow** (passive, hook-driven):
```
Lead created (any source) → before_insert hook fires
    → attribution_engine.get_real_lead_source() inspects UTM params
    → Sets lead_source = "Marketing-{campaign}" or "Standard-{campaign}"
    → If CRM app installed, enqueues sync to CRM Lead
```

**OOH/Offline tracking flow**:
```
Create Tracking Link (destination URL + UTM params)
    → Auto-generate QR code → Print for billboard/poster
    → User scans QR → /t/<short_code> → handle_redirect()
    → IP anonymized → click recorded → redirect to destination with UTM
```

---

## 2. FRAPPE APP ARCHITECTURE ANALYSIS

### 2.1 Architectural Approach

**Hybrid: Domain-driven modules + Event-driven hooks + Adapter pattern**

The app uses a clean separation:
- `api/` — Dedicated API layer for the Vue SPA (10 modules, ~100 whitelisted methods)
- `utils/` — Business logic (accounting, permissions, adapters, integrations)
- `doctype/` — Data models with minimal controller logic
- `hooks.py` — Event wiring (doc_events, scheduler, permissions)
- `frontend/` — Standalone Vue 3 SPA (not Frappe desk pages)

This is **not** a monolithic ERPNext customization. It's a properly structured standalone app that integrates with ERPNext via:
- GL entry creation through `erpnext.accounts.general_ledger`
- Custom Fields on Lead (UTM fields via fixtures)
- Lead doc_event hook for attribution
- Cost Center and Account lookups

### 2.2 Folder Structure Analysis

```
marketing_hub/
├── api/              # Vue SPA API layer — whitelisted methods called by frontend
│                     # Exists because the frontend is a standalone SPA, not desk forms
├── config/           # Desktop module definition for Frappe desk sidebar
├── marketing_hub/    # Frappe module directory (doctype, report, workspace, fixtures)
│   ├── doctype/      # 29 DocType definitions (JSON schema + Python controller)
│   ├── report/       # ROAS Analysis script report
│   └── workspace/    # 4 workspace JSON definitions (desk navigation)
├── patches/          # 14 data migration patches (seeding, schema changes)
├── public/           # Static assets (CSS, JS, built frontend)
├── templates/        # Jinja templates (email, pages)
├── tests/            # 8 test files (pytest)
├── utils/            # Core business logic
│   └── social_adapters/  # Platform-specific adapter implementations
├── www/              # Website pages (SPA entry point, tracking redirect)
├── hooks.py          # Central wiring: events, scheduler, permissions, fixtures
├── install.py        # Post-install setup (file folder, notifications)
└── patches.txt       # Patch execution order
```

**Key architectural decision**: The API layer (`api/`) exists because the frontend is a Vue SPA communicating exclusively through `frappe.call()`. The DocType controllers are intentionally thin — business logic lives in `utils/` to keep controllers focused on lifecycle hooks. This is a good Frappe pattern.

---

## 3. BENCH & MULTI-SITE ANALYSIS

### 3.1 Site Structure

- **No multi-site assumptions**: The app uses `frappe.local.site` only for display (passed to frontend context). No hardcoded site references.
- **Multi-company aware**: Marketing Hub Settings has a `company_settings` child table allowing per-company expense accounts, cost centers, and payable accounts. Most API methods accept a `company` parameter with fallback to `frappe.defaults.get_user_default("Company")`.
- **No containerization assumptions**: No Dockerfile, docker-compose, or Procfile present. Standard bench deployment assumed.

### 3.2 Dependencies

- **Required apps**: `[]` — Explicitly empty. ERPNext is a runtime dependency (accounting module imports `erpnext.accounts.general_ledger`) but not declared in `required_apps`.
- **Optional integrations**: `frappe_whatsapp` (checked at runtime via `frappe.db.exists("DocType", "WhatsApp Message")`), CRM app (checked via `frappe.db.exists("DocType", "CRM Lead")`)
- **Python packages**: `qrcode[pil]` (optional, for QR generation), `requests` (for API calls)

### 3.3 Workers & Scheduler

| Job | Schedule | Function | Risk |
|---|---|---|---|
| `publish_scheduled_posts` | `all` (every ~60s) | Queries all due Social Posts, publishes sequentially | **Medium** — blocking API calls per post; large backlogs stall the scheduler worker |
| `sync_all_connectors` | `hourly` | Iterates connectors, makes HTTP requests with retry+backoff | **Medium** — `time.sleep()` inside the scheduler worker blocks it; should use `frappe.enqueue` |

**Production concern**: `sync_all_connectors` uses `time.sleep()` for retry backoff (up to 120s for rate limits) inside the scheduler worker. This blocks the short-queue worker and can delay other scheduled tasks. Should be refactored to enqueue each connector sync individually.

---

## 4. DOCTYPE DEEP ANALYSIS

### 4.1 Marketing Campaign (Core Entity)

- **Purpose**: Central entity representing a marketing campaign. Links to channels, activities, content, expenses, and analytics.
- **Fields**: 14 — `campaign_name` (autoname), `description`, `status`, `budget`, `start_date`, `end_date`, `company`, `customer`, `project`, `is_omni_campaign`, `channels` (child table), `total_actual_cost`
- **Naming**: `field:campaign_name` (user-defined, must be unique)
- **Controller**: Minimal — only `validate_dates()` (end > start)
- **Permissions**: System Manager (full), Marketing Manager (RWCE), Marketing User (RWC)
- **Hook-driven permission**: Custom `permission_query_conditions` and `has_permission` in `utils/permissions.py`
- **Relationships**: Parent of Campaign Activity, Campaign Content; linked from Marketing Expense, Omni Blast, Analytics Daily Log, Social Post, Tracking Link
- **Risk**: No `validate` on budget (can be 0/negative). No status transition enforcement in controller (status can be set to anything via API).

### 4.2 Social Post (Publishing Entity)

- **Purpose**: Represents a single post to a single social media platform.
- **Fields**: 31 — content, platform (Link→Social Media Network), post_type, status, scheduled_time, engagement metrics (impressions, reach, clicks, likes, comments_count, shares, engagement_rate), media fields, hashtags, mentions, target_audience, omni_blast reference
- **Naming**: `format:POST-{####}`
- **Controller** (`social_post.py`):
  - `validate`: content length check (against network specs), scheduled time future check, engagement rate calc, approval permission check
  - `before_insert`: sets default status = "Draft"
  - `on_update`: sets `published_time` when status transitions to Published
- **Status lifecycle**: Draft → Scheduled → Publishing → Published / Failed / Deleted
- **Risk**: Status transitions aren't enforced at the model level. Any user with write access can set `status = "Published"` directly without going through the publishing pipeline. The `validate_approval_permissions` check only fires on save, not on specific transitions.

### 4.3 Omni Blast (Submittable — Multi-Channel Orchestrator)

- **Purpose**: Submit a single piece of content to multiple social networks simultaneously.
- **Fields**: 16 — blast_title, content, campaign (Link), networks (Table MultiSelect → Social Media Network), blast_type, scheduled_time, media fields, hashtags, mentions, target_audience, status, created_posts (text list of generated post names)
- **Naming**: `format:BLAST-{####}`
- **Submittable**: Yes — `on_submit` generates individual Social Post documents per network
- **Controller** (`omni_blast.py`):
  - `validate`: requires networks, requires scheduled_time for scheduled blasts
  - `on_submit → generate_posts()`: iterates networks, checks channel permissions from settings, adapts content (e.g., SMS truncation to 160 chars, OOH prefix), creates Social Post per network
  - `execute_blast()`: publishes all generated posts; >5 posts runs in background via `frappe.enqueue`
- **Relationships**: Creates 1:N Social Posts, links to Campaign
- **Risk**: `created_posts` stored as newline-separated text (not a child table Link). If posts are deleted manually, this list becomes stale. No reconciliation logic.

### 4.4 Marketing Expense (Submittable — Financial Entity)

- **Purpose**: Track marketing costs with proper GL entry posting to ERPNext accounts.
- **Fields**: 18 — expense_category, campaign, company, amount, currency, posting_date, expense_account, payment_account, cost_center, project, is_paid, gl_entry_posted, naming_series
- **Naming**: `naming_series:` (user-configurable)
- **Submittable**: Yes
- **Controller** (`marketing_expense.py`):
  - `validate`: sets defaults (expense account from category, cost center from company, currency)
  - `before_submit`: `check_budget_exceeded` — warning only, does NOT block submission
  - `on_submit`: Creates GL entries (debit expense account, credit payment/payable account), updates campaign `total_actual_cost`
  - `on_cancel`: Reverses GL entries, recalculates campaign cost
- **ERPNext integration**: Calls `erpnext.accounts.general_ledger.make_gl_entries` directly. Validates account company, account type, group status.
- **Risk**: Budget check is advisory (msgprint, not throw). An over-budget expense is submitted and posted to GL without blocking. This is a design choice but should be configurable.

### 4.5 Marketing Hub Settings (Single — Global Config)

- **Purpose**: System-wide configuration — agency mode, channel enable/disable, company defaults, post approval settings.
- **Fields**: 39 data fields — agency_mode, enable_sms_blast, enable_whatsapp_blast, enable_email_blast, require_post_approval, max_campaigns_per_client, session_timeout_days, auto_post_interval_minutes, company_settings (child table)
- **Single**: Yes (one instance per site)
- **Controller**: Validates session timeout (1-365 days), auto-post interval (5-1440 min), agency settings, company settings (no duplicate companies, account-company matching)
- **Permissions**: System Manager (full), Marketing Manager (read+write only)

### 4.6 Social Media Network (Platform Config)

- **Purpose**: Configuration-driven platform definitions. The adapter pattern reads API endpoints, auth settings, content specs from this DocType.
- **Fields**: 33 — network_name, network_type (Social Media/Email/SMS/Messaging/Out of Home), api_base_url, publish_endpoint, delete_endpoint, analytics_endpoint, auth_type, api_version, request_content_field, response_id_field, response_url_template, max_text_length, max_hashtags, max_media_count, supports_html, custom_adapter_class, network_code, is_active
- **Naming**: `field:network_name`
- **Seeded via patch**: `seed_social_media_networks.py` creates Facebook, Instagram, LinkedIn, Twitter/X, WhatsApp, Email, SMS, Google Ads, Pinterest, TikTok, YouTube, Snapchat, Reddit, Billboards, Radio, TV, Print, Transit
- **Risk**: `custom_adapter_class` allows arbitrary Python class loading via `importlib.import_module()`. This is powerful but dangerous if a non-admin can modify this field. Currently restricted to System Manager permissions.

### 4.7 Analytics Connector

- **Purpose**: Configures sync connection to ad platforms; fetches analytics data on schedule.
- **Fields**: 14 — platform, ad_account (Link), sync_frequency, sync_status, next_sync_date, last_sync_date, consecutive_failures, total_syncs, failed_syncs, last_error
- **Controller** (497 lines — largest controller):
  - `sync_analytics()`: Retry with exponential backoff (max 3), rate-limit handling (Retry-After), auto-pause after 5 consecutive failures
  - `sync_network_ads()`: Dispatches to `_sync_{platform}_ads()` methods via dynamic method name construction
  - `create_analytics_logs()`: Creates Analytics Daily Log entries from fetched data
  - Platform-specific methods: `_sync_meta_ads`, `_sync_google_ads`, `_sync_linkedin_ads`, `_sync_twitter_ads`
- **Risk**: Uses `time.sleep()` for retry delays — blocks the worker thread. Dynamic method dispatch via `hasattr/getattr` on scrubbed platform name.

### 4.8 Analytics Daily Log

- **Purpose**: Daily KPI storage per campaign per connector — impressions, clicks, spend, revenue, conversions, CTR, CPC, CPM, CPA, ROAS.
- **Fields**: 24 KPI fields + metadata
- **Naming**: `format:LOG-{connector}-{YYYY}-{MM}-{DD}-{###}`
- **No controller logic**: Pure data storage
- **Used by**: Dashboard API, ROAS Analysis report, campaign metrics enrichment

### 4.9 Tracking Link & Tracking Link Click

- **Tracking Link**: URL shortener with UTM parameter appending, QR code generation
  - Fields: 16 — link_name, destination_url, short_code, campaign, UTM fields, total_clicks, unique_clicks, qr_code, status
  - `before_insert`: Auto-generates SHA-256 short code (8 chars), ensures uniqueness
  - `record_click()`: Increments total_clicks, checks unique by IP
  - `get_destination_with_utm()`: Appends UTM params to destination URL
- **Tracking Link Click**: Click log (5 fields — tracking_link, ip_address, clicked_at, user_agent, referrer)
  - Autoname: hash
  - No controller logic

### 4.10 Content Asset

- **Purpose**: Media library for campaign assets (images, videos, documents).
- **Fields**: 15 — asset_name, asset_type, channel, file_attachment, thumbnail, file_size, dimensions, usage_count, tags, status
- **Controller**: `before_save` calculates file size from attached File doc; `increment_usage()` tracks usage count

### 4.11 Marketing Segment

- **Purpose**: Audience segmentation with JSON filter definitions. Queries Lead/Customer/Contact based on filters.
- **Fields**: 11 — segment_name, segment_type (Lead/Customer/Contact/Custom), filters_json, segment_size, status, auto_refresh
- **Controller**: Validates JSON format, calculates segment size by running `frappe.db.count()` with user-defined filters
- **Risk**: `filters_json` is passed directly to `frappe.get_all(..., filters=filters)` and `frappe.db.count(base_doctype, filters=filters)`. While Frappe's ORM does parameterize these, the user-controlled `base_doctype` (from `segment_type`) is passed directly as a doctype name. An attacker with write access to Marketing Segment could set `segment_type` to a sensitive DocType and enumerate records.

### 4.12 Remaining DocTypes (Summary)

| DocType | Purpose | Fields | Notes |
|---|---|---|---|
| Ad Account | OAuth credentials for ad platforms | 16 | Stores access_token, refresh_token |
| Agency Package | Subscription tier definition | 12 | campaign_limit, monthly_fee, included_channels |
| Attribution Model | Lead attribution calculation methods | 7 | Seeded: First Touch, Last Touch, Linear, etc. |
| Blast Type | Scheduling types for blasts | 8 | Seeded: Immediate, Scheduled, Recurring |
| Campaign Activity | Individual activities within campaigns | 20 | Links to campaign, segment; status-driven execution |
| Campaign Content | Per-channel content for campaigns | 18 | Template + custom overrides per channel |
| Client Subscription | Agency client billing records | 9 | Links Agency Package ↔ Client |
| Marketing Expense Category | Expense classification | 6 | Links to default accounting account |
| Marketing Ledger Entry | Marketing-specific ledger | 9 | Empty controller — appears unused |
| Marketing Template | Reusable content templates | 18 | Per-channel templates with asset items |
| Media Type | Media classification | 8 | Seeded: Image, Video, Document, etc. |
| Post Type | Social post classification | 6 | Seeded: Text, Image, Video, Carousel, Story, Reel |

---

## 5. HOOKS ANALYSIS

### 5.1 Complete Hook Map

```python
# === DOCUMENT EVENTS ===
doc_events = {
    "Lead": {
        "before_insert": "marketing_hub.utils.attribution_engine.get_real_lead_source"
        # Fires on EVERY Lead creation across the entire site
        # Reads UTM params from frappe.form_dict + doc fields
        # Sets doc.lead_source, doc.utm_campaign
        # Enqueues CRM sync if CRM app installed
    },
    "Campaign Activity": {
        "on_update": "marketing_hub.utils.omni_blast.execute_if_scheduled"
        # Auto-executes blast when activity status = "Scheduled" and time has passed
        # Silent try/except — failures are only logged, not raised
    }
}

# === SCHEDULER EVENTS ===
scheduler_events = {
    "all": ["marketing_hub.utils.auto_post.publish_scheduled_posts"],
    # Runs every ~60 seconds. Queries Social Posts where status in
    # (Draft, Scheduled) and scheduled_time <= now. Publishes each sequentially.
    # Risk: makes blocking HTTP API calls inside the scheduler worker.

    "hourly": ["marketing_hub.utils.analytics_sync.sync_all_connectors"],
    # Iterates all active connectors where next_sync_date <= now.
    # Makes HTTP requests with retry+backoff (time.sleep inside worker).
    # Per-connector: commit on success, rollback on failure.
}

# === PERMISSIONS ===
permission_query_conditions = {
    "Marketing Campaign": "...get_campaign_permission_query_conditions",
    "Campaign Activity": "...get_campaign_activity_permission_query_conditions",
    "Marketing Segment": "...get_marketing_segment_permission_query_conditions",
}
# Applies SQL WHERE clauses to list views. System/Marketing/Sales Managers see all.
# Others see only owned records or those with User Permission entries.

has_permission = {
    "Marketing Campaign": "...has_campaign_permission",
    "Campaign Activity": "...has_campaign_activity_permission",
}
# Document-level permission checks. Campaign Activity delegates to parent Campaign.

# === POST-MIGRATE ===
after_migrate = [
    "marketing_hub.install.setup_file_folder",     # Creates "Marketing Hub" folder
    "marketing_hub.install.setup_notifications",   # Creates 2 Notification documents
]

# === FIXTURES ===
fixtures = [
    {"dt": "Custom Field", "filters": [["name", "in", [
        "Lead-utm_campaign", "Lead-utm_source", "Lead-utm_medium"
    ]]]},
    {"dt": "Workspace", ...},           # 4 workspaces
    {"dt": "Social Media Network", ...}, # All active networks
    {"dt": "Attribution Model"},         # All attribution models
]

# === WEBSITE ROUTES ===
website_route_rules = [
    {"from_route": "/marketing/<path:app_path>", "to_route": "marketing"},
    {"from_route": "/marketing_hub/<path:app_path>", "to_route": "marketing_hub"},
    {"from_route": "/t/<short_code>", "to_route": "tracking_redirect"},
]
```

### 5.2 Hidden Side Effects

1. **Lead `before_insert` hook**: Fires on EVERY Lead creation, not just marketing-sourced ones. If `utm_campaign` or `campaign_name` exists, it overwrites `doc.lead_source` with a formatted string. This means any other app that sets `lead_source` before this hook runs will have its value silently overwritten.

2. **Campaign Activity `on_update` hook**: When a Campaign Activity is saved with `status = "Scheduled"` and `scheduled_time <= now`, it immediately tries to execute the blast. This is a side-effect on save — users might not expect saving to trigger publishing.

3. **`after_migrate`**: `setup_notifications` creates Notification documents with `ignore_permissions=True`. If these notifications already exist (by name), they're skipped. But if someone renames them, duplicates will be created on next migrate.

---

## 6. CLIENT SCRIPT + SERVER SCRIPT ANALYSIS

### 6.1 Frontend Architecture

The app uses a **standalone Vue 3 SPA** (not Frappe desk pages). All business logic is server-side, called via `frappe.call()` through the `api/` layer. There are no Frappe Client Scripts or Server Scripts used.

**Frontend structure**:
- 16 page components in `frontend/src/pages/`
- 10 shared components in `frontend/src/components/`
- 2 layout components (AdminLayout, AgentLayout)
- 2 Pinia stores (config, user)
- Router with 18 routes under `/marketing/*`

**Key observations**:
- No client-side validation that doesn't exist server-side (good)
- Frontend calls map 1:1 to `api/` whitelisted methods
- Frappe UI components used for forms, dialogs, toasts
- No direct `frappe.db` calls from frontend (good)

### 6.2 Performance Concerns

- **Content.vue** (814 lines): Largest page, handles asset library with filtering. Uses standard `frappe.call()` — no infinite scroll or virtualization.
- **Dashboard.vue** (542 lines): Makes single `get_dashboard_data` call that runs ~10 SQL queries server-side. Reasonable.
- **No WebSocket usage** for real-time updates (publishing status, analytics sync progress).

---

## 7. API & WHITELISTED METHOD AUDIT

### 7.1 Summary Statistics

- **103 total `@frappe.whitelist()` methods** across all files
- **2 `allow_guest=True` endpoints**: `handle_redirect` (tracking), `oauth_callback`
- **0 rate-limiting** on any endpoint

### 7.2 Guest-Accessible Endpoints (Critical)

**`handle_redirect(short_code)`** — `api/tracking.py:141`
- Purpose: Tracking link click redirect
- Input: `short_code` from URL path
- Safety: ✅ Parameterized query lookup. IP anonymized before storage. No PII exposed.
- Risk: No rate limiting. An attacker could inflate click counts by scripting rapid requests.

**`oauth_callback(code, state)`** — `utils/oauth_integration.py:218`
- Purpose: OAuth2 authorization code exchange
- Input: `code` (auth code from platform), `state` (CSRF token)
- Safety: ✅ State verified against Redis cache (600s expiry). Token exchange happens server-side.
- Risk: **The callback creates an Ad Account with `ignore_permissions=True` and stores access/refresh tokens.** If the OAuth state can be predicted or the cache is shared across sites, a guest could inject tokens. However, state is a `frappe.generate_hash(length=20)` — 20 hex chars = 80 bits of entropy, which is sufficient.

### 7.3 SQL Safety Audit

**Fixed in PR #1**: `content.py` `order_by` parameter was directly interpolated. Now validated via regex allowlist.

**Remaining safe patterns**:
- All `frappe.db.sql()` calls (78 total non-test) use `%(param)s` parameterization or `%s` positional parameters
- No string formatting of user input into SQL WHERE clauses
- `accounting.py:get_marketing_expense_summary()` builds WHERE clause from filter dict, but uses `%s` positional params

**One concern**: `permissions.py` constructs SQL WHERE clauses with f-strings using `frappe.db.escape(user)`:
```python
f"`tabMarketing Campaign`.owner = '{frappe.db.escape(user)}'"
```
While `frappe.db.escape` does prevent injection, this pattern is fragile — if someone removes the escape call during refactoring, it becomes a vulnerability. Frappe's recommended approach is `%(user)s` parameterization.

### 7.4 Authorization Gaps

Most API methods rely on Frappe's implicit permission checking (`frappe.get_doc` throws if no read permission). However:

- **`get_campaign_list`**: Calls `frappe.get_all` which applies `permission_query_conditions`. ✅
- **`refresh_segment`**: Calls `frappe.get_doc` then `save(ignore_permissions=True)`. The initial `get_doc` checks read permission, but the `ignore_permissions` save means any user with read access can trigger a segment recalculation. Minor risk.
- **`schedule_post`**: Calls `doc.save(ignore_permissions=True)`. Any user who can call this whitelist method can schedule any post regardless of ownership. The method doesn't verify write permission.
- **`update_metrics`**: Same pattern — `doc.save(ignore_permissions=True)`. Any authenticated user can update engagement metrics on any post.

---

## 8. DATABASE & DATA MODEL ANALYSIS

### 8.1 Entity Relationship Map

```
Marketing Campaign (1) ──► (N) Campaign Activity
Marketing Campaign (1) ──► (N) Campaign Content
Marketing Campaign (1) ──► (N) Marketing Expense
Marketing Campaign (1) ──► (N) Analytics Daily Log (via campaign field)
Marketing Campaign (1) ──► (N) Social Post (via campaign field)
Marketing Campaign (1) ──► (N) Tracking Link (via campaign field)

Social Media Network (1) ──► (N) Social Post (via platform)
Social Media Network (1) ──► (N) Ad Account (via social_media_network)
Social Media Network (1) ──► (N) Analytics Connector (via platform)
Social Media Network (1) ──► (N) Omni Blast networks (Table MultiSelect)

Omni Blast (1) ──► (N) Social Post (via omni_blast field, stored as text list)

Analytics Connector (1) ──► (N) Analytics Daily Log (via connector field)
Analytics Connector ──► Ad Account (Link)

Marketing Segment ──► Campaign Activity (via segment field)

Tracking Link (1) ──► (N) Tracking Link Click

Marketing Expense ──► Marketing Expense Category ──► Account
Marketing Expense ──► Company ──► Cost Center

Agency Package (1) ──► (N) Client Subscription ──► Client (Customer)
```

### 8.2 N+1 Query Problems

**Critical — `get_campaign_list`** (`api/campaigns.py:42-75`):
```python
campaigns = frappe.get_all("Marketing Campaign", ...)
for campaign in campaigns:
    metrics = frappe.db.sql("SELECT SUM(spend)... FROM Analytics Daily Log WHERE campaign = %s")
    campaign["leads_count"] = frappe.db.count("Lead", {"campaign_name": campaign.campaign_name})
```
For 20 campaigns (default limit): 1 list query + 20 analytics queries + 20 lead count queries = **41 queries**. Should use a single JOIN or subquery.

**Critical — `get_dashboard_data`** (`api/dashboard.py`):
Runs ~10 separate SQL queries for a single dashboard load. Some could be combined.

**Medium — `get_campaign_assigned_users`** (`utils/permissions.py:278`):
```python
for assignment in assigned_users:
    user_doc = frappe.get_cached_doc("User", assignment.user)
```
N+1 but mitigated by `get_cached_doc`.

### 8.3 Missing Indexes

- `Analytics Daily Log`: No explicit index on `log_date` + `campaign` (the combination used in most dashboard queries). The patch `add_analytics_daily_log_unique_index.py` exists but would need to verify what it adds.
- `Tracking Link Click`: Queried by `tracking_link` + `ip_address` for deduplication — no composite index defined.
- `Social Post`: Queried by `status` + `scheduled_time` every minute by scheduler — no composite index.

---

## 9. ERPNext OVERRIDE ANALYSIS

### 9.1 What's Overridden

The app does **NOT** override any ERPNext DocType classes, controllers, forms, or reports. This is clean.

### 9.2 What's Extended

| Extension | Type | Risk |
|---|---|---|
| `Lead` — 3 Custom Fields (utm_campaign, utm_source, utm_medium) | Fixture | ✅ Low — adds fields, doesn't modify existing ones |
| `Lead.before_insert` hook — attribution engine | doc_event | ⚠️ Medium — silently overwrites `lead_source` on every Lead |
| GL Entry creation via `erpnext.accounts.general_ledger.make_gl_entries` | Direct import | ⚠️ Medium — coupled to ERPNext's internal API |
| `Company.cost_center`, `Company.default_currency`, etc. | Read-only lookups | ✅ Low |
| `Account` validation (company, type, group) | Read-only lookups | ✅ Low |
| `Cost Center` validation | Read-only lookups | ✅ Low |

### 9.3 Upgrade Risks

1. **`erpnext.accounts.general_ledger.make_gl_entries`**: This is an internal ERPNext function. If its signature changes in ERPNext v15 point releases, `marketing_expense.on_submit` will break. Recommend using `doc.get_gl_dict()` (which the code does correctly) and watching ERPNext release notes.

2. **Lead Custom Fields**: Safe — Custom Fields are the standard Frappe extension mechanism. Won't break on ERPNext upgrades.

3. **No `override_doctype_class`**: The app doesn't monkey-patch any ERPNext class. Clean.

---

## 10. SECURITY AUDIT

### 10.1 Permissions Summary

| DocType | System Manager | Marketing Manager | Marketing User | Sales Manager |
|---|---|---|---|---|
| Marketing Campaign | Full + Delete | RWC | RWC | Full (via hook) |
| Marketing Expense | Full + Submit | RWC + Submit | Read only | — |
| Social Post | Full + Delete | Full + Delete | RWC | — |
| Omni Blast | Full | Full + Submit | RWC + Submit | — |
| Marketing Hub Settings | Full | Read + Write | — | — |
| Tracking Link | Full | — | — | — |

**Missing permissions**: Tracking Link has only System Manager permission. Marketing Manager/User cannot create or view tracking links via desk forms (but CAN via the API if they can call the whitelist method).

### 10.2 `ignore_permissions=True` Usage

Found in 14 non-test, non-patch files:

| Location | Pattern | Risk |
|---|---|---|
| `tracking.py:177,187` | `doc.save(ignore_permissions=True)` + click insert | ✅ Expected — guest redirect handler |
| `social_adapter.py:49,126,158` | `post.save(ignore_permissions=True)` | ⚠️ Medium — bypasses permission on status change |
| `social_post.py:104,127,157` | `doc.save(ignore_permissions=True)` | ⚠️ Medium — `update_metrics` callable by any user |
| `content_asset.py:29` | `self.save(ignore_permissions=True)` | Low — internal method |
| `marketing_segment.py:76` | `save(ignore_permissions=True)` | Low — refresh method |
| `crm_integration.py:42,46,110` | `insert/save(ignore_permissions=True)` | ⚠️ Medium — CRM lead creation bypasses CRM permissions |
| `permissions.py:221,252` | User Permission insert/delete | Expected — permission management |
| `oauth_integration.py:112,267` | Token save, Ad Account creation | ⚠️ — Ad Account created via guest callback |
| `install.py:13,66` | Setup operations | Expected |

### 10.3 Dangerous Patterns

1. **Dynamic class loading** (`social_adapter.py:80-84`):
   ```python
   module_path, class_name = network_doc.custom_adapter_class.rsplit('.', 1)
   module = importlib.import_module(module_path)
   adapter_class = getattr(module, class_name)
   ```
   If `custom_adapter_class` can be set by a non-System Manager, this is arbitrary code execution. Currently safe because Social Media Network requires System Manager to edit.

2. **`frappe.form_dict` access in hook** (`attribution_engine.py:22-24`):
   ```python
   utm_campaign = frappe.form_dict.get("utm_campaign") or doc.get("utm_campaign")
   ```
   Reads UTM params from the HTTP request's form data during Lead insertion. This means the attribution engine's behavior depends on how the Lead was created (web form vs API vs desk). The `frappe.form_dict` may contain stale data from a different request in async contexts.

3. **No GDPR/data protection configuration**: `user_data_fields` in hooks.py is commented out. Tracking Link Click stores anonymized IPs (good) but no mechanism to delete click data on user request.

### 10.4 Multi-Tenant Considerations

- Company filtering is consistent but optional. If `company` param is not passed to API methods, data from all companies is returned to any user with the right role.
- Permission query conditions correctly scope campaigns/activities to user, but Marketing Segment and other DocTypes use simpler owner-based or role-based filtering.

---

## 11. PERFORMANCE & SCALE REVIEW

### 11.1 Scheduler Worker Blocking

**Critical**: `analytics_sync.sync_all_connectors()` runs in the scheduler worker and calls `time.sleep()` for retry backoff. Each connector sync can block for up to 2+ minutes (120s rate-limit sleep + request time). With 10+ connectors, this can block the `short` queue for 20+ minutes, delaying all other scheduled tasks including `publish_scheduled_posts`.

**Fix**: Each connector sync should be enqueued as a separate background job via `frappe.enqueue`.

### 11.2 N+1 Query Performance

`get_campaign_list` with 20 campaigns = 41 queries. At 100 campaigns this becomes 201 queries per page load. The dashboard API runs ~10 queries per load but they're mostly aggregate queries with good performance characteristics.

### 11.3 Frontend Performance

- **JS bundle**: Vue 3 SPA with code-splitting (lazy-loaded routes). Build output goes to `public/frontend/`. Reasonable size for an internal tool.
- **No pagination controls**: Most list views default to `limit=20` or `limit=50` but don't expose offset/pagination to the user.
- **No caching**: Dashboard data is fetched fresh on every load. High-traffic deployments should consider caching aggregate metrics in Redis.

### 11.4 Database Hotspots

- `Tracking Link Click`: Append-only table. Could grow very large for high-traffic tracking links. No TTL or archival mechanism.
- `Analytics Daily Log`: One row per connector per day. Moderate growth (365 × connectors per year).
- `Social Post`: Engagement metrics updated via `ignore_permissions` — could see write contention if analytics sync and manual updates overlap.

---

## 12. REPORTS, PRINTS & WEB FORMS

### 12.1 ROAS Analysis (Script Report)

- **Location**: `marketing_hub/report/roas_analysis/roas_analysis.py` (365 lines)
- **Features**: Groups by Campaign, Channel, or Month. Calculates spend, revenue, ROAS, ROI, CPA, CTR, CPM. Includes chart data.
- **Data source**: Joins `Analytics Daily Log` with `Marketing Campaign`
- **Security**: Uses `frappe.db.sql` with parameterized queries. ✅
- **Performance**: Single aggregate query with GROUP BY — efficient.

### 12.2 Web Forms & Portal Pages

- No Web Forms defined
- No Portal Pages
- The `/marketing/*` route serves the Vue SPA via `www/marketing/index.py`
- The `/t/<short_code>` route handles tracking redirects via `www/tracking_redirect.py`

### 12.3 Print Formats

- No custom Print Formats defined
- Marketing Expense could benefit from a print format for expense reports/receipts

---

## 13. CODE QUALITY & MAINTAINABILITY

### 13.1 Strengths

1. **Clean separation of concerns**: API layer, business logic (utils), data models (doctypes) are properly separated
2. **Adapter pattern**: Social media publishing uses a well-designed adapter pattern with abstract base class, generic configuration-driven adapter, and platform-specific overrides
3. **Proper ERPNext integration**: Uses `doc.get_gl_dict()` for GL entries, Custom Fields for Lead extension, hooks for attribution — all standard Frappe patterns
4. **Consistent error handling**: Most operations use try/except with `frappe.log_error()` for logging and graceful fallbacks
5. **Multi-company support**: Per-company settings via child table, company parameter on most APIs

### 13.2 Issues

1. **Dead code**: `Marketing Ledger Entry` DocType has an empty controller and appears unused — no references in any Python file
2. **Inconsistent status management**: Social Post status can be set to any value via API without transition validation
3. **Test coverage gap**: 8 test files for ~13K lines Python. API layer (the largest surface area) has zero test coverage
4. **`setup_workspace_visibility`** in `permissions.py:164-186`: Contains a comment "this won't work as expected" and falls through to a debug log. Dead code that should be removed.
5. **Duplicate `publish_post`**: Even after consolidation in PR #1, there are still 3 `publish_post` functions: `social_post.py:88`, `auto_post.py:33`, `social_adapter.py:171`. The social_adapter version now delegates to auto_post, but social_post.py has its own independent implementation.
6. **`content_orchestration.py` uses `frappe.msgprint` in server-side utility functions**: msgprint during batch operations will accumulate messages. Not appropriate for background jobs.

### 13.3 Naming Inconsistencies

- Module directory is `marketing_hub/marketing_hub/` (standard Frappe, but confusing)
- Some files use copyright "I-Varse Technologies", others "Puxxo", others "Frappe Technologies Pvt. Ltd.", others "Your Name"
- Mixed naming conventions: `_get_company()` (private) imported as `_get_company` in API files, but the utility function is public (`get_company`)

### 13.4 Maintainability Score: **6.5/10**

Good architectural decisions (adapter pattern, API layer separation, ERPNext integration approach) offset by thin test coverage, dead code, and permission inconsistencies.

---

## 14. FUNCTIONAL TRACE MAPPING

### 14.1 Omni Blast → Social Post Publishing (Critical Path)

```
1. User creates Omni Blast document (Vue SPA → api/ is not involved for DocType CRUD)
   └─ OmniBlast.validate() → checks networks exist, scheduled_time set

2. User submits Omni Blast (Frappe desk submit action)
   └─ OmniBlast.on_submit()
      └─ self.generate_posts()
         ├─ For each network in self.networks:
         │   ├─ frappe.get_doc("Social Media Network", network_name)
         │   ├─ frappe.get_single("Marketing Hub Settings") ← called N times (N+1)
         │   ├─ Check enable_sms_blast / enable_whatsapp_blast / enable_email_blast
         │   ├─ Adapt content (SMS: truncate 160, OOH: prefix)
         │   ├─ frappe.get_doc({...}).insert() → creates Social Post (status=Draft)
         │   └─ Append name to created_post_links
         └─ self.created_posts = "\n".join(created_post_links)

3. User calls execute_blast() (or it fires automatically via scheduler)
   └─ OmniBlast.execute_blast()
      ├─ If >5 posts: frappe.enqueue(_execute_blast_posts, queue="default")
      └─ _execute_blast_posts(blast_name, post_list)
         └─ For each post_name:
            ├─ frappe.get_doc("Social Post", post_name)
            └─ publish_to_platform(post)
               ├─ frappe.get_doc("Social Media Network", post.platform)
               ├─ get_platform_adapter(network) → GenericAdapter or custom
               ├─ adapter.publish(post)
               │   ├─ adapter.get_ad_account(post.company)
               │   ├─ adapter.check_token_expiry() → may refresh via OAuth
               │   ├─ HTTP POST to platform API endpoint
               │   └─ return {success, platform_post_id, url}
               ├─ post.status = "Published" (or "Failed")
               ├─ post.save(ignore_permissions=True)
               └─ frappe.db.commit()

4. Side effects:
   ├─ SocialPost.on_update() → sets published_time
   └─ If all posts done: blast.status = "Published"
```

### 14.2 Tracking Link Click (Guest Path)

```
1. User scans QR / clicks tracking URL → GET /t/<short_code>
   └─ website_route_rules → www/tracking_redirect.py
      └─ tracking_redirect.get_context()
         └─ handle_redirect(short_code)   [allow_guest=True]

2. handle_redirect():
   ├─ frappe.db.get_value("Tracking Link", {short_code, status: Active})
   ├─ Extract IP → _anonymize_ip(raw_ip) → zero last octet
   ├─ Extract User-Agent, Referer (truncated to 500 chars)
   ├─ doc.total_clicks += 1
   ├─ Check unique: frappe.db.exists("Tracking Link Click", {link, ip})
   │   └─ If new IP: doc.unique_clicks += 1
   ├─ doc.save(ignore_permissions=True)
   ├─ Insert Tracking Link Click (ignore_permissions=True)
   ├─ frappe.db.commit()
   └─ Redirect to destination URL with UTM params appended

3. No side effects beyond click recording and redirect.
```

### 14.3 Marketing Expense GL Posting

```
1. User creates Marketing Expense document
   └─ MarketingExpense.validate()
      ├─ set_defaults() → expense_account from category, cost_center from company
      ├─ set_currency() → from company default
      └─ validate_accounting_entries() → validates account company, type, group

2. User submits
   └─ MarketingExpense.before_submit()
      └─ check_budget_exceeded() → msgprint warning (does NOT block)
   └─ MarketingExpense.on_submit()
      ├─ self.make_gl_entries()
      │   └─ accounting.make_gl_entries(self)
      │      ├─ Debit: expense_account (amount)
      │      ├─ Credit: payment_account (if is_paid) or payable_account
      │      ├─ Both entries: cost_center, project, posting_date
      │      └─ erpnext.accounts.general_ledger.make_gl_entries(gl_entries)
      └─ update_campaign_spent_amount(self)
         └─ UPDATE Marketing Campaign SET total_actual_cost = SUM(expenses)
```

---

## 15. HIDDEN INSIGHTS

### 15.1 Undocumented Behavior

1. **Lead attribution hook fires on all Leads**: The `before_insert` hook on `Lead` runs for every Lead created in the system, even those completely unrelated to marketing. If `campaign_name` is set (e.g., from a standard CRM Campaign), the hook will attempt to look up a Marketing Campaign with that name and overwrite `lead_source`. This coupling means installing Marketing Hub changes Lead behavior globally.

2. **Omni Blast `on_submit` immediately calls `generate_posts`**: The submit action creates N Social Posts synchronously. For a blast to 18 networks, this means 18 `frappe.get_doc` + 18 `insert` calls during the submit transaction. If any network check fails (e.g., SMS disabled), `frappe.throw` rolls back the entire submit including already-created posts.

3. **`execute_if_scheduled` on Campaign Activity `on_update`**: Any save of a Campaign Activity with status "Scheduled" and a past scheduled_time will trigger blast execution. This includes administrative edits, bulk updates, and migrate-triggered saves.

4. **OAuth callback guest endpoint creates Ad Accounts**: The `oauth_callback` creates an Ad Account with stored access/refresh tokens via `ignore_permissions=True`. The only protection is the Redis-cached state parameter (600s TTL). After the state expires, the Ad Account remains.

5. **`sync_all_connectors` is registered as `hourly` but the docstring says `all`**: The hooks.py registers it under `hourly`, but the docstring in analytics_sync.py says "Called by Frappe scheduler (hooks.py → scheduler_events → 'all')". The hooks.py is correct (hourly), but this documentation mismatch could cause confusion.

### 15.2 Dangerous Coupling

1. **Marketing Expense → ERPNext GL**: Direct import of `erpnext.accounts.general_ledger.make_gl_entries`. If ERPNext is not installed, the MarketingExpense class will fail to import entirely (import at module top level in marketing_expense.py).

2. **Marketing Hub Settings is a god object**: With 39+ fields and child tables, it controls: agency mode, channel permissions, post approval, company defaults, auto-post intervals, session timeouts. Every subsystem reads from this single doctype. Changes to settings have cascading effects across the entire app.

### 15.3 What Would Unexpectedly Break

1. **Removing a Social Media Network**: If a Social Media Network record is deleted while Social Posts reference it via `platform` Link field, Frappe will prevent deletion (link validation). But if `custom_adapter_class` is set, any related import will fail with `ModuleNotFoundError`.

2. **ERPNext upgrade changing `make_gl_entries` signature**: Would break Marketing Expense submission silently or with a cryptic error.

3. **Disabling agency mode while active subscriptions exist**: No cascade logic — Client Subscriptions remain in "Active" status but `check_client_subscription` returns `{"valid": True, "message": "Internal mode"}`, effectively ignoring all subscription limits.

4. **Deleting a Marketing Campaign**: Campaign Activity permission check does `frappe.get_doc("Marketing Campaign", doc.campaign)` — if campaign is deleted, this throws `DoesNotExistError` which is caught and returns `False` (access denied). Orphaned activities become inaccessible.

---

## 16. REVERSE ENGINEERING REVIEW

### 16.1 Keep (Good Architecture)

| Component | Reason |
|---|---|
| Adapter pattern for social media | Extensible, config-driven, supports custom classes. Gold standard for multi-platform integration. |
| API layer separation (`api/`) | Clean SPA-backend contract. Easy to version or replace frontend. |
| ERPNext financial integration | GL entries, cost centers, Chart of Accounts setup — done correctly. |
| Permission system | Custom `permission_query_conditions` + `has_permission` — proper Frappe pattern. |
| Tracking link with QR generation | Clean URL shortening, UTM parameter appending, IP anonymization. |
| Per-company settings via child table | Proper multi-company support without hardcoding. |
| Analytics Connector retry logic | Exponential backoff, rate-limit handling, auto-pause after failures. |

### 16.2 Redesign

| Component | Issue | Better Approach |
|---|---|---|
| Omni Blast → Social Post relationship | Text list of names, no formal link | Use a child table or proper Link field with back-reference |
| Status management (Social Post, Campaign) | No transition enforcement | Implement a state machine or use Frappe Workflow |
| Scheduler worker blocking | `time.sleep()` in sync_all_connectors | Enqueue each connector sync as a separate background job |
| N+1 queries in campaign list | 41 queries per page load | Single SQL query with JOINs and subqueries |
| Budget enforcement | Advisory only (msgprint) | Add a hard-block option configurable in Settings |
| Lead attribution hook | Fires on every Lead, may overwrite source | Make it conditional — only fire when UTM params are present |
| `ignore_permissions=True` on Social Post ops | `update_metrics`, `schedule_post` bypass perms | Remove `ignore_permissions` and let Frappe handle authorization |

### 16.3 Eliminate

| Component | Reason |
|---|---|
| `Marketing Ledger Entry` DocType | Empty controller, no references in codebase. Dead DocType. |
| `setup_workspace_visibility` function | Contains "this won't work as expected" comment. Dead code. |
| `social_post.py:publish_post` (third copy) | Redundant with `auto_post.publish_post` and `social_adapter.publish_post` delegation |
| `get_agency_mode` fallback to "Marketing Hub Setup" | References a DocType that doesn't exist in the codebase. Dead fallback. |

---

## 17. FINAL VERDICT

### 17.1 System Maturity

**MVP+ (Late MVP / Early Production)**

The app has a solid architectural foundation (adapter pattern, proper ERPNext integration, clean API layer) but lacks the hardening required for production deployment: no status transition enforcement, thin test coverage, N+1 query patterns, scheduler worker blocking, and inconsistent permission enforcement.

### 17.2 Top 20 Critical Risks (by severity)

| # | Risk | Severity | Location |
|---|---|---|---|
| 1 | Scheduler worker blocking via `time.sleep()` in analytics sync | **High** | `analytics_sync.py:87,101` |
| 2 | N+1 queries in campaign list (41 queries/page) | **High** | `api/campaigns.py:42-75` |
| 3 | `ignore_permissions=True` on `update_metrics`, `schedule_post` | **High** | `social_post.py:127,157` |
| 4 | No status transition enforcement on Social Post/Campaign | **High** | `social_post.py` (no state machine) |
| 5 | ERPNext hard dependency not declared in `required_apps` | **High** | `hooks.py:12` (empty), `marketing_expense.py:9-15` |
| 6 | Lead `before_insert` hook fires globally, can overwrite `lead_source` | **High** | `attribution_engine.py:57` |
| 7 | Dynamic class loading from `custom_adapter_class` field | **Medium** | `social_adapter.py:80-84` |
| 8 | No rate limiting on any API endpoint | **Medium** | All 103 whitelisted methods |
| 9 | Tracking Link Click table has no TTL/archival | **Medium** | `tracking_link_click.json` |
| 10 | `frappe.form_dict` access in attribution hook (stale in async) | **Medium** | `attribution_engine.py:22-24` |
| 11 | Guest OAuth callback creates Ad Account with `ignore_permissions` | **Medium** | `oauth_integration.py:267` |
| 12 | Budget check is advisory only (msgprint, not throw) | **Medium** | `accounting.py:297-304` |
| 13 | `Marketing Hub Settings` fetched per-network in generate_posts (N+1) | **Medium** | `omni_blast.py:42` |
| 14 | No GDPR `user_data_fields` configuration | **Medium** | `hooks.py:274-293` (commented) |
| 15 | Permission query conditions use f-strings with `frappe.db.escape` | **Low** | `permissions.py:24-33` |
| 16 | `created_posts` stored as text (stale if posts deleted) | **Low** | `omni_blast.py:91` |
| 17 | Tracking Link has only System Manager permissions | **Low** | `tracking_link.json` |
| 18 | `execute_if_scheduled` fires on any Campaign Activity save | **Low** | `omni_blast.py:59-66` |
| 19 | Missing composite indexes on high-query-volume tables | **Low** | Analytics Daily Log, Social Post |
| 20 | Dead code: Marketing Ledger Entry, workspace visibility function | **Low** | Multiple locations |

### 17.3 Top 20 Improvements (by impact)

| # | Improvement | Impact | Effort |
|---|---|---|---|
| 1 | Enqueue each connector sync individually instead of synchronous loop | **Critical** | Low |
| 2 | Replace N+1 campaign metrics with single SQL JOIN | **High** | Medium |
| 3 | Add ERPNext to `required_apps` (or make GL integration conditional) | **High** | Low |
| 4 | Implement status state machine for Social Post | **High** | Medium |
| 5 | Remove `ignore_permissions=True` from `schedule_post`/`update_metrics` | **High** | Low |
| 6 | Add composite index on `(campaign, log_date)` for Analytics Daily Log | **High** | Low |
| 7 | Add composite index on `(status, scheduled_time)` for Social Post | **High** | Low |
| 8 | Make Lead attribution hook conditional (only when UTM params exist) | **High** | Low |
| 9 | Add API-layer test coverage (currently 0%) | **High** | High |
| 10 | Add rate limiting to tracking redirect endpoint | **Medium** | Low |
| 11 | Replace Omni Blast `created_posts` text field with child table | **Medium** | Medium |
| 12 | Add TTL/archival for Tracking Link Click records | **Medium** | Medium |
| 13 | Configure `user_data_fields` for GDPR compliance | **Medium** | Low |
| 14 | Add Tracking Link permissions for Marketing Manager/User roles | **Medium** | Low |
| 15 | Remove dead code (Marketing Ledger Entry, workspace visibility) | **Medium** | Low |
| 16 | Consolidate all 3 `publish_post` functions into one canonical implementation | **Medium** | Medium |
| 17 | Make budget enforcement configurable (warning vs. hard block) | **Medium** | Low |
| 18 | Cache Marketing Hub Settings reads (called repeatedly) | **Medium** | Low |
| 19 | Add WebSocket notifications for publishing/sync progress | **Low** | Medium |
| 20 | Add frontend pagination controls for list views | **Low** | Medium |

### 17.4 Production Readiness Score

## **52 / 100**

**Breakdown**:

| Category | Score | Max | Notes |
|---|---|---|---|
| Architecture & Design | 14 | 20 | Strong adapter pattern, clean separation. Loses points for god-object Settings, dead DocTypes. |
| ERPNext Integration | 8 | 10 | Correct GL entries, custom fields, hooks. Loses points for undeclared dependency. |
| Security | 7 | 15 | SQL injection fixed, IP anonymization added. Loses points for `ignore_permissions` abuse, no rate limiting, guest endpoint risks. |
| Data Model | 7 | 10 | Good relationships, proper naming. Loses points for text-list relationships, missing indexes. |
| Performance | 4 | 10 | N+1 queries, scheduler blocking, no caching. Major production risk. |
| Testing | 2 | 10 | 8 test files for 13K lines. Zero API layer coverage. |
| Code Quality | 6 | 10 | Clean code overall, but dead code, inconsistent naming, 3 publish_post copies. |
| Operations Readiness | 4 | 15 | No monitoring, no GDPR config, no TTL on click data, advisory-only budget checks. |

**Rationale**: The system demonstrates strong architectural vision and correct ERPNext integration patterns. It's well beyond prototype quality. However, the combination of scheduler worker blocking (operational risk), N+1 queries (performance risk), inconsistent permission enforcement (security risk), and thin test coverage (reliability risk) means it needs hardening before production deployment with real campaign budgets and external platform tokens.

**Recommended path**: Fix the top 8 improvements (mostly Low effort), add basic API tests, and it moves to 65-70 territory — viable for production with monitoring.
