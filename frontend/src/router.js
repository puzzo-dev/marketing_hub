import { createRouter, createWebHistory } from "vue-router"
import { hasRole, primaryRole, ROLES } from "@/lib/session"

const { manager, head, planner, contentLead, publisher, ooh, client } = ROLES
const staff = [manager, head, planner, contentLead, publisher, ooh]
const isClient = () => primaryRole.value === ROLES.client
const page = (name) => () => import(`./pages/${name}.vue`)

// `roles` lists who may open a route; a System Manager may open all of them.
// `fixed` stops the shell scrolling the page, for screens whose panes scroll alone.
const routes = [
  { path: "/", name: "Home", component: () => (isClient() ? import("./pages/ClientHome.vue") : primaryRole.value === ROLES.manager ? import("./pages/Home.vue") : import("./pages/RoleHome.vue")), meta: { roles: [...staff, client] } },
  { path: "/approvals", name: "Approvals", component: page("Approvals"), meta: { roles: [manager, head], fixed: true } },
  { path: "/exercises/:name/edit", name: "EditExercise", props: true, component: page("EditExercise"), meta: { roles: [manager] } },
  { path: "/exercises/new", name: "NewExercise", component: page("NewExercise"), meta: { roles: [manager] } },
  {
    path: "/exercises", name: "Exercises", meta: { roles: [...staff, client], fixed: true },
    component: () => (isClient() ? import("./pages/ClientExercises.vue") : import("./pages/Exercises.vue")),
    children: [{ path: ":name", name: "Exercise", props: true, component: () => (isClient() ? import("./pages/ClientExercise.vue") : import("./pages/Exercise.vue")) }],
  },
  { path: "/content/new", name: "NewContent", component: page("NewContent"), meta: { roles: [manager, planner, contentLead] } },
  {
    path: "/content", name: "Content", component: page("Content"), meta: { roles: [manager, planner, contentLead, publisher], fixed: true },
    children: [{ path: ":name", name: "ContentDetail", props: true, component: page("ContentDetail") }],
  },
  {
    path: "/placements", name: "Placements", component: page("Placements"), meta: { roles: [manager, publisher], fixed: true },
    children: [{ path: ":name", name: "Placement", props: true, component: page("Placement") }],
  },
  { path: "/out-of-home/new", name: "NewOOHBooking", component: page("NewOOHBooking"), meta: { roles: [manager, ooh] } },
  {
    path: "/out-of-home", name: "OutOfHome", component: page("OutOfHome"), meta: { roles: [manager, ooh], fixed: true },
    children: [{ path: ":name", name: "OOHBooking", props: true, component: page("OOHBooking") }],
  },
  { path: "/vendors", name: "Vendors", component: page("Vendors"), meta: { roles: [ooh], fixed: true } },
  {
    path: "/purchase-orders", name: "PurchaseOrders", component: page("PurchaseOrders"), meta: { roles: [ooh], fixed: true },
    children: [{ path: ":name", name: "PurchaseOrder", props: true, component: page("PurchaseOrder") }],
  },
  { path: "/reports", name: "Reports", component: page("Reports"), meta: { roles: [manager, head] } },
  { path: "/cross-brand", name: "CrossBrand", component: page("CrossBrand"), meta: { roles: [head] } },
  { path: "/channels", name: "Channels", component: page("Channels"), meta: { roles: ["System Manager"] } },
  {
    path: "/leads", name: "Leads", component: page("Leads"), meta: { roles: [manager], fixed: true },
    children: [{ path: ":name", name: "Lead", props: true, component: page("Lead") }],
  },
  { path: "/out-of-home-map", name: "OOHMap", component: page("OOHMap"), meta: { roles: [manager, ooh] } },
  { path: "/proof/:name", name: "OOHProof", props: true, component: page("OOHProof"), meta: { roles: [ooh] } },
  { path: "/setup", name: "Setup", component: page("Setup"), meta: { roles: ["System Manager"] } },
  { path: "/my/content", name: "ClientContent", component: () => import("./pages/ClientList.vue"), props: { kind: "content" }, meta: { roles: [client] } },
  { path: "/my/out-of-home", name: "ClientOOH", component: () => import("./pages/ClientList.vue"), props: { kind: "ooh" }, meta: { roles: [client] } },
  { path: "/my/results", name: "ClientResults", component: () => import("./pages/ClientList.vue"), props: { kind: "results" }, meta: { roles: [client] } },
  { path: "/my/spend", name: "ClientSpend", component: () => import("./pages/ClientList.vue"), props: { kind: "spend" }, meta: { roles: [client] } },
  { path: "/no-access", name: "NoAccess", component: page("NoAccessPage") },
  { path: "/:pathMatch(.*)*", name: "NotFound", component: page("NotFoundPage") },
]

export const router = createRouter({ history: createWebHistory("/marketing"), routes })

router.beforeEach((to) => {
  const allowed = to.meta.roles
  if (allowed && !hasRole(...allowed)) return { name: "NoAccess" }
})
