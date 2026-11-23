<template>
  <div class="flex min-h-0 flex-1">
    <section v-if="!(stacked && hasDetail)" class="flex min-h-0 flex-col" :class="split ? 'w-[400px] shrink-0 border-e' : 'min-w-0 flex-1'" :aria-label="title">
      <PaneHeader :title="title">
        <template #actions>
          <template v-if="statuses.length">
            <TabButtons v-if="!compact" v-model="status" :options="statusButtons" />
            <Select v-else v-model="status" variant="ghost" :options="statusButtons" />
          </template>
          <Button v-if="canAct" variant="solid" :label="action.label" icon-left="lucide-plus" @click="$router.push(action.to)" />
        </template>
      </PaneHeader>

      <ScrollArea class="min-h-0 flex-1">
        <div class="px-3 pb-10 pt-3 sm:px-5">
          <div v-if="isFetching && !rows.length && !error" class="flex flex-col gap-2" aria-busy="true"><Skeleton v-for="n in 6" :key="n" class="h-[60px] w-full" /></div>
          <ErrorState v-else-if="error" icon="lucide-triangle-alert" title="Something went wrong on our side" text="Nothing was lost. Try again." action-label="Try again" @action="list.reload?.() || list.execute?.()" />
          <ErrorState v-else-if="!isFetching && !rows.length" icon="lucide-folder" :title="emptyTitle" :text="emptyText" :action-label="canAct ? action.label : undefined" @action="$router.push(action.to)" />

          <List v-else class="w-full list-row-px-3" :columns="template" :row-height="rowHeight(!!subs.length || compact)" :active="active">
            <ListHeader v-if="!compact">
              <ListHeaderCell>{{ cols[0].label }}</ListHeaderCell>
              <ListHeaderCell v-for="c in tableCols" :key="c.field" :class="c.currency && 'justify-end'">{{ c.label }}</ListHeaderCell>
            </ListHeader>
            <ListRows :items="rows" row-key="name" v-slot="{ item, value }">
              <ListRow :value="value" :route="rowTo(item)">
                <ListCell>
                  <div class="flex min-w-0 flex-col gap-1.5">
                    <div class="truncate text-base text-ink-gray-8">{{ format(item[cols[0].field], cols[0]) }}</div>
                    <div v-if="subtitle(item)" class="truncate text-sm text-ink-gray-6">{{ subtitle(item) }}</div>
                  </div>
                </ListCell>
                <template v-if="!compact">
                  <ListCell v-for="c in tableCols" :key="c.field" :class="c.currency && 'justify-end'">
                    <Badge v-if="c.badge" :label="item[c.field]" :theme="badgeTheme(item[c.field])" />
                    <span v-else class="truncate text-base text-ink-gray-7">{{ format(item[c.field], c) }}</span>
                  </ListCell>
                </template>
                <ListCell v-else-if="badgeCol" class="justify-end">
                  <Badge :label="item[badgeCol.field]" :theme="badgeTheme(item[badgeCol.field])" />
                </ListCell>
              </ListRow>
            </ListRows>
          </List>
          <p v-if="note" class="pt-3 text-sm text-ink-gray-6">{{ note }}</p>
        </div>
      </ScrollArea>
    </section>

    <!-- The open record. The list narrows to a column to make room and takes the full width back on close. -->
    <section v-if="hasDetail" class="flex min-h-0 min-w-0 flex-1 flex-col" aria-label="Details">
      <router-view :key="$route.params.name" />
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import { Badge, Button, ScrollArea, Select, Skeleton, TabButtons, useList } from "frappe-ui"
import { List, ListCell, ListHeader, ListHeaderCell, ListRow, ListRows } from "frappe-ui/list"
import PaneHeader from "@/components/PaneHeader.vue"
import ErrorState from "@/pages/ErrorState.vue"
import { badgeTheme } from "@/lib/status"
import { openIn, rowHeight } from "@/lib/tweaks"
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
// On a phone, or when the Tweak panel says "Full page", an open record replaces the list.
const stacked = computed(() => isMobile.value || openIn.value === "page")
const split = computed(() => hasDetail.value && !stacked.value)
const compact = computed(() => isMobile.value || split.value)
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

// The first column is the row's title. Columns marked `sub` fold into a second line under it, as the
// frappe-ui tickets list does, so the table keeps few columns and the title keeps its room.
const subs = computed(() => props.columns.filter((c) => c.sub))
const cols = computed(() => props.columns.filter((c) => !c.sub))
const badgeCol = computed(() => cols.value.find((c, i) => i > 0 && c.badge && i === cols.value.length - 1))
const tableCols = computed(() => cols.value.slice(1))
const template = computed(() =>
  compact.value
    ? ["minmax(0,1fr)", ...(badgeCol.value ? ["7.5rem"] : [])]
    : ["minmax(0,1fr)", ...tableCols.value.map((c) => c.width || "minmax(0,1fr)")],
)
const subtitle = (row) => {
  const fields = compact.value ? [...subs.value, ...tableCols.value.filter((c) => c !== badgeCol.value)] : subs.value
  return fields.map((c) => format(row[c.field], c)).filter((v) => v !== "—").join(" · ")
}
const active = computed(() => route.params.name || null)
const rowTo = (row) => (props.rowRoute && router.hasRoute(props.rowRoute) ? { name: props.rowRoute, params: { name: row.name } } : undefined)

function format(value, column) {
  if (value == null || value === "") return "—"
  if (column.currency) return new Intl.NumberFormat(undefined, { style: "currency", currency: column.currency, maximumFractionDigits: 0 }).format(value)
  return value
}
// A button or row only works when its screen exists, so an unbuilt route shows nothing.
const canAct = computed(() => props.action && router.hasRoute(props.action.to.name))
</script>
