<template>
  <div class="flex min-h-0 flex-1 flex-col">
    <PaneHeader :title="name" :close="{ name: 'PurchaseOrders' }">
      <template #actions>
        <Badge v-if="doc" :label="doc.status" :theme="badgeTheme(doc.status)" />
        <Button label="Open in ERPNext" icon-right="lucide-external-link" :link="`/app/purchase-order/${name}`" />
      </template>
    </PaneHeader>
    <div class="min-h-0 flex-1 overflow-y-auto">
      <div v-if="!doc" class="flex flex-col gap-3 px-3 py-4 sm:px-5" aria-busy="true"><Skeleton class="h-8 w-64" /><Skeleton class="h-24 w-full" /></div>
      <div v-else class="flex flex-col gap-6 px-3 pb-10 pt-5 sm:px-5">
        <FieldRows :rows="rows" />
        <div class="flex flex-col gap-1">
          <h3 class="h-7 text-sm font-semibold text-ink-gray-8">Progress</h3>
          <div v-for="s in steps" :key="s.label" class="flex min-h-9 items-center gap-3">
            <span class="flex size-5 items-center justify-center rounded-full" :class="s.done ? 'bg-surface-gray-10 text-ink-white' : 'border border-outline-gray-3'">
              <FeatherIcon v-if="s.done" name="check" class="size-3" />
            </span>
            <span class="text-base" :class="s.done ? 'text-ink-gray-8' : 'text-ink-gray-6'">{{ s.label }}</span>
          </div>
        </div>
        <p class="text-sm text-ink-gray-6">Receiving and billing happen in ERPNext.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"
import { Badge, Button, FeatherIcon, Skeleton, useDoc } from "frappe-ui"
import PaneHeader from "@/components/PaneHeader.vue"
import FieldRows from "@/components/FieldRows.vue"
import { badgeTheme } from "@/lib/status"

const props = defineProps({ name: String })
const { doc: docRef } = useDoc({ doctype: "Purchase Order", name: props.name })
const doc = computed(() => docRef.value || null)
const rows = computed(() => [
  ["Vendor", doc.value.supplier_name],
  ["Booking", doc.value.mkt_booking],
  ["Amount", doc.value.grand_total],
  ["Ordered on", doc.value.transaction_date],
])
// Receiving and billing are ERPNext's own percentages on the order.
const steps = computed(() => [
  { label: "Purchase order created", done: true },
  { label: "Goods received", done: (doc.value?.per_received || 0) >= 100 },
  { label: "Vendor billed", done: (doc.value?.per_billed || 0) >= 100 },
])
</script>
