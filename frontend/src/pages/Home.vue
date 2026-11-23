<template>
  <AppHeader title="Home">
    <template #actions>
      <div class="w-56"><LinkSelect doctype="Marketing Campaign" label-field="campaign_name" placeholder="All exercises" v-model="exercise" /></div>
      <Select v-model="period" :options="periods" size="sm" />
    </template>
  </AppHeader>

  <ErrorState v-if="call.error.value" icon="lucide-triangle-alert" title="Something went wrong on our side" text="Nothing was lost. Try again." action-label="Try again" @action="call.reload?.() || call.execute?.()" />

  <div v-else class="flex flex-col gap-4 p-4 sm:p-5">
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-5">
      <NumberCard v-for="k in cards" :key="k.title" v-bind="k" />
    </div>

    <div class="grid grid-cols-1 gap-4 lg:grid-cols-3">
      <section :class="[card, 'h-80 lg:col-span-2']">
        <AreaChart v-bind="trendChart" />
      </section>
      <section :class="[card, 'h-80']">
        <DonutChart v-bind="channelShare" />
      </section>

      <section :class="[card, 'h-96 lg:col-span-2']">
        <BarChart v-bind="exerciseChart" />
      </section>
      <section :class="[card, 'h-96']">
        <BarChart v-bind="channelChart" />
      </section>
    </div>

    <section :class="[card, 'overflow-hidden']">
      <h3 class="pb-2 text-lg-medium text-ink-gray-9">Exercises</h3>
      <div class="grid h-8 grid-cols-[minmax(0,1.6fr)_repeat(4,minmax(0,1fr))] items-center gap-3 rounded-4 bg-surface-gray-2 px-3 text-sm text-ink-gray-6">
        <span>Exercise</span><span>Spend</span><span>Impressions</span><span>Clicks</span><span>Conversions</span>
      </div>
      <router-link v-for="r in data.by_exercise" :key="r.exercise" :to="{ name: 'Exercise', params: { name: r.exercise } }" class="grid h-11 grid-cols-[minmax(0,1.6fr)_repeat(4,minmax(0,1fr))] items-center gap-3 border-b px-3 text-base hover:bg-surface-gray-1">
        <span class="truncate text-ink-gray-8">{{ r.name }}</span><span class="text-ink-gray-8">{{ money(r.spend) }}</span><span class="text-ink-gray-6">{{ num(r.impressions) }}</span><span class="text-ink-gray-6">{{ num(r.clicks) }}</span><span class="text-ink-gray-6">{{ num(r.conversions) }}</span>
      </router-link>
      <p v-if="!data.by_exercise.length" class="py-3 text-base text-ink-gray-6">No analytics in this period. Numbers appear once an analytics connector has synced.</p>
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from "vue"
import { Select, useCall } from "frappe-ui"
import AppHeader from "@/components/AppHeader.vue"
import ErrorState from "./ErrorState.vue"
import { AreaChart, BarChart, DonutChart, NumberCard } from "frappe-ui/charts"
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

const card = "flex min-w-0 flex-col rounded-xl border border-outline-gray-1 bg-surface-elevation-2 px-4 py-3"
const kpi = (title, key, format, extra = {}) => ({
  title,
  loading: loading.value,
  value: data.value.kpis[key]?.value ?? null,
  format,
  delta: data.value.kpis[key]?.change ?? null,
  deltaSuffix: "%",
  deltaCaption: caption.value,
  ...extra,
})
const cards = computed(() => [
  kpi("Spend", "spend", money),
  kpi("Impressions", "impressions", num),
  kpi("Clicks", "clicks", num),
  kpi("Leads", "leads", num),
  kpi("Cost per lead", "cost_per_lead", money, { delta: null, negativeIsBetter: true }),
])

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
