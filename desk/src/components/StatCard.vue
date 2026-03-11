<template>
  <div class="rounded-lg border border-outline-gray-1 bg-surface-white p-4 shadow-sm">
    <div class="text-sm text-ink-gray-5">{{ label }}</div>
    <div class="mt-1 text-2xl font-semibold text-ink-gray-9">{{ value }}</div>
    <div v-if="change !== undefined" class="mt-1 flex items-center gap-1 text-xs"
      :class="change >= 0 ? 'text-ink-green-3' : 'text-ink-red-3'"
    >
      <component :is="change >= 0 ? IconTrendingUp : IconTrendingDown" class="h-3 w-3" />
      {{ change >= 0 ? '+' : '' }}{{ change }}% from last month
    </div>
    <div v-else-if="subtext" class="mt-1 text-xs text-ink-gray-6">{{ subtext }}</div>
  </div>
</template>

<script setup>
import IconTrendingUp from '~icons/lucide/trending-up'
import IconTrendingDown from '~icons/lucide/trending-down'

defineProps({
  label: String,
  value: [String, Number],
  change: Number,
  subtext: String,
})
</script>
