# Marketing Hub - Comprehensive TODO List
**Generated**: January 24, 2026  
**Based On**: COMPREHENSIVE_ANALYSIS.md audit results

---

## Priority Legend
- 🔴 **CRITICAL** - Blockers, must fix for MVP
- 🟠 **HIGH** - Major issues, needed for production
- 🟡 **MEDIUM** - Important improvements, quality issues
- 🟢 **LOW** - Nice to have, technical debt cleanup

---

## Phase 1: MVP Fixes (Critical Path - 60 hours)

### 🔴 CRITICAL: Frontend-Backend API Connection (8 hours)

#### 1.1 Create Missing API Endpoints
**File**: `marketing_hub/www/marketing/api.py` (new file)

- [ ] Create `get_dashboard_data()` method
  - Return: active_campaigns, total_spend, leads_generated, roi, recent_activities
  - Query Analytics Daily Log for metrics
  - Calculate period-over-period changes
  
- [ ] Create `get_analytics_data(from_date, to_date)` method
  - Return: daily metrics array for charts
  - Group by date from Analytics Daily Log
  - Include: spend, revenue, impressions, clicks, conversions
  
- [ ] Create `get_campaign_list(filters, limit, offset)` method
  - Return: campaigns with calculated metrics
  - Include: status, budget_utilization, roas, leads_count
  - Apply role-based filtering
  
- [ ] Create `get_social_posts(filters, limit, offset)` method
  - Return: posts with engagement metrics
  - Include: platform, status, scheduled_time, performance
  - Group by status for filtering

- [ ] Register routes in `www/marketing/index.py`
  ```python
  @frappe.whitelist()
  def get_dashboard_data():
      from marketing_hub.www.marketing.api import get_dashboard_data as get_data
      return get_data()
  ```

**Estimated**: 8 hours  
**Blocks**: Dashboard.vue, Analytics.vue, Campaigns.vue, Social.vue

---

#### 1.2 Fix Frontend API Calls (4 hours)

- [ ] **Dashboard.vue** - Update createResource
  ```javascript
  const dashboard = createResource({
    url: 'marketing_hub.www.marketing.api.get_dashboard_data',
    auto: true
  })
  ```

- [ ] **Analytics.vue** - Update createResource with date params
  ```javascript
  const analyticsResource = createResource({
    url: 'marketing_hub.www.marketing.api.get_analytics_data',
    params: { from_date, to_date },
    auto: true
  })
  ```

- [ ] **Campaigns.vue** - Update to use custom endpoint
  ```javascript
  const campaignsResource = createResource({
    url: 'marketing_hub.www.marketing.api.get_campaign_list',
    params: { filters: {}, limit: 20 },
    auto: true
  })
  ```

- [ ] **Social.vue** - Update to use custom endpoint
  ```javascript
  const postsResource = createResource({
    url: 'marketing_hub.www.marketing.api.get_social_posts',
    params: { filters: {}, limit: 20 },
    auto: true
  })
  ```

- [ ] Add error states for all pages
  ```vue
  <div v-if="resource.error">
    <p>{{ resource.error }}</p>
  </div>
  ```

- [ ] Add loading spinners
  ```vue
  <div v-if="resource.loading">
    <LoadingIndicator />
  </div>
  ```

- [ ] Add empty states
  ```vue
  <div v-if="!resource.loading && !resource.data?.length">
    <EmptyState message="No campaigns yet" />
  </div>
  ```

**Estimated**: 4 hours  
**Blocks**: Portal functionality

---

### 🔴 CRITICAL: Database Schema Fixes (2 hours)

#### 1.3 Add Composite Unique Index

- [ ] **Analytics Daily Log** - Add unique constraint
  ```json
  // In analytics_daily_log.json
  "unique": 1,
  "unique_key": ["date", "campaign", "platform", "ad_account"]
  ```

- [ ] Create migration patch
  ```python
  # patches/add_analytics_daily_log_unique_index.py
  def execute():
      frappe.db.sql("""
          ALTER TABLE `tabAnalytics Daily Log`
          ADD UNIQUE INDEX unique_analytics_log 
          (date, campaign, platform, ad_account)
      """)
  ```

- [ ] Update patches.txt
  ```
  marketing_hub.patches.add_analytics_daily_log_unique_index
  ```

- [ ] Test with duplicate data scenarios

**Estimated**: 2 hours  
**Blocks**: Data integrity

---

### 🟠 HIGH: Basic Testing Infrastructure (30 hours)

#### 1.4 Unit Tests for Core Utilities (16 hours)

- [ ] **test_attribution_engine.py**
  - Test UTM parameter extraction
  - Test priority-based attribution logic
  - Test CRM integration (mocked)
  - Test edge cases (missing params, null values)

- [ ] **test_content_orchestration.py**
  - Test content adaptation (channel limits)
  - Test template rendering with variables
  - Test UTM parameter generation
  - Test content recommendations

- [ ] **test_permissions.py**
  - Test row-level filtering (agency mode)
  - Test campaign visibility by client
  - Test role-based access control

- [ ] **test_analytics_sync.py**
  - Test ROAS calculation
  - Test daily log creation
  - Test duplicate prevention
  - Test OAuth token refresh (mocked)

**Estimated**: 16 hours

---

#### 1.5 Integration Tests for Key Workflows (14 hours)

- [ ] **test_campaign_workflow.py**
  - Test campaign creation with custom fields
  - Test campaign activity execution
  - Test segment targeting
  - Test budget tracking

- [ ] **test_omni_blast_workflow.py**
  - Test Omni Blast creation
  - Test network selection
  - Test Social Post generation
  - Test blast execution (email + WhatsApp)

- [ ] **test_social_post_workflow.py**
  - Test Social Post creation with network link
  - Test content validation (character limits)
  - Test scheduling
  - Test status transitions

- [ ] **test_content_workflow.py**
  - Test Content Asset upload
  - Test Marketing Template creation
  - Test Campaign Content linking
  - Test template variable replacement

**Estimated**: 14 hours

---

### 🟡 MEDIUM: Documentation Consolidation (16 hours)

#### 1.6 Merge Redundant Documentation Files

**Action Plan**:

1. **Create ARCHITECTURE.md** (4 hours)
   - [ ] Merge: ACTUAL_CURRENT_STATE.md + IMPLEMENTATION_SUMMARY.md
   - [ ] Sections: System Overview, Doctypes (17), Utilities (10), Hooks
   - [ ] Include: Database schema, doctype relationships, architecture diagrams
   - [ ] Delete source files after merge

2. **Create DEVELOPER_GUIDE.md** (4 hours)
   - [ ] Merge: SETUP_GUIDE.md + VUE_PORTAL_SETUP.md + PORTAL_DESIGN_REFACTOR.md
   - [ ] Sections: Installation, Development Setup, Testing, Contributing
   - [ ] Include: Local dev environment, debugging, code style, PR process
   - [ ] Delete source files after merge

3. **Create USER_GUIDE.md** (4 hours)
   - [ ] Merge: CONTENT_MANAGEMENT_GUIDE.md + MARKETING_HUB_SETTINGS_GUIDE.md + SETTINGS_IMPLEMENTATION.md
   - [ ] Sections: Features, Workflows, Settings, Best Practices
   - [ ] Include: Step-by-step guides, screenshots, FAQs
   - [ ] Delete source files after merge

4. **Create ROADMAP.md** (2 hours)
   - [ ] Merge: IMPLEMENTATION_ROADMAP.md + CURRENT_STATE_AND_ROADMAP.md
   - [ ] Sections: Completed, In Progress, Planned, Long-term Vision
   - [ ] Include: Priority matrix, effort estimates, dependencies
   - [ ] Delete source files after merge

5. **Update README.md** (2 hours)
   - [ ] Add quick start guide
   - [ ] Link to consolidated docs
   - [ ] Add feature overview with status badges
   - [ ] Include screenshots/demo

**Documents to Delete** (11 files):
- ACTUAL_CURRENT_STATE.md
- IMPLEMENTATION_SUMMARY.md
- CURRENT_STATE_AND_ROADMAP.md
- IMPLEMENTATION_ROADMAP.md
- SETUP_GUIDE.md
- VUE_PORTAL_SETUP.md
- PORTAL_DESIGN_REFACTOR.md
- CONTENT_MANAGEMENT_GUIDE.md
- CONTENT_SYSTEM_SUMMARY.md
- MARKETING_HUB_SETTINGS_GUIDE.md
- SETTINGS_IMPLEMENTATION.md

**Keep**:
- README.md (updated)
- ARCHITECTURE.md (new)
- DEVELOPER_GUIDE.md (new)
- USER_GUIDE.md (new)
- ROADMAP.md (new)
- COMPREHENSIVE_ANALYSIS.md (audit reference)
- DESIGN_BEFORE_AFTER.md (historical reference)
- TESTING_CHECKLIST.md (useful as-is)
- ERPNEXT_INTEGRATION.md (specific integration guide)
- WORKSPACE_PERMISSIONS.md (specific guide)
- INTEGRATION_GUIDE.md (if exists, specific guide)
- FORK-MAINTENANCE.md (Git workflow guide)

**Estimated**: 16 hours

---

## Phase 2: Production Readiness (150 hours)

### 🟠 HIGH: Google Ads Integration (40 hours)

#### 2.1 Complete OAuth Implementation (8 hours)

- [ ] Set up Google Cloud Console project
  - Create OAuth 2.0 credentials
  - Configure consent screen
  - Add authorized redirect URIs

- [ ] Test OAuth flow in `oauth_integration.py`
  - Authorization URL generation
  - Callback handling
  - Token storage in Social Login Key
  - Token refresh automation

- [ ] Create Admin UI for OAuth setup
  - Settings page for client_id/secret
  - "Connect Google Ads" button
  - Connection status indicator

**Estimated**: 8 hours

---

#### 2.2 Implement Analytics Sync (16 hours)

- [ ] Complete `_sync_google_ads()` in `analytics_sync.py`
  - Use Google Ads API v14
  - Fetch campaign metrics (impressions, clicks, cost, conversions)
  - Map to Analytics Daily Log fields
  - Handle rate limits and pagination

- [ ] Create conversion tracking setup
  - Google Ads conversion actions
  - Webhook for conversion events
  - Link ERPNext leads to Google Ads conversions

- [ ] Add error handling
  - API quota exceeded
  - Invalid credentials
  - Network errors
  - Log to Error Log doctype

- [ ] Test with real Google Ads account
  - Verify data accuracy
  - Test daily sync scheduler
  - Validate ROAS calculations

**Estimated**: 16 hours

---

#### 2.3 Implement Campaign Management (16 hours)

- [ ] Create campaign creation API
  - Campaign CRUD operations
  - Ad group management
  - Keyword management
  - Budget setting

- [ ] Add campaign sync
  - Pull existing campaigns from Google Ads
  - Map to ERPNext Campaign doctype
  - Two-way sync (ERPNext <-> Google Ads)

- [ ] Create UI for campaign management
  - Campaign creation wizard
  - Keyword research tool
  - Budget allocation interface

**Estimated**: 16 hours

---

### 🟠 HIGH: Meta Ads Integration (40 hours)

#### 2.4 Complete OAuth Implementation (8 hours)

- [ ] Set up Meta Business account
  - Create Facebook App
  - Add Marketing API access
  - Configure OAuth redirect URIs

- [ ] Test OAuth flow
  - Authorization for Facebook + Instagram
  - Long-lived token exchange
  - Token refresh automation

- [ ] Create Admin UI for OAuth setup
  - Settings page for app_id/secret
  - "Connect Meta Ads" button
  - Account selection (if multiple)

**Estimated**: 8 hours

---

#### 2.5 Implement Analytics Sync (16 hours)

- [ ] Complete `_sync_meta_ads()` in `analytics_sync.py`
  - Use Marketing API v18
  - Fetch insights (reach, impressions, spend, conversions)
  - Map to Analytics Daily Log
  - Handle Instagram data separately

- [ ] Create conversion tracking
  - Facebook Pixel integration
  - Conversions API for server-side tracking
  - Link ERPNext leads to Meta conversions

- [ ] Add error handling
  - API errors (rate limits, permissions)
  - Invalid ad account
  - Missing metrics

- [ ] Test with real Meta Ads account
  - Verify data for Facebook campaigns
  - Verify data for Instagram campaigns
  - Test daily sync

**Estimated**: 16 hours

---

#### 2.6 Implement Posting (16 hours)

- [ ] Complete `_execute_meta_ads_blast()` in `omni_blast.py`
  - Create Facebook posts via API
  - Create Instagram posts via API
  - Upload media (images/videos)
  - Schedule posts

- [ ] Implement in `auto_post.py`
  - Post to Facebook Page
  - Post to Instagram Business Account
  - Handle Stories, Reels
  - Status callback handling

- [ ] Add post sync
  - Pull published posts back
  - Update engagement metrics (likes, comments, shares)
  - Handle post deletion

**Estimated**: 16 hours

---

### 🟡 MEDIUM: Code Quality Improvements (32 hours)

#### 2.7 Fix Functional Redundancies (12 hours)

**Issue 1: Omni Blast Duplication**

- [ ] Refactor `utils/omni_blast.py`
  - Extract shared blast logic to `OmniBlastExecutor` class
  - Make it reusable by both Campaign Activity and Omni Blast doctype
  - Remove duplicate `execute_blast()` methods

- [ ] Update Campaign Activity
  - Use `OmniBlastExecutor` for omni-channel blasts
  - Keep email/WhatsApp/SMS logic

- [ ] Update Omni Blast doctype
  - Use `OmniBlastExecutor` for social media blasts
  - Focus on Social Post generation

**Issue 2: Content Preview Duplication**

- [ ] Create `utils/preview_generator.py`
  - Extract `generate_preview(content, variables)` method
  - Handle HTML rendering
  - Handle variable replacement
  - Handle media preview

- [ ] Update Campaign Content
  - Use shared `preview_generator.generate_preview()`
  - Remove local preview logic

- [ ] Update Marketing Template
  - Use shared `preview_generator.generate_preview()`
  - Remove local preview logic

- [ ] Update Social Post
  - Use shared `preview_generator.generate_preview()`
  - Remove local preview logic

**Issue 3: ROAS Calculation Duplication**

- [ ] Make Analytics Daily Log the single source of truth
  - Keep ROAS calculation in `analytics_daily_log.py`
  - Cache result in ROAS field

- [ ] Update Marketing Expense
  - Remove ROAS calculation
  - Fetch from Analytics Daily Log
  - Add `get_campaign_roas(campaign)` utility method

**Estimated**: 12 hours

---

#### 2.8 Fix Data Redundancies (8 hours)

**Issue: Channel Specifications Duplication**

- [ ] Move channel specs to Social Media Network doctype
  - Add fields: char_limit, image_width, image_height, video_max_duration
  - Populate for existing networks

- [ ] Remove hardcoded specs from `marketing_template.js`
  - Fetch from Social Media Network
  - Auto-populate on network selection

- [ ] Remove hardcoded specs from `content_orchestration.py`
  - Query Social Media Network
  - Use dynamic specs in `get_channel_best_practices()`

- [ ] Remove hardcoded specs from `social_post.py`
  - Fetch from linked Social Media Network
  - Validate against network's char_limit

- [ ] Create migration to populate specs for existing networks
  ```python
  # patches/populate_network_specs.py
  specs = {
      "Facebook": {"char_limit": 63206, "image_width": 1200, "image_height": 630},
      # ... etc
  }
  ```

**Estimated**: 8 hours

---

#### 2.9 Add Type Hints and Constants (12 hours)

- [ ] Create `constants.py` file
  ```python
  # marketing_hub/marketing_hub/constants.py
  class ChannelType:
      EMAIL = "Email"
      WHATSAPP = "WhatsApp"
      SMS = "SMS"
      PUSH = "Push Notification"
  
  class PostStatus:
      DRAFT = "Draft"
      SCHEDULED = "Scheduled"
      PUBLISHED = "Published"
      FAILED = "Failed"
  
  class NetworkType:
      SOCIAL_MEDIA = "Social Media"
      ADVERTISING = "Advertising Platform"
      MESSAGING = "Messaging"
      SEARCH_ENGINE = "Search Engine"
  ```

- [ ] Add type hints to all utility modules
  ```python
  from typing import Dict, List, Optional, Any
  
  def get_dashboard_data() -> Dict[str, Any]:
      ...
  ```

- [ ] Replace magic strings with constants
  ```python
  # Before
  if channel == "Email":
  
  # After
  from marketing_hub.marketing_hub.constants import ChannelType
  if channel == ChannelType.EMAIL:
  ```

- [ ] Update all 10 utility files with type hints

**Estimated**: 12 hours

---

### 🟡 MEDIUM: Advanced Reports (20 hours)

#### 2.10 Create Script Reports

- [ ] **Campaign Performance Report** (6 hours)
  - Columns: campaign, budget, spend, leads, conversions, roas, roi
  - Filters: date_range, status, channel
  - Charts: Spend vs Revenue, Lead funnel
  - Downloadable as CSV/Excel

- [ ] **Attribution Report** (6 hours)
  - Columns: source, medium, campaign, leads, conversion_rate, revenue
  - Filters: date_range, attribution_model
  - Charts: Source breakdown, Campaign effectiveness
  - Attribution model selector (first-touch, last-touch, linear)

- [ ] **Channel Performance Report** (4 hours)
  - Columns: channel, impressions, clicks, ctr, conversions, cost_per_conversion
  - Filters: date_range, campaign
  - Charts: Channel comparison, Cost efficiency

- [ ] **Detailed ROAS Analysis Report** (4 hours)
  - Enhance existing ROAS Analysis
  - Add: time-series chart, campaign comparison, channel breakdown
  - Add predictive ROAS (ML-based if possible)

**Estimated**: 20 hours

---

### 🟡 MEDIUM: Form Submission Handlers (18 hours)

#### 2.11 Implement Campaign Creation

- [ ] Create backend handler
  ```python
  # www/marketing/api.py
  @frappe.whitelist()
  def create_campaign(data):
      campaign = frappe.get_doc({
          "doctype": "Campaign",
          "campaign_name": data.get("name"),
          "description": data.get("description"),
          # ... more fields
      })
      campaign.insert()
      return campaign.name
  ```

- [ ] Update NewCampaign.vue
  - Add form validation
  - Add submit button with loading state
  - Call backend API
  - Redirect to campaign after creation
  - Show success/error messages

- [ ] Add file upload for campaign assets
  - Media upload component
  - Link to Content Asset

**Estimated**: 8 hours

---

#### 2.12 Implement Social Post Creation

- [ ] Create backend handler
  ```python
  @frappe.whitelist()
  def create_social_post(data):
      post = frappe.get_doc({
          "doctype": "Social Post",
          "post_title": data.get("title"),
          "platform": data.get("network"),
          # ... more fields
      })
      post.insert()
      return post.name
  ```

- [ ] Update NewSocialPost.vue
  - Add network selector (from Social Media Network)
  - Add character counter based on selected network
  - Add media upload
  - Add preview pane
  - Submit handler with validation

- [ ] Create tabbed interface for Omni Blast
  - One tab per selected network
  - Customizable content per network
  - Shared content option

**Estimated**: 10 hours

---

## Phase 3: Feature Completion (200 hours)

### 🟢 LOW: Remaining Platform Integrations (120 hours)

#### 3.1 LinkedIn Ads (40 hours)

- [ ] OAuth implementation (8 hours)
- [ ] Analytics sync (16 hours)
- [ ] Sponsored Content posting (16 hours)

#### 3.2 TikTok Ads (40 hours)

- [ ] OAuth implementation (8 hours)
- [ ] Analytics sync (16 hours)
- [ ] Video ad posting (16 hours)

#### 3.3 Twitter/X Ads (40 hours)

- [ ] OAuth implementation (8 hours)
- [ ] Analytics sync (16 hours)
- [ ] Tweet posting with media (16 hours)

---

### 🟢 LOW: Agency Mode Billing (40 hours)

#### 3.4 Create Billing Doctypes (16 hours)

- [ ] **Agency Package** doctype
  - Fields: package_name, price, channels_allowed, campaign_limit, user_limit
  - Tiers: Basic, Professional, Enterprise

- [ ] **Client Subscription** doctype
  - Fields: client, package, start_date, end_date, status, usage_stats
  - Auto-renewal logic
  - Payment status tracking

- [ ] **Usage Tracker** (child table)
  - Fields: date, campaigns_created, blasts_sent, storage_used
  - Daily aggregation

---

#### 3.5 Implement Usage Limits (12 hours)

- [ ] Campaign creation limit enforcement
  - Check subscription.campaign_limit before create
  - Show upgrade prompt if limit reached

- [ ] Channel access control
  - Check subscription.channels_allowed
  - Disable unavailable channels in UI

- [ ] Storage limit enforcement
  - Check Content Asset upload against limit
  - Show storage usage in dashboard

---

#### 3.6 Payment Gateway Integration (12 hours)

- [ ] Integrate with Stripe/Razorpay
  - Subscription creation
  - Auto-renewal
  - Invoice generation
  - Payment failure handling

- [ ] Create billing dashboard
  - Current plan, usage stats
  - Upgrade/downgrade options
  - Payment history

**Estimated**: 40 hours

---

### 🟢 LOW: YouTube & Pinterest (40 hours)

#### 3.7 YouTube Integration (20 hours)

- [ ] OAuth with YouTube Data API v3
- [ ] Video upload
- [ ] Analytics sync (views, watch time, engagement)
- [ ] Shorts posting

#### 3.8 Pinterest Integration (20 hours)

- [ ] OAuth with Pinterest API v5
- [ ] Pin creation with images
- [ ] Board management
- [ ] Analytics sync (impressions, saves, clicks)

**Estimated**: 40 hours

---

## Phase 4: Polish & Optimization (80 hours)

### 🟢 LOW: Performance Optimization (20 hours)

#### 4.1 Database Optimization

- [ ] Add indexes on frequently queried fields
  - Campaign: status, client, created_at
  - Social Post: platform, status, scheduled_time
  - Analytics Daily Log: date, campaign, platform

- [ ] Optimize N+1 queries
  - Use eager loading for related doctypes
  - Batch database operations

- [ ] Add database query caching
  - Cache dashboard metrics (5 min TTL)
  - Cache segment calculations

**Estimated**: 8 hours

---

#### 4.2 Frontend Performance

- [ ] Implement lazy loading for routes
  ```javascript
  const Dashboard = () => import('./pages/Dashboard.vue')
  ```

- [ ] Add pagination for large lists
  - Campaigns list (20 per page)
  - Social posts list (20 per page)
  - Analytics data (30 days default)

- [ ] Optimize chart rendering
  - Use canvas instead of SVG for large datasets
  - Debounce filter changes

- [ ] Add service worker for offline support

**Estimated**: 8 hours

---

#### 4.3 API Rate Limiting

- [ ] Implement rate limiting for API calls
  - Dashboard: 60 requests/min per user
  - Analytics: 30 requests/min per user
  - Bulk operations: 10 requests/min per user

- [ ] Add request throttling for external APIs
  - Google Ads: 50 requests/min
  - Meta Ads: 200 requests/hour
  - Exponential backoff on rate limit errors

**Estimated**: 4 hours

---

### 🟢 LOW: Error Handling & Logging (16 hours)

#### 4.4 Standardize Error Responses

- [ ] Create error response utility
  ```python
  # utils/errors.py
  class APIError(Exception):
      def __init__(self, message, code, details=None):
          self.message = message
          self.code = code
          self.details = details
  
  def handle_error(e):
      if isinstance(e, APIError):
          return {"error": e.message, "code": e.code}
      frappe.log_error(str(e))
      return {"error": "Internal server error", "code": 500}
  ```

- [ ] Wrap all whitelisted methods with error handler
  ```python
  @frappe.whitelist()
  def get_dashboard_data():
      try:
          # ... logic
      except Exception as e:
          return handle_error(e)
  ```

- [ ] Add structured logging
  ```python
  frappe.logger().info(f"Dashboard data requested by {frappe.session.user}")
  ```

**Estimated**: 8 hours

---

#### 4.5 Improve Error Messages

- [ ] Replace generic errors with specific messages
  ```python
  # Before
  frappe.throw("Error")
  
  # After
  frappe.throw(_("Campaign '{0}' has exceeded budget limit of {1}").format(
      campaign.name, frappe.format(campaign.budget, {"fieldtype": "Currency"})
  ))
  ```

- [ ] Add user-friendly error pages in Vue
  - 404 - Page not found
  - 403 - Permission denied
  - 500 - Server error
  - Network error - Offline mode

- [ ] Add error boundary component
  ```vue
  <ErrorBoundary>
    <RouterView />
  </ErrorBoundary>
  ```

**Estimated**: 8 hours

---

### 🟢 LOW: Comprehensive Testing (44 hours)

#### 4.6 Increase Test Coverage (30 hours)

- [ ] Doctype tests (10 hours)
  - Test validation logic
  - Test on_save/on_submit hooks
  - Test permission queries

- [ ] API endpoint tests (10 hours)
  - Test all whitelisted methods
  - Test with different user roles
  - Test error scenarios

- [ ] Frontend component tests (10 hours)
  - Test Vue components with Vitest
  - Test user interactions
  - Test edge cases (empty states, errors)

**Estimated**: 30 hours

---

#### 4.7 End-to-End Testing (14 hours)

- [ ] Set up Cypress/Playwright
- [ ] Test critical user paths
  - Campaign creation flow
  - Omni Blast execution
  - Social post scheduling
  - Analytics viewing
  - Settings configuration

**Estimated**: 14 hours

---

## Summary Statistics

### By Priority
- 🔴 **CRITICAL**: 14 hours (3 tasks) - Phase 1
- 🟠 **HIGH**: 110 hours (6 tasks) - Phase 1-2
- 🟡 **MEDIUM**: 86 hours (8 tasks) - Phase 2
- 🟢 **LOW**: 280 hours (15 tasks) - Phase 3-4

### By Phase
- **Phase 1 (MVP)**: 60 hours - Critical path to functional MVP
- **Phase 2 (Production)**: 150 hours - Production-ready with key platforms
- **Phase 3 (Feature Complete)**: 200 hours - All platforms implemented
- **Phase 4 (Polish)**: 80 hours - Performance & quality improvements

### Total Effort
**490 hours** (~12 weeks with 1 full-time developer)

### MVP Timeline (Phase 1 Only)
**60 hours** (~1.5 weeks with 1 full-time developer)

---

## Task Dependencies

```
Phase 1 (MVP) - All tasks can start immediately
├── 1.1 Create API Endpoints (blocking 1.2)
├── 1.2 Fix Frontend API Calls (depends on 1.1)
├── 1.3 Database Fixes (independent)
├── 1.4 Unit Tests (independent)
├── 1.5 Integration Tests (independent)
└── 1.6 Documentation (independent)

Phase 2 (Production) - Depends on Phase 1 completion
├── 2.1-2.3 Google Ads (independent)
├── 2.4-2.6 Meta Ads (independent)
├── 2.7-2.9 Code Quality (independent)
├── 2.10 Reports (independent)
└── 2.11-2.12 Form Handlers (depends on 1.1)

Phase 3 (Feature Complete) - Depends on Phase 2 completion
├── 3.1 LinkedIn (independent)
├── 3.2 TikTok (independent)
├── 3.3 Twitter (independent)
├── 3.4-3.6 Agency Mode (independent)
├── 3.7 YouTube (independent)
└── 3.8 Pinterest (independent)

Phase 4 (Polish) - Can start after Phase 2
├── 4.1-4.3 Performance (depends on Phase 2)
├── 4.4-4.5 Error Handling (independent)
└── 4.6-4.7 Testing (depends on features being complete)
```

---

## Recommended Execution Strategy

### Sprint 1-2 (Week 1-2): MVP Push
**Goal**: Functional portal with working API
- Complete 1.1, 1.2, 1.3 (frontend-backend connection)
- Start 1.4, 1.5 (testing)
- **Deliverable**: Working Dashboard, Campaigns, Social, Analytics pages

### Sprint 3-4 (Week 3-4): Testing & Docs
**Goal**: Stable MVP with tests
- Complete 1.4, 1.5 (testing)
- Complete 1.6 (documentation)
- **Deliverable**: 70% test coverage, consolidated docs

### Sprint 5-8 (Week 5-8): Platform Integrations
**Goal**: Google Ads + Meta Ads working
- Complete 2.1-2.3 (Google Ads)
- Complete 2.4-2.6 (Meta Ads)
- **Deliverable**: Production-ready with 2 major platforms

### Sprint 9-12 (Week 9-12): Code Quality & Reports
**Goal**: Clean, maintainable codebase
- Complete 2.7-2.9 (refactoring)
- Complete 2.10-2.12 (reports + forms)
- **Deliverable**: Production-ready with all core features

### Sprint 13+ (Week 13+): Feature Expansion
**Goal**: Complete platform coverage
- Phase 3 & 4 as needed
- **Deliverable**: Feature-complete product

---

*End of TODO List*
