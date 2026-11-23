<template>
  <AppHeader title="Out of home map">
    <template #actions><Button label="List" :route="{ name: 'OutOfHome' }" /></template>
  </AppHeader>
  <ErrorState v-if="error" icon="lucide-map-pin" title="The map did not load" :text="error.message" action-label="Try again" @action="bookings.reload?.()" />
  <div v-else class="flex min-h-0 flex-1">
    <div class="flex flex-1 p-3 sm:p-5"><div ref="el" class="min-h-[420px] flex-1 overflow-hidden rounded-6 border" role="img" aria-label="Map of booked sites" /></div>
    <aside v-if="!isMobile" class="w-96 shrink-0 overflow-y-auto border-s">
      <router-link v-for="b in rows" :key="b.name" :to="{ name: 'OOHBooking', params: { name: b.name } }" class="flex h-[60px] items-center gap-3 border-b px-4 hover:bg-surface-gray-2" :class="b.name === picked && 'bg-surface-gray-2'">
        <span class="flex min-w-0 flex-1 flex-col gap-1.5"><span class="truncate text-base text-ink-gray-8">{{ b.site }}</span><span class="truncate text-sm text-ink-gray-6">{{ b.start_date }} to {{ b.end_date }}</span></span>
        <Badge :label="b.status" :theme="badgeTheme(b.status)" />
      </router-link>
    </aside>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue"
import { Badge, Button, useList } from "frappe-ui"
import L from "leaflet"
import "leaflet/dist/leaflet.css"
import AppHeader from "@/components/AppHeader.vue"
import ErrorState from "./ErrorState.vue"
import { badgeTheme } from "@/lib/status"
import { isMobile } from "@/lib/viewport"

// Sites carry a latitude and longitude; a booking is drawn where its site is.
const bookings = useList({ doctype: "OOH Booking", fields: ["name", "site", "status", "start_date", "end_date"], filters: { status: ["not in", ["Ended", "Cancelled"]] }, limit: 200 })
const sites = useList({ doctype: "OOH Site", fields: ["name", "latitude", "longitude"], limit: 500 })
const error = computed(() => bookings.error?.value || sites.error?.value)
const rows = computed(() => bookings.data.value || [])
const picked = ref(null)
const el = ref(null)
let map, layer
const COLORS = { blue: "#2F7BFF", green: "#1E8E5A", amber: "#C77D0A", gray: "#6B7075", red: "#D13B3B" }
onMounted(() => {
  map = L.map(el.value, { zoomControl: true }).setView([6.5244, 3.3792], 11)
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", { attribution: "© OpenStreetMap contributors", maxZoom: 19 }).addTo(map)
  layer = L.layerGroup().addTo(map)
  draw()
})
function draw() {
  if (!layer) return
  layer.clearLayers()
  const at = Object.fromEntries((sites.data.value || []).map((s) => [s.name, s]))
  const pts = []
  for (const b of rows.value) {
    const s = at[b.site]
    if (!s?.latitude) continue
    pts.push([s.latitude, s.longitude])
    L.circleMarker([s.latitude, s.longitude], { radius: 9, color: "#fff", weight: 2, fillColor: COLORS[badgeTheme(b.status)], fillOpacity: 1 })
      .on("click", () => (picked.value = b.name)).bindTooltip(`${b.site} · ${b.status}`).addTo(layer)
  }
  if (pts.length) map.fitBounds(pts, { padding: [40, 40], maxZoom: 14 })
}
watch([rows, () => sites.data.value], draw)
</script>
