<template>
  <Dropdown :options="options" placement="bottom-start">
    <template #default="{ open }">
      <button
        class="flex h-12 w-full items-center gap-2 rounded-md px-2 py-2 duration-200 ease-in-out"
        :class="
          open
            ? 'bg-white shadow-sm'
            : 'hover:bg-gray-100'
        "
      >
        <BrandLogo class="flex-shrink-0" />
        <div
          v-show="isExpanded"
          class="flex flex-1 flex-col text-left overflow-hidden"
        >
          <div class="text-sm font-medium leading-tight text-gray-900 truncate">
            Marketing Hub
          </div>
          <div class="text-xs leading-tight text-gray-600 truncate">
            {{ userName }}
          </div>
        </div>
        <FeatherIcon
          v-show="isExpanded"
          name="chevron-down"
          class="h-4 w-4 text-gray-500 flex-shrink-0"
          aria-hidden="true"
        />
      </button>
    </template>
    <template #dropdown-content="{ items }">
      <div class="min-w-[180px] rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 py-1">
        <template v-for="group in items" :key="group.group">
          <div v-show="group.items?.length">
            <div v-show="!group.hideLabel && group.group" class="px-3 py-2 text-xs font-medium text-gray-500">
              {{ group.group }}
            </div>
            <div
              v-for="item in group.items"
              :key="item.label"
              @click="item.onClick"
              class="flex items-center gap-2.5 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 cursor-pointer transition-colors"
            >
              <FeatherIcon
                v-show="item.icon"
                :name="item.icon"
                class="h-4 w-4 text-gray-600"
              />
              <span>{{ item.label }}</span>
            </div>
          </div>
        </template>
      </div>
    </template>
  </Dropdown>
</template>

<script setup>
import { Dropdown, FeatherIcon } from "frappe-ui";
import BrandLogo from "./BrandLogo.vue";
import { computed } from "vue";

defineProps({
  options: {
    type: Array,
    required: true,
  },
  isExpanded: {
    type: Boolean,
    default: true,
  },
});

const userName = computed(() =>
  (typeof frappe !== 'undefined' && frappe?.session?.user_fullname) || 'User'
);
</script>
