<template>
  <NotFound v-if="!role" title="No access to Marketing Hub" text="Your account has no marketing role yet. Ask an administrator to give you one." />
  <template v-else>
    <component :is="isMobile ? MobileShell : DesktopShell" :scroll="!$route.meta.fixed">
      <template v-if="!isMobile" #sidebar>
        <Sidebar>
          <SidebarHeader :title="company" :subtitle="role" :menu-items="headerMenu" />
          <div class="min-h-0 flex-1 overflow-y-auto px-2">
            <template v-for="(section, i) in sections" :key="i">
              <SidebarLabel v-if="section.label">{{ section.label }}</SidebarLabel>
              <SidebarItem v-for="item in section.items" :key="item.route" :label="item.label" :icon="item.icon" :route="{ name: item.route }" />
            </template>
          </div>
          <div class="shrink-0 px-2 pb-2">
            <SidebarItem label="Settings" icon="lucide-settings" @click="settingsOpen = true" />
            <SidebarItem label="Help" icon="lucide-circle-help" href="https://docs.frappe.io" target="_blank" />
            <SidebarCollapseToggle />
          </div>
        </Sidebar>
      </template>
      <router-view />
      <template v-if="isMobile" #nav>
        <MobileNav>
          <MobileNavItem v-for="item in sections.flatMap((s) => s.items).slice(0, 5)" :key="item.route" :label="item.label" :icon="item.icon" :route="{ name: item.route }" />
        </MobileNav>
      </template>
    </component>
    <SettingsDialog v-model:open="settingsOpen" v-model:tab="settingsTab">
      <SettingsSidebar>
        <SettingsNavGroup label="Your account">
          <SettingsNavItem value="account"><template #prefix><Avatar size="xs" :label="user.fullName || 'You'" :image="user.image || undefined" /></template>Account</SettingsNavItem>
          <SettingsNavItem value="appearance">Appearance</SettingsNavItem>
        </SettingsNavGroup>
        <SettingsNavGroup v-if="isAdmin()" label="Site">
          <SettingsNavItem value="desk">Desk setup</SettingsNavItem>
        </SettingsNavGroup>
      </SettingsSidebar>
      <SettingsContent>
        <SettingsPanel value="account">
          <SettingsHeader title="Account" description="Who you are signed in as and what you can do here." />
          <SettingsBody>
            <SettingsRow title="Name"><span class="text-base text-ink-gray-8">{{ user.fullName || "—" }}</span></SettingsRow>
            <SettingsRow title="Role in Marketing Hub"><span class="text-base text-ink-gray-8">{{ role }}</span></SettingsRow>
            <SettingsRow title="Sign out" description="End this session on this device."><Button label="Log out" @click="logout" /></SettingsRow>
          </SettingsBody>
        </SettingsPanel>
        <SettingsPanel value="appearance">
          <SettingsHeader title="Appearance" />
          <SettingsBody>
            <SettingsRow title="Color scheme" description="System follows your device."><Select :model-value="colorScheme" :options="schemes" @update:model-value="setColorScheme" /></SettingsRow>
          </SettingsBody>
        </SettingsPanel>
        <SettingsPanel value="desk">
          <SettingsHeader title="Desk setup" description="Brands, channels, roles and accounting are set up in Desk." />
          <SettingsBody>
            <SettingsRow title="Marketing Hub Settings" description="Channels, the OOH purchase item and defaults."><Button label="Open" @click="go('/app/marketing-hub-settings')" /></SettingsRow>
            <SettingsRow title="Desk" description="The full ERPNext workspace."><Button label="Open Desk" @click="go('/app')" /></SettingsRow>
          </SettingsBody>
        </SettingsPanel>
      </SettingsContent>
    </SettingsDialog>
  </template>
</template>

<script setup>
import { computed, ref } from "vue"
import { useRouter } from "vue-router"
import {
  Avatar, Button, DesktopShell, MobileShell, MobileNav, MobileNavItem, Select, SettingsBody, SettingsContent, SettingsDialog, SettingsHeader,
  SettingsNavGroup, SettingsNavItem, SettingsPanel, SettingsRow, SettingsSidebar, Sidebar, SidebarCollapseToggle, SidebarHeader, SidebarItem,
  SidebarLabel, useColorScheme,
} from "frappe-ui"
import NotFound from "@/pages/ErrorState.vue"
import { hasRole, isAdmin, primaryRole, user } from "@/lib/session"
import { NAV } from "@/lib/nav"
import { isMobile } from "@/lib/viewport"

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
const company = "Marketing Hub"

const go = (url) => (window.location.href = url)
const logout = () => go("/api/method/logout")

// The header menu: switch to another installed app, then the account actions.
const apps = computed(() => (window.installed_apps || []).filter((a) => a.name !== "marketing_hub" && a.route))
const headerMenu = computed(() => [
  ...(apps.value.length ? [{ group: "Switch app", options: apps.value.map((a) => ({ label: a.title, icon: "lucide-layout-grid", onClick: () => go(a.route) })) }] : []),
  { group: user.value.fullName || "Account", options: [
    { label: "Settings", icon: "lucide-settings", onClick: () => (settingsOpen.value = true) },
    { label: "Open Desk", icon: "lucide-layout-dashboard", onClick: () => go("/app") },
    { label: "Log out", icon: "lucide-log-out", onClick: logout },
  ] },
])

const settingsOpen = ref(false)
const settingsTab = ref("account")
const { colorScheme, setColorScheme } = useColorScheme()
const schemes = [{ label: "System", value: "system" }, { label: "Light", value: "light" }, { label: "Dark", value: "dark" }]
</script>
