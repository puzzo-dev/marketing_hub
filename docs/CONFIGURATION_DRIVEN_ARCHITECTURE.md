# Configuration-Driven Social Media Architecture

## Overview

The Marketing Hub social media integration is now **fully configuration-driven**, meaning you can add new social media platforms **WITHOUT writing any Python code**. Just create a Social Media Network record and configure the API settings!

---

## Architecture Philosophy

### ❌ OLD Approach (Rigid):
- Add platform → Write Python adapter class → Update factory mapping
- Every new platform requires code changes
- Defeats the purpose of having Social Media Network doctype

### ✅ NEW Approach (Flexible):
- Add platform → Create doctype record → Configure API settings → Done!
- No code needed for 90% of platforms
- Social Media Network doctype is the **single source of truth**

---

## Two Approaches

### 1. Generic Adapter (Recommended) 🌟

**Use for:** Most platforms with standard REST APIs

**How it works:**
- GenericAdapter reads ALL configuration from Social Media Network doctype
- Dynamically builds API requests based on your settings
- Handles authentication, placeholders, response parsing automatically

**Example platforms:**
- TikTok
- YouTube
- Pinterest
- Snapchat
- Telegram
- Reddit
- Tumblr
- Discord
- Slack

### 2. Custom Adapter (For Complex Cases)

**Use for:** Platforms with unusual API patterns

**When needed:**
- Multi-step workflows (Instagram: create container → publish)
- Complex authentication flows
- Non-standard API patterns
- Special rate limiting logic

**Example platforms:**
- Facebook/Instagram (2-step publish for Instagram)
- LinkedIn (complex media upload)
- Twitter/X (chunked media upload)

---

## Adding a Platform (Zero Code!)

### Step 1: Create Social Media Network Record

Go to: **Marketing Hub → Social Media Network → New**

Fill in basic info:
```
Network Name: TikTok
Network Code: tiktok
API Base URL: https://open.tiktokapis.com
Max Text Length: 2200
```

### Step 2: Configure API Settings

Expand **API Configuration** section:

#### Authentication:
```
Auth Type: Bearer Token
```

#### Endpoints (with placeholders):
```
Publish Endpoint: /v2/post/publish/
Delete Endpoint: /v2/post/publish/content/manage/
Analytics Endpoint: /v2/post/publish/video/query/
```

#### HTTP Method:
```
Publish Method: POST
```

#### Request Field Mapping:
```
Request Content Field: text
Request Media Field: video_info.video_url
```

#### Response Field Mapping:
```
Response ID Field: data.publish_id
Response URL Template: https://www.tiktok.com/@{account_id}/video/{post_id}
```

### Step 3: Save and Test!

That's it! The GenericAdapter will now handle TikTok publishing automatically.

---

## API Configuration Fields Reference

### `auth_type`
How to authenticate with the platform API:
- **OAuth 2.0**: Use access token from Ad Account
- **Bearer Token**: Send token in Authorization header
- **API Key**: Send as query parameter or custom header
- **Basic Auth**: Username/password authentication
- **Custom**: For special authentication logic (requires custom adapter)

### `api_version`
Platform API version to use:
- Examples: `v18.0` (Meta), `202401` (LinkedIn), `2` (Twitter)
- Used in API endpoint construction

### `publish_endpoint`
API endpoint for publishing content:
- Supports placeholders: `{account_id}`, `{api_version}`
- Example: `/v2/ugcPosts?author=urn:li:person:{account_id}`

### `delete_endpoint`
API endpoint for deleting posts:
- Supports placeholder: `{post_id}`
- Example: `/v2/posts/{post_id}`

### `analytics_endpoint`
API endpoint for fetching post metrics:
- Supports placeholder: `{post_id}`
- Example: `/v2/posts/{post_id}/metrics`

### `publish_method`
HTTP method for publish requests:
- Usually `POST`, sometimes `PUT`

### `request_content_field`
JSON field name for post content in publish request:
- Examples: `text`, `message`, `caption`, `status`
- For nested fields use dot notation: `share_commentary.text`

### `request_media_field`
JSON field name for media URLs in publish request:
- Examples: `image_url`, `media`, `attachments`
- For nested fields: `media.media_category`

### `response_id_field`
JSON path to post ID in publish response:
- Examples: `id`, `data.id`, `data.publish_id`
- Uses dot notation for nested extraction

### `response_url_template`
Template for generating post URL:
- Placeholders: `{post_id}`, `{account_id}`
- Example: `https://twitter.com/{account_id}/status/{post_id}`

### `custom_adapter_class`
Optional: Python class path for custom adapter:
- Example: `marketing_hub.utils.social_adapters.meta.MetaAdapter`
- Leave empty to use GenericAdapter

---

## Placeholder System

The GenericAdapter supports dynamic placeholders in endpoints:

### Available Placeholders:

- `{account_id}`: Replaced with ad_account.account_id
- `{post_id}`: Replaced with post ID from response
- `{api_version}`: Replaced with social_media_network.api_version

### Example Usage:

```python
# Social Media Network Config:
publish_endpoint = "/v2/person/{account_id}/posts"
response_url_template = "https://platform.com/posts/{post_id}"

# At Runtime:
# account_id = "12345" from Ad Account
# post_id = "abc789" from API response

# Results in:
# POST https://api.platform.com/v2/person/12345/posts
# Post URL: https://platform.com/posts/abc789
```

---

## Response Field Extraction

The GenericAdapter can extract values from nested JSON responses using dot notation:

### Example Response:
```json
{
  "success": true,
  "data": {
    "post": {
      "id": "abc123",
      "created_at": "2024-01-15"
    }
  }
}
```

### Configuration:
```
response_id_field: data.post.id
```

### Extraction Logic:
```python
# GenericAdapter extracts:
post_id = response_data['data']['post']['id']  # "abc123"
```

---

## Real-World Examples

### Example 1: TikTok (Simple Generic)

```yaml
Network Name: TikTok
Auth Type: Bearer Token
Publish Endpoint: /v2/post/publish/
Request Content Field: text
Request Media Field: video_info.video_url
Response ID Field: data.publish_id
```

**No custom adapter needed!** ✨

### Example 2: Pinterest (Simple Generic)

```yaml
Network Name: Pinterest
Auth Type: OAuth 2.0
Publish Endpoint: /v5/pins
Request Content Field: description
Request Media Field: media_source.source_type
Response ID Field: id
Response URL Template: https://www.pinterest.com/pin/{post_id}/
```

**No custom adapter needed!** ✨

### Example 3: Instagram (Custom Adapter)

```yaml
Network Name: Instagram
Custom Adapter Class: marketing_hub.utils.social_adapters.meta.MetaAdapter
```

**Custom adapter needed** because Instagram requires:
1. Create media container → Get container_id
2. Publish container → Get post_id
This 2-step flow needs special handling.

---

## Authentication Types

### OAuth 2.0 (Most Common)

Configuration:
```yaml
auth_type: OAuth 2.0
```

How it works:
- Access token stored in Ad Account doctype
- Sent as: `Authorization: Bearer {access_token}`
- Auto-refreshes when expired using refresh_token

### API Key

Configuration:
```yaml
auth_type: API Key
```

How it works:
- API key stored in Ad Account.access_token
- Can be sent as:
  - Query parameter: `?api_key={token}`
  - Header: `X-API-Key: {token}`

### Bearer Token

Configuration:
```yaml
auth_type: Bearer Token
```

How it works:
- Similar to OAuth 2.0 but no refresh logic
- Sent as: `Authorization: Bearer {access_token}`

### Basic Auth

Configuration:
```yaml
auth_type: Basic Auth
```

How it works:
- Username/password from Ad Account
- Encoded and sent as: `Authorization: Basic {encoded}`

---

## Factory Pattern (Hybrid Approach)

The `get_platform_adapter()` factory function intelligently chooses the adapter:

```python
def get_platform_adapter(network_name: str, platform: str):
    social_network = frappe.get_doc("Social Media Network", network_name)
    
    # Check if custom adapter specified
    if social_network.custom_adapter_class:
        # Dynamically import custom adapter
        module_path, class_name = social_network.custom_adapter_class.rsplit('.', 1)
        module = importlib.import_module(module_path)
        adapter_class = getattr(module, class_name)
        return adapter_class(network_name, platform)
    
    # Default to GenericAdapter (reads all config from doctype)
    return GenericAdapter(network_name, platform)
```

This allows:
- **Default behavior**: Use GenericAdapter (configuration-driven)
- **Special cases**: Specify custom adapter in doctype field
- **No code changes**: Everything controlled via doctype

---

## Migration Path for Existing Platforms

### Before:
```python
# Hardcoded in code
adapters = {
    "Facebook": MetaAdapter,
    "Instagram": MetaAdapter,
    "LinkedIn": LinkedInAdapter,
    "Twitter/X": TwitterAdapter,
}
```

### After:
```python
# In Social Media Network doctype:
Facebook → custom_adapter_class: marketing_hub.utils.social_adapters.meta.MetaAdapter
Instagram → custom_adapter_class: marketing_hub.utils.social_adapters.meta.MetaAdapter
LinkedIn → custom_adapter_class: marketing_hub.utils.social_adapters.linkedin.LinkedInAdapter
Twitter/X → custom_adapter_class: marketing_hub.utils.social_adapters.twitter.TwitterAdapter
```

### Run Migration:
```bash
cd ~/CodeBase/erpNext/frappe-bench-v15
bench --site erpnext.local execute marketing_hub.setup.setup_platform_configs.update_existing_with_config
```

---

## Testing the Configuration

### Step 1: Create Test Platform

Create a Social Media Network record for a simple platform (e.g., httpbin.org for testing):

```yaml
Network Name: Test Platform
API Base URL: https://httpbin.org
Publish Endpoint: /post
Request Content Field: message
Response ID Field: json.message
```

### Step 2: Create Ad Account

```yaml
Platform: Test Platform
Account ID: test-account
Access Token: test-token-123
```

### Step 3: Test Publish

```python
# In Frappe console:
from marketing_hub.utils.social_adapter import get_platform_adapter

adapter = get_platform_adapter("Test Platform", "Test Platform")
result = adapter.publish(
    ad_account="test-account",
    post_content="Hello Configuration!",
    media_urls=[]
)
print(result)
```

---

## Benefits of Configuration-Driven Approach

### 1. **No Code Required** ✨
Add new platforms through UI only - no Python knowledge needed

### 2. **Single Source of Truth** 📍
All platform config in Social Media Network doctype, not scattered in code

### 3. **Easy Maintenance** 🔧
Update API endpoints/fields without code deployment

### 4. **Flexibility** 🎯
Mix generic and custom adapters as needed

### 5. **Scalability** 📈
Add 10+ platforms in minutes, not days

### 6. **Version Control** 📝
Platform configs are data, can be exported/imported with fixtures

### 7. **Testing** ✅
Test different configurations without code changes

### 8. **Non-Developer Friendly** 👥
System admins can add platforms without developer involvement

---

## Advanced: Creating a Custom Adapter

Only needed for <10% of platforms with complex APIs.

### Step 1: Create Adapter Class

```python
# marketing_hub/utils/social_adapters/myplatform.py

from marketing_hub.utils.social_adapters.base import BasePlatformAdapter

class MyPlatformAdapter(BasePlatformAdapter):
    """Custom adapter for MyPlatform with special logic"""
    
    def publish(self, ad_account, post_content, media_urls=None, **kwargs):
        # Step 1: Special preprocessing
        processed_content = self._special_preprocessing(post_content)
        
        # Step 2: Custom API call
        response = self.make_request(
            endpoint="/custom/endpoint",
            method="POST",
            payload={"custom_field": processed_content}
        )
        
        return {
            "post_id": response.get("custom_id"),
            "post_url": f"https://myplatform.com/{response.get('custom_id')}"
        }
    
    def _special_preprocessing(self, content):
        # Platform-specific logic here
        return content.upper()  # Example
```

### Step 2: Configure in Doctype

```yaml
Network Name: MyPlatform
Custom Adapter Class: marketing_hub.utils.social_adapters.myplatform.MyPlatformAdapter
```

### Step 3: Factory Loads It Automatically

```python
# This happens automatically:
adapter = get_platform_adapter("MyPlatform", "MyPlatform")
# Returns: MyPlatformAdapter instance
```

---

## Troubleshooting

### Issue: "Adapter class not found"

**Cause**: Invalid custom_adapter_class path

**Solution**: 
1. Check Python module path is correct
2. Ensure class name matches
3. Verify file exists in utils/social_adapters/
4. Factory will fall back to GenericAdapter

### Issue: "Field not found in response"

**Cause**: Incorrect response_id_field path

**Solution**:
1. Check actual API response structure
2. Use dot notation for nested fields
3. Test with API directly first

### Issue: "Authentication failed"

**Cause**: Missing or invalid access token

**Solution**:
1. Verify Ad Account has valid access_token
2. Check auth_type matches platform requirements
3. Test token directly with curl/postman

### Issue: "Endpoint not found"

**Cause**: Incorrect publish_endpoint or missing placeholders

**Solution**:
1. Check API documentation for correct endpoint
2. Verify placeholder names match available values
3. Test endpoint with hardcoded values first

---

## Future Enhancements

### 1. **UI Configuration Builder** 🎨
Visual tool to build API configurations without knowing field names

### 2. **Platform Templates** 📋
Pre-built configurations for popular platforms (import and use)

### 3. **Configuration Validation** ✅
Test API configuration before saving

### 4. **Response Mapping Builder** 🗺️
Visual tool to map API response fields

### 5. **Rate Limit Configuration** ⏱️
Configure platform-specific rate limits in doctype

### 6. **Webhook Support** 🔔
Configure webhooks for platform notifications

---

## Summary

The new configuration-driven architecture makes Marketing Hub truly extensible:

- **90% of platforms**: No code needed, just configure doctype
- **10% of platforms**: Optional custom adapters for special cases
- **100% flexibility**: Mix and match approaches as needed

**The Social Media Network doctype is now the boss!** 👑
