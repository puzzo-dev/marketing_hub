<template>
  <List v-if="rows.length" class="list-row-px-0" :columns="columns.map((c) => c.width || 'minmax(0,1fr)')" :row-height="rowHeight(false)">
    <ListHeader>
      <ListHeaderCell v-for="c in columns" :key="c.key" :class="c.end && 'justify-end'">{{ c.label }}</ListHeaderCell>
    </ListHeader>
    <ListRows :items="rows" :row-key="rowKey" v-slot="{ item, value }">
      <ListRow :value="value" :route="route ? route(item) : undefined">
        <ListCell v-for="(c, i) in columns" :key="c.key" :class="c.end && 'justify-end'">
          <Badge v-if="c.badge && item[c.key]" :label="item[c.key]" :theme="badgeTheme(item[c.key])" />
          <span v-else class="truncate text-base" :class="i === 0 ? 'text-ink-gray-8' : 'text-ink-gray-7'">{{ show(item[c.key], c) }}</span>
        </ListCell>
      </ListRow>
    </ListRows>
  </List>
  <p v-else class="text-base text-ink-gray-6">{{ empty }}</p>
</template>

<script setup>
// A plain table for detail pages and reports, built from frappe-ui's List. `columns` is
// [{ key, label, width, end, badge, money }]; `route(item)` makes a row a link.
import { Badge } from "frappe-ui"
import { List, ListCell, ListHeader, ListHeaderCell, ListRow, ListRows } from "frappe-ui/list"
import { rowHeight } from "@/lib/tweaks"
import { badgeTheme } from "@/lib/status"

defineProps({
  rows: { type: Array, default: () => [] },
  columns: { type: Array, required: true },
  rowKey: { type: String, default: "name" },
  
  route: Function,
  empty: { type: String, default: "Nothing here yet." },
})

const money = (v) => new Intl.NumberFormat(undefined, { style: "currency", currency: "NGN", maximumFractionDigits: 0 }).format(v)
const show = (v, c) => (v == null || v === "" ? "—" : c.money ? money(v) : v)
