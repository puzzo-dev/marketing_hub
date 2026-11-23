<template>
  <NotFound v-if="!role" title="No access to Marketing Hub" text="Your account has no marketing role yet. Ask an administrator to give you one." />
  <component :is="isMobile ? MobileShell : DesktopShell" v-else :scroll="!$route.meta.fixed">
    <template v-if="!isMobile" #sidebar>
      <Sidebar>
        <SidebarHeader :title="company" :subtitle="role" :menu-items="accountMenu" />
        <div class="flex-1 overflow-y-auto px-2">
          <template v-for="(section, i) in sections" :key="i">
            <SidebarLabel v-if="section.label">{{ section.label }}</SidebarLabel>
            <SidebarItem v-for="item in section.items" :key="item.route" :label="item.label" :icon="item.icon" :route="{ name: item.route }" />
          </template>
        </div>
        <SidebarItem label="Help" icon="lucide-circle-help" href="https://docs.frappe.io" target="_blank" />
        <SidebarCollapseToggle />
      </Sidebar>
    </template>
    <router-view :key="$route.fullPath" />
    <template v-if="isMobile" #nav>
      <MobileNav>
        <MobileNavItem v-for="item in sections.flatMap((s) => s.items).slice(0, 5)" :key="item.route" :label="item.label" :icon="item.icon" :route="{ name: item.route }" />
      </MobileNav>
    </template>
  </component>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from "vue"
import {
  DesktopShell, MobileShell, MobileNav, MobileNavItem, Sidebar, SidebarHeader, SidebarItem, SidebarLabel, SidebarCollapseToggle,
} from "frappe-ui"
import NotFound from "@/pages/ErrorState.vue"
import { useRouter } from "vue-router"
import { hasRole, primaryRole, user } from "@/lib/session"
import { NAV } from "@/lib/nav"

const role = computed(() => primaryRole.value)
const router = useRouter()
// Only routes that exist and that this person may open get a sidebar item.
const sections = computed(() =>
  (NAV[role.value] || [])
    .map((s) => ({ ...s, items: s.items.filter((i) => router.hasRoute(i.route) && canOpen(i.route)) }))
    .filter((s) => s.items.length),
)
const canOpen = (name) => {
  const allowed = router.getRoutes().find((r) => r.name === name)?.meta.roles
  return !allowed || hasRole(...allowed)
}
const company = computed(() => window.frappe?.boot?.sitename?.split(".")[0] || "Marketing Hub")
const accountMenu = computed(() => [
  { label: user.value.fullName || "Account", disabled: true },
  { label: "Open Desk", icon: "lucide-settings-2", onClick: () => (window.location.href = "/app") },
  { label: "Log out", icon: "lucide-log-out", onClick: () => (window.location.href = "/api/method/logout") },
])

// One shell per viewport: the sidebar on a desktop, a tab bar on a phone.
const query = window.matchMedia("(max-width: 639px)")
const isMobile = ref(query.matches)
const onChange = (e) => (isMobile.value = e.matches)
query.addEventListener("change", onChange)
onBeforeUnmount(() => query.removeEventListener("change", onChange))
</script>
