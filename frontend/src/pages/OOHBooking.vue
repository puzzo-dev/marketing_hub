<template>
  <div class="flex min-h-0 flex-1 flex-col">
  <PaneHeader :title="doc?.site || name" :close="{ name: 'OutOfHome' }">
      <template v-if="next" #actions><Button variant="solid" :label="`Move to ${next}`" :loading="busy" @click="advance" /></template>
    </PaneHeader>
  <div class="min-h-0 flex-1 overflow-y-auto">
  <div v-if="!doc" class="flex flex-col gap-3 px-3 py-4 sm:px-5" aria-busy="true"><Skeleton class="h-8 w-64" /><Skeleton class="h-24 w-full" /></div>
  <div v-else class="flex flex-col gap-6 px-3 pb-10 pt-5 sm:px-5">
    <div class="flex items-center gap-2"><Badge :label="doc.status" :theme="badgeTheme(doc.status)" /></div>
    <ol class="flex flex-wrap gap-2" aria-label="Progress">
      <li v-for="s in STEPS" :key="s" class="flex h-7 items-center rounded-4 px-2 text-sm" :class="STEPS.indexOf(s) <= STEPS.indexOf(doc.status) ? 'bg-surface-gray-7 text-ink-white' : 'bg-surface-gray-2 text-ink-gray-6'">{{ s }}</li>
    </ol>
    <FieldRows :rows="rows" />
    <router-link v-if="doc.purchase_order" :to="{ name: 'PurchaseOrder', params: { name: doc.purchase_order } }" class="text-base text-ink-gray-8 underline">Purchase order {{ doc.purchase_order }}</router-link>
    <ErrorMessage :message="error" />
  </div>
  </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue"
import { Badge, Button, ErrorMessage, Skeleton, useCall, useDoc } from "frappe-ui"
import PaneHeader from "@/components/PaneHeader.vue"
import FieldRows from "@/components/FieldRows.vue"
import { badgeTheme } from "@/lib/status"

const STEPS = ["Proposed", "Approved", "Production", "Live", "Ended"]
const props = defineProps({ name: String })
const { doc: docRef, reload } = useDoc({ doctype: "OOH Booking", name: props.name })
const doc = computed(() => docRef.value || docRef)
const next = computed(() => STEPS[STEPS.indexOf(doc.value?.status) + 1])
const rows = computed(() => [["Exercise", doc.value.campaign], ["Dates", `${doc.value.start_date} to ${doc.value.end_date}`], ["Agreed rate", doc.value.agreed_rate], ["Approved by", doc.value.approver]])
const busy = ref(false)
const error = ref("")
const run = useCall({ url: "/api/method/run_doc_method", method: "POST", immediate: false })
async function advance() {
  busy.value = true
  error.value = ""
  try {
    await run.submit({ docs: JSON.stringify(doc.value), method: "advance" })
    reload?.()
    location.reload()
  } catch (e) {
    error.value = e?.message || "That step did not go through."
  } finally {
    busy.value = false
  }
}
</script>
