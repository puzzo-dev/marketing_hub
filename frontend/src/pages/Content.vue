<template>
  <ListScreen
    v-if="view === 'list'"
    title="Content" doctype="Content Item" row-route="ContentDetail"
    :columns="[
      { label: 'Title', field: 'title', width: 'minmax(0, 1.6fr)', strong: true },
      { label: 'Exercise', field: 'campaign', sub: true },
      { label: 'Type', field: 'type', width: '120px' },
      { label: 'Due', field: 'due_date', width: '120px' },
      { label: 'Status', field: 'status', width: '130px', badge: true },
    ]"
    status-field="status" :statuses="STATUSES"
    :action="canCreate ? { label: 'New content', to: { name: 'ContentDetail', params: { name: 'new' } } } : null"
    empty-title="No content yet" empty-text="Content you create for an exercise appears here with its review status."
  >
    <template #toolbar><ViewSwitch v-if="!isMobile" /></template>
  </ListScreen>
  <template v-else>
    <AppHeader title="Content">
      <template #actions><ViewSwitch /></template>
    </AppHeader>
    <ErrorState v-if="error" icon="lucide-file-text" title="Content did not load" :text="error.message" action-label="Try again" @action="list.reload?.()" />
    <div v-else class="min-h-0 flex-1 overflow-y-auto" :aria-busy="isFetching">
      <ContentKanban v-if="view === 'kanban'" :items="items" :statuses="STATUSES" />
      <ContentCalendar v-else-if="view === 'calendar'" :items="items" />
      <ContentReport v-else :items="items" :statuses="STATUSES" />
    </div>
  </template>
</template>

<script setup>
import { computed } from "vue"
import { useRoute } from "vue-router"
import { useList } from "frappe-ui"
import AppHeader from "@/components/AppHeader.vue"
import ListScreen from "@/components/ListScreen.vue"
import ViewSwitch from "@/components/ViewSwitch.vue"
import ContentKanban from "@/components/ContentKanban.vue"
import ContentCalendar from "@/components/ContentCalendar.vue"
import ContentReport from "@/components/ContentReport.vue"
import ErrorState from "./ErrorState.vue"
import { hasRole, ROLES } from "@/lib/session"
import { isMobile } from "@/lib/viewport"

const STATUSES = ["Draft", "In review", "Approved", "Posted"]
const canCreate = hasRole(ROLES.manager, ROLES.planner, ROLES.contentLead)
const route = useRoute()
const view = computed(() => (["kanban", "calendar", "report"].includes(route.query.view) ? route.query.view : "list"))
// The list view loads its own rows; the other three share one fetch.
const list = useList({
  doctype: "Content Item",
  fields: ["name", "title", "campaign", "type", "status", "due_date", "creation"],
  orderBy: "due_date asc",
  limit: 500,
  immediate: view.value !== "list",
})
const { data, isFetching, error } = list
const items = computed(() => data.value || [])
</script>
