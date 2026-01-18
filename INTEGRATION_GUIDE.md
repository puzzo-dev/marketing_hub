# Marketing Hub - Integration Guide

## Dependencies

Marketing Hub leverages existing Frappe ecosystem apps:

### Required Dependencies
- **frappe_whatsapp**: WhatsApp blast functionality
  - Automatically handles bulk messaging
  - Template management
  - Delivery tracking

### Optional Integrations
- **CRM**: Enhanced lead tracking and conversion metrics
  - Auto-sync marketing leads to CRM
  - Track deal conversions
  - Calculate engagement scores
  - Link marketing activities to CRM timeline

## OAuth Integration

Marketing Hub uses **Frappe's Social Login Key** doctype for platform authentication.

### Supported Platforms

#### Advertising Platforms
1. **Google Ads**
   - Campaign management
   - Performance metrics sync
   - Conversion tracking

2. **Meta Ads (Facebook/Instagram)**
   - Campaign insights
   - Audience management
   - Creative performance

3. **LinkedIn Ads**
   - Sponsored content tracking
   - Lead gen forms integration
   - ABM campaign metrics

4. **TikTok Ads**
   - Video ad performance
   - Creator marketplace tracking

5. **Twitter/X Ads**
   - Promoted content metrics
   - Engagement tracking

### Setup OAuth for Platforms

#### 1. Configure Social Login Key (via Desk)
Navigate to: **Setup > Integrations > Social Login Key**

Create a new entry for each platform:
- **Provider Name**: Match exactly (e.g., "Google Ads", "Meta Ads")
- **Client ID**: From platform developer console
- **Client Secret**: From platform developer console
- **Enable Social Login**: ❌ Uncheck (we're using it for API, not login)
- **Access Token URL**: Platform-specific token endpoint
- **Authorize URL**: Platform OAuth URL

#### 2. Or Use Ad Account Doctype
Marketing Hub can also store credentials directly:
- Navigate to **Marketing Hub > Ad Account**
- Platform-specific credentials
- Auto-refresh tokens
- Multi-account support per platform

#### 3. Initiate OAuth Flow (via Code)
```python
from marketing_hub.utils.oauth_integration import initiate_oauth_flow

# Start OAuth flow
result = initiate_oauth_flow("Google Ads", company="Your Company")
# Returns authorization URL
# Redirect user to result['auth_url']
```

#### 4. Handle Callback
The callback is automatically handled at:
```
/api/method/marketing_hub.utils.oauth_integration.oauth_callback
```

This creates an **Ad Account** record with access token and refresh token.

### Platform-Specific Setup

#### Google Ads
**Developer Console**: https://console.cloud.google.com/
1. Create OAuth 2.0 credentials
2. Add redirect URI: `{your_site}/api/method/marketing_hub.utils.oauth_integration.oauth_callback`
3. Enable Google Ads API
4. Get Developer Token from Google Ads account

**Required Fields in Ad Account:**
- `account_id`: Customer ID (e.g., "123-456-7890")
- `developer_token`: From Google Ads Manager account

#### Meta Ads (Facebook)
**Developer Console**: https://developers.facebook.com/
1. Create a new app
2. Add "Marketing API" product
3. Configure OAuth redirect URI
4. Get App ID and App Secret

**Required Fields in Ad Account:**
- `account_id`: Ad Account ID (e.g., "act_123456789")
- Note: Prefix with "act_" if not already

#### LinkedIn Ads
**Developer Console**: https://www.linkedin.com/developers/
1. Create a new app
2. Request access to Marketing Developer Platform
3. Add redirect URI
4. Get Client ID and Client Secret

**Required Fields in Ad Account:**
- `account_id`: Ad Account URN or ID

#### TikTok Ads
**Developer Console**: https://business-api.tiktok.com/
1. Create TikTok Business account
2. Register for Business API access
3. Create an app
4. Get App ID and Secret

**Required Fields in Ad Account:**
- `account_id`: Advertiser ID

#### Twitter/X Ads
**Developer Console**: https://developer.twitter.com/
1. Apply for Elevated access
2. Create OAuth 2.0 app
3. Get Client ID and Client Secret

**Required Fields in Ad Account:**
- `account_id`: Account ID from Ads Manager

## WhatsApp Integration (frappe_whatsapp)

Marketing Hub uses frappe_whatsapp app for all WhatsApp functionality.

### Setup
1. **Install frappe_whatsapp** (already required dependency)
   ```bash
   bench get-app frappe_whatsapp
   bench --site your-site install-app frappe_whatsapp
   ```

2. **Configure WhatsApp Account**
   - Navigate to: **Setup > WhatsApp Settings**
   - Add WhatsApp Account with Business API credentials
   - Set as default outgoing account

3. **Create WhatsApp Templates**
   - Navigate to: **WhatsApp Templates**
   - Create message templates matching campaign needs
   - Get template approval from Meta

### Usage in Marketing Hub
WhatsApp blasts automatically use frappe_whatsapp:

```python
from marketing_hub.utils.omni_blast import execute_blast

# Execute WhatsApp blast
activity = frappe.get_doc("Campaign Activity", "ACTIVITY-001")
activity.channel = "WhatsApp"
activity.segment = "TARGET-SEGMENT"
result = execute_blast(activity)

# Creates Bulk WhatsApp Message automatically
# Links to campaign for tracking
```

## CRM Integration

### Auto-Sync Leads
When a lead is created/updated with marketing attribution:
1. Attribution engine tags the lead
2. Lead is automatically synced to CRM Lead (if CRM installed)
3. UTM data and campaign info transferred
4. CRM activity created linking to campaign

### Track Conversions
```python
from marketing_hub.utils.crm_integration import get_campaign_performance_with_crm

# Get full funnel metrics
performance = get_campaign_performance_with_crm("CAMPAIGN-001")
# Returns:
# - leads: Total leads generated
# - crm_leads: Synced to CRM
# - deals: Converted to deals
# - won_deals: Closed won
# - total_revenue: Sum of won deal values
# - avg_deal_size: Average revenue per won deal
# - conversion_to_deal: Lead → Deal %
# - win_rate: Deal → Won %
```

### Link WhatsApp Messages
```python
from marketing_hub.utils.crm_integration import link_whatsapp_to_campaign

# Link WhatsApp conversation to campaign
link_whatsapp_to_campaign("WA-MSG-001", "CAMPAIGN-001")
# Creates CRM activity if lead exists in CRM
```

### Engagement Scoring
```python
from marketing_hub.utils.crm_integration import get_lead_engagement_score

# Calculate lead engagement
score = get_lead_engagement_score("LEAD-001")
# Considers: emails, calls, WhatsApp, activities
# Higher score = more engaged lead
```

## API Usage

### Make Authenticated API Requests
```python
from marketing_hub.utils.oauth_integration import make_api_request

# Example: Fetch Google Ads campaigns
campaigns = make_api_request(
    platform="Google Ads",
    endpoint="customers/123456789/campaigns",
    method="GET",
    company="Your Company"
)

# Example: Create Meta Ad Set
ad_set = make_api_request(
    platform="Meta Ads",
    endpoint="act_123456789/adsets",
    method="POST",
    data={
        "name": "My Ad Set",
        "campaign_id": "123456",
        "daily_budget": 5000,
        "billing_event": "IMPRESSIONS",
        "optimization_goal": "REACH",
        "targeting": {...}
    },
    company="Your Company"
)
```

### Token Refresh
Tokens are automatically refreshed when expired:
```python
from marketing_hub.utils.oauth_integration import refresh_access_token

# Manual refresh if needed
success = refresh_access_token("AD-ACCOUNT-001")
```

## Analytics Sync Workflow

### Automated Daily Sync
Scheduler runs daily to sync all active Analytics Connectors:

```python
# In hooks.py
scheduler_events = {
    "daily": [
        "marketing_hub.utils.analytics_sync.sync_all_connectors"
    ]
}
```

### Manual Sync
```python
from marketing_hub.utils.analytics_sync import sync_connector

# Sync specific connector
result = sync_connector("ANALYTICS-CONNECTOR-001")
# Returns: {"status": "Success", "synced_campaigns": 5}
```

### Analytics Flow
1. Connector fetches campaigns from platform API (OAuth authenticated)
2. For each campaign, fetch daily metrics
3. Create/update Analytics Daily Log
4. Calculate derived metrics (CTR, CPC, ROAS)
5. Aggregate for campaign-level reporting

## Testing Integrations

### Test OAuth Flow
```python
# From bench console
from marketing_hub.utils.oauth_integration import initiate_oauth_flow

result = initiate_oauth_flow("Google Ads", company="Test Company")
print(result['auth_url'])
# Visit URL in browser, complete OAuth
# Check if Ad Account was created
```

### Test WhatsApp Integration
```python
# From bench console
from marketing_hub.utils.omni_blast import _execute_whatsapp_blast

activity = frappe.get_doc("Campaign Activity", {
    "parent": "TEST-CAMPAIGN",
    "segment": "TEST-SEGMENT",
    "channel": "WhatsApp"
})
result = _execute_whatsapp_blast(activity)
print(result)
# Check Bulk WhatsApp Message and WhatsApp Message docs created
```

### Test CRM Sync
```python
# From bench console
from marketing_hub.utils.crm_integration import sync_lead_with_crm

lead_name = "LEAD-00001"
marketing_data = {
    "campaign": "TEST-CAMPAIGN",
    "utm_source": "google",
    "utm_medium": "cpc"
}
crm_lead = sync_lead_with_crm(lead_name, marketing_data)
print(f"CRM Lead created: {crm_lead}")
# Check CRM Lead doctype for new record
```

### Test Analytics Sync
```python
# From bench console
from marketing_hub.utils.analytics_sync import sync_connector

result = sync_connector("YOUR-CONNECTOR-NAME")
print(result)
# Check Analytics Daily Log for new entries
```

## Troubleshooting

### OAuth Issues
**Problem**: "No credentials found"
**Solution**:
1. Check Social Login Key exists for platform
2. Or ensure Ad Account exists and is Active
3. Verify access token hasn't expired (auto-refresh should handle)

**Problem**: "Token refresh failed"
**Solution**:
1. Check refresh token is stored in Ad Account
2. Verify platform OAuth config is correct
3. Re-authorize if refresh token is invalid

### WhatsApp Issues
**Problem**: "frappe_whatsapp app not installed"
**Solution**:
```bash
bench get-app frappe_whatsapp
bench --site your-site install-app frappe_whatsapp
```

**Problem**: "No default WhatsApp account configured"
**Solution**:
1. Navigate to WhatsApp Settings
2. Configure at least one WhatsApp Account
3. Set it as default outgoing account

### CRM Integration Issues
**Problem**: CRM sync not working
**Solution**:
1. Check if CRM app is installed: `bench list-apps`
2. Verify CRM Lead doctype exists
3. Check error logs: `bench --site your-site logs`

### Analytics Sync Issues
**Problem**: Sync returns "Error"
**Solution**:
1. Check Analytics Connector has correct account_id
2. Verify OAuth credentials are valid
3. Check platform API rate limits
4. Review error logs for specific API errors

## Best Practices

### 1. Security
- Never commit OAuth credentials to git
- Use environment variables for sensitive tokens
- Rotate access tokens regularly
- Restrict API permissions to minimum required

### 2. Rate Limiting
- Respect platform API rate limits
- Use queue for bulk operations
- Implement exponential backoff for retries

### 3. Data Privacy
- Store only necessary user data
- Implement data retention policies
- Provide opt-out mechanisms
- Comply with GDPR/CCPA

### 4. Monitoring
- Monitor OAuth token expiry
- Track API call failures
- Set up alerts for sync failures
- Review error logs regularly

## Migration from Stubs

If you had previous stub implementations, here's what changed:

### WhatsApp Blast
- **Before**: Stub returning potential_recipients
- **After**: Real implementation using frappe_whatsapp
- **Action**: No changes needed, automatically uses real API

### Analytics Sync
- **Before**: Stub implementations for all platforms
- **After**: Real OAuth-authenticated API calls for Google Ads and Meta Ads
- **Action**: Configure OAuth credentials for platforms

### Attribution Engine
- **Before**: Only tagged leads
- **After**: Also syncs to CRM and creates activities
- **Action**: No changes needed if CRM not installed, automatic if installed

## Next Steps

1. ✅ Configure OAuth for advertising platforms
2. ✅ Set up frappe_whatsapp with Business API
3. ✅ Install CRM app if needed for full funnel tracking
4. ⏳ Create remaining doctypes (see SETUP_GUIDE.md)
5. ⏳ Test end-to-end workflows
6. ⏳ Build Vue dashboard for visualization

---

For detailed doctype specifications and field definitions, see [SETUP_GUIDE.md](./SETUP_GUIDE.md)
For skill requirements and domain knowledge needed, see [.github/SKILLS.md](.github/SKILLS.md)
