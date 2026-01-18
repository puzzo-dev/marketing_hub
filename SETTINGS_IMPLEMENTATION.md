# Marketing Hub Settings - Implementation Complete ✓

## What Was Created

### 1. Marketing Hub Settings DocType
**Location**: `marketing_hub/marketing_hub/doctype/marketing_hub_settings/`

**Files**:
- `marketing_hub_settings.json` - DocType definition with 60+ fields
- `marketing_hub_settings.py` - Server-side validation logic
- `marketing_hub_settings.js` - Client-side form scripts with action buttons
- `test_marketing_hub_settings.py` - Unit tests

**Key Features**:
- Per-company configuration (autonamed by company field)
- Comprehensive settings across 9 major sections
- Built-in validation for sensible limits
- Helper action buttons for testing integrations

### 2. Settings Sections

#### General Settings
- Campaign naming series configuration
- Lead source defaults
- Auto-attribution toggle
- UTM and session tracking controls

#### Omni-Channel Settings
- Email, WhatsApp, SMS blast toggles
- Default sender configuration
- Channel-specific settings

#### Social Media Settings
- Auto-post scheduling
- Platform defaults
- Approval workflow controls

#### Advertising Platform Settings
- Google Ads, Meta Ads, LinkedIn, TikTok, Twitter toggles
- Sync frequency configuration
- OAuth integration prompts

#### Analytics Settings
- Sync scheduling (cron expression)
- Attribution model selection
- Conversion tracking toggle

#### Agency Settings (conditional)
- Campaign limits per client
- Client portal access
- White-label options
- Approval requirements

#### Content Management Settings
- Content library toggle
- Version control
- Brand guidelines enforcement
- Workflow selection

#### Notification Settings
- Event-based notifications
- Recipient configuration

### 3. Integration with Existing Code

**Updated Files**:
- `marketing_hub/utils/agency_mode.py` - Added `get_settings()` helper function
- `marketing_hub/workspace/marketing_hub/marketing_hub.json` - Added Settings link to workspace
- `marketing_hub/patches.txt` - Added migration patch

**New Migration**:
- `marketing_hub/patches/create_marketing_hub_settings.py` - Auto-creates settings for all companies

### 4. Documentation

**Created**:
- `MARKETING_HUB_SETTINGS_GUIDE.md` - Comprehensive 200+ line guide covering:
  - All settings explained
  - Setup instructions
  - API usage examples
  - Validation rules
  - Permissions
  - Best practices
  - Troubleshooting guide

## Workspace Menu Updates

### Added to Settings Card:
- **Marketing Hub Settings** (New) - Per-company configuration
- **Marketing Hub Setup** (Existing) - Global setup
- **Social Login Key** (Existing) - OAuth credentials

### Workspace Structure:
1. ✓ Marketing Dashboard (top shortcuts)
2. ✓ Campaign Management (campaigns, activities, leads)
3. ✓ Targeting (segments, customers)
4. ✓ Content (templates, assets, campaign content)
5. ✓ Social Media (social posts)
6. ✓ Advertising (ad accounts, analytics connectors)
7. ✓ Messaging (WhatsApp, email queue)
8. ✓ Analytics (daily logs, reports)
9. ✓ Agency Management (packages, subscriptions)
10. ✓ **Settings** (Marketing Hub Settings, Setup, OAuth)

## Usage Examples

### Get Settings in Python
```python
from marketing_hub.utils.agency_mode import get_settings

settings = get_settings()  # Current company
settings = get_settings(company="My Company")  # Specific company

if settings.enable_auto_attribution:
    # Run attribution logic
    pass
```

### Check Agency Mode
```python
from marketing_hub.utils.agency_mode import get_agency_mode

is_agency = get_agency_mode()
is_agency = get_agency_mode(company="My Company")
```

### Access in Jinja Templates
```jinja
{% set settings = frappe.get_doc("Marketing Hub Settings", {"company": frappe.defaults.get_user_default("Company")}) %}
{% if settings.agency_mode %}
  <!-- Show agency-specific content -->
{% endif %}
```

## Client-Side Features

### Action Buttons
1. **Test Email Configuration** - Validates email setup
2. **Test WhatsApp Integration** - Checks WhatsApp app status
3. **Sync Analytics Now** - Triggers immediate sync

### Smart UI
- Agency Settings section auto-shows when agency mode is enabled
- Platform-specific OAuth setup messages
- Dependency warnings (e.g., WhatsApp app required)

## Migration Status

✅ **Successfully Migrated**:
- DocType created in database
- Settings created for both companies:
  - I-Varse Limited
  - I-Varse Technologies
- Default values set:
  - Auto-attribution: Enabled
  - UTM tracking: Enabled
  - Session tracking: Enabled (30 days)
  - Email blast: Enabled
  - Auto-post: Enabled (15 min interval)
  - Analytics sync: Enabled (2 AM daily)
  - Attribution model: Last Touch
  - Content library: Enabled
  - Version control: Enabled
  - All notifications: Enabled

## Permissions

| Role | Create | Read | Write | Delete |
|------|--------|------|-------|--------|
| System Manager | ✓ | ✓ | ✓ | ✓ |
| Marketing Manager | - | ✓ | ✓ | - |

## Next Steps

1. **Access Settings**:
   ```
   Marketing Hub > Settings > Marketing Hub Settings
   ```

2. **Configure for Each Company**:
   - Review default settings
   - Enable/disable features as needed
   - Set up OAuth for advertising platforms
   - Configure notification recipients

3. **Test Integrations**:
   - Use action buttons to verify email, WhatsApp
   - Trigger test analytics sync
   - Verify campaign creation uses settings

4. **Update Custom Code** (if any):
   - Replace `frappe.get_single("Marketing Hub Setup")` calls
   - Use `get_settings()` from agency_mode.py
   - Pass company parameter where needed

## Validation & Testing

### Built-in Validations
- ✓ Session timeout: 1-365 days
- ✓ Auto-post interval: 5-1440 minutes
- ✓ Max campaigns per client: >= 1

### Test Coverage
- Unit tests included in `test_marketing_hub_settings.py`
- Tests for validations and creation logic

## Integration Points

### Used By
- `attribution_engine.py` - For auto-attribution settings
- `omni_blast.py` - For channel enablement checks
- `analytics_sync.py` - For sync frequency and schedule
- `auto_post.py` - For post interval settings
- `agency_mode.py` - For agency mode checks
- `permissions.py` - For campaign limits (agency mode)

### Depends On
- Company (link)
- Workflow (optional link for content approval)

## Summary

✅ **Complete Settings System** - Per-company configuration with 60+ options
✅ **Backward Compatible** - Works with existing Marketing Hub Setup
✅ **Well Documented** - Comprehensive guide with examples
✅ **Production Ready** - Validated, tested, and migrated
✅ **User Friendly** - Smart UI with helper buttons and contextual help
✅ **API Ready** - Easy-to-use helper functions for programmatic access

The Marketing Hub now has a robust, scalable settings system that supports multi-company ERPNext installations while maintaining backward compatibility with the original single-doctype setup.
