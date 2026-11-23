<template>
  <TabButtons v-model="view" :options="VIEWS" aria-label="View" />
</template>

<script setup>
import { computed } from "vue"
import { useRoute, useRouter } from "vue-router"
import { TabButtons } from "frappe-ui"

// One screen, several views of the same records, kept in the address (?view=kanban) so a
// view can be linked to and the back button works.
const VIEWS = [
  { label: "List", value: "list" },
  { label: "Kanban", value: "kanban" },
  { label: "Calendar", value: "calendar" },
  { label: "Report", value: "report" },
]
const route = useRoute()
const router = useRouter()
const view = computed({
  get: () => (VIEWS.some((v) => v.value === route.query.view) ? route.query.view : "list"),
  set: (v) => router.push({ query: { ...route.query, view: v === "list" ? undefined : v } }),
})
</script>
