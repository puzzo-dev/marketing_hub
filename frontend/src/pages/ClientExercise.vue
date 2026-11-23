<template>
  <PageHeader><Breadcrumbs :items="[{ label: 'Overview', route: { name: 'Home' } }, { label: ex?.campaign_name || name }]" /></PageHeader>
  <ErrorState v-if="call.error.value" icon="lucide-lock" title="You do not have access to this" text="Ask your agency to share this exercise with you." />
  <div v-else-if="ex" class="flex flex-col">
    <Tabs v-model="tab" :tabs="[{ value: 'overview', label: 'Overview' }, { value: 'content', label: 'Posted content' }, { value: 'ooh', label: 'Out of home' }, { value: 'results', label: 'Results' }, { value: 'spend', label: 'Spend' }]" variant="underline" class="px-3 sm:px-5" />
    <div class="flex max-w-3xl flex-col gap-3 p-5">
      <template v-if="tab === 'overview'"><Badge :label="ex.status" :theme="badgeTheme(ex.status)" /><p class="text-base text-ink-gray-8">{{ ex.objective }}</p><p class="text-sm text-ink-gray-6">{{ ex.start_date }} to {{ ex.end_date }}</p></template>
      <template v-else-if="tab === 'content'"><div v-for="c in content" :key="c.name" class="flex h-11 items-center border-b px-3 text-base text-ink-gray-8">{{ c.title }}</div><p v-if="!content.length" class="text-base text-ink-gray-6">Nothing posted yet.</p></template>
      <template v-else-if="tab === 'ooh'"><div v-for="o in ooh" :key="o.site + o.start_date" class="flex h-11 items-center gap-3 border-b px-3 text-base"><span class="flex-1 text-ink-gray-8">{{ o.site }}</span><span class="text-sm text-ink-gray-6">{{ o.start_date }} to {{ o.end_date }}</span><Badge :label="o.status" :theme="badgeTheme(o.status)" /></div><p v-if="!ooh.length" class="text-base text-ink-gray-6">No live sites yet.</p></template>
      <template v-else-if="tab === 'results'"><div class="rounded-6 bg-surface-gray-1 p-4"><div class="text-sm text-ink-gray-6">Leads</div><div class="mt-1 text-2xl font-semibold text-ink-gray-9">{{ results?.leads ?? "—" }}</div></div></template>
      <template v-else><div class="rounded-6 bg-surface-gray-1 p-4"><div class="text-sm text-ink-gray-6">Spent of {{ money(spend?.budget) }}</div><div class="mt-1 text-2xl font-semibold text-ink-gray-9">{{ money(spend?.spent) }}</div></div></template>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue"
import { Badge, Breadcrumbs, PageHeader, Tabs, useCall } from "frappe-ui"
import ErrorState from "./ErrorState.vue"
import { badgeTheme } from "@/lib/status"

const props = defineProps({ name: String })
const tab = ref("overview")
// Clients call the client-safe API only; it never returns rates, vendors or approvers.
const get = (method) => {
  const c = useCall({ url: `/api/method/marketing_hub.api.client.${method}`, params: { name: props.name } })
  return [c, computed(() => c.data.value?.message ?? c.data.value)]
}
const [call, ex] = get("exercise")
const [, content] = [0, get("posted_content")[1]]
const ooh = get("out_of_home")[1]
const results = get("results")[1]
const spend = get("spend")[1]
const money = (v) => (v == null ? "—" : new Intl.NumberFormat(undefined, { style: "currency", currency: "NGN", maximumFractionDigits: 0 }).format(v))
</script>
