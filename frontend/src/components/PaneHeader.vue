<template>
  <AppHeader v-if="isMobile" :title="title" :back="back || close">
    <template v-if="$slots.actions" #actions><slot name="actions" /></template>
  </AppHeader>
  <header v-else class="flex h-12 shrink-0 items-center justify-between gap-2 border-b bg-surface-base px-3 sm:px-5">
    <div class="flex min-w-0 items-center gap-2"><slot name="title"><PageHeaderTitle :title="title" /></slot></div>
    <div class="flex shrink-0 items-center gap-2">
      <slot name="actions" />
      <Button v-if="close" variant="ghost" icon="lucide-x" aria-label="Close" @click="$router.push(close)" />
    </div>
  </header>
</template>

<script setup>
// The header of one pane. Every pane header is 48px tall with the same gutter, so the
// sidebar header, the list header and the detail header sit on one line. A phone gets the
// mobile header; `close` (a route) adds a close button on a desktop and a back button on a phone.
import { Button, PageHeaderTitle } from "frappe-ui"
import AppHeader from "@/components/AppHeader.vue"
import { isMobile } from "@/lib/viewport"

defineProps({ title: { type: String, default: "" }, close: Object, back: Object })
</script>
