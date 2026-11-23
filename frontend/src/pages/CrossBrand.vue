<template>
  <AppHeader title="Cross-brand report" />
  <div class="flex flex-col gap-6 px-3 py-4 sm:px-5">
    <div class="flex flex-col gap-2">
      <h3 class="text-lg-medium text-ink-gray-9">By brand</h3>
      <div class="grid h-8 grid-cols-[minmax(0,1.4fr)_100px_140px_140px] items-center gap-3 rounded-4 bg-surface-gray-2 px-3 text-sm text-ink-gray-6"><span>Brand</span><span>Exercises</span><span>Budget</span><span>Spend</span></div>
      <div v-for="r in rows" :key="r.brand" class="grid h-11 grid-cols-[minmax(0,1.4fr)_100px_140px_140px] items-center gap-3 border-b px-3 text-base">
        <span class="text-ink-gray-8">{{ r.brand || "No brand" }}</span><span class="text-ink-gray-6">{{ r.exercises }}</span><span class="text-ink-gray-6">{{ money(r.budget) }}</span><span class="text-ink-gray-8">{{ money(r.spent) }}</span>
      </div>
      <p v-if="!rows.length" class="text-base text-ink-gray-6">No exercises yet.</p>
      <p class="text-sm text-ink-gray-5">Only the Marketing Head sees every brand.</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"
import { useList } from "frappe-ui"
import AppHeader from "@/components/AppHeader.vue"

const { data } = useList({ doctype: "Marketing Campaign", fields: ["brand", "count(name) as exercises", "sum(budget) as budget", "sum(total_spent) as spent"], groupBy: "brand", limit: 100 })
const rows = computed(() => data.value || [])
const money = (v) => (v == null ? "—" : new Intl.NumberFormat(undefined, { style: "currency", currency: "NGN", maximumFractionDigits: 0 }).format(v))
</script>
