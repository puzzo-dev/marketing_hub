# Marketing Hub - Installation & Setup Guide

**Version**: 1.0  
**Date**: January 24, 2026  
**For**: Frappe Framework v15+, ERPNext v15+

---

## Prerequisites

### System Requirements
- Frappe Framework v15 or higher
- ERPNext v15 or higher (required for accounting integration)
- Python 3.10+
- Node.js 18+
- MariaDB 10.6+ or PostgreSQL 14+

### Optional Dependencies
- **frappe_whatsapp app** - For WhatsApp blast functionality
- **CRM app** - For enhanced lead attribution and tracking

---

## Installation

### 1. Get the App

```bash
cd ~/frappe-bench
bench get-app https://github.com/your-org/marketing_hub --branch develop
```

### 2. Install on Site

```bash
bench --site your-site.local install-app marketing_hub
```

### 3. Run Migrations

```bash
bench --site your-site.local migrate
```

---

## Configuration

### Marketing Hub Settings

Navigate to: **Desk → Marketing Settings → Marketing Hub Settings**

#### Core Settings
- **Company**: Select default company
- **Default Currency**: Set for marketing expenses
- **Enable Agency Mode**: Toggle for multi-client operations

#### Email Configuration
Marketing Hub uses **ERPNext Email Settings**:
- Navigate to: **Setup → Email → Email Account**
- Configure SMTP server for campaign emails
- Marketing Hub will use Frappe's Email Queue system
- No additional email configuration needed in Marketing Hub

#### WhatsApp Configuration
Marketing Hub integrates with **frappe_whatsapp app**:

1. **Install frappe_whatsapp**:
   ```bash
   bench get-app https://github.com/frappe/frappe_whatsapp
   bench --site your-site.local install-app frappe_whatsapp
   ```

2. **Configure WhatsApp Account**:
   - Navigate to: **Setup → WhatsApp Account**
   - Add WhatsApp Business API credentials
   - Test connection

3. **Enable in Marketing Hub Settings**:
   - Check "Enable WhatsApp Blasts"
   - Select WhatsApp Account

#### SMS Configuration
Marketing Hub uses **ERPNext SMS Settings**:
- Navigate to: **Setup → SMS Settings**
- Configure SMS gateway (Twilio, AWS SNS, etc.)
- Marketing Hub will use this for SMS blasts
- No additional SMS configuration needed

#### Accounting Settings
- **Enable GL Entry**: Auto-create GL entries for marketing expenses
- **Default Expense Account**: Default marketing expense account
- **Default Cost Center**: Default cost center for campaigns
- **Default Payable Account**: Account for unpaid expenses
- **Enable Budget Alerts**: Warn when campaigns exceed budget

#### Social Media Settings
- **Auto Post Interval**: Minutes between scheduled post checks
- **Default Post Status**: Draft or Scheduled for new posts
- **Enable Platform Validation**: Validate content length per platform

---

## Initial Setup

### 1. Create Chart of Accounts
Marketing Hub automatically creates marketing accounts:

```bash
# This runs automatically during first install
# To run manually:
bench --site your-site.local execute marketing_hub.patches.setup_marketing_chart_of_accounts.execute
```

**Created Accounts** (under Indirect Expenses):
- Marketing Expenses (Group)
  - Advertising Expense
  - Content Creation Expense
  - Social Media Marketing
  - Email Marketing
  - SEO and SEM
  - Events and Trade Shows
  - Print Media
  - Influencer Marketing
  - Agency and Consulting Fees
  - Marketing Software and Tools
  - Out of Home Advertising
  - Public Relations
  - Market Research
  - Other Marketing Expenses

### 2. Configure Social Media Networks

Navigate to: **Marketing Hub → Social Media Network**

**Default Networks** (auto-created):
- Facebook
- Instagram
- Twitter/X
- LinkedIn
- TikTok
- YouTube
- Pinterest
- Google Ads
- Meta Ads
- LinkedIn Ads

**Add OAuth Credentials**:
1. Open each network
2. Add Client ID and Client Secret
3. Configure OAuth scopes
4. Test connection

### 3. Create Marketing Segments

Navigate to: **Marketing Hub → Marketing Segment**

**Example Segment**:
```json
{
  "filters": [
    ["Lead", "status", "=", "Open"],
    ["Lead", "source", "=", "Website"]
  ]
}
```

### 4. Setup Marketing Templates

Navigate to: **Marketing Hub → Marketing Template**

**Create templates for**:
- Email campaigns
- WhatsApp messages
- Social media posts
- SMS messages

**Use variables**:
- `{customer_name}`
- `{product_name}`
- `{campaign_name}`
- `{custom_field}`

---

## Frontend Portal Setup

### Enable Vue Portal

Marketing Hub includes a Vue.js portal at `/marketing`

**Access**: `https://your-site.local/marketing`

**Configure**:
1. Navigate to Marketing Hub Settings
2. Enable "Vue Portal"
3. Set session timeout (minutes)

### Development Setup

```bash
cd apps/marketing_hub/desk
npm install
npm run dev
```

**Production Build**:
```bash
cd apps/marketing_hub/desk
npm run build
bench --site your-site.local clear-cache
```

---

## Integration with ERPNext

### CRM Integration

Marketing Hub automatically integrates with ERPNext CRM:

**Lead Attribution**:
- UTM parameters captured on lead creation
- Campaign attribution via hooks
- Auto-sync to CRM app (if installed)

**Custom Fields** (auto-created on Lead):
- utm_campaign
- utm_source
- utm_medium
- utm_content
- utm_term

### Accounting Integration

**GL Entry Creation**:
- Marketing Expense submit → GL entries created
- Debit: Marketing Expense Account
- Credit: Payment Account or Payable Account

**Budget Tracking**:
- Campaign.budget_amount (custom field)
- Campaign.total_spent (auto-calculated)
- Alerts when budget exceeded

**Reports**:
- Marketing Expense Analysis
- Campaign Budget vs Actual
- ROAS Analysis
- Campaign Performance

### Project Integration

Link campaigns to projects:
- Track marketing spend per project
- Cost center allocation
- Project-wise ROI analysis

---

## Platform Integrations (Optional)

### Google Ads Integration

1. **Create Google Cloud Project**:
   - Enable Google Ads API
   - Create OAuth 2.0 credentials
   - Add to Social Media Network

2. **Configure in Marketing Hub**:
   - Navigate to Ad Account
   - Select platform: Google Ads
   - Add Client ID and Secret
   - Authorize account

3. **Sync Analytics**:
   - Navigate to Analytics Connector
   - Select Google Ads account
   - Set sync frequency
   - Run initial sync

### Meta Ads Integration

1. **Create Meta App**:
   - Facebook Developer Portal
   - Create business app
   - Add Marketing API permissions

2. **Configure in Marketing Hub**:
   - Navigate to Ad Account
   - Select platform: Meta Ads
   - Add App ID and Secret
   - Authorize account

### LinkedIn Ads Integration

1. **Create LinkedIn App**:
   - LinkedIn Developer Portal
   - Request Marketing API access
   - Get Client ID and Secret

2. **Configure in Marketing Hub**:
   - Navigate to Ad Account
   - Select platform: LinkedIn Ads
   - Add credentials
   - Authorize account

---

## Permissions

### Roles

**Marketing Manager**:
- Full access to all marketing features
- Create, edit, delete campaigns
- Approve expenses
- View all reports

**Marketing User**:
- Create and edit campaigns
- Create content and posts
- View assigned campaigns only
- Cannot approve expenses

**Accounts Manager**:
- View marketing expenses
- View financial reports
- No campaign access

### Agency Mode

Enable for multi-client operations:

1. **Enable in Settings**:
   - Marketing Hub Settings → Enable Agency Mode

2. **Add Client Field to Campaign**:
   - Custom field auto-created
   - Link to Customer

3. **Row-Level Security**:
   - Users see only their client's campaigns
   - Marketing Manager sees all

---

## Scheduled Jobs

Marketing Hub runs automated tasks:

**Daily** (3:00 AM):
- `marketing_hub.utils.analytics_sync.sync_all_connectors`
  - Syncs analytics from all active connectors

**Every Minute**:
- `marketing_hub.utils.auto_post.publish_scheduled_posts`
  - Publishes posts scheduled for current time

**Configure**:
```python
# In hooks.py
scheduler_events = {
    "daily": ["marketing_hub.utils.analytics_sync.sync_all_connectors"],
    "all": ["marketing_hub.utils.auto_post.publish_scheduled_posts"]
}
```

---

## Troubleshooting

### Issue: Marketing accounts not created

**Solution**:
```bash
bench --site your-site.local execute marketing_hub.patches.setup_marketing_chart_of_accounts.execute
```

### Issue: Email blasts not sending

**Check**:
1. ERPNext Email Account configured
2. SMTP credentials valid
3. Email Queue running: `bench --site your-site.local run-scheduler`

### Issue: WhatsApp blasts failing

**Check**:
1. frappe_whatsapp app installed
2. WhatsApp Account configured in frappe_whatsapp
3. Marketing Hub Settings → WhatsApp Account selected
4. Test connection in WhatsApp Account

### Issue: GL entries not created

**Check**:
1. Marketing Hub Settings → Enable GL Entry = checked
2. Marketing Expense → Expense Account is not a group
3. Marketing Expense → Payment Account is Bank/Cash type
4. Check error log: Accounting → Error Log

### Issue: Budget alerts not showing

**Check**:
1. Marketing Hub Settings → Enable Budget Alerts = checked
2. Campaign → Budget Amount is set
3. Marketing Expense → Campaign is linked

### Issue: Frontend portal not loading

**Check**:
1. Vue build exists: `apps/marketing_hub/desk/dist/`
2. Clear cache: `bench --site your-site.local clear-cache`
3. Rebuild: `cd apps/marketing_hub/desk && npm run build`

---

## Upgrading

### From Previous Versions

```bash
cd ~/frappe-bench
bench update --app marketing_hub
bench --site your-site.local migrate
bench --site your-site.local clear-cache
```

### Breaking Changes

**v1.0 (Jan 24, 2026)**:
- Social Post.platform changed from Select to Link (Social Media Network)
- Ad Account.platform changed to Link
- Omni Blast system introduced

**Migration**:
- Automatic migration patch included
- Existing data preserved
- Default networks auto-created

---

## Next Steps

1. **Configure Settings**: Marketing Hub Settings
2. **Setup Integrations**: Email, WhatsApp, SMS via ERPNext
3. **Create Segments**: Marketing Segment
4. **Add Templates**: Marketing Template
5. **Setup Campaigns**: Campaign doctype
6. **Create Content**: Content Asset library
7. **Configure OAuth**: Social Media Network (optional)

---

## Support

- **Documentation**: `/apps/marketing_hub/README.md`
- **Accounting Guide**: `/apps/marketing_hub/ACCOUNTING_IMPLEMENTATION.md`
- **Content Guide**: `/apps/marketing_hub/CONTENT_MANAGEMENT_GUIDE.md`
- **Permissions**: `/apps/marketing_hub/WORKSPACE_PERMISSIONS.md`

---

**Installation Complete** ✅

Your Marketing Hub is ready to use with ERPNext email settings, SMS settings, and optional frappe_whatsapp integration.
