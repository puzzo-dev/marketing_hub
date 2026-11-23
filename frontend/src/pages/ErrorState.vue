<template>
  <div class="flex flex-1 items-center justify-center p-8">
    <div class="flex max-w-sm flex-col items-center gap-3 text-center">
      <span class="flex size-12 items-center justify-center rounded-6 bg-surface-gray-2 text-ink-gray-6">
        <span :class="[icon, 'size-6']" />
      </span>
      <h2 class="text-lg-medium text-ink-gray-9">{{ title }}</h2>
      <p class="text-base text-ink-gray-6">{{ text }}</p>
      <div class="flex items-center gap-3">
        <slot><Button v-if="actionLabel" variant="solid" :label="actionLabel" @click="$emit('action')" /></slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button } from "frappe-ui"
defineProps({
  title: String,
  text: String,
  icon: { type: String, default: "lucide-file-x" },
  actionLabel: String,
})
defineEmits(["action"])
</script>
