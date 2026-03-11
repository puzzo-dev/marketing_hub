<template>
  <div
    class="relative flex h-full flex-col justify-between border-r bg-surface-menu-bar"
    :class="isCollapsed ? 'w-14' : 'w-[220px]'"
  >
    <!-- Header: UserDropdown with brand logo + app switcher -->
    <div class="p-2">
      <UserMenu :isCollapsed="isCollapsed" @open-settings="showSettings = true" />
    </div>

    <!-- Navigation -->
    <div class="flex-1 overflow-y-auto px-2">
      <template v-for="section in sidebarSections" :key="section.label">
        <div v-if="section.label && !isCollapsed" class="mt-4 mb-1 px-2 text-xs font-medium uppercase text-ink-gray-5">
          {{ section.label }}
        </div>
        <div v-else-if="section.label" class="mt-3 mb-1 border-t border-outline-gray-1 mx-1" />
        <nav class="space-y-0.5">
          <router-link
            v-for="item in section.items"
            :key="item.label"
            :to="item.to"
            custom
            v-slot="{ navigate }"
          >
            <button
              @click="navigate"
              class="group flex w-full items-center gap-2 rounded px-2 py-1.5 text-sm"
              :class="
                item.isActive
                  ? 'bg-surface-selected text-ink-gray-9 font-medium'
                  : 'text-ink-gray-7 hover:bg-surface-gray-2'
              "
              :title="isCollapsed ? item.label : undefined"
            >
              <component :is="item.icon" class="h-4 w-4 flex-shrink-0" />
              <span v-if="!isCollapsed">{{ item.label }}</span>
            </button>
          </router-link>
        </nav>
      </template>
    </div>

    <!-- Footer: collapse toggle -->
    <div class="m-2 flex flex-col gap-1">
      <button
        @click="isCollapsed = !isCollapsed"
        class="flex h-7 w-full items-center gap-2 rounded px-2 text-sm text-ink-gray-5 hover:bg-surface-gray-2"
        :title="isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'"
      >
        <component :is="isCollapsed ? IconPanelLeftOpen : IconPanelLeftClose" class="h-4 w-4" />
        <span v-if="!isCollapsed">Collapse</span>
      </button>
    </div>

    <!-- Settings dialog -->
    <SettingsDialog v-model="showSettings" />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import UserMenu from './UserMenu.vue'
import SettingsDialog from './SettingsDialog.vue'

import IconLayoutDashboard from '~icons/lucide/layout-dashboard'
import IconMegaphone from '~icons/lucide/megaphone'
import IconShare2 from '~icons/lucide/share-2'
import IconBarChart3 from '~icons/lucide/bar-chart-2'
import IconSend from '~icons/lucide/send'
import IconUsers from '~icons/lucide/users'
import IconFileText from '~icons/lucide/file-text'
import IconSettings from '~icons/lucide/settings'
import IconPanelLeftOpen from '~icons/lucide/panel-left-open'
import IconPanelLeftClose from '~icons/lucide/panel-left-close'
import IconWallet from '~icons/lucide/wallet'

const route = useRoute()

const isCollapsed = ref(false)
const showSettings = ref(false)

function isActiveRoute(path) {
  if (path === '/marketing') return route.path === '/marketing'
  return route.path === path || route.path.startsWith(path + '/')
}

const sidebarSections = computed(() => {
  const sections = [
    {
      label: '',
      items: [
        { label: 'Dashboard', icon: IconLayoutDashboard, to: '/marketing', isActive: isActiveRoute('/marketing') },
      ],
    },
    {
      label: 'Marketing',
      items: [
        { label: 'Campaigns', icon: IconMegaphone, to: '/marketing/campaigns', isActive: isActiveRoute('/marketing/campaigns') },
        { label: 'Omni Blast', icon: IconSend, to: '/marketing/blast/new', isActive: isActiveRoute('/marketing/blast') },
        { label: 'Social Media', icon: IconShare2, to: '/marketing/social', isActive: isActiveRoute('/marketing/social') },
        { label: 'Segments', icon: IconUsers, to: '/marketing/segments', isActive: isActiveRoute('/marketing/segments') },
        { label: 'Content', icon: IconFileText, to: '/marketing/content', isActive: isActiveRoute('/marketing/content') },
        { label: 'Expenses', icon: IconWallet, to: '/marketing/expenses', isActive: isActiveRoute('/marketing/expenses') },
        { label: 'Analytics', icon: IconBarChart3, to: '/marketing/analytics', isActive: isActiveRoute('/marketing/analytics') },
      ],
    },
  ]

  sections.push({
    label: 'System',
    items: [
      { label: 'Settings', icon: IconSettings, to: '/marketing/settings', isActive: isActiveRoute('/marketing/settings') },
    ],
  })

  return sections
})
</script>
