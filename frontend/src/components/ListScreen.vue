<template>
  <div class="flex min-h-0 flex-1">
    <section v-if="!(isMobile && hasDetail)" class="flex min-h-0 flex-col" :class="split ? 'w-[400px] shrink-0 border-e' : 'min-w-0 flex-1'" :aria-label="title">
      <PaneHeader :title="title">
        <template #actions><Button v-if="canAct" variant="solid" :label="action.label" iconLeft="lucide-plus" @click="$router.push(action.to)" /></template>
      </PaneHeader>

      <div class="min-h-0 flex-1 overflow-y-auto">
        <div v-if="statuses.length" class="px-3 pt-3 sm:px-5">
          <TabButtons v-model="status" :options="statusButtons" />
        </div>

        <div v-if="isFetching && !rows.length && !error" class="flex flex-col gap-2 px-3 py-3 sm:px-5" aria-busy="true"><Skeleton v-for="n in 6" :key="n" class="h-11 w-full" /></div>

        <ErrorState v-else-if="error" icon="lucide-triangle-alert" title="Something went wrong on our side" text="Nothing was lost. Try again." action-label="Try again" @action="list.reload?.() || list.execute?.()" />

        <ErrorState v-else-if="!isFetching && !rows.length" icon="lucide-folder" :title="emptyTitle" :text="emptyText" :action-label="canAct ? action.label : undefined" @action="$router.push(action.to)" />

        <div v-else-if="compact" class="flex flex-col px-3 py-1 sm:px-5">
          <button v-for="row in rows" :key="row.name" type="button" class="-mx-2 flex min-h-14 items-center gap-3 rounded-4 border-b px-2 py-2 text-start hover:bg-surface-gray-1" :class="row.name === $route.params.name && 'bg-surface-gray-2'" :aria-current="row.name === $route.params.name ? 'true' : undefined" @click="open(row)">
            <span class="flex min-w-0 flex-1 flex-col gap-1">
              <span class="truncate text-base text-ink-gray-8">{{ format(row[columns[0].field], columns[0]) }}</span>
              <span class="truncate text-sm text-ink-gray-6">{{ columns.slice(1, -1).map((c) => format(row[c.field], c)).filter((v) => v !== "—").join(" · ") }}</span>
            </span>
            <Badge v-if="columns.at(-1).badge" :label="row[columns.at(-1).field]" :theme="badgeTheme(row[columns.at(-1).field])" />
          </button>
        </div>

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
      </div>
    </section>

    <!-- The open record. The list narrows to make room and takes the full width back when it closes. -->
    <section v-if="hasDetail" class="flex min-h-0 min-w-0 flex-1 flex-col" aria-label="Details">
      <router-view :key="$route.params.name" />
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import { Badge, Button, Skeleton, TabButtons, useList } from "frappe-ui"
import PaneHeader from "@/components/PaneHeader.vue"
import ErrorState from "@/pages/ErrorState.vue"
import { badgeTheme } from "@/lib/status"
import { isMobile } from "@/lib/viewport"

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
const route = useRoute()
// A record is open when the child route is showing; the list then narrows to a column.
const hasDetail = computed(() => route.name === props.rowRoute)
const split = computed(() => hasDetail.value && !isMobile.value)
const compact = computed(() => isMobile.value || hasDetail.value)
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
