# Content Management System - Marketing Hub

## Overview

The Marketing Hub Content Management System helps you orchestrate content across multiple channels with different requirements. It provides:

1. **Content Assets** - Central library for images, videos, documents
2. **Marketing Templates** - Channel-specific content templates with specifications
3. **Campaign Content** - Link templates to campaigns with customization
4. **Content Orchestration** - Tools to adapt and schedule content across channels

## Content Management Workflow

### 1. Create Content Assets

Content Assets are your central media library:

```
Marketing Hub → Content Asset → New
```

**Asset Types:**
- Image (JPG, PNG, GIF)
- Video (MP4, MOV)
- Document (PDF, DOCX)
- Audio (MP3, WAV)
- HTML/Text

**Key Fields:**
- Asset Name
- Asset Type
- Channel (optimized for specific channel)
- File/External URL
- Dimensions (1920x1080, etc.)
- Tags for organization
- Status (Draft/Review/Approved/Archived)

**Usage Tracking:**
- Automatically tracks how many times asset is used
- Shows last used date
- Helps identify high-performing assets

### 2. Create Marketing Templates

Marketing Templates define channel-specific content with proper specifications:

```
Marketing Hub → Marketing Template → New
```

**Template Structure:**

**Content Fields:**
- Subject/Title (for email, ads)
- Headline (primary message)
- Body Text (main content)
- Call to Action (CTA button text)
- Link URL

**Creative Assets:**
- Primary Asset (main image/video)
- Secondary Assets (additional media)

**Channel Specifications (Auto-populated):**

| Channel | Character Limit | Image Specs | Video Specs |
|---------|----------------|-------------|-------------|
| **Meta Ads** | 125 | 1200x628 (Feed), 1080x1080 (Square), 1080x1920 (Stories) | MP4/MOV, 1-241s, 16:9/1:1/9:16 |
| **Google Ads** | 90 | 1200x628 (Landscape), 1200x1200 (Square) | MP4/AVI/WebM, Up to 3min |
| **LinkedIn Ads** | 150 | 1200x627 (Single), 1080x1080 (Carousel) | MP4, 3s-30min, 16:9/1:1/9:16 |
| **TikTok Ads** | 100 | 1080x1920 | MP4/MOV, 5-60s, 9:16/1:1/16:9 |
| **Twitter/X** | 280 | 1200x675, 800x800 (Carousel) | MP4/MOV, Up to 2:20 |
| **Reddit Ads** | 300 | 1200x628 | MP4/MOV, Up to 15min |
| **WhatsApp** | 1024 | Any (max 5MB) | MP4/3GP, max 16MB |
| **SMS** | 160 | N/A | N/A |
| **Email** | No limit | Max width 600px | Embedded/Linked |

**Dynamic Variables:**
Templates support variables like `{customer_name}`, `{product_name}` that get replaced at runtime.

Example Template Variables (JSON):
```json
{
  "customer_name": "John Doe",
  "product_name": "Marketing Suite",
  "discount_code": "SAVE20",
  "company_name": "Acme Corp"
}
```

### 3. Create Campaign Content

Link templates to campaigns and customize per channel:

```
Campaign → Campaign Content → New
```

**Workflow:**

1. **Select Campaign & Channel**
   - Choose which campaign and channel (Meta Ads, Google Ads, Email, etc.)

2. **Choose Template**
   - Select existing template or start blank
   - Template content auto-fills

3. **Customize (Optional)**
   - Override subject, headline, body, CTA
   - Add custom assets
   - Modify link URL

4. **UTM Tracking**
   - Auto-generated UTM parameters
   - Format: `utm_campaign`, `utm_source`, `utm_medium`
   - Appended to all links automatically

5. **Preview & Schedule**
   - Live preview shows how content looks
   - Set scheduled date for publishing
   - Status tracking (Draft → Scheduled → Live → Completed)

6. **Performance Tracking**
   - Sent, Delivered, Opened, Clicked counts
   - Per-channel metrics

## Content Orchestration Tools

### Bulk Create Content for Multiple Channels

Create campaign content for all channels at once:

```python
# In Campaign form or custom script
frappe.call({
    method: "marketing_hub.utils.content_orchestration.create_campaign_content_for_channels",
    args: {
        campaign: "CAMPAIGN-001",
        channels: "Meta Ads, Google Ads, LinkedIn Ads, Email"
    },
    callback: function(r) {
        console.log("Created:", r.message);
    }
});
```

### Adapt Content Between Channels

Automatically adapt content from one channel to another:

```python
# Adapt Meta Ads content for TikTok
frappe.call({
    method: "marketing_hub.utils.content_orchestration.adapt_content_for_channel",
    args: {
        source_content: "CAMPAIGN-001-meta_ads-001",
        target_channel: "TikTok Ads"
    },
    callback: function(r) {
        console.log("Adapted content:", r.message);
    }
});
```

**Adaptation Logic:**
- Strips HTML tags for text-only channels (SMS, Google Ads)
- Truncates content to fit character limits
- Adjusts formatting for channel specifications

### Get Content Recommendations

Get AI/rule-based recommendations:

```python
frappe.call({
    method: "marketing_hub.utils.content_orchestration.get_content_recommendations",
    args: {
        campaign: "CAMPAIGN-001",
        channel: "Meta Ads"
    },
    callback: function(r) {
        console.log("Templates:", r.message.suggested_templates);
        console.log("Tips:", r.message.content_tips);
    }
});
```

Returns:
- Suggested templates from successful campaigns
- Channel-specific best practices
- Specification warnings

### Bulk Schedule Content

Schedule multiple channels at once:

```python
frappe.call({
    method: "marketing_hub.utils.content_orchestration.bulk_schedule_content",
    args: {
        campaign: "CAMPAIGN-001",
        schedule_plan: [
            {channel: "Meta Ads", scheduled_date: "2026-01-20 10:00:00"},
            {channel: "Google Ads", scheduled_date: "2026-01-20 10:00:00"},
            {channel: "Email", scheduled_date: "2026-01-20 14:00:00"}
        ]
    }
});
```

## Platform-Specific Best Practices

### Meta Ads (Facebook/Instagram)

**Content Strategy:**
- Lead with value proposition in first 125 characters
- Use square (1:1) or vertical (9:16) formats for mobile
- Include faces in images (increases engagement)
- Test 3-5 ad variants per campaign

**Creative Specs:**
- Primary text: 125 characters (recommended)
- Headline: 40 characters max
- Image: 1080x1080 (square) or 1200x628 (landscape)
- Video: 1-60 seconds (shorter performs better)

**Best Performing:**
- User-generated content style
- Before/after comparisons
- Social proof (testimonials, reviews)
- Limited-time offers

### Google Ads

**Search Ads:**
- Include primary keyword in headline 1
- Highlight unique value prop in headline 2
- Use all available headlines (3) and descriptions (2)
- Include pricing if competitive

**Display Ads:**
- Responsive display ads (multiple sizes)
- Clear brand logo
- Minimal text on images
- Strong CTA

**Performance Max:**
- Provide 5+ headlines, 4+ descriptions
- Multiple image orientations
- Video assets (even short clips)
- Let AI optimize combinations

### LinkedIn Ads

**Content Approach:**
- Professional, B2B-focused messaging
- Lead with business problem/solution
- Include statistics or data
- Use company/employee testimonials

**Targeting:**
- Job title, company size, industry
- Account-based marketing (ABM) lists
- Lookalike audiences from customers

**Creative Tips:**
- Use professional headshots
- Charts/graphs perform well
- Carousel for case studies
- Video for thought leadership

### TikTok Ads

**Content Style:**
- Native, authentic (not overly polished)
- Hook in first 3 seconds
- Show product in action
- Use trending sounds/effects

**Format:**
- 9:16 vertical video (full screen)
- 15-60 seconds optimal
- Text overlays for context
- No black bars

**Engagement Tactics:**
- Behind-the-scenes content
- User challenges
- Influencer partnerships
- Educational "how-to" content

### Email Marketing

**Subject Lines:**
- 6-10 words, 40-50 characters
- Personalization increases open rates
- Avoid spam triggers (FREE, !!!, ALL CAPS)
- Test emoji usage

**Design:**
- Mobile-first (>60% opens on mobile)
- Max width 600px
- Single column layout
- Clear visual hierarchy

**Content:**
- Personalize beyond "Hi {name}"
- Single primary CTA
- Alt text for images
- Plain text fallback

**Timing:**
- B2B: Tuesday-Thursday, 10am-2pm
- B2C: Weekends often outperform
- Test your specific audience

## Integration with Campaign Execution

### Omni-Channel Blast with Content

When executing an omni-channel blast, the system automatically:

1. Fetches Campaign Content for each channel
2. Renders templates with dynamic variables
3. Applies UTM tracking to all links
4. Sends via appropriate API (Meta, Google, WhatsApp, etc.)
5. Records performance metrics

### Content Approval Workflow

**Recommended Workflow:**

1. **Creator** - Creates template (Status: Draft)
2. **Reviewer** - Reviews content, requests changes (Status: Review)
3. **Approver** - Approves final version (Status: Approved)
4. **Campaign Manager** - Schedules for campaign (Status: Active)
5. **Archive** - After campaign ends (Status: Archived)

### A/B Testing Content

Create multiple Campaign Content entries for same channel:

```
CAMPAIGN-001-meta_ads-001 (Variant A - Benefit-focused)
CAMPAIGN-001-meta_ads-002 (Variant B - Feature-focused)
CAMPAIGN-001-meta_ads-003 (Variant C - Social proof)
```

Track performance metrics to determine winner.

## API Reference

### Create Campaign Content
```python
content = frappe.new_doc("Campaign Content")
content.campaign = "CAMPAIGN-001"
content.channel = "Meta Ads"
content.template = "TMPL-0001"
content.custom_headline = "Custom Headline"
content.insert()
```

### Render Template with Variables
```python
template = frappe.get_doc("Marketing Template", "TMPL-0001")
rendered = template.render({
    "customer_name": "John",
    "discount": "20%"
})
print(rendered["body_text"])  # Variables replaced
```

### Track Asset Usage
```python
asset = frappe.get_doc("Content Asset", "ASSET-0001")
asset.increment_usage()  # Increments count, updates last_used
```

### Get Channel Best Practices
```python
from marketing_hub.utils.content_orchestration import get_channel_best_practices

specs = get_channel_best_practices()
meta_specs = specs["Meta Ads"]
print(meta_specs["image_sizes"])
print(meta_specs["best_practices"])
```

## Tips for Success

### 1. Build a Content Library
- Create 20-30 reusable assets
- Tag assets by campaign type, industry, audience
- Regularly update with high-performing content
- Archive outdated/underperforming assets

### 2. Template Everything
- Create templates for recurring campaign types
- Document what works in template notes
- Version templates (v1, v2, etc.)
- Share successful templates across team

### 3. Test Systematically
- Always run A/B tests (minimum 2 variants)
- Test one variable at a time (headline, image, CTA)
- Need statistical significance (>100 conversions per variant)
- Document learnings

### 4. Follow Platform Guidelines
- Each platform reviews ads (Meta: 24hrs, Google: 1-2 days)
- Avoid "clickbait" or misleading content
- Use original, high-quality images
- Comply with ad policies (alcohol, healthcare, etc.)

### 5. Optimize for Mobile
- 70%+ of social media usage is mobile
- Vertical video outperforms horizontal
- Large text/buttons for touchscreens
- Fast loading times

## Example: Creating a Multi-Channel Campaign

### Step 1: Upload Assets
```
1. Upload hero image (1200x628) → ASSET-0001
2. Upload square variant (1080x1080) → ASSET-0002
3. Upload video (15sec, 9:16) → ASSET-0003
```

### Step 2: Create Templates

**Meta Ads Template:**
- Headline: "Transform Your Marketing in 30 Days"
- Body: "Join 10,000+ marketers using {product_name}. Get started today with {discount_code}."
- CTA: "Start Free Trial"
- Primary Asset: ASSET-0001

**Email Template:**
- Subject: "Exclusive Offer: {discount_code} Inside"
- Headline: Same as Meta
- Body: Extended version with bullet points
- CTA: Same

### Step 3: Create Campaign Content

```python
# Bulk create for all channels
create_campaign_content_for_channels(
    campaign="SUMMER-PROMO",
    channels="Meta Ads, Google Ads, Email, LinkedIn Ads"
)
```

### Step 4: Customize Per Channel

- Meta Ads: Use square image (ASSET-0002)
- LinkedIn: Adjust tone to B2B
- Email: Add product images, testimonials
- Google: Shorter, keyword-focused headline

### Step 5: Schedule & Launch

```python
bulk_schedule_content(
    campaign="SUMMER-PROMO",
    schedule_plan=[
        {"channel": "Email", "scheduled_date": "2026-01-20 08:00:00"},  # First
        {"channel": "Meta Ads", "scheduled_date": "2026-01-20 10:00:00"},  # 2hrs later
        {"channel": "Google Ads", "scheduled_date": "2026-01-20 10:00:00"},
        {"channel": "LinkedIn Ads", "scheduled_date": "2026-01-21 09:00:00"}  # Next day
    ]
)
```

### Step 6: Monitor & Optimize

Check Campaign Analytics report:
- Which channel has best ROAS?
- Which content variant performs best?
- Pause underperforming content
- Scale winning variants

## Troubleshooting

### Content Not Showing in Campaign

Check:
1. Campaign Content status is "Live" or "Scheduled"
2. Scheduled date is in future (for scheduled)
3. Campaign name matches exactly
4. Channel is included in Campaign's "channels_used" field

### Template Variables Not Replacing

Check:
1. Variables JSON is valid
2. Variable names match exactly (case-sensitive)
3. Using correct format: `{variable_name}` not `{{variable_name}}`
4. Calling `template.render(context)` with context dict

### Preview Not Generating

Check:
1. Template or custom content is filled
2. Save document (preview generates on save)
3. Check browser console for errors
4. Try clearing cache

### Asset File Not Uploading

Check:
1. File size limits (varies by channel)
2. File format is supported
3. Browser upload limits
4. Frappe file size configuration

---

**Need Help?**
- Check Marketing Hub documentation
- Review successful campaign examples
- Contact system administrator
- Test in sandbox first
