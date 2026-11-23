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
- A list screen is full width. Opening a record (a nested route such as `/content/:name`) narrows
  the list to a 400px column and shows the record beside it; closing the record gives the width
  back. On a phone the record replaces the list.
- The sidebar footer holds Settings, Help and the collapse toggle. The header menu switches to
  another installed app, opens Settings or Desk, and logs out.

## Page states

Every page has a loading, an error and an empty state, and a detail page has a no-access state.
Lists show skeleton rows while loading; charts and number cards use their own `loading` prop.

## Not yet checked

The pages have not been built or opened in a browser. The review in `review-ui-states` (Playwright
capture of every state) needs a running site and has not been run. Run `yarn install && yarn build`
in `frontend/`, then `bench migrate`, before the first look.
