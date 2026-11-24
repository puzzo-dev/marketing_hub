<template>
  <div class="flex min-h-0 flex-1 flex-col">
    <AppHeader :title="title || name" :back="back">
      <template #title><Breadcrumbs :items="[{ label: parentLabel, route: back }, { label: title || name }]" /></template>
      <template v-if="$slots.actions" #actions><slot name="actions" /></template>
    </AppHeader>
    <div class="min-h-0 flex-1 overflow-y-auto">
      <ErrorState v-if="state === 'error'" icon="lucide-lock" :title="errorTitle" :text="errorText" :action-label="`Back to ${parentLabel.toLowerCase()}`" @action="$router.push(back)" />
      <div v-else-if="state === 'loading'" class="grid grid-cols-1 gap-8 px-3 pb-10 pt-5 sm:px-5 lg:grid-cols-[minmax(0,1fr)_320px] lg:gap-10" aria-busy="true">
        <div class="flex flex-col gap-3"><Skeleton class="h-8 w-64" /><Skeleton class="h-24 w-full" /><Skeleton class="h-40 w-full" /></div>
        <div class="flex flex-col gap-3"><Skeleton class="h-5 w-24" /><Skeleton class="h-28 w-full" /></div>
      </div>
      <!-- The record: its details take the wide left column; attachments and meta sit in the narrow right one. -->
      <div v-else class="grid grid-cols-1 gap-8 px-3 pb-10 pt-5 sm:px-5 lg:grid-cols-[minmax(0,1fr)_320px] lg:gap-10">
        <div class="flex min-w-0 flex-col gap-6">
          <div class="flex min-w-0 flex-col gap-1.5">
            <div class="flex min-w-0 items-center gap-2"><h1 class="truncate text-xl-semibold text-ink-gray-9">{{ title || name }}</h1><slot name="badges" /></div>
            <p v-if="subtitle" class="text-base text-ink-gray-6">{{ subtitle }}</p>
          </div>
          <slot />
        </div>
        <aside class="flex min-w-0 flex-col gap-6" aria-label="Attachments and details"><slot name="aside" /></aside>
      </div>
    </div>
  </div>
</template>

<script setup>
// The page every record opens on. Details go in the default slot (left, wide); attachments
// and meta go in the `aside` slot (right, narrow). On a phone the aside stacks under the details.
import { Breadcrumbs, Skeleton } from "frappe-ui"
import AppHeader from "@/components/AppHeader.vue"
import ErrorState from "@/pages/ErrorState.vue"

defineProps({
  name: String,
  title: String,
  subtitle: String,
  parentLabel: { type: String, required: true },
  back: { type: Object, required: true }, // route to the list
  state: { type: String, default: "ready" }, // 'loading' | 'error' | 'ready'
  errorTitle: { type: String, default: "You cannot open this" },
  errorText: { type: String, default: "It may belong to another exercise, or it may have been removed." },
})
</script>
