<template>
  <NotFound v-if="!role" title="No access to Marketing Hub" text="Your account has no marketing role yet. Ask an administrator to give you one." />
  <template v-else>
    <div class="h-screen w-full bg-surface-base text-ink-gray-9">
    <component :is="isMobile ? MobileShell : DesktopShell" :scroll="!$route.meta.fixed">
      <template v-if="!isMobile" #sidebar>
        <Sidebar width="14rem" class="border-r">
          <SidebarHeader :title="company" :subtitle="role" :menu-items="headerMenu" />
          <ScrollArea class="min-h-0 flex-1" viewport-class="px-2 pt-0.5 pb-10">
            <div class="flex flex-col gap-4">
            <div v-for="(section, i) in sections" :key="i" class="flex flex-col gap-0.5">
              <div v-if="section.label" class="flex h-7 items-center"><SidebarLabel>{{ section.label }}</SidebarLabel></div>
              <div class="flex flex-col gap-0.5">
                <SidebarItem v-for="item in section.items" :key="item.route" :route="{ name: item.route }">
                  <template #prefix><span :class="item.icon" class="size-4" aria-hidden="true" /></template>
                  <span class="flex-1 truncate text-sm">{{ item.label }}</span>
                  <template v-if="item.route === 'Approvals' && waiting" #suffix><Badge variant="ghost" :label="String(waiting)" /></template>
                </SidebarItem>
              </div>
            </div>
            </div>
          </ScrollArea>
          <div class="mt-auto px-2 pb-2">
            <SidebarItem label="Settings" icon="lucide-settings" @click="settingsOpen = true" />
            <SidebarCollapseToggle />
          </div>
        </Sidebar>
      </template>
      <div class="flex min-h-0 flex-1 flex-col" :class="!fullWidth && !isMobile && 'mx-auto w-full max-w-screen-xl'"><router-view /></div>
      <template v-if="isMobile" #nav>
        <MobileNav>
          <MobileNavItem v-for="item in sections.flatMap((s) => s.items).slice(0, 5)" :key="item.route" :label="item.label" :icon="item.icon" :route="{ name: item.route }" />
        </MobileNav>
      </template>
    </component>
    </div>
    <TweakPanel v-if="!isMobile" />
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
            <SettingsRow title="Full width" description="Off keeps the page in a centered column on a wide screen."><Switch v-model="fullWidth" /></SettingsRow>
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
  Avatar, Badge, Button, ScrollArea, DesktopShell, MobileShell, MobileNav, MobileNavItem, Select, SettingsBody, SettingsContent, SettingsDialog, SettingsHeader,
  SettingsNavGroup, SettingsNavItem, SettingsPanel, SettingsRow, SettingsSidebar, Sidebar, SidebarCollapseToggle, SidebarHeader, SidebarItem,
  SidebarLabel, Switch, useCall, useColorScheme,
} from "frappe-ui"
import TweakPanel from "@/components/TweakPanel.vue"
import NotFound from "@/pages/ErrorState.vue"
import { hasRole, isAdmin, primaryRole, user } from "@/lib/session"
import { NAV } from "@/lib/nav"
import { isMobile } from "@/lib/viewport"
import { fullWidth } from "@/lib/layout"

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

// Open approvals for this person, shown as a count beside "Approvals" like the unread counts in frappe-ui's own sidebars.
const open = useCall({ url: "/api/method/frappe.client.get_count", params: { doctype: "Workflow Action", filters: { status: "Open" } }, immediate: canOpen("Approvals"), refetch: true })
const waiting = computed(() => Number(open.data.value?.message ?? open.data.value ?? 0) || 0)

const go = (url) => (window.location.href = url)
const logout = () => go("/api/method/logout")

// The header menu: switch to another installed app, then the account actions.
const apps = computed(() => (window.installed_apps || []).filter((a) => a.name !== "marketing_hub" && a.route))
const headerMenu = computed(() => [
  ...(apps.value.length ? [{ group: "Switch app", options: apps.value.map((a) => ({ label: a.title, icon: "lucide-layout-grid", onClick: () => go(a.route) })) }] : []),
  { group: user.value.fullName || "Account", options: [
    { label: fullWidth.value ? "Use a centered column" : "Use full width", icon: "lucide-move-horizontal", onClick: () => (fullWidth.value = !fullWidth.value) },
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
