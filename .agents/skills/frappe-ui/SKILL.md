---
description: How to use the frappe-ui Vue component library including setup, design system tokens, all 30+ components with props/slots/events, data-fetching APIs, utilities and directives
---

# Frappe UI — Component Library & Data-Fetching

> Source: https://ui.frappe.io (v0.1.265+) — Vue 3 component library based on the Frappe design system

---

## 1. Getting Started

### New Project (Starter Template)
```bash
npx degit netchampfaris/frappe-ui-starter frontend
```

### Adding to Existing Frappe App
```bash
bench new-app myapp
cd apps/myapp
npx degit netchampfaris/frappe-ui-starter frontend
bench --site mysite set-config ignore_csrf 1   # prevents CSRF errors in dev
cd frontend && yarn && yarn dev                  # port 8080
```

- Vite dev server proxies to Frappe backend (port 8000)
- Open `http://mysite:8080`
- Production base URL: `/frontend` — change in `src/router.js` via `createWebHistory`
- In production, `csrf_token` is auto-attached to `window` in `index.html`

### Configure Frappe Resource Fetcher

```javascript
// main.js
import { setConfig, frappeRequest, resourcesPlugin } from 'frappe-ui'

setConfig('resourceFetcher', frappeRequest)  // auto-parse Frappe message/exc
app.use(resourcesPlugin)                     // enable Options API resources
```

---

## 2. Design System Tokens

### Background Colors
Prefixed with `surface`. Classes: `bg-surface-gray-2`, `bg-surface-cards`, `bg-surface-modal`, `bg-surface-selected`

| Group | Variants |
|-------|----------|
| Colors | `gray`, `red`, `green`, `amber`, `blue`, `orange`, `violet`, `cyan`, `pink` |
| Surfaces | `menu`, `cards`, `modal`, `selected` |

### Border Colors
Groups: `gray`, `red`, `green`, `amber`, `blue`, `orange`

### Drop Shadow
Standard shadow utilities.

### Border Radius
Standard radius utilities.

---

## 3. Components Reference

All imported from `frappe-ui`:

```javascript
import {
  Alert, Avatar, Badge, Breadcrumbs, Button, Calendar, Charts,
  Checkbox, Combobox, DatePicker, Dialog, Dropdown, ErrorMessage,
  FileUploader, ListView, MonthPicker, MultiSelect, Password,
  Popover, Progress, Rating, Select, Sidebar, Slider, Switch,
  Tabs, TextEditor, TextInput, Textarea, TimePicker, Tooltip, Tree
} from 'frappe-ui'
```

### Alert
Status message with themed styling.
- **Props**: `title`, `theme` (info/warning/error/success)
- **Slots**: `icon`, `default`, `actions`
- **Events**: `close`
- Supports controlled state (v-model)

### Avatar
User/entity avatar with image, initials, or icon fallback.

### Badge
Status labels, counts, or metadata.
- **Props**: `theme` (color), `size`, `variant` (solid/subtle/outline), `label`
- **Slots**: `prefix`, `default` (overrides label), `suffix`

### Breadcrumbs
Navigation breadcrumb trail.

### Button
Primary action element with variants, sizes, icons, loading state.

### Calendar
Full calendar component.

### Charts
Interactive data visualization (frappe-charts based). Bar, line, pie, donut, heatmap.

### Checkbox
Checkbox input.

### Combobox
Searchable select/autocomplete.

### DatePicker / MonthPicker / TimePicker
Date, month, and time selection components.

### Dialog
Modal dialog with configurable header, body, and actions.

### Dropdown
Flexible action/option menu with groups, submenus, switches, and custom triggers.
- **Props**: `button` (config object), `options` (array), `placement`, `side`, `offset`
- **Slots**: `default` (custom trigger, receives `{open, close}`), `item` (custom item rendering)

### ErrorMessage
Error display component.

### FileUploader
File upload with drag-and-drop.

### ListView
Data table/list component.

### MultiSelect
Multiple selection input.

### Password
Password input with visibility toggle.

### Popover
Floating content triggered by click/hover.

### Progress
Progress bar/indicator.

### Rating
Star/score rating input.

### Select
Single-value dropdown select.

### Sidebar
Vertical navigation panel with sections and collapsible groups.
- **Props**: `items`, `sections`
- **Slots**: `header`, `footer`
- **Events**: emit on selection change

### Slider
Range slider input.

### Switch
Toggle on/off control.
- **Props**: `size`, `label`, `description` (helper text), `disabled`, `icon`, `labelClass`
- **Events**: `update:modelValue`

### Tabs
Tab panels for organizing content sections.
- **Props**: `as` (container element), `tabs` (array), `vertical` (boolean)
- **Slots**: `tab` (custom tab trigger), `default` (tab panel content)
- **Events**: `update:modelValue`
- Supports horizontal and vertical orientation, icons

### TextEditor
Rich text editor.

### TextInput
Flexible input for text, numbers, etc.
- **Props**: `type` (text/email/number/password/etc), `size`, `variant`, `placeholder`, `disabled`, `id`, `modelValue`, `debounce` (ms), `required`
- **Slots**: `prefix` (left), `suffix` (right)
- **Events**: `update:modelValue`, `change`, `input`

### Textarea
Multi-line text input.

### Tooltip
Hover/focus tooltip.

### Tree
Hierarchical collapsible tree structure.
- **Props**: `node` (root data), `nodeKey` (unique identifier), `options` (layout/behavior config)
- **Slots**: `node` (full override), `node-icon`, `node-label`

---

## 4. Data Fetching

### 4.1 createResource (Generic API)

```javascript
import { createResource } from 'frappe-ui'

let post = createResource({
  // Request
  url: 'frappe.client.get_list',   // drops /api/method with frappeRequest
  method: 'GET',                    // default: POST
  params: { doctype: 'ToDo' },
  makeParams() { return { id: 1 } },  // dynamic params (reactive)
  debounce: 500,                    // ms

  // State
  initialData: [],
  auto: true,                       // auto-fetch on creation
  cache: 'unique-key',             // string or array; caches in memory + IndexedDB

  // Lifecycle Events
  beforeSubmit(params) {},
  validate(params) {
    if (!params.id) return 'id is required'  // return string = throw error
  },
  onError(error) {},
  onSuccess(data) {},
  transform(data) {                 // transform before setting
    return data.map(d => ({ ...d, open: false }))
  },
})
```

#### API Properties & Methods

```javascript
// Reactive state
post.data           // response data
post.loading        // true during fetch
post.error          // error from request or validate
post.promise        // awaitable promise
post.params         // sent params
post.fetched        // true after first successful fetch
post.previousData   // set to current data during reload

// Actions
post.fetch()                // make the request
post.reload()               // alias for fetch
post.submit({ id: 2 })      // fetch with new params
post.reset()                // reset to initial state
post.update({ url, params })  // update config
post.setData(newData)          // override data
post.setData(data => data.filter(d => d.open))  // modify
```

#### Caching

```javascript
let post = createResource({
  url: 'frappe.client.get_list',
  cache: 'todos',          // string key
  cache: ['todos', filters.value],  // reactive array key
})
// Same cache key in different components → shared data
// Persisted to IndexedDB
```

#### Options API Style

```javascript
export default {
  resources: {
    posts() {
      return {
        url: 'frappe.client.get_list',
        auto: true,  // auto-fetch
      }
    },
  },
  // Access: this.$resources.posts.data
}
```

#### Frappe Backend Integration

```javascript
// With frappeRequest configured, you can drop /api/method:
let todos = createResource({
  url: 'frappe.client.get_list',  // NOT /api/method/frappe.client.get_list
  params: { doctype: 'ToDo' },
})
// Response: data extracted from `message` key, errors from `exc`
```

### 4.2 createListResource (DocType Lists)

```javascript
import { createListResource } from 'frappe-ui'

let todos = createListResource({
  doctype: 'ToDo',
  fields: ['name', 'description', 'status'],
  filters: { allocated_to: 'user@example.com' },
  orderBy: 'creation desc',
  start: 0,
  pageLength: 20,
  auto: true,
  cache: 'todos',
})

// Template usage
<div v-for="todo in todos.data" :key="todo.name">
  {{ todo.description }}
  <Badge>{{ todo.status }}</Badge>
</div>
<Button @click="todos.next()">Next Page</Button>
```

Options API: use `type: 'list'` in resource definition.

### 4.3 createDocumentResource (Single Document)

```javascript
import { createDocumentResource } from 'frappe-ui'

let todo = createDocumentResource({
  doctype: 'ToDo',
  name: 'TODO-0001',
  whitelistedMethods: {
    sendEmail: 'send_email',  // maps to controller @whitelist method
  },
})

// API
todo.doc            // full document object with all fields
todo.setValue.submit({ status: 'Closed' })   // update fields
todo.delete.submit()                          // delete document
todo.sendEmail.submit({ email: 'a@b.com' })  // call whitelisted method
```

Options API: use `type: 'document'`.

---

## 5. Utilities

```javascript
import { debounce, fileToBase64, pageMetaPlugin } from 'frappe-ui'
```

### debounce
```javascript
let debouncedSearch = debounce(onSearch, 500)
// Runs at most once every 500ms
```

### fileToBase64
```javascript
let base64 = fileToBase64(file)  // file: File instance
```

### pageMeta (Reactive Document Title)
```javascript
// main.js
app.use(pageMetaPlugin)

// Component (Options API)
export default {
  pageMeta() {
    return { title: 'Dashboard', emoji: '📊' }
    // or: { title: 'Dashboard', icon: '/path/to/icon.png' }
  }
}
```

---

## 6. Directives

### onOutsideClick
Detect clicks outside an element.

```vue
<template>
  <div v-on-outside-click="handleOutside">...</div>
</template>
<script>
import { onOutsideClickDirective } from 'frappe-ui'
export default {
  directives: { onOutsideClick: onOutsideClickDirective },
  methods: {
    handleOutside() { this.menuOpen = false }
  }
}
</script>
```

### visibility (IntersectionObserver)
Trigger function when element enters/exits viewport.

```vue
<template>
  <div v-visibility="onVisibilityChange">Observed element</div>
</template>
<script>
import { visibilityDirective } from 'frappe-ui'
export default {
  directives: { visibility: visibilityDirective },
  methods: {
    onVisibilityChange(visible, entry) {
      // visible: boolean
      // entry: IntersectionObserverEntry
    }
  }
}
</script>
```
