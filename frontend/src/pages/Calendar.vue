<template>
  <AppHeader title="Calendar">
    <template #actions>
      <div class="flex items-center gap-1">
        <Button variant="ghost" icon="lucide-chevron-left" aria-label="Previous month" @click="shift(-1)" />
        <span class="w-32 text-center text-base text-ink-gray-8">{{ label }}</span>
        <Button variant="ghost" icon="lucide-chevron-right" aria-label="Next month" @click="shift(1)" />
      </div>
    </template>
  </AppHeader>
  <ErrorState v-if="error" icon="lucide-calendar" title="The calendar did not load" :text="error.message" action-label="Try again" @action="list.reload?.()" />
  <div v-else class="flex flex-col px-3 py-4 sm:px-5" :aria-busy="isFetching">
    <div class="grid grid-cols-7 border-b pb-2 text-sm text-ink-gray-6">
      <span v-for="d in DAYS" :key="d" class="px-2">{{ d }}</span>
    </div>
    <div class="grid grid-cols-7">
      <div v-for="c in cells" :key="c.key" class="flex min-h-28 flex-col gap-1 border-b border-e p-2" :class="c.out && 'bg-surface-gray-1'">
        <span class="text-sm" :class="c.today ? 'font-semibold text-ink-gray-9' : 'text-ink-gray-6'">{{ c.day }}</span>
        <router-link v-for="p in c.items" :key="p.name" :to="{ name: 'Placement', params: { name: p.name } }" class="flex min-w-0 items-center gap-1.5 rounded-4 px-1.5 py-1 text-sm hover:bg-surface-gray-2">
          <span class="size-2 shrink-0 rounded-full" :class="DOT[badgeTheme(p.status)]"></span>
          <span class="truncate text-ink-gray-8">{{ p.content_item }}</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue"
import { Button, useList } from "frappe-ui"
import AppHeader from "@/components/AppHeader.vue"
import ErrorState from "./ErrorState.vue"
import { badgeTheme } from "@/lib/status"

// Placements by the day they are scheduled for: a month at a time, Monday first.
const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
const DOT = { green: "bg-surface-green-6", blue: "bg-surface-blue-5", amber: "bg-surface-amber-5", red: "bg-surface-red-5", gray: "bg-surface-gray-5" }
const month = ref(new Date(new Date().getFullYear(), new Date().getMonth(), 1))
const iso = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`
const start = computed(() => {
  const d = new Date(month.value)
  d.setDate(1 - ((d.getDay() + 6) % 7))
  return d
})
const end = computed(() => { const d = new Date(start.value); d.setDate(d.getDate() + 41); return d })
const list = useList({
  doctype: "Placement",
  fields: ["name", "content_item", "status", "scheduled_for"],
  filters: () => ({ scheduled_for: ["between", [iso(start.value), iso(end.value)]] }),
  orderBy: "scheduled_for asc",
  limit: 500,
})
const { data, isFetching, error } = list
const label = computed(() => month.value.toLocaleString("en", { month: "long", year: "numeric" }))
const cells = computed(() => {
  const by = {}
  for (const p of data.value || []) (by[String(p.scheduled_for).slice(0, 10)] ||= []).push(p)
  return Array.from({ length: 42 }, (_, i) => {
    const d = new Date(start.value); d.setDate(d.getDate() + i)
    return { key: iso(d), day: d.getDate(), out: d.getMonth() !== month.value.getMonth(), today: iso(d) === iso(new Date()), items: by[iso(d)] || [] }
  })
})
const shift = (n) => { const d = new Date(month.value); d.setMonth(d.getMonth() + n); month.value = d }
</script>
