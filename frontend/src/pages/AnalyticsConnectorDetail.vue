<template>
  <div class="flex h-full flex-col overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="[
          { label: 'Connectors', route: { path: '/marketing/connectors' } },
          { label: connector.doc?.connector_name || connectorName }
        ]" />
      </template>
      <template #right-header>
        <Badge v-if="connector.doc" :label="connector.doc.sync_status" variant="subtle" :theme="theme(connector.doc.sync_status)" />
        <Button variant="ghost" @click="openDesk"><template #prefix><IconExternalLink class="h-4 w-4" /></template>Desk</Button>
      </template>
    </LayoutHeader>

    <div v-if="connector.doc" class="flex-1 overflow-auto p-5">
      <div class="mx-auto max-w-4xl space-y-5">
        <!-- Header Card -->
        <div class="rounded-lg border border-outline-gray-1 bg-surface-white p-5 shadow-sm">
          <h2 class="text-lg font-semibold text-ink-gray-9">{{ connector.doc.connector_name }}</h2>
          <p class="mt-1 text-sm text-ink-gray-6">{{ connector.doc.platform }} · {{ connector.doc.ad_account }}</p>
          <div v-if="connector.doc.last_error" class="mt-3 rounded-md bg-surface-red-1 p-3 text-sm text-ink-red-3">{{ connector.doc.last_error }}</div>
        </div>

        <!-- Stats -->
        <div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div class="rounded-lg border border-outline-gray-1 bg-surface-white p-4 text-center">
            <div class="text-xs font-medium text-ink-gray-5">Total Syncs</div>
            <div class="mt-1.5 text-lg font-semibold text-ink-gray-9">{{ connector.doc.total_syncs || 0 }}</div>
          </div>
          <div class="rounded-lg border border-outline-gray-1 bg-surface-white p-4 text-center">
            <div class="text-xs font-medium text-ink-gray-5">Failed</div>
            <div class="mt-1.5 text-lg font-semibold text-ink-red-3">{{ connector.doc.failed_syncs || 0 }}</div>
          </div>
          <div class="rounded-lg border border-outline-gray-1 bg-surface-white p-4 text-center">
            <div class="text-xs font-medium text-ink-gray-5">Consecutive Failures</div>
            <div class="mt-1.5 text-lg font-semibold text-ink-amber-3">{{ connector.doc.consecutive_failures || 0 }}</div>
          </div>
          <div class="rounded-lg border border-outline-gray-1 bg-surface-white p-4 text-center">
            <div class="text-xs font-medium text-ink-gray-5">Last Sync</div>
            <div class="mt-1.5 text-sm font-medium text-ink-gray-9">{{ fmtDate(connector.doc.last_sync_date) }}</div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex gap-2">
          <Button v-if="!connector.doc.sync_in_progress" variant="solid" @click="triggerSync" :loading="syncing">
            <template #prefix><IconRefreshCw class="h-4 w-4" /></template>Sync Now
          </Button>
          <Button v-else variant="outline" disabled>
            <template #prefix><IconLoader class="h-4 w-4 animate-spin" /></template>Syncing...
          </Button>
          <Button variant="outline" @click="fetchCampaigns" :loading="fetching">
            <template #prefix><IconGlobe class="h-4 w-4" /></template>Fetch Platform Campaigns
          </Button>
        </div>

        <!-- Settings -->
        <div class="rounded-lg border border-outline-gray-1 bg-surface-white p-5 shadow-sm">
          <h3 class="mb-4 text-base font-medium text-ink-gray-9">Settings</h3>
          <div class="grid gap-4 sm:grid-cols-2">
            <FormControl label="Connector Name" v-model="editForm.connector_name" type="text" />
            <FormControl label="Sync Frequency" v-model="editForm.sync_frequency" type="select" :options="freqOpts" />
            <FormControl label="Sync Start Date" v-model="editForm.sync_start_date" type="date" />
            <FormControl label="Is Active" v-model="editForm.is_active" type="checkbox" />
            <FormControl label="Auto Create Campaigns" v-model="editForm.auto_create_campaigns" type="checkbox" />
          </div>
          <div class="mt-4 flex justify-end gap-2">
            <Button variant="subtle" @click="resetForm">Reset</Button>
            <Button variant="solid" @click="saveSettings" :loading="saving">Save</Button>
          </div>
        </div>

        <!-- Platform Campaigns -->
        <div v-if="platformCampaigns.length" class="rounded-lg border border-outline-gray-1 bg-surface-white p-5 shadow-sm">
          <h3 class="mb-3 text-base font-medium text-ink-gray-9">Platform Campaigns</h3>
          <div class="divide-y divide-outline-gray-1">
            <div v-for="camp in platformCampaigns" :key="camp.id" class="flex items-center justify-between py-2">
              <div>
                <p class="text-sm font-medium text-ink-gray-9">{{ camp.name }}</p>
                <p class="text-xs text-ink-gray-5">ID: {{ camp.id }} · {{ camp.status }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="connector.loading" class="flex flex-1 items-center justify-center">
      <LoadingIndicator class="h-6 w-6" />
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Breadcrumbs, Badge, Button, FormControl, LoadingIndicator, getDocResource, call } from 'frappe-ui'
import LayoutHeader from '@/components/LayoutHeader.vue'
import { toast } from '@/utils/toast'

import IconExternalLink from '~icons/lucide/external-link'
import IconRefreshCw from '~icons/lucide/refresh-cw'
import IconGlobe from '~icons/lucide/globe'
import IconLoader from '~icons/lucide/loader'

const route = useRoute()
const connectorName = route.params.name

const connector = getDocResource({
  doctype: 'Analytics Connector',
  name: connectorName,
  auto: true,
})

const syncing = ref(false)
const fetching = ref(false)
const saving = ref(false)
const platformCampaigns = ref([])

const editForm = ref({})

const freqOpts = [{ label: 'Hourly', value: 'Hourly' }, { label: 'Daily', value: 'Daily' }, { label: 'Weekly', value: 'Weekly' }]

watch(() => connector.doc, (doc) => {
  if (doc) {
    editForm.value = {
      connector_name: doc.connector_name,
      sync_frequency: doc.sync_frequency,
      sync_start_date: doc.sync_start_date,
      is_active: doc.is_active,
      auto_create_campaigns: doc.auto_create_campaigns,
    }
  }
}, { immediate: true })

function theme(s) { if (s === 'Active') return 'green'; if (s === 'Error') return 'red'; if (s === 'Paused') return 'orange'; return 'gray' }
function fmtDate(dt) { return dt ? new Date(dt).toLocaleString() : '—' }
function openDesk() { window.open(`/app/analytics-connector/${connectorName}`, '_blank') }
function resetForm() {
  if (connector.doc) {
    editForm.value = {
      connector_name: connector.doc.connector_name,
      sync_frequency: connector.doc.sync_frequency,
      sync_start_date: connector.doc.sync_start_date,
      is_active: connector.doc.is_active,
      auto_create_campaigns: connector.doc.auto_create_campaigns,
    }
  }
}

async function triggerSync() {
  syncing.value = true
  try {
    const res = await call('marketing_hub.marketing_hub.doctype.analytics_connector.analytics_connector.sync_connector', { connector_name: connectorName })
    toast({ title: res.status, text: res.message, icon: res.status === 'Success' ? 'check' : 'alert-triangle', iconClasses: res.status === 'Success' ? 'text-green-600' : 'text-amber-600' })
    connector.reload()
  } catch (e) {
    toast({ title: 'Error', text: e.message || 'Sync failed', icon: 'x', iconClasses: 'text-red-600' })
  } finally { syncing.value = false }
}

async function fetchCampaigns() {
  fetching.value = true
  try {
    const res = await call('marketing_hub.marketing_hub.doctype.analytics_connector.analytics_connector.get_campaigns_from_platform', { connector_name: connectorName })
    if (res.status === 'Success') platformCampaigns.value = res.campaigns || []
    else toast({ title: 'Error', text: res.message, icon: 'x', iconClasses: 'text-red-600' })
  } catch (e) {
    toast({ title: 'Error', text: e.message || 'Fetch failed', icon: 'x', iconClasses: 'text-red-600' })
  } finally { fetching.value = false }
}

async function saveSettings() {
  saving.value = true
  try {
    await call('frappe.client.set_value', {
      doctype: 'Analytics Connector',
      name: connectorName,
      fieldname: editForm.value,
    })
    toast({ title: 'Success', text: 'Settings saved', icon: 'check', iconClasses: 'text-green-600' })
    connector.reload()
  } catch (e) {
    toast({ title: 'Error', text: e.message || 'Save failed', icon: 'x', iconClasses: 'text-red-600' })
  } finally { saving.value = false }
}
</script>
