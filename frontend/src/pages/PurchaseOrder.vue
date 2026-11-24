<template>
  <RecordPage :name="name" :title="name" parent-label="Purchase orders" :back="{ name: 'PurchaseOrders' }" :state="state"
    error-title="You cannot open this purchase order" error-text="It may belong to another exercise, or it may have been removed.">
    <template #actions><Button label="Open in ERPNext" icon-right="lucide-external-link" :link="`/app/purchase-order/${name}`" /></template>
    <template #badges><Badge v-if="doc" :label="doc.status" :theme="badgeTheme(doc.status)" /></template>
    <FieldRows :rows="rows" />
    <div class="flex flex-col gap-1">
      <h2 class="h-7 text-sm font-semibold text-ink-gray-8">Progress</h2>
      <div v-for="s in steps" :key="s.label" class="flex min-h-9 items-center gap-3">
        <span class="flex size-5 items-center justify-center rounded-full" :class="s.done ? 'bg-surface-gray-10 text-ink-white' : 'border border-outline-gray-3'">
          <span v-if="s.done" class="lucide-check size-3" aria-hidden="true" />
        </span>
        <span class="text-base" :class="s.done ? 'text-ink-gray-8' : 'text-ink-gray-6'">{{ s.label }}</span>
      </div>
    </div>
    <p class="text-sm text-ink-gray-6">Receiving and billing happen in ERPNext.</p>
    <template #aside>
      <AttachmentList doctype="Purchase Order" :name="name" empty="No invoice or vendor files attached." />
      <AsideSection title="Details"><FieldRows compact :rows="[['Created', doc?.creation], ['Last changed', doc?.modified], ['Created by', doc?.owner]]" /></AsideSection>
    </template>
  </RecordPage>
</template>

<script setup>
import { computed } from "vue"
import { Badge, Button, useDoc } from "frappe-ui"
import RecordPage from "@/components/RecordPage.vue"
import AsideSection from "@/components/AsideSection.vue"
import AttachmentList from "@/components/AttachmentList.vue"
import FieldRows from "@/components/FieldRows.vue"
import { badgeTheme } from "@/lib/status"

const props = defineProps({ name: String })
const { doc: docRef, error: loadError } = useDoc({ doctype: "Purchase Order", name: props.name })
const doc = computed(() => docRef.value || null)
const state = computed(() => (loadError?.value ? "error" : doc.value ? "ready" : "loading"))
const rows = computed(() => [
  ["Vendor", doc.value?.supplier_name],
  ["Booking", doc.value?.mkt_booking],
  ["Amount", doc.value?.grand_total],
  ["Ordered on", doc.value?.transaction_date],
])
// Receiving and billing are ERPNext's own percentages on the order.
const steps = computed(() => [
  { label: "Purchase order created", done: true },
  { label: "Goods received", done: (doc.value?.per_received || 0) >= 100 },
  { label: "Vendor billed", done: (doc.value?.per_billed || 0) >= 100 },
])
</script>
