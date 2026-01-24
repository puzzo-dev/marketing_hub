# Doctype UI Audit - Marketing Hub

**Date**: January 24, 2026  
**Status**: Comprehensive audit of all doctypes for desk and portal UI

---

## Executive Summary

- **Total Doctypes**: 20
- **Desk Forms**: 20/20 (100%) - All have standard Frappe forms
- **Vue Desk Pages**: 6/20 (30%) - Partial modern UI coverage
- **Portal Pages**: 0/20 (0%) - No public-facing portal
- **API Endpoints**: 2 files (api.py, analytics.py)

---

## Vue Desk Pages (Modern UI)

### ✅ Existing Vue Pages (6)
1. **Dashboard.vue** - Main dashboard view
2. **Campaigns.vue** - Campaign list/management
3. **NewCampaign.vue** - Campaign creation form
4. **Social.vue** - Social media management
5. **NewSocialPost.vue** - Social post creation
6. **Analytics.vue** - Analytics/reporting view

### ❌ Missing Vue Pages (14 high-priority)
1. **Content.vue** - Content management & templates
2. **ContentEditor.vue** - Rich content editor
3. **Segments.vue** - Marketing segment management
4. **OmniBlast.vue** - Omni-channel blast creation
5. **Expenses.vue** - Marketing expense tracking
6. **LeadAttribution.vue** - Lead attribution dashboard
7. **Settings.vue** - Marketing Hub settings UI
8. **Networks.vue** - Social network configuration
9. **Templates.vue** - Marketing template library
10. **Activities.vue** - Campaign activity timeline
11. **Connections.vue** - Platform connection management
12. **Accounts.vue** - Ad account management
13. **Reporting.vue** - Advanced reporting & exports
14. **Calendar.vue** - Content calendar view

---

## Doctype Breakdown

### Core Campaign Management (5 doctypes)

| Doctype | Desk Form | Vue Page | Portal | Priority |
|---------|-----------|----------|--------|----------|
| Campaign | ✅ | ✅ Campaigns.vue | ❌ | HIGH |
| Campaign Activity | ✅ | ❌ | ❌ | HIGH |
| Campaign Content | ✅ | ❌ | ❌ | HIGH |
| Omni Blast | ✅ | ❌ | ❌ | HIGH |
| Blast Type | ✅ | ❌ | ❌ | LOW |

**Assessment**: 
- ✅ Basic campaign list works
- ❌ Missing: Activity timeline, Content editor, Omni Blast UI

---

### Content Management (4 doctypes)

| Doctype | Desk Form | Vue Page | Portal | Priority |
|---------|-----------|----------|--------|----------|
| Content Asset | ✅ | ❌ | ❌ | HIGH |
| Marketing Template | ✅ | ❌ | ❌ | HIGH |
| Template Asset Item | ✅ | ❌ | ❌ | MEDIUM |
| Media Type | ✅ | ❌ | ❌ | LOW |

**Assessment**:
- ✅ Can manage via standard forms
- ❌ Missing: Rich content editor, Template library UI, Asset manager

---

### Lead Management (2 doctypes)

| Doctype | Desk Form | Vue Page | Portal | Priority |
|---------|-----------|----------|--------|----------|
| Marketing Segment | ✅ | ❌ | ❌ | HIGH |
| Attribution Model | ✅ | ❌ | ❌ | MEDIUM |

**Assessment**:
- ✅ Basic segment creation works
- ❌ Missing: Segment builder UI, Attribution dashboard

---

### Social Media (2 doctypes)

| Doctype | Desk Form | Vue Page | Portal | Priority |
|---------|-----------|----------|--------|----------|
| Social Post | ✅ | ✅ NewSocialPost.vue | ❌ | MEDIUM |
| Social Media Network | ✅ | ❌ | ❌ | LOW |

**Assessment**:
- ✅ Social post creation UI exists
- ✅ Social media calendar (Social.vue)
- ❌ Missing: Network configuration UI

---

### Accounting (2 doctypes)

| Doctype | Desk Form | Vue Page | Portal | Priority |
|---------|-----------|----------|--------|----------|
| Marketing Expense | ✅ | ❌ | ❌ | HIGH |
| Marketing Expense Category | ✅ | ❌ | ❌ | LOW |

**Assessment**:
- ✅ Can enter expenses via form
- ❌ Missing: Expense tracking dashboard, Budget vs actual view

---

### Analytics (1 doctype)

| Doctype | Desk Form | Vue Page | Portal | Priority |
|---------|-----------|----------|--------|----------|
| Analytics Daily Log | ✅ | ✅ Analytics.vue | ❌ | MEDIUM |

**Assessment**:
- ✅ Analytics view exists
- ❌ Missing: Detailed drill-down, Export functionality

---

### Platform Integrations (3 doctypes)

| Doctype | Desk Form | Vue Page | Portal | Priority |
|---------|-----------|----------|--------|----------|
| Marketing Hub Connection | ✅ | ❌ | ❌ | HIGH |
| Ad Account | ✅ | ❌ | ❌ | MEDIUM |
| Analytics Connector | ✅ | ❌ | ❌ | MEDIUM |

**Assessment**:
- ✅ Can configure via forms
- ❌ Missing: OAuth flow UI, Account linking wizard

---

### Settings (1 doctype)

| Doctype | Desk Form | Vue Page | Portal | Priority |
|---------|-----------|----------|--------|----------|
| Marketing Hub Settings | ✅ | ❌ | ❌ | HIGH |

**Assessment**:
- ✅ Standard settings form works
- ❌ Missing: Modern settings UI with tabs/sections

---

## Portal Requirements (Public-Facing)

### ❌ No Portal Pages Exist

**Required Portal Pages**:
1. **Public Campaign Tracker** - Track campaign performance (if public)
2. **Content Submission Portal** - For external contributors
3. **Lead Attribution Page** - Show attribution data to clients (agency mode)
4. **Analytics Dashboard** - Client-facing analytics (agency mode)
5. **Approval Workflow** - Content approval for agencies

**Priority**: MEDIUM (Nice to have for agency mode)

---

## API Coverage

### Existing APIs (2 files)

#### `/marketing/api.py` - Main API
- ✅ Campaign CRUD
- ✅ Social post CRUD
- ✅ Segment management
- ✅ Content management
- ✅ Omni blast execution
- ❌ Missing: Expense APIs, Settings APIs

#### `/marketing/analytics.py` - Analytics API
- ✅ Analytics data fetching
- ❌ Missing: Export APIs, Custom report generation

---

## Priority Implementation Plan

### Phase 1: Critical Missing UI (Est: 80 hours)
1. **Content.vue** (16h) - Content management dashboard
   - List all content assets
   - Filter by campaign, media type, status
   - Bulk actions (approve, archive)
   - Preview pane

2. **ContentEditor.vue** (24h) - Rich content editor
   - WYSIWYG editor (TipTap/Quill)
   - Template variable insertion
   - Asset picker
   - Multi-channel preview

3. **Segments.vue** (16h) - Segment builder UI
   - Visual filter builder
   - Segment preview (record count)
   - Test segment button
   - Save as template

4. **OmniBlast.vue** (16h) - Blast creation wizard
   - Channel selection
   - Segment selection
   - Content selection
   - Scheduling
   - Preview & send

5. **Expenses.vue** (8h) - Expense tracker
   - Expense list with filters
   - Budget vs actual chart
   - Category breakdown
   - Quick add expense

### Phase 2: Enhanced Features (Est: 60 hours)
6. **Activities.vue** (12h) - Activity timeline
   - Gantt chart view
   - Calendar view
   - Drag-drop scheduling
   - Status workflow

7. **Templates.vue** (12h) - Template library
   - Template cards with preview
   - Filter by channel, category
   - Clone/edit buttons
   - Usage statistics

8. **Settings.vue** (12h) - Settings UI
   - Tab-based navigation
   - API key management
   - Email/SMS/WhatsApp config
   - Platform connections

9. **LeadAttribution.vue** (12h) - Attribution dashboard
   - Attribution funnel
   - Touch point timeline
   - Model comparison
   - Source breakdown

10. **Connections.vue** (12h) - Platform connections
    - OAuth wizard
    - Test connection
    - Sync status
    - Account picker

### Phase 3: Advanced Features (Est: 40 hours)
11. **Calendar.vue** (12h) - Content calendar
    - Month/week/day views
    - Drag-drop posts
    - Multi-channel legend
    - Quick edit popup

12. **Reporting.vue** (16h) - Advanced reports
    - Report builder UI
    - Custom metrics
    - Export to PDF/Excel
    - Scheduled reports

13. **Networks.vue** (8h) - Network configuration
    - Network cards
    - Enable/disable toggle
    - OAuth setup wizard
    - Rate limits display

14. **Accounts.vue** (4h) - Ad accounts
    - Account list
    - Link new account
    - Spend summary
    - Active campaigns

### Phase 4: Portal Pages (Est: 60 hours - OPTIONAL)
15. **Portal Campaign Tracker** (16h)
16. **Portal Content Submission** (16h)
17. **Portal Analytics Dashboard** (16h)
18. **Portal Approval Workflow** (12h)

---

## Technical Debt

### Current Issues
1. **Mixed UI Paradigm**: 70% standard forms, 30% Vue pages
2. **No Portal**: Agency features can't be client-facing
3. **Limited API**: Some features only accessible via desk
4. **No Real-time Updates**: No websockets for live data

### Recommendations
1. **Prioritize Content & Omni Blast UIs** - Core functionality gaps
2. **Complete Vue Migration** - For consistency
3. **Add Portal Auth** - For agency mode
4. **Implement WebSockets** - For real-time analytics

---

## Implementation Approach

### For Desk UI (Vue Pages)
```javascript
// Use Frappe UI library (already installed)
import { createResource, FeatherIcon, Button } from 'frappe-ui'

// Standard pattern
export default {
  name: 'ContentEditor',
  components: { FeatherIcon, Button },
  setup() {
    const content = createResource({
      url: '/api/method/marketing_hub.api.get_content',
      auto: true
    })
    return { content }
  }
}
```

### For Portal Pages
```python
# www/marketing/portal/content.py
import frappe
from frappe import _

def get_context(context):
    context.no_cache = 1
    # Check permissions
    if not frappe.has_website_permission("Content Asset"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    # Return data
    context.content_items = frappe.get_all("Content Asset",
        filters={"owner": frappe.session.user},
        fields=["name", "title", "status"]
    )
```

---

## Next Steps

1. ✅ Complete SMS blast implementation (DONE)
2. 🔄 Create Phase 1 Vue pages (IN PROGRESS)
   - Start with Content.vue
   - Then Segments.vue
   - Then OmniBlast.vue
3. ⏳ Add missing APIs for new UIs
4. ⏳ Implement portal pages (agency mode)

---

**Total Effort Estimate**: 240 hours (6 weeks @ 40h/week)
- Phase 1 (Critical): 80 hours
- Phase 2 (Enhanced): 60 hours
- Phase 3 (Advanced): 40 hours
- Phase 4 (Portal): 60 hours

**Recommended Priority**: Phase 1 → Phase 2 → Phase 3 → Phase 4 (optional)
