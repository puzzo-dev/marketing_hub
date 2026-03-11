# Marketing Hub: Desk vs Portal Functionality

## Overview
Marketing Hub has two distinct user interfaces serving different audiences:

---

## 1. DESK (Admin Interface)

### Location
- **Path**: `/marketing/*`
- **Code**: `marketing_hub/desk/` (Vue.js SPA)
- **Route**: Defined in `hooks.py` as `website_route_rules`

### Target Users
- Marketing Team Members
- Campaign Managers
- Social Media Managers
- Marketing Analysts
- Administrators

### Features
✅ **Currently Implemented:**
- Dashboard with analytics overview
- Campaigns management (create, edit, view)
- Social media posts management
- Omni-channel blast wizard (Email, SMS, WhatsApp, Push)
- Segments builder (visual audience targeting)
- Analytics and reporting
- Settings and configuration

🚧 **Partially Implemented:**
- Content library management
- Advanced analytics (in progress)

❌ **Not Implemented:**
- User onboarding flow
- Role-based access (agent vs admin modes)

### Technology Stack
- **Frontend**: Vue 3 + Vite
- **UI Library**: Frappe UI
- **Router**: Vue Router
- **State**: Pinia (if needed)

### Access Control
- Requires Frappe Desk user permissions
- Role-based: Marketing Manager, Marketing User, System Manager

---

## 2. PORTAL (Customer/Public Interface)

### Location
- **Templates**: `marketing_hub/templates/pages/`
- **Base Template**: `marketing_portal_base.html`
- **CSS**: `/assets/marketing_hub/css/portal.css`

### Target Users
- Customers
- Partners
- External stakeholders
- Public viewers (for some content)

### Features
✅ **Currently Implemented:**
- Onboarding page (`/onboarding`)
- Base portal template with styling

❌ **Not Implemented:**
- Customer campaign preferences
- Subscription management
- Unsubscribe pages
- Email preference center
- Newsletter archives
- Public campaign landing pages
- Social media feeds (public view)
- Event registration pages
- Content downloads portal

### Technology Stack
- **Frontend**: Jinja2 templates + vanilla JS
- **Styling**: CSS with Frappe variables
- **Framework**: Frappe Web Forms

### Access Control
- Website User role
- Guest access (for public pages)
- Customer-specific permissions

---

## Key Differences

| Aspect | Desk | Portal |
|--------|------|--------|
| **Users** | Internal marketing team | External customers/public |
| **Technology** | Vue.js SPA | Jinja2 templates |
| **Authentication** | Frappe session (desk users) | Website users / Guest |
| **Navigation** | Sidebar with full menu | Simple top nav / footer |
| **Features** | Full CRUD operations | View-only + preferences |
| **Data Access** | All campaign data | Limited to user's data |
| **Permissions** | Role-based (detailed) | Website User role |
| **API Access** | Direct frappe.call() | Public API endpoints |

---

## Recommended Portal Pages to Build

### Priority 1 (Essential)
1. **Email Preference Center** (`/preferences`)
   - Manage subscription preferences
   - Update contact information
   - Communication frequency settings

2. **Unsubscribe Pages** (`/unsubscribe`)
   - One-click unsubscribe
   - Reason collection
   - Re-subscribe option

3. **Newsletter Archives** (`/newsletters`)
   - Browse past newsletters
   - Search functionality
   - Category filtering

### Priority 2 (Important)
4. **Campaign Landing Pages** (`/campaigns/<slug>`)
   - Dynamic landing pages for campaigns
   - Lead capture forms
   - UTM tracking integration

5. **Event Registration** (`/events`)
   - Event listings
   - Registration forms
   - Calendar integration

6. **Content Library (Public)** (`/resources`)
   - Whitepapers, case studies
   - Download with lead capture
   - Categories and tags

### Priority 3 (Nice to have)
7. **Customer Dashboard** (`/portal`)
   - Campaign engagement stats
   - Email open/click history
   - Downloaded resources

8. **Referral Program** (`/refer`)
   - Referral link generation
   - Tracking referrals
   - Rewards dashboard

---

## Implementation Roadmap

### Phase 1: Email Management (2-3 days)
- [ ] Email preference center
- [ ] Unsubscribe flow
- [ ] Re-subscribe mechanism
- [ ] API endpoints for preference management

### Phase 2: Content Portal (3-4 days)
- [ ] Newsletter archives
- [ ] Campaign landing page builder
- [ ] Dynamic landing pages
- [ ] Content library (public)

### Phase 3: Customer Dashboard (4-5 days)
- [ ] Customer portal home
- [ ] Engagement statistics
- [ ] Preference management UI
- [ ] Download history

### Phase 4: Advanced Features (5-7 days)
- [ ] Event management
- [ ] Referral program
- [ ] Lead scoring visibility
- [ ] Personalized recommendations

---

## Code Organization

```
marketing_hub/
├── desk/                          # Desk (Vue.js SPA)
│   ├── src/
│   │   ├── components/           # Vue components
│   │   ├── pages/               # Desk pages
│   │   ├── router.js            # Desk routing
│   │   └── App.vue
│   └── public/
│
├── templates/
│   ├── pages/                    # Portal pages (Jinja2)
│   │   ├── onboarding.html
│   │   ├── preferences.html     # TODO
│   │   ├── unsubscribe.html     # TODO
│   │   └── newsletters.html     # TODO
│   └── marketing_portal_base.html  # Portal base template
│
├── www/
│   └── marketing/                # Desk route handler
│       └── index.py
│
└── public/
    ├── css/
    │   └── portal.css           # Portal styling
    └── js/
        └── marketing_hub.js     # Portal JS
```

---

## Next Steps

1. **Review User Requirements**
   - Which portal features are most critical?
   - What's the expected user flow?
   - Any specific compliance requirements (GDPR, CAN-SPAM)?

2. **Design Portal Pages**
   - Create wireframes for priority pages
   - Match branding/styling
   - Mobile-responsive designs

3. **Implement API Endpoints**
   - Preference management APIs
   - Unsubscribe APIs
   - Newsletter archive APIs

4. **Build Portal Templates**
   - Extend `marketing_portal_base.html`
   - Create individual page templates
   - Add portal-specific JavaScript

5. **Testing**
   - Test as guest user
   - Test as website user
   - Test permission boundaries
   - Mobile testing

---

## Questions to Consider

1. Should portal users be able to create accounts or only manage existing preferences?
2. Do we need social login for the portal?
3. What metrics should be visible to customers?
4. Should there be different portal experiences for different customer segments?
5. Do we need multi-language support for portal pages?
