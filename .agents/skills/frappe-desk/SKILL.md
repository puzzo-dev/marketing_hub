---
description: How to build and customize Frappe Desk workspaces, reports (script/query/report-builder), charts, Portal pages, Vue inside Desk, link formatters, and the Apps Page hook
---

# Frappe Framework — Desk, Workspaces, Reports & Portal

> Sources: https://docs.frappe.io/framework/user/en/desk/workspace, /blocks, /customization, /access,
> /reports/script-report, /query-report, /report-builder, /portal-pages, /apps-page,
> /guides/desk, /guides/desk/making_charts, /guides/desk/formatter_for_link_fields,
> https://docs.frappe.io/framework/using-vue-inside-a-desk-page

---

## 1. Workspaces

### Creating a Workspace
1. Click **Create Workspace** button
2. Enter Title and click Create
3. For child: select parent in the **Parent** field

### Sidebar Sections
- **MY WORKSPACES** — private, visible only to owner
- **PUBLIC** — visible to all users (requires Workspace Manager role to create/edit/delete)
- Drag & drop to rearrange or nest as child/parent

### Workspace Blocks

| Block | Purpose | Key Features |
|-------|---------|-------------|
| **Text** | Paragraph/description | Markdown-like formatting |
| **Chart** | Any Dashboard Chart | Links to `Dashboard Chart` doctype |
| **Shortcut** | Quick link to DocType/Report/Page | Can include filters, shows record count pill, choose opening view |
| **Spacer** | Whitespace between blocks | Position control |
| **Onboarding** | Step-by-step new user guide | Description + optional video link |
| **Quick List** | Recently updated records | Supports filters, refresh, create, open list view |
| **Number Card** | Existing Number Card display | Links to `Number Card` doctype |

### Customization (Edit Mode)

**Workspace-level** (via sidebar):
- Edit details (title, icon, parent/child, public/private)
- Create duplicate
- Delete / Hide workspace
- Rearrange position (drag & drop)

**Page-level** (Edit Mode button):
- Add / Edit / Remove blocks
- Resize block width
- Rearrange blocks (drag & drop)

> **Best Practice**: Use the workspace builder UI for all customization. Adding blocks via the workspace document won't know the correct position.

### Access Control

| Mechanism | How It Works |
|-----------|-------------|
| **Modules** | Users see workspaces based on module access. Remove module → workspace hidden |
| **Roles** | Restrict workspace even when module is accessible. E.g., only `Website Manager` sees Website Workspace |
| **Default Workspace** | Set per user via My Settings → Default Workspace field |

### Fixtures

```python
# hooks.py — include workspaces in app fixtures
fixtures = [
    {"dt": "Workspace", "filters": [["module", "=", "Marketing Hub"]]},
]
```

---

## 2. Reports

### 2.1 Script Report (Most Powerful)

File structure:
```
module/report/report_name/
├── report_name.json    # Report definition
├── report_name.py      # Python: execute() function
└── report_name.js      # JS: client-side filters
```

**Python — `execute()` function:**

```python
def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    report_summary = get_summary(data)
    return columns, data, None, chart, report_summary
    # Returns: columns, data, message, chart, report_summary, skip_total_rows
```

**Columns format:**
```python
columns = [
    {"fieldname": "account", "label": _("Account"), "fieldtype": "Link", "options": "Account", "width": 200},
    {"fieldname": "balance", "label": _("Balance"), "fieldtype": "Currency", "options": "currency", "width": 120},
]
```

**Data format:** List of dicts matching column fieldnames:
```python
data = [
    {"account": "Marketing - ACME", "balance": 15000.00},
]
```

**Chart return format:**
```python
chart = {
    "data": {
        "labels": ["Jan", "Feb", "Mar"],
        "datasets": [
            {"name": _("Budget"), "values": [1000, 1200, 800]},
            {"name": _("Actual"), "values": [900, 1100, 750]}
        ]
    },
    "type": "bar",  # bar, line, pie, donut, heatmap
    "colors": ["#98D8C8", "#F7464A"],
}
```

**Report summary (top-line KPIs):**
```python
report_summary = [
    {"value": profit, "indicator": "Green" if profit > 0 else "Red",
     "label": _("Total Profit"), "datatype": "Currency", "currency": "INR"}
]
```

**JS filters with `depends_on`:**
```javascript
frappe.query_reports['Campaign Performance'] = {
    filters: [
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("Company"),
            reqd: 1,
        },
        {
            fieldname: "periodicity",
            label: __("Periodicity"),
            fieldtype: "Select",
            options: ["Monthly", "Quarterly", "Yearly"],
            default: "Monthly",
            depends_on: 'eval:doc.company=="Acme Corp"',
        },
    ],
};
```

### 2.2 Query Report

SQL-only. Created via `/app/report`:
1. Set Report Type = "Query Report"
2. Set Reference DocType (controls access)
3. Set Module (determines section)
4. Write SQL query — use `%(filter_name)s` for parameterized filters

### 2.3 Report Builder

Visual, no-code. Access from any doctype List → Menu → Report Builder:
- Drag/drop columns
- Add filters, group by, sort
- Save and share

---

## 3. Portal Pages

### Route Mapping

The `www` folder maps directly to website URLs:
```
custom_app/www/
├── custom_page.html          → /custom_page
├── custom_page.py            → context provider
├── custom_page.css            → page styles
├── custom_page.js             → page scripts
└── custom_page/
    ├── index.html             → /custom_page
    └── subpage.html           → /custom_page/subpage
```

- `.html` or `.md` files both work
- Override standard pages by creating same-named file in your app's `www/`

### Jinja Templating

```html
{% extends "templates/web.html" %}
{% block title %}{{ _("Marketing Dashboard") }}{% endblock %}
{% block page_content %}
<h1>{{ _("Marketing Dashboard") }}</h1>
{% if campaigns %}
<ul>
  {% for c in campaigns %}
  <li>{{ c.campaign_name }} — {{ c.status }}</li>
  {% endfor %}
</ul>
{% endif %}
{% endblock %}
```

### Python Context (`get_context`)

```python
# custom_page.py
import frappe

def get_context(context):
    context.campaigns = frappe.get_all("Marketing Campaign",
        fields=["campaign_name", "status"],
        filters={"status": "Running"})
    return context
```

### Context Keys

| Key | Effect |
|-----|--------|
| `add_breadcrumbs` | Auto-generate breadcrumbs from folder structure |
| `no_breadcrumbs` | Hide breadcrumbs |
| `show_sidebar` | Show portal sidebar |
| `no_header` | Hide page header |
| `no_cache` | Disable page caching |
| `sitemap` | Include/exclude from sitemap (0 or 1) |
| `title` | Page title |
| `base_template` | Custom base template path |

Set via HTML comments, frontmatter, or Python context.

**Frontmatter example:**
```markdown
---
title: Marketing Dashboard
metatags:
  description: Real-time marketing analytics
---
# Marketing Dashboard
...
```

### Vue SPA as Portal Page

For Vue SPAs served via portal, use `website_route_rules` in `hooks.py`:

```python
website_route_rules = [
    {"from_route": "/marketing/<path:app_path>", "to_route": "marketing"},
]
```

### Home Page Configuration

Priority: Role → Portal Settings (logged in) → `get_website_user_home_page` hook → Website Settings (guest)

---

## 4. Vue Inside Desk Pages

### Step 1: Create Page DocType

Navigate to `/app/page` → Create new Page. This generates:
```
module/page/my_page/
├── __init__.py
├── my_page.json
└── my_page.js
```

### Step 2: Create Vue Bundle

Create in `public/js/`:
```
app/public/js/my_page/
├── MyPage.vue
└── my_page.bundle.js
```

**MyPage.vue:**
```vue
<script setup>
import { ref } from 'vue';
const message = ref('Hello from Vue!');
</script>
<template>
  <h1>{{ message }}</h1>
</template>
```

**my_page.bundle.js:**
```javascript
import { createApp } from 'vue';
import MyPage from './MyPage.vue';

function setup_vue(wrapper) {
    const app = createApp(MyPage);
    app.mount(wrapper.get(0));
    return app;
}
frappe.ui.setup_vue = setup_vue;
export default setup_vue;
```

### Step 3: Load Bundle in Page JS

```javascript
frappe.pages['my-page'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'My Page',
        single_column: true,
    });
    // Hot reload in dev mode
    if (frappe.boot.developer_mode) {
        frappe.hot_update ??= frappe.hot_update;
        frappe.hot_update.push(() => load_vue(wrapper));
    }
};

frappe.pages['my-page'].on_page_show = (wrapper) => load_vue(wrapper);

async function load_vue(wrapper) {
    const $parent = $(wrapper).find('.layout-main-section');
    $parent.empty();
    await frappe.require('my_page.bundle.js');
    frappe.my_page_app = frappe.ui.setup_vue($parent);
}
```

### Build
```bash
bench build                        # all apps
npm run build -- --apps myapp --watch  # dev mode with hot reload
```

---

## 5. Link Field Formatter

Customize how Link fields display:

```javascript
frappe.form.link_formatters['Marketing Campaign'] = function(value, doc) {
    if (doc.campaign_name && doc.campaign_name !== value) {
        return value + ': ' + doc.campaign_name;
    }
    return value;
}
```

> **Note**: Both `name` and the descriptive field must be in the document. Add to `build.json` or load before doc.

---

## 6. Apps Page Hook

Show your app on the Frappe Apps Page (`/app`):

```python
# hooks.py (v15+)
add_to_apps_screen = [{
    "name": "marketing_hub",
    "logo": "/assets/marketing_hub/logo.png",
    "title": "Marketing Hub",
    "route": "/marketing",
    "has_permission": "marketing_hub.api.check_app_permission"
}]
```

Set a **default app** per user or site-wide so users land directly on login.

---

## 7. Making Charts (frappe-charts)

Use [Frappe Charts](https://frappe.github.io/charts/) for line, bar, percentage, pie, donut, heatmap charts.

Dashboard Chart doctype structure:
```json
{
    "chart_type": "Count",     // Count, Sum, Average, Group By
    "document_type": "Marketing Campaign",
    "based_on": "creation",
    "timespan": "Last Year",
    "time_interval": "Monthly",
    "type": "Bar"              // Bar, Line, Pie, Donut, Heatmap
}
```
