<template>
  <div class="flex h-full flex-col overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="[{ label: 'Marketing Hub' }, { label: 'Tracking Links' }]" />
      </template>
      <template #right-header>
        <Button variant="ghost" @click="linksResource.reload()" :loading="linksResource.loading">
          <template #icon>
            <IconRefreshCw class="h-4 w-4" />
          </template>
        </Button>
        <Button variant="solid" label="Create Link" @click="showCreateDialog = true">
          <template #prefix>
            <IconPlus class="h-4 w-4" />
          </template>
        </Button>
      </template>
    </LayoutHeader>

    <div class="flex-1 overflow-auto p-5">
      <!-- Stats Row -->
      <div class="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard label="Total Links" :value="links.length" />
        <StatCard label="Total Clicks" :value="totalClicks" />
        <StatCard label="Unique Clicks" :value="totalUnique" />
      </div>

      <!-- Links List -->
      <div class="rounded-lg border border-outline-gray-1 bg-surface-white">
        <div class="border-b border-outline-gray-1 px-5 py-3">
          <h4 class="text-base font-medium text-ink-gray-9">All Tracking Links</h4>
        </div>

        <div v-if="linksResource.loading" class="flex items-center justify-center py-12">
          <LoadingIndicator class="h-6 w-6" />
        </div>

        <div v-else-if="links.length" class="divide-y divide-outline-gray-1">
          <div
            v-for="link in links"
            :key="link.name"
            class="flex items-start gap-4 px-5 py-4 transition-colors hover:bg-surface-gray-2"
          >
            <!-- QR Thumbnail -->
            <div class="flex h-14 w-14 shrink-0 items-center justify-center rounded-lg border border-outline-gray-1 bg-surface-gray-1">
              <img v-if="link.qr_code" :src="link.qr_code" alt="QR" class="h-12 w-12 object-contain" />
              <IconQrCode v-else class="h-6 w-6 text-ink-gray-5" />
            </div>

            <!-- Link Info -->
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-2">
                <h4 class="text-sm font-medium text-ink-gray-9 line-clamp-1">{{ link.link_name }}</h4>
                <Badge :label="link.status" variant="subtle" :theme="link.status === 'Active' ? 'green' : 'gray'" />
              </div>
              <p class="mt-0.5 text-xs text-ink-gray-5 line-clamp-1">{{ link.destination_url }}</p>
              <div class="mt-1 flex items-center gap-3 text-xs text-ink-gray-6">
                <span v-if="link.campaign">{{ link.campaign }}</span>
                <span>{{ link.total_clicks || 0 }} clicks</span>
                <span>{{ link.unique_clicks || 0 }} unique</span>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex shrink-0 items-center gap-2">
              <Button variant="subtle" size="sm" @click="copyUrl(link.tracking_url)">
                <template #icon>
                  <IconCopy class="h-3.5 w-3.5" />
                </template>
              </Button>
              <Button variant="subtle" size="sm" @click="showDetail(link)">
                <template #icon>
                  <IconExternalLink class="h-3.5 w-3.5" />
                </template>
              </Button>
            </div>
          </div>
        </div>

        <div v-else class="relative flex h-52 w-full justify-center">
          <div class="absolute left-1/2 flex -translate-x-1/2 flex-col items-center gap-3" style="top: 25%">
            <IconLink2 class="h-7 w-7 text-ink-gray-5" />
            <span class="text-base font-medium text-ink-gray-8">No tracking links yet</span>
            <span class="text-center text-sm text-ink-gray-6">Create tracking links with QR codes for your OOH campaigns</span>
            <Button @click="showCreateDialog = true" variant="solid" label="Create First Link">
              <template #prefix>
                <IconPlus class="h-4 w-4" />
              </template>
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Link Dialog -->
    <Dialog v-model="showCreateDialog" :options="{ title: 'Create Tracking Link', size: 'lg' }" :disableOutsideClickToClose="true">
      <template #body-content>
        <div class="space-y-4">
          <FormControl label="Link Name" v-model="newLink.link_name" :required="true" placeholder="e.g. Billboard NYC Q1" />
          <FormControl label="Destination URL" v-model="newLink.destination_url" :required="true" placeholder="https://yoursite.com/landing-page" />

          <div class="grid grid-cols-2 gap-4">
            <FormControl label="Campaign (Optional)" type="autocomplete" v-model="newLink.campaign" :options="campaignOptions" placeholder="Link to a campaign" />
            <FormControl label="Channel" type="select" v-model="newLink.channel"
              :options="[
                { label: 'QR Code', value: 'QR Code' },
                { label: 'Billboard', value: 'Billboard' },
                { label: 'Print Ad', value: 'Print Ad' },
                { label: 'Flyer', value: 'Flyer' },
                { label: 'Event', value: 'Event' },
                { label: 'Business Card', value: 'Business Card' },
                { label: 'Other', value: 'Other' },
              ]" />
          </div>

          <h5 class="text-sm font-medium text-ink-gray-7">UTM Parameters</h5>
          <div class="grid grid-cols-2 gap-4">
            <FormControl label="Source" v-model="newLink.utm_source" placeholder="qr" />
            <FormControl label="Medium" v-model="newLink.utm_medium" placeholder="offline" />
          </div>
          <div class="grid grid-cols-3 gap-4">
            <FormControl label="Campaign Tag" v-model="newLink.utm_campaign" placeholder="summer_sale" />
            <FormControl label="Term" v-model="newLink.utm_term" placeholder="Optional" />
            <FormControl label="Content" v-model="newLink.utm_content" placeholder="Optional" />
          </div>
        </div>
      </template>
      <template #actions>
        <Button variant="ghost" label="Cancel" @click="showCreateDialog = false" />
        <Button variant="solid" label="Create & Generate QR" :loading="creating" @click="createLink" />
      </template>
    </Dialog>

    <!-- Link Detail Dialog -->
    <Dialog v-model="showDetailDialog" :options="{ title: selectedLink?.link_name || 'Link Detail', size: 'lg' }">
      <template #body-content>
        <div v-if="selectedLink" class="space-y-5">
          <!-- QR Code Display -->
          <div class="flex items-start gap-6">
            <div class="flex h-40 w-40 shrink-0 items-center justify-center rounded-lg border border-outline-gray-1 bg-white p-2">
              <img v-if="selectedLink.qr_code" :src="selectedLink.qr_code" alt="QR Code" class="h-full w-full object-contain" />
              <IconQrCode v-else class="h-12 w-12 text-ink-gray-4" />
            </div>
            <div class="flex-1 space-y-2">
              <div>
                <label class="text-xs font-medium text-ink-gray-5">Tracking URL</label>
                <div class="mt-0.5 flex items-center gap-2">
                  <code class="flex-1 truncate rounded bg-surface-gray-2 px-2 py-1 text-xs text-ink-gray-9">{{ selectedLink.tracking_url }}</code>
                  <Button variant="ghost" size="sm" @click="copyUrl(selectedLink.tracking_url)">
                    <template #icon><IconCopy class="h-3.5 w-3.5" /></template>
                  </Button>
                </div>
              </div>
              <div>
                <label class="text-xs font-medium text-ink-gray-5">Destination</label>
                <p class="mt-0.5 truncate text-xs text-ink-gray-7">{{ selectedLink.destination_url }}</p>
              </div>
              <div class="grid grid-cols-3 gap-4 pt-2">
                <div>
                  <div class="text-xs text-ink-gray-5">Total Clicks</div>
                  <div class="text-lg font-semibold text-ink-gray-9">{{ selectedLink.total_clicks || 0 }}</div>
                </div>
                <div>
                  <div class="text-xs text-ink-gray-5">Unique Clicks</div>
                  <div class="text-lg font-semibold text-ink-gray-9">{{ selectedLink.unique_clicks || 0 }}</div>
                </div>
                <div>
                  <div class="text-xs text-ink-gray-5">Last Clicked</div>
                  <div class="text-sm text-ink-gray-7">{{ selectedLink.last_clicked ? formatDate(selectedLink.last_clicked) : '—' }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- UTM Info -->
          <div v-if="selectedLink.utm_source || selectedLink.utm_medium || selectedLink.utm_campaign" class="rounded-lg border border-outline-gray-1 p-3">
            <label class="mb-2 text-xs font-medium text-ink-gray-5">UTM Parameters</label>
            <div class="grid grid-cols-3 gap-2 text-xs">
              <div v-if="selectedLink.utm_source"><span class="text-ink-gray-5">Source: </span><span class="text-ink-gray-9">{{ selectedLink.utm_source }}</span></div>
              <div v-if="selectedLink.utm_medium"><span class="text-ink-gray-5">Medium: </span><span class="text-ink-gray-9">{{ selectedLink.utm_medium }}</span></div>
              <div v-if="selectedLink.utm_campaign"><span class="text-ink-gray-5">Campaign: </span><span class="text-ink-gray-9">{{ selectedLink.utm_campaign }}</span></div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex gap-2">
            <Button v-if="selectedLink.qr_code" variant="subtle" label="Download QR" @click="downloadQR(selectedLink)">
              <template #prefix><IconDownload class="h-4 w-4" /></template>
            </Button>
            <Button variant="subtle" label="Copy Tracking URL" @click="copyUrl(selectedLink.tracking_url)">
              <template #prefix><IconCopy class="h-4 w-4" /></template>
            </Button>
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  Breadcrumbs,
  createResource,
  Button,
  FormControl,
  Badge,
  Dialog,
  LoadingIndicator,
  call,
} from 'frappe-ui'
import { toast } from '@/utils/toast'
import LayoutHeader from '@/components/LayoutHeader.vue'
import StatCard from '@/components/StatCard.vue'

import IconRefreshCw from '~icons/lucide/refresh-cw'
import IconPlus from '~icons/lucide/plus'
import IconCopy from '~icons/lucide/copy'
import IconExternalLink from '~icons/lucide/external-link'
import IconLink2 from '~icons/lucide/link-2'
import IconQrCode from '~icons/lucide/qr-code'
import IconDownload from '~icons/lucide/download'

const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const creating = ref(false)
const selectedLink = ref(null)

const newLink = ref({
  link_name: '',
  destination_url: '',
  campaign: '',
  channel: 'QR Code',
  utm_source: 'qr',
  utm_medium: 'offline',
  utm_campaign: '',
  utm_term: '',
  utm_content: '',
})

const linksResource = createResource({
  url: 'marketing_hub.api.tracking.get_tracking_links',
  auto: true,
})

const campaignsResource = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'Marketing Campaign',
    fields: ['name', 'campaign_name'],
    filters: { status: ['in', ['Draft', 'Active']] },
    limit_page_length: 100,
  },
  auto: true,
})

const links = computed(() => linksResource.data || [])
const campaignOptions = computed(() =>
  (campaignsResource.data || []).map(c => ({ label: c.campaign_name, value: c.name }))
)
const totalClicks = computed(() => links.value.reduce((sum, l) => sum + (l.total_clicks || 0), 0))
const totalUnique = computed(() => links.value.reduce((sum, l) => sum + (l.unique_clicks || 0), 0))

async function createLink() {
  if (!newLink.value.link_name || !newLink.value.destination_url) {
    toast({ title: 'Validation Error', text: 'Link Name and Destination URL are required', icon: 'alert-circle', iconClasses: 'text-ink-amber-2' })
    return
  }

  creating.value = true
  try {
    const result = await call('marketing_hub.api.tracking.create_tracking_link', {
      data: JSON.stringify(newLink.value),
    })

    toast({ title: 'Link Created', text: `Tracking URL: ${result.tracking_url}`, icon: 'check', iconClasses: 'text-ink-green-2' })
    showCreateDialog.value = false
    newLink.value = { link_name: '', destination_url: '', campaign: '', channel: 'QR Code', utm_source: 'qr', utm_medium: 'offline', utm_campaign: '', utm_term: '', utm_content: '' }
    linksResource.reload()
  } catch (e) {
    toast({ title: 'Error', text: e.message || 'Failed to create link', icon: 'x', iconClasses: 'text-ink-red-2' })
  } finally {
    creating.value = false
  }
}

function showDetail(link) {
  selectedLink.value = link
  showDetailDialog.value = true
}

function copyUrl(url) {
  navigator.clipboard.writeText(url).then(() => {
    toast({ title: 'Copied', text: 'URL copied to clipboard', icon: 'check', iconClasses: 'text-ink-green-2' })
  })
}

function downloadQR(link) {
  if (!link.qr_code) return
  const a = document.createElement('a')
  a.href = link.qr_code
  a.download = `qr_${link.short_code}.png`
  a.click()
}

function formatDate(date) {
  if (!date) return '—'
  return new Date(date).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}
</script>
