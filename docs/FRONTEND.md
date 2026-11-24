# Frontend

One Vue 3 app at `/marketing` serves every role, clients included. It is built on frappe-ui and
uses no other component library.

## Structure

- `src/layouts/AppLayout.vue`: frappe-ui `DesktopShell` with a `Sidebar` on a desktop, `MobileShell`
  with a `MobileNav` tab bar on a phone. The sidebar comes from `src/lib/nav.js` by role; an item
  appears only if its route exists and the role may open it.
- `src/lib/session.js`: roles from the page boot (`window.frappe.boot.user.roles`).
- `src/router.js`: each route lists the roles that may open it. A System Manager may open all.
- `src/components/AppHeader.vue`: the header of every page. Desktop `PageHeader`; phone
  `PageHeaderMobile` with a back button on detail pages.
- `src/components/ListScreen.vue`: the list page used by Exercises, Content, Placements, Out of
  home, Vendors, Purchase orders and Leads. It owns loading, empty, error and phone states.
- Data is read with frappe-ui's `useList`, `useDoc`, `useNewDoc` and `useCall`; charts come from
  `frappe-ui/charts`.

## Layout rules

- The app is one screen tall (`index.css` sets `html, body, #app` to 100%). The sidebar and the
  page header never scroll; each pane scrolls on its own. A route with `meta.fixed` turns the
  shell's page scroll off (list screens, Approvals); every other route scrolls inside the shell.
- Every header is 48px with the same gutter (`px-3 sm:px-5`): the sidebar header, `PageHeader`
  (`AppHeader`) and `PaneHeader`, so they sit on one line.
- A list screen is always full width. Every record opens on a page of its own (`/placements/:name`, `/content/:name`, and so on) through `RecordPage`: the record's details take the wide left column; attachments (`AttachmentList`) and meta take the narrow right column (320px). On a phone the right column stacks under the details. Approvals is the one two-pane screen, because it is a queue of decisions, not a record.
- The sidebar footer holds Settings, Help and the collapse toggle. The header menu switches to
  another installed app, opens Settings or Desk, and logs out.

## Page states

Every page has a loading, an error and an empty state, and a detail page has a no-access state.
Lists show skeleton rows while loading; charts and number cards use their own `loading` prop.

## Screens by role

Each role has its own sidebar and a complete screen set; the same record opens the same way for all of them, and only the actions differ.

| Role | Home | Screens |
|---|---|---|
| Brand Manager | Dashboard | Approvals, Exercises (8 tabs, Edit), Content (4 views), Placements (Approve, Reject), Out of home (Approve, map), Leads, Reports |
| Marketing Head | Home | Approvals (covers an absent Brand Manager), Exercises (Overview, Budget, Changes), Cross-brand report |
| Content Lead, Media Planner | Home | Exercises (Overview, Plan, Content), Content (4 views), Request a change |
| Publisher | Home | Placements (Schedule), Content (4 views) |
| OOH Coordinator | Home | Out of home (New booking, map, proof), Vendors, Purchase orders, Exercises |
| Client (read only) | Overview | Exercises, Out of home, Posted content, Results, Spend |
| Admin | Setup guide | Channels, Add channel |

Rules the screens follow: only the exercise's Brand Manager changes things directly; everyone else submits a change request or a placement through its ERPNext workflow, which routes to the approver. A placement shows its `status` (Scheduled, Posted, Failed) and, separately, its `approval_state` (Pending, Approved, Rejected). An OOH booking has no reject step.

## State inventory

The design canvas has a board for each of these, per list and role: loading skeleton, empty (with its first action), error (list failed, record not openable, tab failed) and toast (approved, approve failed, booking approved, saved, sent for approval). `frontend/e2e/ui-states/findings.json` lists the review findings, including the ones not fixed (the Approvals page decides its pane from five flags; Reports and Cross-brand show empty text before data arrives).

## Not yet checked

The pages have not been built or opened in a browser. The review in `review-ui-states` (Playwright
capture of every state) needs a running site and has not been run. Run `yarn install && yarn build`
in `frontend/`, then `bench migrate`, before the first look.

## Screens beyond the lists

- **Purchase orders, leads, placements, exercises, content, out-of-home:** a record opens on its own page with details on the left and attachments and meta on the right (`RecordPage`). The list keeps the full width.
- **Content views:** Content has a view switch (List, Kanban, Calendar, Report) on one route; there is no calendar page. frappe-ui 1.2.0 has no Kanban or Report component and only an experimental Calendar, so `ContentKanban`, `ContentCalendar` and the report are local components built from frappe-ui parts.
- **Out of home map** (`/out-of-home-map`): Leaflet with OpenStreetMap tiles; a booking is drawn where its OOH Site's latitude and longitude are. Needs `yarn install` for `leaflet`.
- **Proof of posting** (`/proof/:name`): a phone page; day and night photos attach to the OOH Booking as files.
- **Setup guide** (`/setup`, System Manager): brand, team, channels, first exercise. Opened from Settings, Desk setup.
- **Add channel** dialog on Channels lists each Social Media Network and whether a sender is installed.

None of these has been run: there is no bench or `node_modules` in the session that wrote them.
