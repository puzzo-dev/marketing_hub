<template>
  <div class="flex h-full flex-col overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="[{ label: 'Marketing Hub' }, { label: 'Leads Pipeline' }]" />
      </template>
      <template #right-header>
        <Button variant="ghost" @click="refreshAll" :loading="overview.loading">
          <template #icon>
            <IconRefreshCw class="h-4 w-4" />
          </template>
        </Button>
      </template>
    </LayoutHeader>

    <div class="flex-1 overflow-auto p-5">
      <!-- Loading -->
      <div v-if="overview.loading && !overview.data" class="flex items-center justify-center py-12">
        <LoadingIndicator class="h-6 w-6" />
      </div>

      <template v-else>
        <!-- KPIs -->
        <div class="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard label="Total Marketing Leads" :value="stats.total_leads" />
          <StatCard label="Last 30 Days" :value="stats.recent_leads" />
          <StatCard label="Converted" :value="stats.converted" />
          <StatCard label="Conversion Rate" :value="stats.conversion_rate + '%'" />
        </div>

        <!-- Charts Row -->
        <div class="mb-6 grid gap-6 lg:grid-cols-2">
          <!-- Leads by Campaign -->
          <div class="rounded-lg border border-outline-gray-1 bg-surface-white p-5">
            <h4 class="mb-4 text-base font-medium text-ink-gray-9">Leads by Campaign</h4>
            <DonutChart v-if="campaignDonutConfig" :config="campaignDonutConfig" />
            <div v-else class="flex h-48 items-center justify-center text-sm text-ink-gray-5">No campaign data yet</div>
          </div>

          <!-- Leads by Source -->
          <div class="rounded-lg border border-outline-gray-1 bg-surface-white p-5">
            <h4 class="mb-4 text-base font-medium text-ink-gray-9">Leads by Source</h4>
            <DonutChart v-if="sourceDonutConfig" :config="sourceDonutConfig" />
            <div v-else class="flex h-48 items-center justify-center text-sm text-ink-gray-5">No source data yet</div>
          </div>
        </div>

        <!-- Leads by Status (horizontal bar-style) -->
        <div v-if="stats.by_status?.length" class="mb-6 rounded-lg border border-outline-gray-1 bg-surface-white p-5">
          <h4 class="mb-4 text-base font-medium text-ink-gray-9">Lead Status Breakdown</h4>
          <div class="space-y-3">
            <div v-for="s in stats.by_status" :key="s.status" class="flex items-center gap-3">
              <span class="w-24 text-sm text-ink-gray-7">{{ s.status || 'Unknown' }}</span>
              <div class="flex-1">
                <div class="h-5 rounded-md" :style="{ width: statusBarWidth(s.count), backgroundColor: statusColor(s.status) }"></div>
              </div>
              <span class="w-8 text-right text-sm font-medium text-ink-gray-9">{{ s.count }}</span>
            </div>
          </div>
        </div>

        <!-- Filters -->
        <div class="mb-4 flex items-center gap-3 rounded-lg border border-outline-gray-1 bg-surface-white px-4 py-3">
          <FormControl type="select" v-model="filterStatus" :options="statusOptions" placeholder="All Statuses" class="w-40" />
          <FormControl type="autocomplete" v-model="filterCampaign" :options="campaignFilterOptions" placeholder="All Campaigns" class="w-48" />
          <Button v-if="filterStatus || filterCampaign" variant="ghost" label="Clear" @click="clearFilters" />
        </div>

        <!-- Leads Table -->
        <div class="rounded-lg border border-outline-gray-1 bg-surface-white">
          <div class="border-b border-outline-gray-1 px-5 py-3">
            <h4 class="text-base font-medium text-ink-gray-9">Marketing-Attributed Leads <span class="text-sm text-ink-gray-5">({{ leadsList.total || 0 }})</span></h4>
          </div>

          <div v-if="leadsResource.loading" class="flex items-center justify-center py-12">
            <LoadingIndicator class="h-6 w-6" />
          </div>

          <div v-else-if="leadsList.leads?.length" class="overflow-x-auto">
            <table class="min-w-full divide-y divide-outline-gray-1">
              <thead>
                <tr>
                  <th class="px-5 py-2.5 text-left text-xs font-medium uppercase text-ink-gray-5">Name</th>
                  <th class="px-5 py-2.5 text-left text-xs font-medium uppercase text-ink-gray-5">Email</th>
                  <th class="px-5 py-2.5 text-left text-xs font-medium uppercase text-ink-gray-5">Status</th>
                  <th class="px-5 py-2.5 text-left text-xs font-medium uppercase text-ink-gray-5">Campaign</th>
                  <th class="px-5 py-2.5 text-left text-xs font-medium uppercase text-ink-gray-5">Source</th>
                  <th class="px-5 py-2.5 text-left text-xs font-medium uppercase text-ink-gray-5">Medium</th>
                  <th class="px-5 py-2.5 text-left text-xs font-medium uppercase text-ink-gray-5">Date</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-outline-gray-1">
                <tr v-for="lead in leadsList.leads" :key="lead.name" class="transition-colors hover:bg-surface-gray-2 cursor-pointer" @click="openLead(lead.name)">
                  <td class="px-5 py-3 text-sm font-medium text-ink-gray-9">{{ lead.lead_name || lead.name }}</td>
                  <td class="px-5 py-3 text-sm text-ink-gray-6">{{ lead.email_id || '—' }}</td>
                  <td class="whitespace-nowrap px-5 py-3">
                    <Badge :label="lead.status" variant="subtle" :theme="leadStatusTheme(lead.status)" />
                  </td>
                  <td class="whitespace-nowrap px-5 py-3 text-sm text-ink-gray-6">{{ lead.utm_campaign || '—' }}</td>
                  <td class="whitespace-nowrap px-5 py-3 text-sm text-ink-gray-6">{{ lead.utm_source || '—' }}</td>
                  <td class="whitespace-nowrap px-5 py-3 text-sm text-ink-gray-6">{{ lead.utm_medium || '—' }}</td>
                  <td class="whitespace-nowrap px-5 py-3 text-sm text-ink-gray-6">{{ formatDate(lead.creation) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-else class="relative flex h-40 w-full justify-center">
            <div class="absolute left-1/2 flex -translate-x-1/2 flex-col items-center gap-3" style="top: 25%">
              <IconUserPlus class="h-7 w-7 text-ink-gray-5" />
              <span class="text-base font-medium text-ink-gray-8">No marketing leads found</span>
              <span class="text-center text-sm text-ink-gray-6">Leads with UTM campaign attribution will appear here</span>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import {
  Breadcrumbs,
  createResource,
  Button,
  FormControl,
  Badge,
  LoadingIndicator,
  DonutChart,
} from 'frappe-ui'
import LayoutHeader from '@/components/LayoutHeader.vue'
import StatCard from '@/components/StatCard.vue'

import IconRefreshCw from '~icons/lucide/refresh-cw'
import IconUserPlus from '~icons/lucide/user-plus'

const filterStatus = ref('')
const filterCampaign = ref('')

const overview = createResource({
  url: 'marketing_hub.api.leads.get_leads_overview',
  auto: true,
})

const leadsResource = createResource({
  url: 'marketing_hub.api.leads.get_leads_list',
  params: { limit: 50 },
  auto: true,
})

const stats = computed(() => overview.data || {
  total_leads: 0, recent_leads: 0, converted: 0, conversion_rate: 0,
  by_status: [], by_campaign: [], by_source: [],
})

const leadsList = computed(() => leadsResource.data || { leads: [], total: 0 })

const statusOptions = [
  { label: 'All Statuses', value: '' },
  { label: 'Open', value: 'Open' },
  { label: 'Replied', value: 'Replied' },
  { label: 'Opportunity', value: 'Opportunity' },
  { label: 'Converted', value: 'Converted' },
  { label: 'Do Not Contact', value: 'Do Not Contact' },
]

const campaignFilterOptions = computed(() => {
  const campaigns = stats.value.by_campaign || []
  return [
    { label: 'All Campaigns', value: '' },
    ...campaigns.map(c => ({ label: c.campaign, value: c.campaign })),
  ]
})

const campaignDonutConfig = computed(() => {
  const data = stats.value.by_campaign
  if (!data?.length) return null
  return {
    title: 'Leads by Campaign',
    data,
    categoryColumn: 'campaign',
    valueColumn: 'count',
    colors: ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4'],
  }
})

const sourceDonutConfig = computed(() => {
  const data = stats.value.by_source
  if (!data?.length) return null
  return {
    title: 'Leads by Source',
    data,
    categoryColumn: 'source',
    valueColumn: 'count',
    colors: ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'],
  }
})

// Watch filters to refetch leads
watch([filterStatus, filterCampaign], () => {
  const params = { limit: 50 }
  if (filterStatus.value) params.status = filterStatus.value
  if (filterCampaign.value) params.campaign = filterCampaign.value
  leadsResource.update({ params })
  leadsResource.reload()
})

function clearFilters() {
  filterStatus.value = ''
  filterCampaign.value = ''
}

function refreshAll() {
  overview.reload()
  leadsResource.reload()
}

function statusBarWidth(count) {
  const max = Math.max(...(stats.value.by_status || []).map(s => s.count), 1)
  return Math.max((count / max) * 100, 2) + '%'
}

function statusColor(status) {
  return { Open: '#3B82F6', Replied: '#F59E0B', Opportunity: '#8B5CF6', Converted: '#10B981', 'Do Not Contact': '#9CA3AF' }[status] || '#D1D5DB'
}

function leadStatusTheme(status) {
  return { Open: 'blue', Replied: 'orange', Opportunity: 'violet', Converted: 'green', 'Do Not Contact': 'gray' }[status] || 'gray'
}

function openLead(name) {
  window.location.href = `/app/lead/${name}`
}

function formatDate(date) {
  if (!date) return '—'
  return new Date(date).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}
</script>
