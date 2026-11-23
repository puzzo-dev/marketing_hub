<template>
  <!-- One row of figures divided by thin rules, with no card around each: the frappe-ui accounting recipe. -->
  <div class="grid grid-cols-2 gap-y-4 divide-outline-gray-2 sm:divide-x" :class="cols">
    <div v-for="k in items" :key="k.label" class="flex flex-col gap-1 px-4 first:pl-0 last:pr-0">
      <div class="text-sm text-ink-gray-6">{{ k.label }}</div>
      <Skeleton v-if="loading" class="h-8 w-24" />
      <div v-else class="text-2xl font-semibold text-ink-gray-9">{{ k.value ?? "—" }}</div>
      <div v-if="k.hint" class="text-sm text-ink-gray-6">{{ k.hint }}</div>
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
