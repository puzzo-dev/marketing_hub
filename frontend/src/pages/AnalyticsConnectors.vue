<template>
  <div class="flex h-full flex-col overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="[{ label: 'Marketing Hub' }, { label: 'Analytics Connectors' }]" />
      </template>
      <template #right-header>
        <Button @click="showCreate = true" variant="solid" label="New Connector">
          <template #prefix><IconPlus class="h-4 w-4" /></template>
        </Button>
      </template>
    </LayoutHeader>

    <div class="flex items-center gap-3 border-b px-5 py-3">
      <div class="relative flex-1 max-w-xs">
        <IconSearch class="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-gray-4" />
        <FormControl type="text" v-model="searchQuery" placeholder="Search connectors..." class="pl-8" />
      </div>
      <div class="flex gap-1.5">
        <Button v-for="s in statusFilters" :key="s.value" @click="selectedStatus = s.value"
          :variant="selectedStatus === s.value ? 'subtle' : 'ghost'" size="sm" :label="s.label" />
      </div>
    </div>

    <div class="flex-1 overflow-auto p-5">
      <div v-if="connectorsResource.loading" class="flex items-center justify-center py-12">
        <LoadingIndicator class="h-6 w-6" />
      </div>
      <div v-else-if="filtered.length === 0" class="relative flex h-full w-full justify-center">
        <div class="absolute left-1/2 flex w-4/12 -translate-x-1/2 flex-col items-center gap-3" style="top: 35%">
          <IconPlug class="h-7 w-7 text-ink-gray-5" />
          <span class="text-base font-medium text-ink-gray-8">No connectors yet</span>
          <Button @click="showCreate = true" variant="solid" label="Create Connector" />
        </div>
      </div>
      <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div v-for="c in filtered" :key="c.name" class="rounded-lg border border-outline-gray-1 bg-surface-white p-4 shadow-sm">
          <div class="mb-3 flex items-start justify-between">
            <div>
              <h4 class="text-base font-medium text-ink-gray-9 line-clamp-1">{{ c.connector_name || c.name }}</h4>
              <p class="mt-0.5 text-xs text-ink-gray-5">{{ c.platform }} · {{ c.ad_account }}</p>
            </div>
            <Badge :label="c.sync_status || 'Active'" variant="subtle" :theme="theme(c.sync_status)" />
          </div>
          <div class="mb-3 grid grid-cols-2 gap-2 text-xs">
            <div class="rounded bg-surface-gray-1 p-1.5"><div class="text-ink-gray-5">Frequency</div><div class="font-medium text-ink-gray-9">{{ c.sync_frequency }}</div></div>
            <div class="rounded bg-surface-gray-1 p-1.5"><div class="text-ink-gray-5">Total Syncs</div><div class="font-medium text-ink-gray-9">{{ c.total_syncs || 0 }}</div></div>
          </div>
          <div v-if="c.last_sync_date" class="mb-3 text-xs text-ink-gray-5"><IconClock class="inline h-3 w-3 mr-1" />Last sync: {{ fmtDate(c.last_sync_date) }}</div>
          <div class="flex gap-2">
            <Button size="sm" variant="outline" @click="$router.push('/marketing/connectors/' + c.name)"><template #prefix><IconSettings class="h-3.5 w-3.5" /></template>Details</Button>
            <Button v-if="!c.sync_in_progress" size="sm" variant="solid" @click="triggerSync(c.name)" :loading="syncing === c.name"><template #prefix><IconRefreshCw class="h-3.5 w-3.5" /></template>Sync</Button>
            <Button v-else size="sm" variant="outline" disabled><template #prefix><IconLoader class="h-3.5 w-3.5 animate-spin" /></template>Syncing</Button>
          </div>
        </div>
      </div>
    </div>

    <Dialog v-model="showCreate" :options="{ title: 'New Analytics Connector', size: 'lg' }">
      <template #body-content>
        <div class="space-y-4">
          <FormControl label="Connector Name" v-model="form.connector_name" type="text" required />
          <FormControl label="Platform" v-model="form.platform" type="autocomplete" :options="platformOpts" required />
          <FormControl label="Ad Account" v-model="form.ad_account" type="autocomplete" :options="adAccountOpts" required />
          <FormControl label="Sync Frequency" v-model="form.sync_frequency" type="select" :options="freqOpts" />
          <FormControl label="Sync Start Date" v-model="form.sync_start_date" type="date" />
          <FormControl label="Auto Create Campaigns" v-model="form.auto_create_campaigns" type="checkbox" />
        </div>
      </template>
      <template #actions>
        <Button variant="solid" @click="create" :loading="creating" label="Create" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Breadcrumbs, createResource, Button, FormControl, LoadingIndicator, Badge, Dialog, call } from 'frappe-ui'
import LayoutHeader from '@/components/LayoutHeader.vue'
import { toast } from '@/utils/toast'

import IconSearch from '~icons/lucide/search'
import IconPlus from '~icons/lucide/plus'
import IconPlug from '~icons/lucide/plug'
import IconClock from '~icons/lucide/clock'
import IconSettings from '~icons/lucide/settings'
import IconRefreshCw from '~icons/lucide/refresh-cw'
import IconLoader from '~icons/lucide/loader'

const searchQuery = ref('')
const selectedStatus = ref('All')
const syncing = ref(null)
const showCreate = ref(false)
const creating = ref(false)
const form = ref({ connector_name: '', platform: '', ad_account: '', sync_frequency: 'Daily', sync_start_date: '', auto_create_campaigns: false })
const statusFilters = [{ label: 'All', value: 'All' }, { label: 'Active', value: 'Active' }, { label: 'Error', value: 'Error' }, { label: 'Paused', value: 'Paused' }]
const platformOpts = ref([])
const adAccountOpts = ref([])
const freqOpts = [{ label: 'Hourly', value: 'Hourly' }, { label: 'Daily', value: 'Daily' }, { label: 'Weekly', value: 'Weekly' }]

const connectorsResource = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'Analytics Connector',
    fields: ['name', 'connector_name', 'platform', 'ad_account', 'is_active', 'sync_frequency', 'sync_status', 'sync_in_progress', 'last_sync_date', 'total_syncs', 'failed_syncs', 'consecutive_failures'],
    limit_page_length: 100,
    order_by: 'modified desc',
  },
  auto: true,
})

const connectors = computed(() => connectorsResource.data || [])
const filtered = computed(() => {
  let r = connectors.value
  if (selectedStatus.value !== 'All') r = r.filter(c => c.sync_status === selectedStatus.value)
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    r = r.filter(c => (c.connector_name || '').toLowerCase().includes(q) || (c.platform || '').toLowerCase().includes(q))
  }
  return r
})

function theme(s) { if (s === 'Active') return 'green'; if (s === 'Error') return 'red'; if (s === 'Paused') return 'orange'; return 'gray' }
function fmtDate(dt) { return dt ? new Date(dt).toLocaleString() : '' }

async function triggerSync(name) {
  syncing.value = name
  try {
    const res = await call('marketing_hub.marketing_hub.doctype.analytics_connector.analytics_connector.sync_connector', { connector_name: name })
    toast({ title: res.status, text: res.message, icon: res.status === 'Success' ? 'check' : 'alert-triangle', iconClasses: res.status === 'Success' ? 'text-green-600' : 'text-amber-600' })
    connectorsResource.reload()
  } catch (e) {
    toast({ title: 'Error', text: e.message || 'Sync failed', icon: 'x', iconClasses: 'text-red-600' })
  } finally { syncing.value = null }
}

async function create() {
  if (!form.value.connector_name || !form.value.platform || !form.value.ad_account) {
    toast({ title: 'Validation', text: 'Fill required fields', icon: 'alert-circle', iconClasses: 'text-amber-600' })
    return
  }
  creating.value = true
  try {
    await call('frappe.client.insert', { doc: { doctype: 'Analytics Connector', ...form.value } })
    toast({ title: 'Success', text: 'Connector created', icon: 'check', iconClasses: 'text-green-600' })
    showCreate.value = false
    form.value = { connector_name: '', platform: '', ad_account: '', sync_frequency: 'Daily', sync_start_date: '', auto_create_campaigns: false }
    connectorsResource.reload()
  } catch (e) {
    toast({ title: 'Error', text: e.message || 'Create failed', icon: 'x', iconClasses: 'text-red-600' })
  } finally { creating.value = false }
}
</script>
