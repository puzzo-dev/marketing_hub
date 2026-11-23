<template>
  <PageHeader>
    <PageHeaderTitle :title="title" />
    <Button v-if="canAct" variant="solid" :label="action.label" iconLeft="lucide-plus" @click="$router.push(action.to)" />
  </PageHeader>

  <div v-if="statuses.length" class="px-3 pt-3 sm:px-5">
    <TabButtons v-model="status" :options="statusButtons" />
  </div>

  <ErrorState v-if="error" icon="lucide-triangle-alert" title="Something went wrong on our side" text="Nothing was lost. Try again." action-label="Try again" @action="list.reload?.() || list.execute?.()" />

  <ErrorState v-else-if="!isFetching && !rows.length" icon="lucide-folder" :title="emptyTitle" :text="emptyText" :action-label="canAct ? action.label : undefined" @action="$router.push(action.to)" />

  <div v-else class="px-3 py-3 sm:px-5">
    <div class="grid h-8 items-center gap-3 rounded-4 bg-surface-gray-2 px-3 text-sm text-ink-gray-6" :style="gridStyle">
      <span v-for="c in columns" :key="c.field" class="truncate">{{ c.label }}</span>
    </div>
    <button v-for="row in rows" :key="row.name" type="button" class="grid h-11 w-full items-center gap-3 border-b px-3 text-start text-base hover:bg-surface-gray-1" :style="gridStyle" @click="open(row)">
      <template v-for="c in columns" :key="c.field">
        <span v-if="c.badge" class="min-w-0"><Badge :label="row[c.field]" :theme="badgeTheme(row[c.field])" /></span>
        <span v-else :class="['truncate', c.strong ? 'text-ink-gray-8' : 'text-ink-gray-6']">{{ format(row[c.field], c) }}</span>
      </template>
    </button>
    <p v-if="note" class="pt-3 text-sm text-ink-gray-5">{{ note }}</p>
  </div>
</template>

<script setup>
import { computed, ref } from "vue"
import { useRouter } from "vue-router"
import { Badge, Button, PageHeader, PageHeaderTitle, TabButtons, useList } from "frappe-ui"
import ErrorState from "@/pages/ErrorState.vue"
import { badgeTheme } from "@/lib/status"

const props = defineProps({
  title: String,
  doctype: String,
  columns: Array, // [{ label, field, width, strong, badge, currency }]
  statusField: String, // filter tabs over this field
  statuses: { type: Array, default: () => [] },
  filters: { type: Object, default: () => ({}) },
  orderBy: { type: String, default: "modified desc" },
  action: Object, // { label, to }
  rowRoute: String, // route name, receives { name }
  emptyTitle: String,
  emptyText: String,
  note: String,
})

const router = useRouter()
const status = ref("All")
const statusButtons = computed(() => ["All", ...props.statuses].map((s) => ({ label: s, value: s })))

const list = useList({
  doctype: props.doctype,
  fields: ["name", ...props.columns.map((c) => c.field)],
  filters: () => ({ ...props.filters, ...(props.statusField && status.value !== "All" ? { [props.statusField]: status.value } : {}) }),
  orderBy: props.orderBy,
  limit: 50,
})
const { data, isFetching, error } = list
const rows = computed(() => data.value || [])

const gridStyle = computed(() => ({
  gridTemplateColumns: props.columns.map((c) => c.width || "minmax(0, 1fr)").join(" "),
}))

function format(value, column) {
  if (value == null || value === "") return "—"
  if (column.currency) return new Intl.NumberFormat(undefined, { style: "currency", currency: column.currency, maximumFractionDigits: 0 }).format(value)
  return value
}
// A button or row only works when its screen exists, so an unbuilt route shows nothing.
const canAct = computed(() => props.action && router.hasRoute(props.action.to.name))
function open(row) {
  if (props.rowRoute && router.hasRoute(props.rowRoute)) router.push({ name: props.rowRoute, params: { name: row.name } })
}
</script>
