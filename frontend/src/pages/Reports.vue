<template>
  <AppHeader title="Exercise report">
    <template #actions><div class="w-64"><LinkSelect doctype="Marketing Campaign" label-field="campaign_name" placeholder="Pick an exercise" v-model="exercise" /></div></template>
  </AppHeader>
  <ErrorState v-if="!exercise" icon="lucide-chart-column" title="Pick an exercise" text="Choose an exercise to see its spend, leads and placements." />
  <div v-else class="flex flex-col gap-6 px-3 py-4 sm:px-5">
    <div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
      <div v-for="k in kpis" :key="k.label" class="rounded-6 bg-surface-gray-1 p-4"><div class="text-sm text-ink-gray-6">{{ k.label }}</div><div class="mt-1 text-2xl font-semibold text-ink-gray-9">{{ k.value }}</div></div>
    </div>
    <div class="flex flex-col gap-2">
      <h3 class="text-lg-medium text-ink-gray-9">Placements by channel</h3>
      <div v-for="r in byChannel" :key="r.channel" class="grid h-10 grid-cols-[minmax(0,1fr)_100px] items-center border-b px-3 text-base"><span class="text-ink-gray-8">{{ r.channel }}</span><span class="text-ink-gray-6">{{ r.count }}</span></div>
      <p v-if="!byChannel.length" class="text-base text-ink-gray-6">No placements yet.</p>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue"
import { useCall, useDoc, useList } from "frappe-ui"
import AppHeader from "@/components/AppHeader.vue"
import ErrorState from "./ErrorState.vue"
import LinkSelect from "@/components/LinkSelect.vue"

const exercise = ref(null)
const { doc } = useDoc({ doctype: "Marketing Campaign", name: () => exercise.value })
const count = (doctype, filters) => {
  const c = useCall({ url: "/api/method/frappe.client.get_count", params: () => ({ doctype, filters: JSON.stringify(filters(exercise.value)) }), immediate: !!exercise.value })
  return computed(() => c.data.value?.message ?? c.data.value)
}
const leads = count("Lead", (e) => ({ mkt_campaign: e }))
const placements = count("Placement", (e) => ({ campaign: e, status: "Posted" }))
const money = (v) => (v == null ? "—" : new Intl.NumberFormat(undefined, { style: "currency", currency: "NGN", maximumFractionDigits: 0 }).format(v))
const spent = computed(() => doc.value?.total_spent)
const kpis = computed(() => [
  { label: "Leads", value: leads.value ?? "—" },
  { label: "Posted", value: placements.value ?? "—" },
  { label: "Budget", value: money(doc.value?.budget) },
  { label: "Spend", value: money(spent.value) },
])
const { data: rows } = useList({ doctype: "Placement", fields: ["channel", "count(name) as count"], filters: () => ({ campaign: exercise.value || "-" }), groupBy: "channel" })
const byChannel = computed(() => rows.value || [])
</script>
