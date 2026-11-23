<template>
  <AppHeader title="Home">
    <template #actions>
      <div class="w-56"><LinkSelect doctype="Marketing Campaign" label-field="campaign_name" placeholder="All exercises" v-model="exercise" /></div>
      <Select v-model="period" :options="periods" />
    </template>
  </AppHeader>

  <ErrorState v-if="call.error.value" icon="lucide-triangle-alert" title="Something went wrong on our side" text="Nothing was lost. Try again." action-label="Try again" @action="call.reload?.() || call.execute?.()" />

  <div v-else class="flex flex-col gap-8 px-3 pb-10 pt-5 sm:px-5">
    <!-- One row of figures divided by thin rules, no card per figure (the frappe-ui accounting recipe). -->
    <div class="grid grid-cols-2 gap-y-4 divide-outline-gray-2 sm:grid-cols-3 sm:divide-x xl:grid-cols-5">
      <div v-for="k in strip" :key="k.key" class="px-4 first:pl-0 last:pr-0">
        <div class="text-xs text-ink-gray-5">{{ k.label }}</div>
        <Skeleton v-if="loading" class="mt-1 h-8 w-24" />
        <div v-else class="mt-1 text-2xl font-semibold text-ink-gray-9">{{ k.format(k.value) }}</div>
        <div class="mt-1 flex h-4 items-center gap-1 text-xs" :class="k.change == null ? 'text-ink-gray-4' : (k.change >= 0) !== !!k.lowerIsBetter ? 'text-ink-green-5' : 'text-ink-red-5'">
          <template v-if="k.change != null">
            <span :class="k.change >= 0 ? 'lucide-arrow-up' : 'lucide-arrow-down'" class="size-3" aria-hidden="true" />
            <span>{{ Math.abs(k.change) }}% {{ caption }}</span>
          </template>
          <span v-else>No change to compare</span>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-x-10 gap-y-8 lg:grid-cols-3">
      <section class="h-80 min-w-0 lg:col-span-2"><AreaChart v-bind="trendChart" /></section>
      <section class="h-80 min-w-0"><DonutChart v-bind="channelShare" /></section>
      <section class="h-80 min-w-0 lg:col-span-2"><BarChart v-bind="exerciseChart" /></section>
      <section class="h-80 min-w-0"><BarChart v-bind="channelChart" /></section>
    </div>

    <section class="flex flex-col gap-2">
      <div class="flex h-7 items-center"><h3 class="text-sm font-semibold text-ink-gray-8">Exercises</h3></div>
      <List v-if="data.by_exercise.length" class="list-row-px-0" :columns="['minmax(0,1fr)', '8rem', '8rem', '6rem', '7rem']" :row-height="52">
        <ListHeader>
          <ListHeaderCell>Exercise</ListHeaderCell><ListHeaderCell class="justify-end">Spend</ListHeaderCell><ListHeaderCell class="justify-end">Impressions</ListHeaderCell><ListHeaderCell class="justify-end">Clicks</ListHeaderCell><ListHeaderCell class="justify-end">Conversions</ListHeaderCell>
        </ListHeader>
        <ListRows :items="data.by_exercise" row-key="exercise" v-slot="{ item, value }">
          <ListRow :value="value" :route="{ name: 'Exercise', params: { name: item.exercise } }">
            <ListCell><span class="truncate text-base text-ink-gray-8">{{ item.name }}</span></ListCell>
            <ListCell class="justify-end"><span class="text-base text-ink-gray-8">{{ money(item.spend) }}</span></ListCell>
            <ListCell class="justify-end"><span class="text-base text-ink-gray-7">{{ num(item.impressions) }}</span></ListCell>
            <ListCell class="justify-end"><span class="text-base text-ink-gray-7">{{ num(item.clicks) }}</span></ListCell>
            <ListCell class="justify-end"><span class="text-base text-ink-gray-7">{{ num(item.conversions) }}</span></ListCell>
          </ListRow>
        </ListRows>
      </List>
      <p v-else class="text-base text-ink-gray-6">No analytics in this period. Numbers appear once an analytics connector has synced.</p>
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from "vue"
import { Select, Skeleton, useCall } from "frappe-ui"
import { List, ListCell, ListHeader, ListHeaderCell, ListRow, ListRows } from "frappe-ui/list"
import AppHeader from "@/components/AppHeader.vue"
import ErrorState from "./ErrorState.vue"
import { AreaChart, BarChart, DonutChart } from "frappe-ui/charts"
import LinkSelect from "@/components/LinkSelect.vue"

const period = ref("30d")
const exercise = ref(null)
const periods = [
  { label: "Last 7 days", value: "7d" },
  { label: "Last 30 days", value: "30d" },
  { label: "Last 90 days", value: "90d" },
]

const call = useCall({
  url: "/api/method/marketing_hub.api.analytics.overview",
  params: () => ({ period: period.value, exercise: exercise.value || undefined }),
  refetch: true,
})
const data = computed(() => {
  const d = call.data.value?.message ?? call.data.value ?? {}
  return { kpis: d.kpis || {}, by_exercise: d.by_exercise || [], by_channel: d.by_channel || [], trend: d.trend || [], period: d.period }
})

const money = (v) => (v == null ? "—" : new Intl.NumberFormat(undefined, { style: "currency", currency: "NGN", maximumFractionDigits: 0 }).format(v))
const num = (v) => (v == null ? "—" : new Intl.NumberFormat().format(v))
const caption = computed(() => `vs the ${period.value.replace("d", "")} days before`)

const strip = computed(() => [
  { label: "Spend", key: "spend", format: money },
  { label: "Impressions", key: "impressions", format: num },
  { label: "Clicks", key: "clicks", format: num },
  { label: "Leads", key: "leads", format: num },
  { label: "Cost per lead", key: "cost_per_lead", format: money, lowerIsBetter: true },
].map((k) => ({ ...k, value: data.value.kpis[k.key]?.value ?? null, change: data.value.kpis[k.key]?.change ?? null })))

const loading = computed(() => call.isFetching?.value ?? false)
const trendChart = computed(() => ({
  loading: loading.value,
  data: data.value.trend,
  x: "date",
  y: ["clicks", "impressions"],
  xAxis: { type: "time", timeGrain: "day" },
  title: "Reach over time",
  subtitle: data.value.period ? `${data.value.period.from} to ${data.value.period.to}` : "",
}))
const channelShare = computed(() => ({
  loading: loading.value,
  data: data.value.by_channel,
  category: "channel",
  value: "spend",
  centerLabel: "spend",
  format: money,
  title: "Spend by channel",
  subtitle: "Share of the period's spend",
}))
const exerciseChart = computed(() => ({
  loading: loading.value,
  data: data.value.by_exercise,
  x: "name",
  y: ["spend"],
  horizontal: true,
  title: "Analytics by exercise",
  subtitle: "Spend in the period, largest first",
}))
const channelChart = computed(() => ({
  loading: loading.value,
  data: data.value.by_channel,
  x: "channel",
  y: ["clicks", "conversions"],
  title: "Analytics by channel",
  subtitle: "Clicks and conversions",
}))
</script>
