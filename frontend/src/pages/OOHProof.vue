<template>
  <div class="mx-auto flex min-h-screen w-full max-w-md flex-col bg-surface-base">
    <header class="flex h-[52px] items-center justify-center border-b px-3 text-lg font-semibold text-ink-gray-9"><span class="truncate">{{ doc?.site || name }}</span></header>
    <div class="flex flex-col gap-4 p-4">
      <div v-if="doc" class="flex items-center gap-2"><Badge :label="doc.status" :theme="badgeTheme(doc.status)" /><span class="truncate text-sm text-ink-gray-6">{{ doc.campaign }}</span></div>
      <h2 class="text-lg font-medium text-ink-gray-9">Proof of posting</h2>
      <FileUploader v-for="s in SLOTS" :key="s.key" :file-types="['image/*']" :upload-args="{}" doctype="OOH Booking" :docname="name" @success="done[s.key] = true">
        <template #default="{ uploading, progress, openFileSelector, error }">
          <button type="button" class="flex h-36 w-full flex-col items-center justify-center gap-1 rounded-6 text-ink-gray-6" :class="done[s.key] ? 'bg-surface-gray-2' : 'border border-dashed border-outline-gray-3'" @click="openFileSelector">
            <span class="text-base text-ink-gray-8">{{ done[s.key] ? `${s.label} photo added` : uploading ? `Uploading ${progress}%` : s.label }}</span>
            <span class="text-sm">{{ error || (done[s.key] ? "Tap to replace" : "Tap to take a photo") }}</span>
          </button>
        </template>
      </FileUploader>
      <p class="text-sm text-ink-gray-6">Photos are attached to this booking. Take one by day and one by night.</p>
    </div>
  </div>
</template>

<script setup>
import { reactive } from "vue"
import { Badge, FileUploader, useDoc } from "frappe-ui"
import { badgeTheme } from "@/lib/status"

const props = defineProps({ name: String })
const SLOTS = [{ key: "day", label: "Day" }, { key: "night", label: "Night" }]
const done = reactive({ day: false, night: false })
const { doc } = useDoc({ doctype: "OOH Booking", name: props.name })
</script>
