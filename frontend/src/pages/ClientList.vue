<template>
  <AppHeader :title="cfg.title" />
  <ErrorState v-if="call.error.value" icon="lucide-triangle-alert" title="Something went wrong on our side" text="Nothing was lost. Try again." action-label="Try again" @action="call.reload?.()" />
  <div v-else class="flex flex-col gap-3 px-3 pb-10 pt-5 sm:px-5">
    <p v-if="cfg.note" class="text-sm text-ink-gray-6">{{ cfg.note }}</p>
    <DataList :rows="rows" row-key="name" :columns="cfg.columns" :route="(r) => ({ name: 'Exercise', params: { name: r.campaign || r.name } })" :empty="cfg.empty" />
  </div>
</template>

<script setup>
// One screen for the client's sidebar pages that look across every exercise they can see.
// Each row opens the exercise it belongs to. Clients only ever call marketing_hub.api.client.
import { computed } from "vue"
import { useCall } from "frappe-ui"
import AppHeader from "@/components/AppHeader.vue"
import DataList from "@/components/DataList.vue"
import ErrorState from "./ErrorState.vue"

const props = defineProps({ kind: { type: String, required: true } })
const CONFIG = {
  content: { title: "Posted content", method: "all_posted_content", empty: "Nothing has been posted yet.", note: "Only content that has been posted is shown here.",
    columns: [{ key: "title", label: "Content" }, { key: "exercise", label: "Exercise", width: "14rem" }, { key: "type", label: "Type", width: "8rem" }, { key: "modified", label: "Posted", width: "10rem" }] },
  ooh: { title: "Out of home", method: "all_out_of_home", empty: "No billboards are live yet.", note: "Costs are on the Spend page.",
    columns: [{ key: "site", label: "Site" }, { key: "exercise", label: "Exercise", width: "14rem" }, { key: "start_date", label: "Starts", width: "9rem" }, { key: "end_date", label: "Ends", width: "9rem" }, { key: "status", label: "Status", width: "8rem", badge: true }] },
  results: { title: "Results", method: "all_results", empty: "No results yet.",
    columns: [{ key: "exercise", label: "Exercise" }, { key: "leads", label: "Leads", width: "8rem", end: true }] },
  spend: { title: "Spend", method: "all_spend", empty: "No spend yet.",
    columns: [{ key: "exercise", label: "Exercise" }, { key: "budget", label: "Budget", width: "10rem", end: true, money: true }, { key: "spent", label: "Spent", width: "10rem", end: true, money: true }] },
}
const cfg = computed(() => CONFIG[props.kind])
const call = useCall({ url: `/api/method/marketing_hub.api.client.${CONFIG[props.kind].method}` })
const rows = computed(() => call.data.value?.message ?? call.data.value ?? [])
</script>
