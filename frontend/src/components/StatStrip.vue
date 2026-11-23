<template>
  <!-- One row of figures divided by thin rules, with no card around each: the frappe-ui accounting recipe. -->
  <div class="grid grid-cols-2 gap-y-4 divide-outline-gray-2 sm:divide-x" :class="cols">
    <div v-for="k in items" :key="k.label" class="px-4 first:pl-0 last:pr-0">
      <div class="text-xs text-ink-gray-5">{{ k.label }}</div>
      <Skeleton v-if="loading" class="mt-1 h-8 w-24" />
      <div v-else class="mt-1 text-2xl font-semibold text-ink-gray-9">{{ k.value ?? "—" }}</div>
      <div v-if="k.hint" class="mt-1 text-xs text-ink-gray-5">{{ k.hint }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"
import { Skeleton } from "frappe-ui"
const props = defineProps({ items: { type: Array, required: true }, loading: Boolean })
// Full class names, so Tailwind can see them.
const cols = computed(() => ({ 1: "sm:grid-cols-1", 2: "sm:grid-cols-2", 3: "sm:grid-cols-3" })[props.items.length] || "sm:grid-cols-4")
</script>
