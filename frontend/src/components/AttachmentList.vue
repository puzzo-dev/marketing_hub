<template>
  <AsideSection :title="title">
    <div v-if="isFetching && !files.length" class="grid grid-cols-2 gap-2" aria-busy="true"><Skeleton class="h-24 w-full" /><Skeleton class="h-24 w-full" /></div>
    <p v-else-if="error" class="text-base text-ink-gray-6">Attachments could not be loaded.</p>
    <p v-else-if="!files.length" class="text-base text-ink-gray-6">{{ empty }}</p>
    <template v-else>
      <div v-if="images.length" class="grid grid-cols-2 gap-2">
        <a v-for="f in images" :key="f.name" :href="f.file_url" target="_blank" rel="noopener" class="block overflow-hidden rounded-4 bg-surface-gray-2" :aria-label="f.file_name">
          <img :src="f.file_url" :alt="f.file_name" loading="lazy" class="h-24 w-full object-cover" />
        </a>
      </div>
      <a v-for="f in others" :key="f.name" :href="f.file_url" target="_blank" rel="noopener" class="flex min-h-9 items-center gap-2 text-base text-ink-gray-8 hover:text-ink-gray-9">
        <span class="lucide-file size-4 shrink-0 text-ink-gray-6" aria-hidden="true" />
        <span class="min-w-0 flex-1 truncate">{{ f.file_name }}</span>
        <span class="shrink-0 text-sm text-ink-gray-6">{{ size(f.file_size) }}</span>
      </a>
    </template>
  </AsideSection>
</template>

<script setup>
import { computed } from "vue"
import { Skeleton, useList } from "frappe-ui"
import AsideSection from "@/components/AsideSection.vue"

const props = defineProps({
  doctype: String,
  name: String, // empty until the record has loaded
  title: { type: String, default: "Attachments" },
  empty: { type: String, default: "No attachments." },
})
const list = useList({
  doctype: "File",
  fields: ["name", "file_name", "file_url", "file_size"],
  filters: () => ({ attached_to_doctype: props.doctype, attached_to_name: props.name || "-" }),
  orderBy: "creation desc",
  limit: 50,
})
const { data, isFetching, error } = list
const files = computed(() => data.value || [])
const isImage = (f) => /\.(png|jpe?g|gif|webp|avif|svg)$/i.test(f.file_url || f.file_name || "")
const images = computed(() => files.value.filter(isImage))
const others = computed(() => files.value.filter((f) => !isImage(f)))
const size = (b) => (!b ? "" : b < 1024 * 1024 ? `${Math.max(1, Math.round(b / 1024))} KB` : `${(b / 1024 / 1024).toFixed(1)} MB`)
</script>
