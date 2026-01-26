<template>
  <div class="rounded-lg border border-outline-gray-1 bg-surface-cards p-5 shadow-sm transition-all hover:shadow-md">
    <div class="flex items-center justify-between">
      <div class="text-sm font-medium text-ink-gray-6">{{ label }}</div>
      <FeatherIcon v-if="icon" :name="icon" class="h-5 w-5 text-ink-gray-4" />
    </div>
    <div class="mt-2 text-2xl font-semibold text-ink-gray-9">
      {{ value }}
    </div>
    <div v-if="change !== undefined" class="mt-1 text-xs" :class="change >= 0 ? 'text-green-600' : 'text-red-600'">
      {{ change >= 0 ? '+' : '' }}{{ change }}% from last month
    </div>
    <div v-else-if="subtext" class="mt-1 text-xs text-ink-gray-6">
      {{ subtext }}
    </div>
  </div>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui'

defineProps({
  label: String,
  value: [String, Number],
  icon: String,
  change: Number,
  subtext: String
})
</script>
