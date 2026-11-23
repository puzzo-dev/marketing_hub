// Who is signed in and what role they work in. The roles come from the page boot
// (window.frappe.boot.user.roles), so nothing is fetched before the first screen.
// The role names are the proposed ones from the spec pack; map them here if a site
// names them differently.
import { computed } from "vue"

export const ROLES = {
  head: "Marketing Head",
  manager: "Brand Manager",
  planner: "Media Planner",
  contentLead: "Content Lead",
  publisher: "Publisher",
  ooh: "OOH Coordinator",
  client: "Marketing Client",
}

// A site that still uses the old role keeps working as a Brand Manager.
const LEGACY = { "Marketing Manager": ROLES.manager }

const bootRoles = () => window.frappe?.boot?.user?.roles || []

export const roles = computed(() => {
  const all = new Set(bootRoles())
  for (const [old, now] of Object.entries(LEGACY)) if (all.has(old)) all.add(now)
  return all
})

export const isAdmin = () => roles.value.has("System Manager")
export const hasRole = (...wanted) => isAdmin() || wanted.some((r) => roles.value.has(r))

// The role the sidebar and the home screen follow. The first match in this order wins,
// so a person with two roles sees the one that can do more.
const ORDER = [ROLES.head, ROLES.manager, ROLES.planner, ROLES.contentLead, ROLES.publisher, ROLES.ooh, ROLES.client]
export const primaryRole = computed(() => (isAdmin() ? ROLES.manager : ORDER.find((r) => roles.value.has(r)) || null))

export const user = computed(() => ({
  id: window.frappe?.session?.user,
  fullName: window.frappe?.session?.user_fullname,
  image: window.frappe?.session?.user_image,
}))
