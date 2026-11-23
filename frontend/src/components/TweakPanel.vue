<template>
  <div class="fixed bottom-4 end-4 z-40 flex flex-col items-end gap-2">
    <div v-if="open" class="flex w-64 flex-col gap-4 rounded-xl border border-outline-gray-2 bg-surface-elevation-2 p-4 shadow-lg" role="group" aria-label="Tweak">
      <div class="flex flex-col gap-1.5">
        <span class="text-sm text-ink-gray-6">Density</span>
        <TabButtons v-model="density" :options="[{ label: 'Compact', value: 'compact' }, { label: 'Relaxed', value: 'relaxed' }]" />
      </div>
      <div class="flex flex-col gap-1.5">
        <span class="text-sm text-ink-gray-6">A record opens</span>
        <TabButtons v-model="openIn" :options="[{ label: 'Beside the list', value: 'beside' }, { label: 'Full page', value: 'page' }]" />
      </div>
      <div class="flex flex-col gap-1.5">
        <span class="text-sm text-ink-gray-6">Page width</span>
        <TabButtons v-model="width" :options="[{ label: 'Full', value: 'full' }, { label: 'Column', value: 'column' }]" />
      </div>
    </div>
    <Button :icon="open ? 'lucide-x' : 'lucide-sliders-horizontal'" :aria-label="open ? 'Close tweaks' : 'Tweak the layout'" @click="open = !open" />
  </div>
</template>

<script setup>
import { computed, ref } from "vue"
import { Button, TabButtons } from "frappe-ui"
import { fullWidth } from "@/lib/layout"
import { density, openIn } from "@/lib/tweaks"

const open = ref(false)
const width = computed({ get: () => (fullWidth.value ? "full" : "column"), set: (v) => (fullWidth.value = v === "full") })
</script>
