<template>
  <Dropdown :options="dropdownItems" v-bind="$attrs">
    <template #default="{ open }">
      <button
        class="flex h-12 items-center rounded-md py-2 duration-300 ease-in-out"
        :class="[
          isCollapsed
            ? 'w-auto px-0'
            : open
              ? 'w-full px-2 bg-surface-white shadow-sm'
              : 'w-full px-2 hover:bg-surface-gray-3',
        ]"
      >
        <BrandLogo class="h-8 w-8 flex-shrink-0 rounded" />
        <div
          v-if="!isCollapsed"
          class="ml-2 flex flex-1 flex-col text-left duration-300 ease-in-out truncate"
        >
          <div class="text-base font-medium leading-none text-ink-gray-9 truncate">
            {{ brandName || 'Marketing Hub' }}
          </div>
          <div class="mt-1 text-sm leading-none text-ink-gray-7 truncate">
            {{ userName }}
          </div>
        </div>
        <IconChevronDown
          v-if="!isCollapsed"
          class="ml-1 h-4 w-4 text-ink-gray-5 flex-shrink-0"
        />
      </button>
    </template>
  </Dropdown>
</template>

<script setup>
import { Dropdown } from 'frappe-ui'
import { computed, markRaw } from 'vue'
import IconChevronDown from '~icons/lucide/chevron-down'
import BrandLogo from './BrandLogo.vue'
import AppSwitcher from './AppSwitcher.vue'
import { useConfigStore } from '@/stores/config'

const props = defineProps({
  isCollapsed: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['open-settings'])

const configStore = useConfigStore()
const brandName = computed(() => configStore.settings.brand_name)

const userName = computed(
  () => (typeof frappe !== 'undefined' && frappe?.session?.user_fullname) || 'User'
)

const dropdownItems = computed(() => [
  {
    component: markRaw(AppSwitcher),
  },
  {
    icon: 'settings',
    label: 'Settings',
    onClick: () => emit('open-settings'),
  },
  {
    icon: 'grid',
    label: 'Switch to Desk',
    onClick: () => (window.location.href = '/app'),
  },
  {
    icon: 'log-out',
    label: 'Log out',
    onClick: () => (window.location.href = '/api/method/logout'),
  },
])
</script>
