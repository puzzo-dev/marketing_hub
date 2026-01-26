# Marketing Hub Portal Development Plan

## Current Architecture (Correct!)

```
marketing_hub/
├── desk/                              # Portal (Vue.js SPA) - ALL daily operations
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.vue         ✅ Done
│   │   │   ├── Campaigns.vue         ✅ Done  
│   │   │   ├── Social.vue            ✅ Done
│   │   │   ├── Analytics.vue         ✅ Done
│   │   │   ├── OmniBlast.vue         ✅ Done
│   │   │   ├── Segments.vue          ✅ Done
│   │   │   └── Content.vue           ❌ TODO
│   │   ├── components/
│   │   └── router.js
│   └── public/
│
├── marketing_hub/
│   ├── doctype/                      # Frappe DocTypes (backend)
│   │   ├── ad_account/              ✅ Done
│   │   ├── campaign/                ✅ Done (ERPNext)
│   │   ├── marketing_segment/       ✅ Done
│   │   ├── omni_blast/              ✅ Done
│   │   └── ...
│   └── workspace/                    # Frappe Desk Workspace (settings/config)
│       └── marketing_hub/
│           └── marketing_hub.json   ✅ Done
│
└── www/
    └── marketing/                    # Portal route handler
        ├── index.html               ✅ Done
        ├── index.py                 ✅ Done
        └── api.py                   ✅ Done
```

## Portal Structure (Following Helpdesk/CRM Pattern)

### Current Portal Features ✅
1. **Dashboard** - Overview metrics, charts
2. **Campaigns** - List, create, manage campaigns
3. **Social Media** - Social posts management
4. **Analytics** - Performance data
5. **Omni Blast** - Multi-channel messaging wizard
6. **Segments** - Audience targeting builder

### Missing Portal Features ❌

#### 1. Content Management (`Content.vue`)
- **Purpose**: Manage marketing assets, templates, media
- **Features**:
  - Asset library (images, videos, files)
  - Email templates
  - Social media templates
  - Content calendar view
  - Version control

#### 2. Email Builder (`EmailBuilder.vue`)
- **Purpose**: Drag-and-drop email template builder
- **Features**:
  - Visual email designer
  - Pre-built components
  - Template library
  - Mobile preview
  - Test send functionality

#### 3. Landing Pages (`LandingPages.vue`)
- **Purpose**: Create and manage landing pages
- **Features**:
  - Page builder
  - Form integration
  - A/B testing
  - Analytics integration
  - SEO settings

#### 4. Automation (`Automation.vue`)
- **Purpose**: Marketing automation workflows
- **Features**:
  - Workflow builder (drag-and-drop)
  - Trigger conditions
  - Action nodes (send email, SMS, assign lead)
  - Journey mapping
  - Performance tracking

#### 5. Lead Scoring (`LeadScoring.vue`)
- **Purpose**: Configure and monitor lead scoring
- **Features**:
  - Scoring rules builder
  - Behavior tracking
  - Score distribution chart
  - Lead qualification thresholds
  - Automated actions

#### 6. Reports (`Reports.vue`)
- **Purpose**: Custom reporting and insights
- **Features**:
  - Report builder
  - Custom metrics
  - Export functionality
  - Scheduled reports
  - Dashboard widgets

#### 7. Settings (`Settings.vue`)
- **Purpose**: Portal-level settings and preferences
- **Features**:
  - User preferences
  - Notification settings
  - Integration connections
  - API keys management
  - Team settings

#### 8. Calendar View (`Calendar.vue`)
- **Purpose**: Marketing calendar for planning
- **Features**:
  - Campaign timeline
  - Content calendar
  - Social posting schedule
  - Event planning
  - Drag-and-drop scheduling

### Portal Navigation Updates Needed

Current sidebar needs these additions:
```javascript
{
  label: 'Content',
  items: [
    { label: 'Content Library', icon: IconFolder, to: '/marketing/content' },
    { label: 'Email Builder', icon: IconMail, to: '/marketing/email-builder' },
    { label: 'Landing Pages', icon: IconLayout, to: '/marketing/landing-pages' },
    { label: 'Templates', icon: IconFileText, to: '/marketing/templates' },
  ]
},
{
  label: 'Automation',
  items: [
    { label: 'Workflows', icon: IconGitBranch, to: '/marketing/automation' },
    { label: 'Lead Scoring', icon: IconTarget, to: '/marketing/lead-scoring' },
    { label: 'Journeys', icon: IconMap, to: '/marketing/journeys' },
  ]
},
{
  label: 'Planning',
  items: [
    { label: 'Calendar', icon: IconCalendar, to: '/marketing/calendar' },
    { label: 'Reports', icon: IconBarChart, to: '/marketing/reports' },
  ]
}
```

## Desk Workspace Features (Traditional Frappe)

The workspace (`marketing_hub/workspace/marketing_hub.json`) already has:
✅ Advertising Accounts cards
✅ Analytics Data cards
✅ Campaign Execution cards
✅ Content Management cards
✅ Settings links

What's missing in workspace:
- More detailed doctype links
- Quick actions for common tasks
- Better organization of reports

## Implementation Priority

### Phase 1: Content Management (Critical) - 3-4 days
1. ✅ Content.vue - Asset library and templates
2. ✅ EmailBuilder.vue - Email template builder
3. ✅ API endpoints for content management
4. ✅ File upload/management integration

### Phase 2: Automation (High Priority) - 5-6 days
1. ✅ Automation.vue - Workflow builder
2. ✅ LeadScoring.vue - Scoring rules
3. ✅ Backend automation engine
4. ✅ Trigger handlers

### Phase 3: Planning Tools (Medium Priority) - 3-4 days
1. ✅ Calendar.vue - Marketing calendar
2. ✅ Reports.vue - Custom reporting
3. ✅ LandingPages.vue - Page builder

### Phase 4: Polish & UX (Low Priority) - 2-3 days
1. ✅ Settings.vue - Portal settings
2. ✅ Onboarding flows
3. ✅ In-app help/tooltips
4. ✅ Keyboard shortcuts

## User Roles & Permissions

Portal should support different role views:

### Marketing Manager (Full Access)
- All features available
- Team management
- Settings configuration
- Budget approval

### Marketing Executive (Standard Access)
- Create/edit campaigns
- Manage content
- View analytics
- Execute blasts

### Social Media Manager (Limited Access)
- Social posts only
- Content library (view)
- Social analytics
- Schedule posts

### Analyst (Read-Only + Reports)
- View all data
- Create reports
- Export data
- Dashboard access

## Technical Details

### API Structure (Following Helpdesk Pattern)
```python
marketing_hub/api/
├── __init__.py
├── auth.py          ✅ Session management
├── dashboard.py     ✅ Dashboard data
├── campaign.py      ❌ Campaign CRUD
├── content.py       ❌ Content management
├── automation.py    ❌ Workflow engine
├── analytics.py     ✅ Analytics data
├── segment.py       ❌ Segment management
└── settings.py      ❌ Settings API
```

### Component Structure (Following CRM Pattern)
```
desk/src/
├── components/
│   ├── Common/             # Shared components
│   ├── Layouts/            # Layout components
│   ├── Modals/             # Dialog components
│   ├── Forms/              # Form components
│   └── Widgets/            # Dashboard widgets
├── composables/            # Vue composables
│   ├── useResource.js
│   ├── usePermissions.js
│   └── useNotifications.js
├── stores/                 # Pinia stores
│   ├── user.js
│   ├── campaigns.js
│   └── segments.js
└── utils/                  # Utility functions
    ├── api.js
    ├── permissions.js
    └── formatting.js
```

## Next Steps

1. **Complete Content.vue** (highest priority from original plan)
   - Asset library interface
   - Template management
   - File upload with preview
   - Search and filtering

2. **Build Settings.vue**
   - User preferences
   - Notification settings
   - Integration management
   - API key management

3. **Add Automation.vue**
   - Visual workflow builder
   - Trigger configuration
   - Action blocks
   - Testing interface

4. **Create Calendar.vue**
   - Full-calendar integration
   - Campaign timeline
   - Content scheduling
   - Drag-and-drop

5. **Update Navigation**
   - Add all new routes
   - Organize by sections
   - Add icons
   - Permission-based visibility

Would you like me to start with Content.vue or another specific feature?
