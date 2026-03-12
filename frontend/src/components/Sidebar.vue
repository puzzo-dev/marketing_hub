<template>
  <div
    class="relative flex h-full flex-col justify-between border-r bg-surface-menu-bar transition-all duration-300 ease-in-out"
    :class="isCollapsed ? 'w-12' : 'w-[220px]'"
  >
    <!-- Header: UserDropdown with brand logo + app switcher -->
    <div class="p-2">
      <UserMenu :isCollapsed="isCollapsed" @open-settings="showSettings = true" />
    </div>

    <!-- Agency Mode Indicator -->
    <div
      v-if="configStore.isAgencyMode"
      class="mx-2 mb-1 flex items-center gap-1.5 rounded-md px-2 py-1.5 transition-all duration-300 ease-in-out"
      :class="isCollapsed ? 'justify-center bg-surface-orange-2' : 'bg-surface-orange-2'"
      :title="isCollapsed ? 'Agency Mode' : undefined"
    >
      <IconBuilding class="size-3.5 flex-shrink-0 text-ink-orange-3" />
      <span
        v-if="!isCollapsed"
        class="text-xs font-medium text-ink-orange-3"
      >Agency Mode</span>
    </div>

    <!-- Navigation -->
    <div class="flex-1 overflow-y-auto">
      <div class="flex flex-col">
        <template v-for="section in sidebarSections" :key="section.label">
          <div v-if="section.label" class="border-t mx-2 my-1.5" />
          <div
            v-if="section.label"
            class="flex items-center gap-1.5 text-ink-gray-5 transition-all duration-300 ease-in-out"
            :class="isCollapsed ? 'h-0 overflow-hidden opacity-0' : 'px-4 pt-[11px] pb-2 w-auto opacity-100'"
          >
            <span class="text-xs font-medium uppercase tracking-wider">{{ section.label }}</span>
          </div>
          <nav class="flex flex-col">
            <router-link
              v-for="item in section.items"
              :key="item.label"
              :to="item.to"
              custom
              v-slot="{ navigate }"
            >
              <button
                @click="navigate"
                class="mx-2 my-[1.5px] flex h-7.5 cursor-pointer items-center rounded text-ink-gray-8 duration-300 ease-in-out focus:outline-none focus-visible:rounded focus-visible:ring-2 focus-visible:ring-outline-gray-3"
                :class="item.isActive ? 'bg-surface-selected shadow-sm' : 'hover:bg-surface-gray-2'"
                :title="isCollapsed ? item.label : undefined"
              >
                <div
                  class="flex w-full items-center justify-between duration-300 ease-in-out"
                  :class="isCollapsed ? 'ml-[3px] p-1' : 'px-2 py-[7px]'"
                >
                  <div class="flex items-center truncate">
                    <component :is="item.icon" class="size-4 flex-shrink-0 text-ink-gray-8" />
                    <span
                      class="flex-1 flex-shrink-0 truncate text-sm duration-300 ease-in-out"
                      :class="isCollapsed ? 'ml-0 w-0 overflow-hidden opacity-0' : 'ml-2 w-auto opacity-100'"
                    >{{ item.label }}</span>
                  </div>
                </div>
              </button>
            </router-link>
          </nav>
        </template>
      </div>
    </div>

    <!-- Footer: collapse toggle -->
    <div class="m-2 flex flex-col gap-1">
      <button
        @click="isCollapsed = !isCollapsed"
        class="mx-0 flex h-7.5 w-full cursor-pointer items-center rounded text-ink-gray-7 duration-300 ease-in-out hover:bg-surface-gray-2"
        :title="isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'"
      >
        <div
          class="flex w-full items-center duration-300 ease-in-out"
          :class="isCollapsed ? 'ml-[3px] p-1' : 'px-2 py-[7px]'"
        >
          <component
            :is="isCollapsed ? IconPanelLeftOpen : IconPanelLeftClose"
            class="size-4 flex-shrink-0 text-ink-gray-7 duration-300 ease-in-out"
            :class="{ '[transform:rotateY(180deg)]': isCollapsed }"
          />
          <span
            class="flex-1 flex-shrink-0 truncate text-sm duration-300 ease-in-out"
            :class="isCollapsed ? 'ml-0 w-0 overflow-hidden opacity-0' : 'ml-2 w-auto opacity-100'"
          >Collapse</span>
        </div>
      </button>
    </div>

    <!-- Settings dialog -->
    <SettingsDialog v-model="showSettings" />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useConfigStore } from '@/stores/config'
import UserMenu from './UserMenu.vue'
import SettingsDialog from './SettingsDialog.vue'

import IconLayoutDashboard from '~icons/lucide/layout-dashboard'
import IconMegaphone from '~icons/lucide/megaphone'
import IconShare2 from '~icons/lucide/share-2'
import IconBarChart3 from '~icons/lucide/bar-chart-2'
import IconSend from '~icons/lucide/send'
import IconUsers from '~icons/lucide/users'
import IconFileText from '~icons/lucide/file-text'
import IconPanelLeftOpen from '~icons/lucide/panel-left-open'
import IconPanelLeftClose from '~icons/lucide/panel-left-close'
import IconWallet from '~icons/lucide/wallet'
import IconBuilding from '~icons/lucide/building'
import IconLink2 from '~icons/lucide/link-2'
import IconUserCheck from '~icons/lucide/user-check'

const route = useRoute()
const configStore = useConfigStore()

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
        { label: 'Leads', icon: IconUserCheck, to: '/marketing/leads', isActive: isActiveRoute('/marketing/leads') },
        { label: 'Content', icon: IconFileText, to: '/marketing/content', isActive: isActiveRoute('/marketing/content') },
        { label: 'Expenses', icon: IconWallet, to: '/marketing/expenses', isActive: isActiveRoute('/marketing/expenses') },
        { label: 'Tracking Links', icon: IconLink2, to: '/marketing/tracking', isActive: isActiveRoute('/marketing/tracking') },
        { label: 'Analytics', icon: IconBarChart3, to: '/marketing/analytics', isActive: isActiveRoute('/marketing/analytics') },
      ],
    },
  ]

  // Agency mode: add Clients section
  if (configStore.isAgencyMode) {
    sections.splice(1, 0, {
      label: 'Agency',
      items: [
        { label: 'Clients', icon: IconBuilding, to: '/marketing/clients', isActive: isActiveRoute('/marketing/clients') },
      ],
    })
  }

  return sections
})
</script>
