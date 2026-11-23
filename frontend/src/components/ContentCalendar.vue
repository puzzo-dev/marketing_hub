<template>
  <div class="flex flex-col px-3 py-3 sm:px-5">
    <div class="flex items-center justify-between pb-3">
      <div class="flex items-center gap-1">
        <Button variant="ghost" icon="lucide-chevron-left" aria-label="Previous month" @click="shift(-1)" />
        <span class="w-36 text-center text-base font-medium text-ink-gray-8">{{ label }}</span>
        <Button variant="ghost" icon="lucide-chevron-right" aria-label="Next month" @click="shift(1)" />
      </div>
      <Button label="Today" @click="month = firstOfMonth(new Date())" />
    </div>
    <div class="grid grid-cols-7 border-b pb-2 text-sm text-ink-gray-6"><span v-for="d in DAYS" :key="d" class="px-2">{{ d }}</span></div>
    <div class="grid grid-cols-7 border-s">
      <div v-for="c in cells" :key="c.key" class="flex min-h-24 flex-col gap-1 border-b border-e p-2" :class="c.out && 'bg-surface-gray-1'">
        <span class="text-sm" :class="c.today ? 'font-semibold text-ink-gray-9' : 'text-ink-gray-6'">{{ c.day }}</span>
        <router-link v-for="i in c.items" :key="i.name" :to="{ name: 'ContentDetail', params: { name: i.name } }" class="flex min-w-0 items-center gap-1.5 rounded-4 px-1.5 py-1 text-sm hover:bg-surface-gray-2">
          <span class="size-2 shrink-0 rounded-full" :class="DOT[badgeTheme(i.status)]"></span><span class="truncate text-ink-gray-8">{{ i.title }}</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue"
import { Button } from "frappe-ui"
import { badgeTheme } from "@/lib/status"

// Content by the day it is due: a month at a time, Monday first.
const props = defineProps({ items: Array })
const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
const DOT = { green: "bg-surface-green-6", blue: "bg-surface-blue-5", amber: "bg-surface-amber-5", red: "bg-surface-red-5", gray: "bg-surface-gray-5" }
const firstOfMonth = (d) => new Date(d.getFullYear(), d.getMonth(), 1)
const month = ref(firstOfMonth(new Date()))
const iso = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`
const label = computed(() => month.value.toLocaleString("en", { month: "long", year: "numeric" }))
const cells = computed(() => {
  const start = new Date(month.value)
  start.setDate(1 - ((start.getDay() + 6) % 7))
  const by = {}
  for (const i of props.items) if (i.due_date) (by[String(i.due_date).slice(0, 10)] ||= []).push(i)
  return Array.from({ length: 42 }, (_, n) => {
    const d = new Date(start); d.setDate(d.getDate() + n)
    return { key: iso(d), day: d.getDate(), out: d.getMonth() !== month.value.getMonth(), today: iso(d) === iso(new Date()), items: by[iso(d)] || [] }
  })
})
const shift = (n) => { const d = new Date(month.value); d.setMonth(d.getMonth() + n); month.value = d }
</script>
