<template>
  <AppHeader title="Exercise report">
    <template #actions><div class="w-64"><LinkSelect doctype="Marketing Campaign" label-field="campaign_name" placeholder="Pick an exercise" v-model="exercise" /></div></template>
  </AppHeader>
  <ErrorState v-if="!exercise" icon="lucide-chart-column" title="Pick an exercise" text="Choose an exercise to see its spend, leads and placements." />
  <ErrorState v-else-if="listError || docError" icon="lucide-triangle-alert" title="This report could not be loaded" text="You may not have access to this exercise. Pick another, or try again." />
  <div v-else class="flex flex-col gap-8 px-3 pb-10 pt-5 sm:px-5">
    <StatStrip :items="kpis" />
    <section class="flex flex-col gap-2">
      <div class="flex h-7 items-center"><h3 class="text-sm font-semibold text-ink-gray-8">Placements by channel</h3></div>
      <DataList :loading="isFetching" :rows="byChannel" row-key="channel" :columns="[{ key: 'channel', label: 'Channel' }, { key: 'count', label: 'Placements', width: '8rem', end: true }]" empty="No placements yet." />
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from "vue"
import { useCall, useDoc, useList } from "frappe-ui"
import StatStrip from "@/components/StatStrip.vue"
import DataList from "@/components/DataList.vue"
import AppHeader from "@/components/AppHeader.vue"
import ErrorState from "./ErrorState.vue"
import LinkSelect from "@/components/LinkSelect.vue"

const exercise = ref(null)
const { doc, error: docErr } = useDoc({ doctype: "Marketing Campaign", name: () => exercise.value })
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
const { data: rows, isFetching, error: listErr } = useList({ doctype: "Placement", fields: ["channel", "count(name) as count"], filters: () => ({ campaign: exercise.value || "-" }), groupBy: "channel" })
const docError = computed(() => !!docErr?.value)
const listError = computed(() => !!listErr?.value)
const byChannel = computed(() => rows.value || [])
</script>
