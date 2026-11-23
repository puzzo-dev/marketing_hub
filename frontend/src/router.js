import { createRouter, createWebHistory } from "vue-router"
import { hasRole, ROLES } from "@/lib/session"

const { manager, head, planner, contentLead, publisher, ooh, client } = ROLES
const staff = [manager, head, planner, contentLead, publisher, ooh]
const page = (name) => () => import(`./pages/${name}.vue`)

// `roles` lists who may open a route; a System Manager may open all of them.
// `fixed` stops the shell scrolling the page, for screens whose panes scroll alone.
const routes = [
  { path: "/", name: "Home", component: page("Home"), meta: { roles: [...staff, client] } },
  { path: "/approvals", name: "Approvals", component: page("Approvals"), meta: { roles: [manager, head], fixed: true } },
  { path: "/exercises", name: "Exercises", component: page("Exercises"), meta: { roles: [...staff, client] } },
  { path: "/exercises/new", name: "NewExercise", component: page("NewExercise"), meta: { roles: [manager] } },
  { path: "/exercises/:name", name: "Exercise", component: page("Exercise"), props: true, meta: { roles: [...staff, client] } },
  { path: "/content", name: "Content", component: page("Content"), meta: { roles: [manager, planner, contentLead, publisher] } },
  { path: "/placements", name: "Placements", component: page("Placements"), meta: { roles: [manager, publisher] } },
  { path: "/out-of-home", name: "OutOfHome", component: page("OutOfHome"), meta: { roles: [manager, ooh, client] } },
  { path: "/vendors", name: "Vendors", component: page("Vendors"), meta: { roles: [ooh] } },
  { path: "/purchase-orders", name: "PurchaseOrders", component: page("PurchaseOrders"), meta: { roles: [ooh] } },
  { path: "/leads", name: "Leads", component: page("Leads"), meta: { roles: [manager] } },
  { path: "/no-access", name: "NoAccess", component: page("NoAccessPage") },
  { path: "/:pathMatch(.*)*", name: "NotFound", component: page("NotFoundPage") },
]

export const router = createRouter({ history: createWebHistory("/marketing"), routes })

router.beforeEach((to) => {
  const allowed = to.meta.roles
  if (allowed && !hasRole(...allowed)) return { name: "NoAccess" }
})
