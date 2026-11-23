<template>
  <PageHeader><PageHeaderTitle :title="greeting" /></PageHeader>
  <div class="flex max-w-4xl flex-col gap-6 p-5">
    <div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
      <router-link v-for="c in cards" :key="c.label" :to="{ name: c.route }" class="rounded-6 bg-surface-gray-1 p-4 hover:bg-surface-gray-2">
        <div class="text-sm text-ink-gray-6">{{ c.label }}</div>
        <div class="mt-1 text-2xl font-semibold text-ink-gray-9">{{ c.count ?? "—" }}</div>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"
import { PageHeader, PageHeaderTitle, useCall } from "frappe-ui"
import { user } from "@/lib/session"

const greeting = computed(() => `Hello, ${(user.value.fullName || "").split(" ")[0] || "there"}`)

// Counts come from Frappe's own get_count, so they follow the same permissions as the lists.
const count = (doctype, filters) => {
  const call = useCall({ url: "/api/method/frappe.client.get_count", params: { doctype, filters: JSON.stringify(filters || {}) } })
  return computed(() => call.data.value?.message ?? call.data.value)
}
const waiting = count("Workflow Action", { status: "Open" })
const live = count("Marketing Campaign", { status: "Live" })
const scheduled = count("Placement", { status: "Scheduled" })
const leads = count("Lead", { status: "Open" })
const cards = computed(() => [
  { label: "Waiting for you", count: waiting.value, route: "Approvals" },
  { label: "Live exercises", count: live.value, route: "Exercises" },
  { label: "Scheduled placements", count: scheduled.value, route: "Placements" },
  { label: "Open leads", count: leads.value, route: "Leads" },
])
</script>
