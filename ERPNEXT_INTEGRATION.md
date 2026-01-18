# Marketing Hub - ERPNext Integration Links

## Direct ERPNext Doctype Extensions

### 1. **Campaign** (ERPNext Core Doctype)
Custom fields added via fixtures:

#### Campaign-channels_used
- **Type**: MultiSelect
- **Label**: Channels
- **Options**: 18 marketing channels (Email, WhatsApp, SMS, Push Notification, Google Ads, Meta Ads, TikTok Ads, Twitter/X Ads, Reddit Ads, LinkedIn Ads, Trade Show, TV, Radio, Telecalling, Outdoor, Print, Event, Omni-Channel)
- **Purpose**: Track which channels are used in the campaign
- **Used in**:
  - `utils/attribution_engine.py` - Determines primary channel for lead attribution
  - `public/js/campaign.js` - Campaign form enhancements

#### Campaign-is_omni_campaign
- **Type**: Check
- **Label**: Omni-Channel Campaign
- **Purpose**: Flag campaigns that use multiple channels simultaneously
- **Used in**:
  - `public/js/campaign.js` - Shows info message when checked

#### Campaign-client
- **Type**: Link → Customer
- **Label**: Client (Agency Mode)
- **Purpose**: Link campaign to customer when operating in agency mode
- **Used in**:
  - `utils/agency_mode.py` - Client subscription validation, limits enforcement
  - `public/js/campaign.js` - Toggle visibility based on agency mode

#### Campaign-project
- **Type**: Link → Project
- **Label**: Project
- **Purpose**: Link campaigns to ERPNext projects for budget tracking
- **Used in**:
  - Campaign form for project-based campaign management

#### Campaign-roas
- **Type**: Float (Precision: 2)
- **Label**: ROAS (Return on Ad Spend)
- **Purpose**: Store calculated return on ad spend
- **Used in**:
  - `public/js/campaign.js` - Calculate ROAS button
  - `utils/analytics_sync.py` - Auto-calculated from analytics data

### 2. **Lead** (ERPNext Core Doctype)
Custom fields added via fixtures:

#### Lead-utm_campaign
- **Type**: Data
- **Label**: UTM Campaign
- **Purpose**: Store campaign tracking parameter from URL
- **Used in**:
  - `utils/attribution_engine.py` - Primary attribution source (highest priority)
  - `utils/crm_integration.py` - Synced to CRM Lead

#### Lead-utm_source
- **Type**: Data
- **Label**: UTM Source
- **Purpose**: Store traffic source from URL (e.g., "google", "facebook")
- **Used in**:
  - `utils/attribution_engine.py` - Attribution logic
  - `utils/crm_integration.py` - Synced to CRM Lead

#### Lead-utm_medium
- **Type**: Data
- **Label**: UTM Medium
- **Purpose**: Store marketing medium from URL (e.g., "cpc", "email")
- **Used in**:
  - `utils/attribution_engine.py` - Attribution logic
  - `utils/crm_integration.py` - Synced to CRM Lead

## ERPNext Doctype References (No Modifications)

### 3. **Customer** (Read-Only Access)
- **Used in**:
  - `utils/omni_blast.py` - Segment recipient fetching
  - `utils/agency_mode.py` - Client management, subscription tracking
  - Campaign-client field (Link field)

### 4. **Project** (Read-Only Access)
- **Used in**:
  - Campaign-project field (Link field)
  - Budget tracking and campaign organization

### 5. **Communication** (Indirect)
- **Used in**:
  - Email blasts via `frappe.sendmail()` create Communication records
  - `utils/crm_integration.py` - Counts email communications for engagement scoring

### 6. **Email Queue** (Indirect)
- **Used in**:
  - `utils/omni_blast.py` - Email blast execution via Frappe's email system

## ERPNext Module Integration

### CRM Module
Marketing Hub extends ERPNext's CRM capabilities:

1. **Lead Management**
   - Auto-attribution of lead sources
   - UTM parameter tracking
   - Campaign association
   - Sync with Frappe CRM app (if installed)

2. **Campaign Tracking**
   - Multi-channel campaign management
   - ROAS calculation
   - Client/project association

3. **Reports Integration**
   - Marketing Hub data appears in Campaign Efficiency report
   - Lead Details report includes UTM data
   - Custom analytics available via Marketing Hub workspace

### Selling Module
Indirect integration through:

1. **Customer Doctype**
   - Segment building for campaigns
   - Agency client management
   - Blast recipient targeting

2. **Sales Order** (Future)
   - Revenue tracking for ROAS calculation
   - Conversion metrics from marketing campaigns

### Projects Module
Integration via:

1. **Project Doctype**
   - Campaign-project linking
   - Budget allocation
   - Timeline tracking

### HR Module (Future Integration Points)
Potential integration for:

1. **Employee** - Marketing team assignment
2. **Department** - Marketing department campaigns
3. **Leave Management** - Campaign planning around team availability

## Event Hooks on ERPNext Doctypes

### hooks.py Configuration
```python
doc_events = {
    "Lead": {
        "on_update": "marketing_hub.utils.attribution_engine.get_real_lead_source"
    }
}
```

This hook:
- Triggers on every Lead save/update
- Checks for UTM parameters
- Applies attribution logic
- Tags lead_source with channel-campaign format
- Syncs to CRM if installed

## Data Flow: ERPNext ↔ Marketing Hub

### Inbound (ERPNext → Marketing Hub)

1. **Lead Creation**
   ```
   Lead (ERPNext) → Attribution Engine → Campaign Link → Analytics
   ```

2. **Campaign Data**
   ```
   Campaign (ERPNext + Custom Fields) → Campaign Activity → Blast Execution
   ```

3. **Customer Data**
   ```
   Customer (ERPNext) → Marketing Segment → Blast Recipients
   ```

4. **Project Budget**
   ```
   Project (ERPNext) → Campaign Budget → ROAS Calculation
   ```

### Outbound (Marketing Hub → ERPNext)

1. **Lead Attribution**
   ```
   UTM Parameters → Attribution Engine → Lead.lead_source Update
   ```

2. **Campaign Metrics**
   ```
   Analytics Sync → Campaign.roas Update
   ```

3. **Revenue Tracking** (Future)
   ```
   Sales Order → Campaign Revenue → ROAS Calculation
   ```

## Permission Model Integration

### ERPNext Roles Used

1. **System Manager**
   - Full access to Marketing Hub
   - Configure OAuth, Ad Accounts
   - Manage agency settings

2. **Sales Manager**
   - Manage campaigns
   - View all analytics
   - Execute blasts
   - Assign campaigns to team

3. **Sales User**
   - Create/edit assigned campaigns
   - View campaign performance
   - Execute approved blasts

4. **Customer** (Portal)
   - View campaign results (agency mode)
   - Read-only access to their campaigns

### Custom Permissions (To Be Configured)

1. **Marketing Manager** (New Role)
   - Full Marketing Hub access
   - Manage all campaigns
   - Configure connectors
   - View all analytics

2. **Marketing Executive** (New Role)
   - Create/edit campaigns
   - Execute blasts
   - View analytics for assigned campaigns

3. **Marketing Analyst** (New Role)
   - Read-only access to all campaigns
   - Full access to analytics and reports
   - Export capabilities

## Database-Level Integration

### Foreign Key Relationships

```
Marketing Hub DocTypes → ERPNext Core
├── Campaign Activity.parent → Campaign.name
├── Marketing Segment → Customer (filter)
├── Marketing Segment → Lead (filter)
├── Analytics Daily Log.campaign → Campaign.name
├── Social Post.campaign → Campaign.name
├── Client Subscription.client → Customer.name
├── Ad Account.company → Company.name
└── Campaign.project → Project.name
```

### Computed Fields

- **Campaign.roas**: Calculated from Analytics Daily Log + Sales Order revenue
- **Lead.lead_source**: Computed from UTM parameters + Campaign
- **Marketing Segment.segment_size**: Computed from Customer/Lead filters

## API Integration Points

### Whitelisted Methods (ERPNext Accessible)

1. `marketing_hub.utils.attribution_engine.calculate_campaign_attribution`
   - Input: Campaign name
   - Output: Lead count, conversions, channels breakdown

2. `marketing_hub.utils.analytics_sync.sync_connector`
   - Input: Analytics Connector name
   - Output: Sync status, campaign count

3. `marketing_hub.utils.agency_mode.get_agency_dashboard_data`
   - Input: None (current user context)
   - Output: Agency metrics, client subscriptions

4. `marketing_hub.utils.crm_integration.get_campaign_performance_with_crm`
   - Input: Campaign name
   - Output: Full funnel metrics (leads → deals → revenue)

### ERPNext APIs Used by Marketing Hub

1. **frappe.sendmail()** - Email blast execution
2. **frappe.get_doc("Lead")** - Lead retrieval and update
3. **frappe.get_doc("Campaign")** - Campaign data access
4. **frappe.get_all("Customer")** - Segment building
5. **frappe.db.get_value()** - Quick field lookups
6. **frappe.enqueue()** - Background job processing

## Workspace Integration

Marketing Hub will have its own workspace that:

1. **Links to ERPNext Doctypes**
   - Campaign (with custom fields)
   - Lead (filtered for marketing)
   - Customer (agency clients)
   - Project (campaign projects)

2. **Provides Quick Actions**
   - Create Campaign
   - Execute Blast
   - Sync Analytics
   - View Dashboard

3. **Shows Reports**
   - Campaign Performance
   - ROAS Analysis
   - Channel Effectiveness
   - Lead Attribution Report

4. **Role-Based Access**
   - Full access: System Manager, Marketing Manager
   - Campaign management: Marketing Executive, Sales Manager
   - Analytics only: Marketing Analyst
   - Limited view: Sales User, Employee

## Future ERPNext Integration Opportunities

1. **Sales Order Integration**
   - Link sales orders to campaigns
   - Auto-calculate revenue ROAS
   - Track customer lifetime value by campaign

2. **Payment Entry Integration**
   - Track actual revenue vs. ad spend
   - Payment terms impact on ROAS
   - Client billing in agency mode

3. **Stock Item Integration**
   - Product-specific campaigns
   - Inventory impact from campaigns
   - SKU-level ROAS

4. **Territory Integration**
   - Geographic campaign targeting
   - Territory-wise performance
   - Regional campaign management

5. **Employee Integration**
   - Marketing team assignment
   - Campaign ownership
   - Performance tracking by marketer

6. **Budget Integration**
   - Campaign budget allocation
   - Budget vs. actual spend tracking
   - Approval workflows for budget overruns

---

**Summary**: Marketing Hub is deeply integrated with ERPNext while maintaining clean separation. It extends core CRM functionality (Campaign, Lead) with custom fields, references Customer/Project doctypes, and provides event hooks for automatic attribution. The integration is designed to be optional - core functionality works standalone, but leverages ERPNext data when available.
