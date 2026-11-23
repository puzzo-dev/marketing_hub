# Marketing Hub: Desk vs the Vue app

Updated 23 Nov 2026. This replaces the earlier version, which described a separate Jinja portal for clients. There is none: every role uses the same Vue app.

## Two surfaces

| | Vue app (`/marketing`) | Frappe Desk (`/app`) |
|---|---|---|
| Who | Everyone: Brand Managers, planners, content leads, publishers, OOH coordinators, the Marketing Head and clients | System Manager and Marketing Manager doing setup |
| For | Daily operations: approvals, exercises, content, placements, out of home, leads, reports | Setup, accounting, Energy Point rules, Role Permissions Manager, raw records |
| Stack | Vue 3, frappe-ui, Tailwind, Vue Router, Pinia | Standard Frappe |
| Code | `frontend/` | the doctype forms and workspaces |

## How roles work in the Vue app

- One layout. The sidebar lists only what the signed-in role can use; clients get a read-only role whose API returns client-safe fields only.
- Only the Brand Manager assigned to an exercise changes it directly. Everyone else sends a change request, which a Frappe workflow routes to that Brand Manager.
- Brands are isolated with User Permissions plus the app's `has_permission` check.

## Where the details live

- Product, technical and data decisions: the spec pack (PRD, TRD, ERD, User stories, Energy Points guide, Screens and UI), kept as a Claude doc.
- Screen designs: the design canvas linked from the Screens and UI tab.
- Route list: `frontend/src/router.js`.

## Out of date in the code

`frontend/src/layouts/` still has separate `AdminLayout.vue` and `AgentLayout.vue`, chosen by `isAdmin` in `stores/user.js`. The design replaces them with one role-based layout. Nothing has been changed in the code yet.
