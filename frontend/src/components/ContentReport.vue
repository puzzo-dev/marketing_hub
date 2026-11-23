<template>
  <div class="flex flex-col gap-6 px-3 py-5 sm:px-5">
    <StatStrip :items="strip" />
    <div class="grid gap-8 lg:grid-cols-2">
      <BarChart :config="statusChart" />
      <BarChart :config="exerciseChart" />
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"
import { BarChart } from "frappe-ui/charts"
import StatStrip from "@/components/StatStrip.vue"

// Counts over the same records the other views show, so the numbers always agree with them.
const props = defineProps({ items: Array, statuses: Array })
const count = (f) => props.items.filter(f).length
const strip = computed(() => [
  { label: "Items", value: String(props.items.length) },
  { label: "In review", value: String(count((i) => i.status === "In review")) },
  { label: "Approved", value: String(count((i) => i.status === "Approved")) },
  { label: "Posted", value: String(count((i) => i.status === "Posted")) },
])
const tally = (key) => {
  const m = {}
  for (const i of props.items) m[i[key] || "None"] = (m[i[key] || "None"] || 0) + 1
  return Object.entries(m).map(([k, v]) => ({ name: k, count: v }))
}
const statusChart = computed(() => ({ title: "By status", subtitle: "Items now", data: props.statuses.map((s) => ({ name: s, count: count((i) => i.status === s) })), xAxis: { key: "name", type: "category" }, yAxis: { title: "Items" }, series: [{ name: "Items", key: "count" }], card: false }))
const exerciseChart = computed(() => ({ title: "By exercise", subtitle: "Items per exercise", data: tally("campaign"), xAxis: { key: "name", type: "category" }, yAxis: { title: "Items" }, series: [{ name: "Items", key: "count" }], card: false }))
</script>
