<template>
  <Popover
    placement="right-start"
    trigger="hover"
    :hoverDelay="0.1"
    :leaveDelay="0.1"
  >
    <template #target="{ togglePopover }">
      <button
        :class="[
          active ? 'bg-surface-gray-3' : 'text-ink-gray-6',
          'group w-full flex h-7 items-center justify-between rounded px-2 text-base hover:bg-surface-gray-2',
        ]"
        @click.prevent="togglePopover()"
      >
        <div class="flex items-center gap-2">
          <IconGrid class="h-4 w-4" />
          <span class="whitespace-nowrap">Apps</span>
        </div>
        <IconChevronRight class="h-4 w-4 text-ink-gray-5" />
      </button>
    </template>
    <template #body>
      <div
        class="flex w-fit mx-2 min-w-32 max-w-48 flex-col rounded-lg border border-outline-gray-2 bg-surface-white p-1.5 text-sm text-ink-gray-8 shadow-xl"
      >
        <a
          :href="app.route"
          v-for="app in appsList"
          :key="app.name"
          class="flex items-center gap-2 rounded p-1.5 hover:bg-surface-gray-2"
        >
          <img class="h-6 w-6" :src="app.logo" />
          <span class="max-w-18 w-full truncate">{{ app.title }}</span>
        </a>
      </div>
    </template>
  </Popover>
</template>

<script setup>
import { Popover, createResource } from 'frappe-ui'
import { computed } from 'vue'
import IconGrid from '~icons/lucide/grid'
import IconChevronRight from '~icons/lucide/chevron-right'

defineProps({
  active: Boolean,
})

const apps = createResource({
  url: 'frappe.apps.get_apps',
  cache: 'apps',
  auto: true,
  transform: (data) => {
    let _apps = [
      {
        name: 'frappe',
        logo: '/assets/frappe/images/framework.png',
        title: 'Desk',
        route: '/app',
      },
    ]
    data.map((app) => {
      if (app.name === 'marketing_hub') return
      _apps.push({
        name: app.name,
        logo: app.logo,
        title: app.title,
        route: app.route,
      })
    })
    return _apps
  },
})

const appsList = computed(() => apps.data || [])
</script>
