<template>
  <AppHeader title="Cross-brand report" />
  <div class="flex flex-col gap-2 px-3 pb-10 pt-5 sm:px-5">
    <DataList :rows="rows.map((r) => ({ ...r, brand: r.brand || 'No brand' }))" row-key="brand" empty="No exercises yet."
      :columns="[{ key: 'brand', label: 'Brand' }, { key: 'exercises', label: 'Exercises', width: '7rem', end: true }, { key: 'budget', label: 'Budget', width: '9rem', end: true, money: true }, { key: 'spent', label: 'Spend', width: '9rem', end: true, money: true }]" />
    <p class="text-sm text-ink-gray-6">Only the Marketing Head sees every brand.</p>
  </div>
</template>

<script setup>
import { computed } from "vue"
import { useList } from "frappe-ui"
import DataList from "@/components/DataList.vue"
import AppHeader from "@/components/AppHeader.vue"

const { data } = useList({ doctype: "Marketing Campaign", fields: ["brand", "count(name) as exercises", "sum(budget) as budget", "sum(total_spent) as spent"], groupBy: "brand", limit: 100 })
const rows = computed(() => data.value || [])
const money = (v) => (v == null ? "—" : new Intl.NumberFormat(undefined, { style: "currency", currency: "NGN", maximumFractionDigits: 0 }).format(v))
</script>
