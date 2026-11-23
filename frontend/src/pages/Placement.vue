<template>
  <div class="flex min-h-0 flex-1 flex-col">
    <PaneHeader :title="doc?.content_item || name" :close="{ name: 'Placements' }">
      <template #actions><Badge v-if="doc?.status" :label="doc.status" :theme="badgeTheme(doc.status)" /></template>
    </PaneHeader>
    <div class="min-h-0 flex-1 overflow-y-auto">
      <div v-if="error" class="px-3 py-5 sm:px-5"><ErrorMessage :message="error" /></div>
      <div v-else-if="!doc" class="flex flex-col gap-3 px-3 py-4 sm:px-5" aria-busy="true"><Skeleton class="h-8 w-64" /><Skeleton class="h-24 w-full" /></div>
      <div v-else class="flex flex-col gap-6 px-3 pb-10 pt-5 sm:px-5">
        <FieldRows :rows="rows" />

      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"
import { Badge, ErrorMessage, Skeleton, useDoc } from "frappe-ui"
import PaneHeader from "@/components/PaneHeader.vue"
import FieldRows from "@/components/FieldRows.vue"
import { badgeTheme } from "@/lib/status"

const props = defineProps({ name: String })
const { doc: docRef, error: err } = useDoc({ doctype: "Placement", name: props.name })
const doc = computed(() => docRef.value || null)
const error = computed(() => err?.value?.message || "")
const rows = computed(() => [
  ["Exercise", doc.value.campaign],
  ["Channel", doc.value.channel],
  ["Scheduled for", doc.value.scheduled_for],
  ["Approval", doc.value.approval_state],
  ["Approver", doc.value.approver],
])
</script>
