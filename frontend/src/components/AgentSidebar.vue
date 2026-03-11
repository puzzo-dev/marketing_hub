<template>
  <div
    class="relative flex h-full flex-col justify-between border-r bg-surface-menu-bar transition-all duration-300 ease-in-out"
    :class="isCollapsed ? 'w-12' : 'w-[220px]'"
  >
    <div class="p-2">
      <UserMenu :isCollapsed="isCollapsed" @open-settings="showSettings = true" />
    </div>

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

    <div class="m-2 flex flex-col gap-1">
      <button
        @click="isCollapsed = !isCollapsed"
        class="mx-0 flex h-7.5 w-full cursor-pointer items-center rounded text-ink-gray-7 duration-300 ease-in-out hover:bg-surface-gray-2"
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
import IconPanelLeftOpen from '~icons/lucide/panel-left-open'
import IconPanelLeftClose from '~icons/lucide/panel-left-close'

const route = useRoute()
const isCollapsed = ref(false)
const showSettings = ref(false)

function isActiveRoute(path) {
  if (path === '/marketing') return route.path === '/marketing'
  return route.path === path || route.path.startsWith(path + '/')
}

const sidebarSections = computed(() => [
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
      { label: 'Analytics', icon: IconBarChart3, to: '/marketing/analytics', isActive: isActiveRoute('/marketing/analytics') },
    ],
  },
])
</script>
