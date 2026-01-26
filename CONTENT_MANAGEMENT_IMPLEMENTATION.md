# Content Management Implementation

## Overview
Complete content library and template management system for Marketing Hub portal.

## Features Implemented

### 1. Asset Management
- **Grid & List Views**: Toggle between visual grid and detailed list views
- **File Upload**: Drag-and-drop interface with multi-file support
- **Asset Types**: Support for images, videos, PDFs, and documents
- **Bulk Actions**: Select multiple assets for status updates or deletion
- **Preview & Download**: Quick actions for asset preview and download
- **Metadata**: Track file size, dimensions, usage count, and modification dates

### 2. Template Management
- **Multi-Channel Templates**: Email, Social Media, SMS, Web, etc.
- **Template Types**: Text, Image, Video, Carousel, Collection
- **Template Editor**: Create templates with name, subject, body text, and CTAs
- **Template Categories**: Organize templates by category
- **Template Variables**: Support for dynamic content placeholders

### 3. Filtering & Search
- **Real-time Search**: Debounced search across asset and template names
- **Multi-Filter Support**:
  - Asset Type (Image, Video, Document, etc.)
  - Channel (Email, Social, SMS, Web, etc.)
  - Status (Draft, Review, Approved, Active, Archived)
  - Category (for templates)
- **View Modes**: Grid and List view options

### 4. Statistics & Analytics
- **Asset Stats**: Total asset count and storage size
- **Usage Tracking**: Monitor asset usage across campaigns
- **Last Modified**: Track recent updates

### 5. User Experience
- **Empty States**: Helpful onboarding for new users
- **Pagination**: Navigate large asset libraries efficiently
- **Responsive Design**: Works across desktop and tablet devices
- **Loading States**: Clear feedback during data operations

## Backend API Endpoints

All endpoints are in `marketing_hub/www/marketing/content.py`:

### Asset Endpoints
- `get_assets()` - List assets with filters, search, and pagination
- `get_asset(name)` - Get single asset details
- `create_asset(data)` - Create new asset
- `update_asset(name, data)` - Update asset metadata
- `delete_asset(name)` - Delete asset
- `bulk_update_assets(names, data)` - Bulk update operations
- `upload_file(file, asset_name, asset_type, channel)` - Upload and auto-create asset

### Template Endpoints
- `get_templates()` - List templates with filters
- `get_template(name)` - Get single template
- `create_template(data)` - Create new template
- `update_template(name, data)` - Update template
- `delete_template(name)` - Delete template

### Helper Endpoints
- `get_asset_types()` - Get available asset types from Media Type doctype
- `get_channels()` - Get channel options
- `get_template_categories()` - Get template categories
- `get_asset_stats()` - Get asset statistics

## Frontend Components

### Content.vue Structure
```
Content.vue (850+ lines)
├── Header Section
│   ├── Title & Description
│   ├── Action Buttons (Upload, New Template)
│   └── Tab Navigation (Assets/Templates)
├── Sidebar Filters
│   ├── Search Input
│   ├── Asset Type Filter
│   ├── Channel Filter
│   ├── Status Filter
│   ├── Category Filter
│   ├── View Mode Toggle (Grid/List)
│   └── Statistics Display
├── Main Content Area
│   ├── Assets Tab
│   │   ├── Bulk Actions Bar
│   │   ├── Grid View
│   │   ├── List View
│   │   ├── Loading State
│   │   └── Empty State
│   ├── Templates Tab
│   │   ├── Grid View
│   │   ├── Loading State
│   │   └── Empty State
│   └── Pagination Controls
├── Upload Dialog
│   ├── Drag-and-Drop Zone
│   ├── Upload Queue
│   └── Asset Metadata Form
└── Template Dialog
    └── Template Creation Form
```

## Data Models

### Content Asset Doctype
- `asset_name` - Asset name
- `asset_type` - Link to Media Type
- `channel` - Marketing channel
- `status` - Draft, Review, Approved, Active, Archived
- `tags` - Categorization tags
- `file_attachment` - Attached file
- `thumbnail` - Preview thumbnail
- `file_size` - File size in bytes
- `dimensions` - Image/video dimensions
- `duration` - Video duration
- `description` - Asset description
- `alt_text` - Accessibility text
- `usage_count` - Times used in campaigns
- `last_used` - Last usage date

### Marketing Template Doctype
- `template_name` - Template name
- `channel` - Marketing channel
- `template_type` - Text, Image, Video, Carousel, Collection
- `status` - Draft, Review, Approved, Active, Archived
- `category` - Template category
- `subject` - Email subject/title
- `headline` - Main headline
- `body_text` - Template body
- `call_to_action` - CTA text and URL
- `primary_asset` - Primary content asset
- `secondary_assets` - Additional assets
- `character_limit` - Channel character limits
- `image_specs` - Image specifications
- `video_specs` - Video specifications
- `link_url` - Destination URL
- `utm_parameters` - Tracking parameters
- `variables` - Dynamic content variables
- `notes` - Internal notes

## Technical Stack

### Frontend
- **Vue 3** - Composition API
- **Frappe UI** - Component library (Badge, Button, FormControl, Dialog)
- **Tailwind CSS** - Utility-first styling
- **Lodash** - Debounce utility

### Backend
- **Frappe Framework** - Python backend
- **Content Asset Doctype** - Asset storage
- **Marketing Template Doctype** - Template storage
- **File Doctype** - File management

## User Workflows

### Upload Asset Workflow
1. Click "Upload Asset" button
2. Drag-and-drop files or browse
3. Select asset type (Image, Video, etc.)
4. Optionally select channel
5. Click "Upload" to process
6. Assets automatically appear in library

### Create Template Workflow
1. Click "New Template" button
2. Enter template name
3. Select channel and template type
4. Add subject/title
5. Write body text
6. Click "Create Template"
7. Template appears in templates tab

### Bulk Asset Management
1. Switch to Assets tab
2. Select multiple assets using checkboxes
3. Choose bulk action:
   - Mark Approved
   - Archive
   - Delete
4. Confirm action
5. Changes applied to all selected assets

## Integration Points

### With Campaigns
- Assets can be linked to campaigns via `Campaign Content` doctype
- Track asset usage in campaigns
- Monitor performance metrics

### With Email Builder
- Templates available in email composition
- Assets available for email content
- Auto-populate UTM parameters

### With Social Media
- Platform-specific asset specs
- Character limit enforcement
- Image dimension validation

### With Analytics
- Asset usage tracking
- Template performance metrics
- Channel effectiveness

## Next Steps

### Planned Enhancements
1. **Asset Preview Modal** - Full-screen preview with metadata editing
2. **Template Preview** - Live template preview with variable substitution
3. **Asset Collections** - Group related assets
4. **Version Control** - Track asset and template versions
5. **Approval Workflows** - Multi-stage review process
6. **Asset Tagging** - Advanced categorization with tags
7. **Smart Search** - AI-powered content discovery
8. **Asset Recommendations** - Suggest relevant assets for campaigns

### Integration Tasks
1. Connect with Campaign Content doctype
2. Integrate with Email Builder
3. Add to Social Media posting workflow
4. Link with Landing Page builder
5. Connect to Analytics dashboard

## Testing Checklist

- [ ] Load assets in grid view
- [ ] Load assets in list view
- [ ] Upload single file
- [ ] Upload multiple files
- [ ] Create new template
- [ ] Edit asset metadata
- [ ] Delete single asset
- [ ] Bulk select and approve assets
- [ ] Bulk archive assets
- [ ] Bulk delete assets
- [ ] Search assets by name
- [ ] Filter by asset type
- [ ] Filter by channel
- [ ] Filter by status
- [ ] Toggle view modes
- [ ] Pagination navigation
- [ ] Download asset
- [ ] View asset stats
- [ ] Switch between tabs

## Build Instructions

```bash
# Build the app
cd /home/puxxo/CodeBase/erpNext/frappe-bench-v15
bench build --app marketing_hub

# Copy index.html to www directory
cd apps/marketing_hub
cp marketing_hub/public/desk/index.html marketing_hub/www/marketing/index.html

# Restart server if needed
cd ../..
bench restart
```

## Access URL
http://127.0.0.1:8002/marketing (Content tab)

## Files Modified/Created

### New Files
- `marketing_hub/www/marketing/content.py` (325 lines)

### Modified Files
- `marketing_hub/desk/src/pages/Content.vue` (850+ lines - complete rewrite)

### Existing Doctypes Used
- `Content Asset` - Asset storage
- `Marketing Template` - Template storage
- `Media Type` - Asset type definitions
- `File` - File management

## Notes
- All API endpoints are whitelisted for portal access
- File uploads use Frappe's built-in file upload API
- CSRF token is automatically included in requests
- Pagination defaults to 20 items per page
- Search is debounced by 300ms for performance
