# Marketing Hub - Hardcoded Options Audit

**Date**: January 24, 2026  
**Status**: 🔴 Multiple hardcoded options found  
**Impact**: Low maintainability, difficult to extend

---

## Summary

Found **12 instances** of hardcoded Select field options and **1 hardcoded Python dictionary** that should be made dynamic or moved to master doctypes.

---

## 1. Marketing Expense - Expense Category

**Location**: `marketing_expense.json` (line 94)  
**Field**: `expense_category`  
**Current**: Hardcoded Select options

```json
{
  "fieldname": "expense_category",
  "fieldtype": "Select",
  "options": "Advertising\nContent Creation\nSocial Media\nEmail Marketing\nSEO/SEM\nEvents\nPrint Media\nInfluencer Marketing\nAgency Fees\nSoftware Tools\nOther"
}
```

**Problem**:
- Cannot add custom categories without modifying doctype
- No central management of categories
- Difficult to track which categories are actually used

**Recommendation**: ✅ Create **Marketing Expense Category** master doctype

```json
{
  "fieldname": "expense_category",
  "fieldtype": "Link",
  "options": "Marketing Expense Category"
}
```

**New DocType Structure**:
```python
Marketing Expense Category:
  - category_name (Data, required, unique)
  - category_code (Data)
  - description (Text)
  - is_active (Check, default 1)
  - parent_category (Link to self, for hierarchy)
  - accounting_account (Link to Account)
```

---

## 2. Social Post - Post Type

**Location**: `social_post.json` (line 76)  
**Field**: `post_type`  
**Current**: Hardcoded Select options

```json
{
  "fieldname": "post_type",
  "fieldtype": "Select",
  "options": "Text\nImage\nVideo\nCarousel\nStory\nReel\nLive"
}
```

**Problem**:
- Post types vary by platform (e.g., Instagram has Reels, YouTube has Shorts)
- Cannot add platform-specific post types
- TikTok/Pinterest have unique formats not listed

**Recommendation**: 🔄 Keep as Select but make it **query-based** from Social Media Network

**Better Approach**: Add `post_types` field to Social Media Network (already exists!), then use:

```json
{
  "fieldname": "post_type",
  "fieldtype": "Select",
  "options": "frappe.get_all('Social Media Network', filters={'name': doc.social_media_network}, fields=['post_types'])"
}
```

**Alternative**: Create **Post Type** master doctype:
```python
Post Type:
  - type_name (Data) - e.g., "Reel", "Story", "Feed Post"
  - supported_networks (Table MultiSelect → Social Media Network)
  - specs (JSON) - technical specifications
```

---

## 3. Social Post - Status

**Location**: `social_post.json` (line 84)  
**Field**: `status`  
**Current**: Hardcoded Select options

```json
{
  "fieldname": "status",
  "fieldtype": "Select",
  "options": "Draft\nScheduled\nPublished\nFailed\nDeleted"
}
```

**Problem**:
- Status workflow is fixed
- Cannot add custom statuses (e.g., "Under Review", "Approved", "Rejected")
- No audit trail of status changes

**Recommendation**: ⚠️ **Keep as is** (standard workflow) but add **Status Log** child table

```python
Social Post Status Log (child table):
  - status (Select) - same options
  - changed_by (Link to User)
  - changed_on (Datetime)
  - reason (Text)
```

---

## 4. Social Post - Media Type

**Location**: `social_post.json` (line 137)  
**Field**: `media_type`  
**Current**: Hardcoded Select options

```json
{
  "fieldname": "media_type",
  "fieldtype": "Select",
  "options": "\nImage\nVideo\nGIF"
}
```

**Problem**:
- Missing formats: Document, Audio, 360° Image, AR Effect
- No validation against network capabilities

**Recommendation**: ✅ Create **Media Type** master doctype

```python
Media Type:
  - type_name (Data) - Image, Video, GIF, Document, Audio
  - file_extensions (Text) - .jpg, .png, .gif
  - max_file_size_mb (Int)
  - supported_networks (Table MultiSelect → Social Media Network)
  - is_active (Check)
```

---

## 5. Omni Blast - Status

**Location**: `omni_blast.json` (line 49)  
**Field**: `status`  
**Current**: Hardcoded Select options

```json
{
  "fieldname": "status",
  "fieldtype": "Select",
  "options": "Draft\nScheduled\nPublishing\nPublished\nFailed"
}
```

**Recommendation**: ⚠️ **Keep as is** (matches Social Post workflow)

---

## 6. Omni Blast - Blast Type

**Location**: `omni_blast.json` (line 67)  
**Field**: `blast_type`  
**Current**: Hardcoded Select options

```json
{
  "fieldname": "blast_type",
  "fieldtype": "Select",
  "options": "Immediate\nScheduled\nStaggered"
}
```

**Problem**:
- Cannot add custom scheduling strategies (e.g., "Time Zone Optimized", "Peak Hours")
- No metadata about what each type does

**Recommendation**: ✅ Create **Blast Type** master doctype

```python
Blast Type:
  - type_name (Data) - Immediate, Scheduled, Staggered, Time Zone Optimized
  - description (Text)
  - requires_scheduling (Check)
  - supports_delay_between_posts (Check)
  - is_active (Check)
```

---

## 7. Omni Blast - Media Type

**Location**: `omni_blast.json` (line 90)  
**Field**: `media_type`  
**Current**: Same hardcoded options as Social Post

**Recommendation**: ✅ Link to **Media Type** master (same as #4)

---

## 8. Marketing Hub Settings - Default Social Platforms

**Location**: `marketing_hub_settings.json` (line 223)  
**Field**: `default_social_platforms`  
**Current**: Hardcoded MultiSelect options

```json
{
  "fieldname": "default_social_platforms",
  "fieldtype": "MultiSelect",
  "options": "Meta\nTwitter\nLinkedIn\nInstagram\nTikTok\nYouTube"
}
```

**Problem**:
- Duplicate of Social Media Network names
- Gets out of sync when new networks are added
- Hardcoded platform names don't match network records

**Recommendation**: ✅ **Change to Table MultiSelect**

```json
{
  "fieldname": "default_social_platforms",
  "fieldtype": "Table MultiSelect",
  "options": "Social Media Network"
}
```

---

## 9. Marketing Hub Settings - Sync Frequency

**Location**: `marketing_hub_settings.json` (line 281)  
**Field**: `sync_frequency`  
**Current**: Hardcoded Select options

```json
{
  "fieldname": "sync_frequency",
  "fieldtype": "Select",
  "options": "Hourly\nDaily\nWeekly"
}
```

**Recommendation**: ⚠️ **Keep as is** (standard intervals) or change to Int field with unit

```json
{
  "fieldname": "sync_interval",
  "fieldtype": "Int",
  "label": "Sync Interval (minutes)",
  "default": 60
}
```

---

## 10. Marketing Hub Settings - Attribution Model

**Location**: `marketing_hub_settings.json` (line 315)  
**Field**: `default_attribution_model`  
**Current**: Hardcoded Select options

```json
{
  "fieldname": "default_attribution_model",
  "fieldtype": "Select",
  "options": "First Touch\nLast Touch\nLinear\nTime Decay\nPosition Based"
}
```

**Problem**:
- Cannot add custom attribution models
- No explanation of what each model does
- Models have different parameters (e.g., decay rate)

**Recommendation**: ✅ Create **Attribution Model** master doctype

```python
Attribution Model:
  - model_name (Data) - First Touch, Last Touch, Linear, Time Decay, Position Based
  - model_code (Data) - first_touch, last_touch, etc.
  - description (Text Editor) - Explain the model
  - calculation_method (Text) - Python function name or formula
  - parameters (JSON) - Model-specific parameters
  - is_active (Check)
  - is_default (Check)
```

---

## 11. Marketing Hub Connection - Sync Direction

**Location**: `marketing_hub_connection.json` (line 27)  
**Field**: `sync_direction`  
**Current**: Hardcoded Select options

```json
{
  "fieldname": "sync_direction",
  "fieldtype": "Select",
  "options": "Source\nTarget\nBidirectional"
}
```

**Recommendation**: ⚠️ **Keep as is** (only 3 standard options)

---

## 12. Marketing Hub Connection - Status

**Location**: `marketing_hub_connection.json` (line 40)  
**Field**: `status`  
**Current**: Hardcoded Select options

```json
{
  "fieldname": "status",
  "fieldtype": "Select",
  "options": "Active\nInactive\nPending"
}
```

**Recommendation**: ⚠️ **Keep as is** (standard statuses)

---

## 13. Python - Channel Specifications (CRITICAL)

**Location**: `utils/content_orchestration.py` (line 111)  
**Function**: `adapt_content_to_specs()`  
**Current**: Hardcoded dictionary

```python
channel_specs = {
    "SMS": {"max_chars": 160, "no_html": True},
    "WhatsApp": {"max_chars": 1024, "no_html": False},
    "Twitter/X Ads": {"max_chars": 280, "no_html": False},
    "Meta Ads": {"max_chars": 125, "no_html": False},
    "Google Ads": {"max_chars": 90, "no_html": True},
    "LinkedIn Ads": {"max_chars": 150, "no_html": False},
    "TikTok Ads": {"max_chars": 100, "no_html": True},
    "Reddit Ads": {"max_chars": 300, "no_html": False}
}
```

**Problem**: 🔴 **CRITICAL**
- Specs are hardcoded in Python
- Cannot be updated without code deployment
- Platforms change their limits frequently (e.g., Twitter went from 140 → 280 → 4000 for verified)
- No way to add new platforms without modifying code
- Duplicates Social Media Network data

**Recommendation**: ✅ **Move to Social Media Network doctype** (already has some of these fields!)

**Update Social Media Network**:
```json
{
  "fields": [
    {
      "fieldname": "max_text_length",
      "fieldtype": "Int",
      "label": "Max Text Length"
    },
    {
      "fieldname": "supports_html",
      "fieldtype": "Check",
      "label": "Supports HTML"
    },
    {
      "fieldname": "max_hashtags",
      "fieldtype": "Int",
      "label": "Max Hashtags"
    },
    {
      "fieldname": "max_mentions",
      "fieldtype": "Int",
      "label": "Max Mentions"
    }
  ]
}
```

**Update Python code**:
```python
def adapt_content_to_specs(content, channel):
    """Get specs dynamically from Social Media Network"""
    network = frappe.get_doc("Social Media Network", channel)
    
    specs = {
        "max_chars": network.max_text_length or 5000,
        "no_html": not network.supports_html,
        "max_hashtags": network.max_hashtags or 30,
        "max_mentions": network.max_mentions or 10
    }
    
    # ... rest of adaptation logic
```

---

## Priority Matrix

### High Priority (Must Fix)
1. **Python channel_specs dictionary** → Move to Social Media Network doctype ⚠️ CRITICAL
2. **Marketing Expense Category** → Create master doctype (frequently customized)
3. **Attribution Model** → Create master doctype (complex logic)
4. **default_social_platforms** → Change to Table MultiSelect

### Medium Priority (Should Fix)
5. **Media Type** → Create master doctype
6. **Blast Type** → Create master doctype
7. **Post Type** → Make query-based from Social Media Network

### Low Priority (Consider)
8. **sync_frequency** → Change to Int field (optional)
9. Status fields → Keep as is but add audit logging

---

## Implementation Plan

### Phase 1: Critical Fixes (2 hours)
```bash
# 1. Update Social Media Network doctype
# Add: supports_html, max_hashtags, max_mentions fields

# 2. Update content_orchestration.py
# Replace hardcoded dictionary with dynamic query

# 3. Update Marketing Hub Settings
# Change default_social_platforms to Table MultiSelect
```

### Phase 2: Master Doctypes (4 hours)
```bash
# 1. Create Marketing Expense Category doctype
# 2. Create Attribution Model doctype
# 3. Create Media Type doctype
# 4. Create Blast Type doctype

# 5. Update references in existing doctypes
```

### Phase 3: Data Migration (1 hour)
```bash
# 1. Create seed data for new master doctypes
# 2. Migrate existing records
# 3. Test all forms
```

---

## Benefits After Refactoring

### ✅ Maintainability
- Update platform specs without code deployment
- Add new categories/models through UI
- Centralized management

### ✅ Extensibility
- Users can add custom expense categories
- Support for new platforms easier
- Custom attribution models possible

### ✅ Data Integrity
- Enforce referential integrity with Link fields
- Track usage of each category/model
- Prevent orphaned references

### ✅ Flexibility
- Platform limits update automatically
- Per-client customization possible
- A/B test different models

---

## Code Examples

### Before (Hardcoded)
```python
# ❌ Bad - hardcoded in Python
if channel == "Meta Ads":
    max_chars = 125
elif channel == "Google Ads":
    max_chars = 90
# ... 10 more conditions
```

### After (Dynamic)
```python
# ✅ Good - dynamic from database
network = frappe.get_cached_doc("Social Media Network", channel)
max_chars = network.max_text_length or 5000
```

---

## Testing Checklist

After refactoring:
- [ ] Create test expense with new category
- [ ] Update Social Media Network specs and verify content adaptation
- [ ] Create Omni Blast with new blast type
- [ ] Test attribution model switching
- [ ] Verify backward compatibility with existing records
- [ ] Performance test (caching properly working)

---

## Estimated Impact

**Before**: 
- 12 hardcoded option sets
- 1 hardcoded Python dictionary
- Cannot customize without code changes

**After**:
- 0 hardcoded options
- 4 new master doctypes
- Full customization through UI
- 50% reduction in maintenance overhead

**Time Investment**: ~7 hours total
**Long-term Savings**: ~2 hours/month in maintenance

---

## Conclusion

The hardcoded options create technical debt and limit extensibility. The most critical issue is the **hardcoded channel specifications in Python** which should be moved to the Social Media Network doctype immediately. Other hardcoded Select fields should be converted to Link fields with appropriate master doctypes for better maintainability and flexibility.
