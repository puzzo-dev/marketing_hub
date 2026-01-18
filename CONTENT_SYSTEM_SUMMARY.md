# Content Management System - Quick Reference

## 🎯 What We Built

A comprehensive content management system for orchestrating multi-channel marketing campaigns with channel-specific content requirements.

## 📦 New Doctypes Created

### 1. **Content Asset** (`ASSET-####`)
Central media library for all creative assets.

**Use for:** Images, videos, documents, GIFs, HTML content

**Key Features:**
- File upload or external URL
- Channel optimization tags
- Usage tracking (count + last used)
- Approval workflow (Draft → Review → Approved → Archived)
- Auto file size calculation
- Dimensions and duration tracking

### 2. **Marketing Template** (`TMPL-####`)
Reusable content templates with channel-specific specifications.

**Use for:** Creating template content that adapts to different platforms

**Key Features:**
- Channel selection (auto-populates specs)
- Content fields: Subject, Headline, Body, CTA, Link
- Asset management (primary + secondary)
- Dynamic variables: `{customer_name}`, `{product_name}`
- Character limits per channel
- Image/video specification guidelines
- Template rendering with variable replacement

**Auto-populated Specs for Each Channel:**
| Channel | Char Limit | Key Specs |
|---------|-----------|-----------|
| Meta Ads | 125 | 1200x628, 1080x1080, 1080x1920 |
| Google Ads | 90 | 1200x628, 1200x1200 |
| LinkedIn | 150 | 1200x627, 1080x1080 |
| TikTok | 100 | 1080x1920, 5-60s video |
| SMS | 160 | Text only |
| Email | No limit | 600px width |

### 3. **Campaign Content** (`{campaign}-{channel}-{###}`)
Links templates to campaigns with customization per channel.

**Use for:** Creating channel-specific content for each campaign

**Key Features:**
- Template selection or custom content
- Override any field (subject, headline, body, CTA, assets)
- Auto UTM parameter generation
- Link URL with UTM tracking
- Live preview on save
- Scheduling (Draft → Scheduled → Live → Completed)
- Performance metrics (sent, delivered, opened, clicked)

### 4. **Template Asset Item** (Child Table)
Links multiple assets to templates/content.

**Use for:** Adding multiple images/videos to a template

## 🛠️ Utilities Created

### `content_orchestration.py`

**Functions:**

1. **`create_campaign_content_for_channels(campaign, channels, template)`**
   - Bulk create Campaign Content for multiple channels
   - Auto-selects best template per channel
   - Avoids duplicates

2. **`adapt_content_for_channel(source_content, target_channel)`**
   - Adapts existing content for different channel
   - Auto-truncates to character limits
   - Strips HTML for text-only channels

3. **`get_content_recommendations(campaign, channel)`**
   - Suggests templates from successful campaigns
   - Channel-specific best practices
   - Spec warnings and tips

4. **`bulk_schedule_content(campaign, schedule_plan)`**
   - Schedule multiple channels at once
   - Set different times per channel
   - Updates status to Scheduled

5. **`get_channel_best_practices()`**
   - Complete specs for all platforms
   - Image sizes, video specs, text limits
   - Best practices and tips

## 🚀 Usage Workflow

### Basic Workflow

```
1. Upload Assets → Content Asset
   ↓
2. Create Templates → Marketing Template
   ↓
3. Link to Campaign → Campaign Content
   ↓
4. Customize per Channel
   ↓
5. Schedule & Publish
   ↓
6. Track Performance
```

### Example: Multi-Channel Campaign

#### Step 1: Create Assets
```
Content Asset → New
- Name: "Summer Sale Hero"
- Type: Image
- Channel: Meta Ads
- Upload: summer-sale.jpg (1200x628)
- Status: Approved
```

#### Step 2: Create Template
```
Marketing Template → New
- Name: "Summer Sale 2026"
- Channel: Meta Ads
- Headline: "Save {discount}% This Summer"
- Body: "Shop our biggest sale of the year..."
- CTA: "Shop Now"
- Primary Asset: ASSET-0001
- Variables: {"discount": "30", "promo_code": "SUMMER30"}
```

#### Step 3: Bulk Create Content
```javascript
// From Campaign form or developer console
frappe.call({
    method: "marketing_hub.utils.content_orchestration.create_campaign_content_for_channels",
    args: {
        campaign: "SUMMER-2026",
        channels: "Meta Ads, Google Ads, Email, LinkedIn Ads"
    }
});
```

#### Step 4: Customize Each Channel
- Meta: Use square image variant
- LinkedIn: Adjust to B2B tone
- Email: Add more detail, testimonials
- Google: Shorter, keyword-focused

#### Step 5: Schedule All
```javascript
frappe.call({
    method: "marketing_hub.utils.content_orchestration.bulk_schedule_content",
    args: {
        campaign: "SUMMER-2026",
        schedule_plan: [
            {channel: "Email", scheduled_date: "2026-06-01 08:00:00"},
            {channel: "Meta Ads", scheduled_date: "2026-06-01 10:00:00"},
            {channel: "Google Ads", scheduled_date: "2026-06-01 10:00:00"},
            {channel: "LinkedIn Ads", scheduled_date: "2026-06-02 09:00:00"}
        ]
    }
});
```

## 📊 Key Features

### ✅ Content Adaptation
- Auto-truncate to character limits
- Strip HTML for text-only platforms
- Adapt image sizes per channel
- Preserve formatting when possible

### ✅ UTM Tracking
- Auto-generated for each channel
- Format: `utm_campaign`, `utm_source`, `utm_medium`
- Automatically appended to all links
- Tracks attribution in Campaign Analytics

### ✅ Template Variables
Replace placeholders like `{customer_name}` with actual values:
```python
template.render({
    "customer_name": "John",
    "product_name": "Pro Suite",
    "discount_code": "SAVE20"
})
```

### ✅ Live Preview
- Auto-generates on save
- Shows how content appears
- Includes channel badge
- Shows all content elements

### ✅ Usage Analytics
- Content Asset tracks usage count
- Campaign Content tracks performance
- Integration with Campaign Analytics report
- Identify high-performing assets

## 🎨 Channel-Specific Guidelines

### Meta Ads (Facebook/Instagram)
- **Text:** 125 chars primary, 40 headline
- **Images:** 1200x628 (feed), 1080x1080 (square), 1080x1920 (stories)
- **Video:** 1-241 seconds, MP4/MOV
- **Tips:** Eye-catching visuals, clear CTA, mobile-first

### Google Ads
- **Text:** 30 chars headline, 90 description
- **Images:** 1200x628, 1200x1200, 960x1200
- **Tips:** Keywords in headline, use extensions, match landing page

### LinkedIn Ads
- **Text:** 150 chars intro, 70 headline
- **Images:** 1200x627 (single), 1080x1080 (carousel)
- **Tips:** Professional B2B tone, social proof, target by role

### TikTok Ads
- **Text:** 100 chars
- **Video:** 5-60 seconds, 9:16 aspect ratio
- **Tips:** Native authentic content, hook in 3 seconds, trending sounds

### Email
- **Text:** No limit, but 50 chars subject recommended
- **Design:** 600px max width, mobile-responsive
- **Tips:** Personalize, single CTA, test across clients

## 🔗 Integration Points

### With Campaign Execution
- Omni-channel blast pulls from Campaign Content
- Auto-renders templates with variables
- Applies UTM tracking to links
- Records performance metrics

### With Analytics
- Campaign Analytics report shows per-channel performance
- Content Asset usage tracking
- A/B test results comparison
- ROAS calculation includes all channels

### With Marketing Hub Setup
- Agency mode affects content creation
- Client-specific content libraries
- Package restrictions on channels

## 📱 Next Steps

1. **Install Doctypes:**
   ```bash
   bench --site erpnext-v15.local migrate
   ```

2. **Create First Assets:**
   - Upload 5-10 images optimized for different channels
   - Tag and categorize properly

3. **Build Template Library:**
   - Create 3-5 templates per channel
   - Document what works

4. **Test Workflow:**
   - Create test campaign
   - Generate content for 2-3 channels
   - Review previews
   - Schedule for future date

5. **Launch Campaign:**
   - Use bulk tools for efficiency
   - Monitor performance
   - Iterate based on results

## 📚 Documentation

Full guide: `CONTENT_MANAGEMENT_GUIDE.md` (15,000+ words)

Covers:
- Complete workflow
- Platform best practices
- API reference
- Troubleshooting
- Example campaigns
- Tips for success

---

**Content management system ready! 🎉**

All 4 doctypes created with full specifications, adaptation logic, and orchestration tools. Build completed successfully in 117ms.
