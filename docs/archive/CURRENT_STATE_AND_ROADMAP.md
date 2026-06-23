# Marketing Hub - Current State & Development Roadmap

## Overview
Marketing Hub is a Frappe Framework-based marketing automation and analytics platform with a modern Vue.js SPA interface. It follows the architecture pattern of CRM and Helpdesk apps.

**Status**: ✅ Core infrastructure complete, ready for feature development
**Stack**: Python/Frappe backend + Vue 3 + Frappe UI + Vite
**Design System**: Frappe UI (official components + Tailwind preset)

---

## ✅ Completed Components

### 1. Vue.js Portal (SPA)
**Location**: `desk/`

#### Components (`desk/src/components/`)
- **Sidebar.vue** - Main navigation using Frappe UI Sidebar with app switcher
- **AppShell.vue** - Layout wrapper
- **AppSwitcher.vue** - Quick app navigation (legacy, integrated into Sidebar)
- **Navbar.vue** - Top navigation bar
- **BrandLogo.vue** - Marketing Hub branding
- **UserMenu.vue** - User profile dropdown (legacy, integrated into Sidebar)
- **SidebarLink.vue** - Navigation item (legacy, using Frappe UI now)

#### Pages (`desk/src/pages/`)
- **Dashboard.vue** - Overview with stats (needs API integration)
- **Campaigns.vue** - Campaign list view (needs data binding)
- **Social.vue** - Social media posts management (needs data binding)
- **Analytics.vue** - Analytics dashboard (needs charts integration)
- **NewCampaign.vue** - Campaign creation form (needs form handling)
- **NewSocialPost.vue** - Social post composer (needs API integration)

#### Design System
- ✅ Frappe UI components (Sidebar, Dropdown, Badge, Button)
- ✅ Frappe UI Tailwind preset with full design tokens
- ✅ Surface, ink, outline color system
- ✅ Responsive layout (mobile-ready via Frappe UI)
- ✅ Inter font family
- ✅ CSS: 105KB (includes full Frappe UI design system)

### 2. Backend Doctypes
**Location**: `marketing_hub/marketing_hub/doctype/`

#### Core Doctypes (13 total)
1. **Ad Account** - Social/ad platform connections
2. **Analytics Connector** - Google Analytics, Facebook Pixel integration
3. **Analytics Daily Log** - Daily performance metrics
4. **Campaign** (Enhanced) - Core campaign management
5. **Campaign Activity** - Campaign events/tasks
6. **Campaign Content** - Multi-channel content management
7. **Content Asset** - Media library (images, videos, files)
8. **Marketing Expense** - Budget tracking
9. **Marketing Hub Connection** - External service integrations
10. **Marketing Hub Settings** - Per-company configuration
11. **Marketing Segment** - Audience segmentation
12. **Marketing Template** - Multi-channel message templates
13. **Social Post** - Social media post management
14. **Template Asset Item** - Template media references

### 3. Python Utilities
**Location**: `marketing_hub/utils/`

- **agency_mode.py** - Multi-client management
- **analytics_sync.py** - Analytics data sync
- **attribution_engine.py** - Multi-touch attribution
- **auto_post.py** - Scheduled social posting
- **content_orchestration.py** - Content calendar
- **crm_integration.py** - Lead/Contact sync
- **oauth_integration.py** - OAuth for social platforms
- **omni_blast.py** - Multi-channel campaigns
- **permissions.py** - Row-level security

### 4. Portal Configuration
- ✅ Route: `/marketing` (SPA mount point)
- ✅ Route rules: `/marketing/*` → Vue Router handles all sub-routes
- ✅ Build output: `marketing_hub/public/desk/` (assets)
- ✅ Entry point: `www/marketing/index.html` (Jinja template with context injection)
- ✅ API backend: `www/marketing/index.py` (Python API methods)

### 5. Custom Fields
**Location**: `fixtures/custom_fields.json`

#### Campaign Enhancements
- `channels_used` - Multi-select for channels
- `is_omni_campaign` - Checkbox for omni-channel
- `client` - Link to Customer (agency mode)
- `project` - Link to Project
- `roas` - Currency field for ROAS

#### Lead/Contact UTM Tracking
- `utm_campaign`, `utm_source`, `utm_medium`, `utm_content`, `utm_term`

---

## 🚧 In Progress

### 1. App Switcher Dropdown
**Issue**: Blank dropdown when clicking logo
**Root Cause**: menuItems structure needs to match Frappe UI Sidebar types
**Fix Applied**: Restructured menuItems to grouped format:
```javascript
menuItems: [
  {
    group: 'Installed Apps',
    items: [{ label, icon, onClick }]
  },
  {
    group: 'Account',
    items: [...]
  },
  {
    group: 'Help',
    items: [...]
  }
]
```

**Update**: Added `window.installed_apps` injection in `index.html`

### 2. Backend API Integration
**Status**: Base structure ready, needs implementation

**Required APIs** (`www/marketing/index.py`):
```python
@frappe.whitelist()
def get_dashboard_data():
    # Returns stats + active campaigns
    # Currently returns dummy data

@frappe.whitelist()
def get_campaigns():
    # List all campaigns with filters

@frappe.whitelist()
def get_social_posts():
    # List social posts

@frappe.whitelist()
def create_campaign(data):
    # Create new campaign

@frappe.whitelist()
def create_social_post(data):
    # Create new social post
```

---

## 📋 Development Roadmap

### Phase 1: Core Data Binding (Week 1-2)
**Priority**: HIGH
**Goal**: Connect Vue pages to Frappe backend

#### Tasks
- [ ] **Dashboard.vue** - Integrate `get_dashboard_data()` API
  - Display real metrics (spend, revenue, ROAS, leads)
  - Show active campaigns list
  - Add date range filter

- [ ] **Campaigns.vue** - Implement campaign list
  - Fetch campaigns from backend
  - Add filters (status, date, channel)
  - Implement search
  - Add pagination
  - Link to campaign detail view

- [ ] **Social.vue** - Social posts management
  - Fetch posts from backend
  - Display post preview
  - Filter by platform/status
  - Schedule post functionality

- [ ] **NewCampaign.vue** - Campaign creation form
  - Form validation
  - Channel selection (multi-select)
  - Budget input
  - Save to backend
  - Success/error handling

- [ ] **NewSocialPost.vue** - Post composer
  - Platform selection
  - Media upload
  - Character counter
  - Preview
  - Schedule/publish

- [ ] **Analytics.vue** - Analytics dashboard
  - Integrate Chart.js or ECharts
  - Display metrics over time
  - Channel performance comparison
  - Export data functionality

### Phase 2: Advanced Features (Week 3-4)
**Priority**: MEDIUM
**Goal**: Implement core marketing automation features

#### Tasks
- [ ] **Multi-Touch Attribution**
  - Configure attribution models (first-touch, last-touch, linear)
  - Display attribution reports
  - Integrate with campaign performance

- [ ] **Content Calendar**
  - Week/month view of scheduled posts
  - Drag-and-drop scheduling
  - Bulk actions

- [ ] **Audience Segmentation**
  - Create segments based on Lead/Contact filters
  - Display segment size
  - Assign segments to campaigns

- [ ] **Template Management**
  - Template editor with variable support
  - Preview templates with sample data
  - Channel-specific templates (Email, WhatsApp, SMS)

- [ ] **Campaign Activities**
  - Task management within campaigns
  - Activity timeline
  - Team assignments

### Phase 3: Integrations (Week 5-6)
**Priority**: MEDIUM
**Goal**: Connect external platforms

#### Tasks
- [ ] **Social Media Integrations**
  - Facebook/Instagram OAuth
  - Twitter/X OAuth
  - LinkedIn OAuth
  - Post directly from Marketing Hub
  - Fetch engagement metrics

- [ ] **Analytics Integrations**
  - Google Analytics connection
  - Facebook Pixel integration
  - Sync daily metrics
  - Display in unified dashboard

- [ ] **Ad Platform Integrations**
  - Facebook Ads Manager
  - Google Ads API
  - Pull ad performance data
  - Manage ad spend tracking

- [ ] **CRM Integration**
  - Sync leads from campaigns
  - Link contacts to campaigns
  - Attribution tracking to Lead source

### Phase 4: Agency Mode (Week 7-8)
**Priority**: LOW (if needed)
**Goal**: Multi-client management for agencies

#### Tasks
- [ ] **Client Management**
  - Link campaigns to clients
  - Per-client dashboards
  - Client-level permissions

- [ ] **Project Management**
  - Link campaigns to projects
  - Project budgets
  - Project reports

- [ ] **Team Collaboration**
  - Assign team members to campaigns
  - Role-based access (account manager, creative, analyst)
  - Activity notifications

### Phase 5: Reporting & Optimization (Week 9-10)
**Priority**: MEDIUM
**Goal**: Advanced reporting and insights

#### Tasks
- [ ] **Custom Reports**
  - Report builder UI
  - Export to PDF/Excel
  - Schedule email reports

- [ ] **A/B Testing**
  - Create campaign variants
  - Split traffic
  - Statistical significance testing

- [ ] **Recommendations Engine**
  - Budget optimization suggestions
  - Best time to post
  - Audience targeting recommendations

- [ ] **ROI Calculator**
  - Revenue attribution
  - Cost breakdown by channel
  - Profit margin analysis

---

## 🔧 Technical Debt & Improvements

### High Priority
- [ ] Add proper error boundaries in Vue components
- [ ] Implement loading states for all API calls
- [ ] Add form validation with Frappe UI FormControl
- [ ] Set up proper TypeScript types (currently using JS)
- [ ] Add unit tests for components
- [ ] Add integration tests for API endpoints

### Medium Priority
- [ ] Optimize bundle size (currently 489KB vendor, 85KB frappe-ui)
- [ ] Implement service worker for offline support
- [ ] Add PWA manifest for mobile app feel
- [ ] Set up Sentry or error tracking
- [ ] Add analytics tracking (e.g., PostHog)

### Low Priority
- [ ] Add dark mode toggle
- [ ] Implement keyboard shortcuts
- [ ] Add tour/onboarding flow
- [ ] Multi-language support (i18n)

---

## 📊 Current Metrics

### Bundle Sizes (Production Build)
- **Vendor**: 489.83 KB (148.94 KB gzipped)
- **Frappe UI**: 85.33 KB (24.96 KB gzipped)
- **App Code**: 10.31 KB (3.53 KB gzipped)
- **CSS**: 105.49 KB (17.44 KB gzipped)
- **Total**: ~591 KB (~195 KB gzipped)

### Code Statistics
- **Vue Components**: 12 components
- **Pages**: 6 pages
- **Doctypes**: 13 doctypes
- **Python Utilities**: 9 utility modules
- **Custom Fields**: 11 custom fields

### Performance Targets
- **First Contentful Paint**: < 1.5s
- **Time to Interactive**: < 3.5s
- **Lighthouse Score**: > 90

---

## 🐛 Known Issues

### Critical
1. ~~App switcher dropdown showing blank~~ (Fixed - added grouped structure + window.installed_apps)
2. 500 error on `/api/method/marketing_hub.www.marketing.index.get_context` (Needs investigation)

### Minor
- Socket.io connection errors (port 9000) - expected in dev mode
- Font preload warnings - non-blocking
- Inter.var font 404 - using system fallback

---

## 🚀 Quick Start for Developers

### Setup
```bash
cd /home/puxxo/CodeBase/erpNext/frappe-bench-v15

# Install deps
cd apps/marketing_hub/desk
npm install

# Development
npm run dev

# Build for production
npm run build

# Clear Frappe cache after build
cd ../../../
bench --site erpnext-v15.local clear-cache
bench restart
```

### File Structure
```
marketing_hub/
├── desk/                                    # Vue.js SPA
│   ├── src/
│   │   ├── pages/                          # Route pages
│   │   ├── components/                     # Reusable components
│   │   ├── stores/                         # Pinia stores (sidebar state)
│   │   ├── App.vue                         # Root component
│   │   ├── router.js                       # Vue Router config
│   │   ├── main.js                         # Entry point
│   │   └── index.css                       # Global styles
│   ├── index.html                          # Dev template
│   ├── vite.config.js                      # Vite config
│   ├── tailwind.config.js                  # Tailwind + Frappe UI preset
│   └── package.json
│
├── marketing_hub/
│   ├── marketing_hub/doctype/              # Frappe doctypes
│   ├── utils/                              # Python utilities
│   ├── templates/                          # Jinja templates
│   ├── www/marketing/                      # Web pages
│   │   ├── index.html                      # Production SPA entry
│   │   └── index.py                        # API methods
│   ├── public/
│   │   ├── desk/                           # Built assets
│   │   ├── js/                             # Desk JS overrides
│   │   └── css/                            # Portal CSS
│   ├── hooks.py                            # Frappe hooks config
│   └── config/desktop.py                   # Workspace config
│
└── fixtures/
    └── custom_fields.json                  # Custom field definitions
```

### API Development Pattern
```python
# www/marketing/index.py
@frappe.whitelist()
def get_my_data():
    # Runs as current user
    return {
        "data": frappe.get_all("Campaign", fields=["name", "campaign_name"])
    }
```

```javascript
// Vue component
import { call } from 'frappe-ui'

const data = await call('marketing_hub.www.marketing.index.get_my_data')
```

---

## 📚 References

### Documentation
- **Frappe UI**: https://ui.frappe.io/
- **Frappe Framework**: https://frappeframework.com/
- **Vue 3**: https://vuejs.org/
- **Vite**: https://vitejs.dev/

### Similar Apps
- **CRM**: `/apps/crm/frontend/` - Reference architecture
- **Helpdesk**: `/apps/helpdesk/desk/` - Reference architecture

---

## 👥 Team & Contact

**Current State**: Solo development
**Support**: dev@itechnologies.ng
**License**: MIT

---

## 📝 Notes

### Design Philosophy
- **Mobile-first**: Responsive design using Frappe UI components
- **Performance**: Code splitting, lazy loading, tree shaking
- **Accessibility**: ARIA labels, keyboard navigation
- **Consistency**: Follow Frappe UI design system strictly

### Code Standards
- **Vue**: Composition API with `<script setup>`
- **Naming**: kebab-case for files, PascalCase for components
- **Imports**: Use `@/` alias for src directory
- **Icons**: Use unplugin-icons with Lucide icon set
- **State**: Pinia for global state, composables for logic

### Commit Messages
- `feat:` New feature
- `fix:` Bug fix
- `refactor:` Code restructuring
- `style:` UI/design changes
- `docs:` Documentation
- `chore:` Build/config changes

---

**Last Updated**: 2026-01-22
**Version**: 0.1.0 (Alpha)
**Status**: 🟡 In Development
