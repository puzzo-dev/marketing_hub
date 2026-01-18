# Marketing Hub - Vue.js Portal Setup

## What Changed

Converted Marketing Hub from Jinja2 templates to a **modern Vue.js SPA** following Helpdesk's architecture.

## Architecture

```
marketing_hub/
├── desk/                          # Vue.js Portal (NEW)
│   ├── src/
│   │   ├── pages/                 # Vue route pages
│   │   │   ├── Dashboard.vue
│   │   │   ├── Campaigns.vue
│   │   │   ├── Social.vue
│   │   │   ├── Analytics.vue
│   │   │   ├── NewCampaign.vue
│   │   │   └── NewSocialPost.vue
│   │   ├── components/
│   │   │   └── Navbar.vue
│   │   ├── App.vue
│   │   ├── router.js
│   │   ├── main.js
│   │   └── index.css
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── package.json
│
├── marketing_hub/
│   ├── public/desk/              # Built assets go here
│   └── www/marketing/
│       ├── index.html            # SPA entry point
│       └── index.py              # API methods
```

## Technology Stack

- **Vue 3** - Composition API
- **Vue Router** - Client-side routing
- **Pinia** - State management
- **Frappe UI** - Component library
- **Tailwind CSS** - Styling
- **Vite** - Build tool

## Development

### Install Dependencies
```bash
cd marketing_hub/desk
yarn install
```

### Development Server
```bash
cd marketing_hub/desk
yarn dev
```
Access at: `http://localhost:5173`

### Production Build
```bash
cd marketing_hub/desk
yarn build
```

## Features

### ✅ Implemented

1. **Modern UI**
   - Clean Tailwind CSS design
   - Responsive layouts
   - Smooth transitions
   - Frappe UI components

2. **Client-Side Routing**
   - `/marketing` - Dashboard
   - `/marketing/campaigns` - Campaign list
   - `/marketing/social` - Social posts
   - `/marketing/analytics` - Analytics table
   - No page reloads

3. **Real-time Data**
   - Frappe UI resources
   - Auto-fetch on mount
   - Reactive updates

4. **Navigation**
   - Top navbar with logo
   - Active route highlighting
   - App switcher dropdown
   - Breadcrumbs

### 🚧 To Implement

1. **Forms**
   - Campaign creation form
   - Social post composer
   - Image upload
   - Form validation

2. **Real-time Features**
   - WebSocket integration
   - Live notifications
   - Auto-refresh stats

3. **Advanced Features**
   - Search functionality
   - Filters and sorting
   - Bulk actions
   - Export functionality

## API Endpoints

### Python Backend (`www/marketing/index.py`)

```python
@frappe.whitelist()
def get_context_for_dev():
    # Dev mode context

@frappe.whitelist()
def get_dashboard_data():
    # Dashboard stats & campaigns
```

Add similar files for:
- `www/marketing/campaigns/index.py`
- `www/marketing/social/index.py`
- `www/marketing/analytics.py`

## Usage

### Access Portal

1. Start Frappe: `bench start`
2. Navigate to: `http://localhost:8000/marketing`
3. Or click "Marketing Hub" in Apps screen

### Adding New Pages

1. Create Vue component in `desk/src/pages/`
2. Add route in `router.js`
3. Add nav link in `Navbar.vue`

Example:
```javascript
// router.js
{
  path: "/marketing/leads",
  name: "Leads",
  component: () => import("@/pages/Leads.vue"),
}
```

### Calling Frappe APIs

```javascript
import { createResource } from "frappe-ui";

const data = createResource({
  url: "marketing_hub.www.marketing.campaigns.index.get_context",
  auto: true, // Auto-fetch on mount
});

// Access data
const campaigns = computed(() => data.data?.campaigns || []);
```

## Comparison with Old Design

| Feature | Jinja Templates | Vue.js SPA |
|---------|----------------|------------|
| **Tech** | Server-rendered HTML | Client-side SPA |
| **Routing** | Server redirects | Vue Router |
| **State** | Page reloads | Reactive state |
| **UX** | Page flickers | Smooth transitions |
| **Dev** | Template syntax | Modern JS/Vue |
| **Reusability** | Template includes | Vue components |
| **Build** | No build step | Vite bundling |

## Benefits

✅ **Modern Stack** - Vue 3, Vite, Tailwind
✅ **Better UX** - No page reloads, smooth navigation
✅ **Component Reuse** - Modular Vue components
✅ **Type Safety** - Can add TypeScript easily
✅ **Fast Development** - Hot module replacement
✅ **Production Ready** - Optimized builds
✅ **Frappe Integration** - Uses frappe-ui library

## Next Steps

1. ✅ Basic portal structure
2. ✅ Dashboard page
3. ✅ Campaigns list page
4. ✅ Social posts page
5. ✅ Analytics page
6. ⏳ Create/edit forms
7. ⏳ WebSocket integration
8. ⏳ Advanced features

## Notes

- Old Jinja templates can be kept as fallback
- Build assets automatically linked by Frappe
- Use `bench build --app marketing_hub` for full rebuild
- Development mode works with Vite dev server

## Troubleshooting

**Build fails:**
```bash
cd desk
rm -rf node_modules yarn.lock
yarn install
yarn build
```

**Assets not loading:**
```bash
bench clear-cache
bench restart
```

**Hot reload not working:**
- Use `yarn dev` in desk/ folder
- Access via `localhost:5173`
- Not `localhost:8000`
