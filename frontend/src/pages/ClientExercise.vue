<template>
  <AppHeader :title="ex?.campaign_name || name" :back="{ name: 'Home' }"><template #title><Breadcrumbs :items="[{ label: 'Overview', route: { name: 'Home' } }, { label: ex?.campaign_name || name }]" /></template></AppHeader>
  <ErrorState v-if="call.error.value" icon="lucide-lock" title="You do not have access to this" text="Ask your agency to share this exercise with you." />
  <div v-else-if="ex" class="flex flex-col">
    <Tabs v-model="tab" :tabs="[{ value: 'overview', label: 'Overview' }, { value: 'content', label: 'Posted content' }, { value: 'ooh', label: 'Out of home' }, { value: 'results', label: 'Results' }, { value: 'spend', label: 'Spend' }]" variant="underline" class="px-3 sm:px-5" />
    <div class="flex flex-col gap-4 px-3 pb-10 pt-5 sm:px-5">
      <ErrorMessage v-if="tabFailed" message="This could not be loaded. Try again in a moment." />
      <template v-else-if="tab === 'overview'"><FieldRows :rows="[['Status', ex.status], ['Dates', `${ex.start_date} to ${ex.end_date}`], ['Objective', ex.objective]]" /></template>
      <DataList v-else-if="tab === 'content'" :rows="content" row-key="title" :columns="[{ key: 'title', label: 'Title' }]" empty="Nothing posted yet." />
      <DataList v-else-if="tab === 'ooh'" :rows="ooh" row-key="site" empty="No live sites yet." :columns="[{ key: 'site', label: 'Site' }, { key: 'start_date', label: 'Starts', width: '9rem' }, { key: 'end_date', label: 'Ends', width: '9rem' }, { key: 'status', label: 'Status', width: '8rem', badge: true }]" />
      <StatStrip v-else-if="tab === 'results'" :items="[{ label: 'Leads', value: results?.leads }]" />
      <StatStrip v-else :items="[{ label: 'Spent', value: money(spend?.spent) }, { label: 'Budget', value: money(spend?.budget) }]" />
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue"
import { Badge, Breadcrumbs, ErrorMessage, Tabs, useCall } from "frappe-ui"
import StatStrip from "@/components/StatStrip.vue"
import DataList from "@/components/DataList.vue"
import FieldRows from "@/components/FieldRows.vue"
import AppHeader from "@/components/AppHeader.vue"
import ErrorState from "./ErrorState.vue"
import { badgeTheme } from "@/lib/status"

const props = defineProps({ name: String })
const tab = ref("overview")
// Clients call the client-safe API only; it never returns rates, vendors or approvers.
const get = (method) => {
  const c = useCall({ url: `/api/method/marketing_hub.api.client.${method}`, params: { name: props.name } })
  return [c, computed(() => c.data.value?.message ?? c.data.value)]
}
const [call, ex] = get("exercise")
const [contentCall, content] = get("posted_content")
const [oohCall, ooh] = get("out_of_home")
const [resultsCall, results] = get("results")
const [spendCall, spend] = get("spend")
// A tab whose own call failed says so, instead of showing the empty text.
const tabFailed = computed(() => ({ content: contentCall, ooh: oohCall, results: resultsCall, spend: spendCall })[tab.value]?.error?.value)
const money = (v) => (v == null ? "—" : new Intl.NumberFormat(undefined, { style: "currency", currency: "NGN", maximumFractionDigits: 0 }).format(v))
</script>
