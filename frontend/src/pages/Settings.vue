<template>
  <div class="flex h-full flex-col overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="[{ label: 'Marketing Hub' }, { label: 'Settings' }]" />
      </template>
      <template #right-header>
        <Button variant="ghost" label="Open in Desk" @click="openFullSettings">
          <template #prefix>
            <IconExternalLink class="h-4 w-4" />
          </template>
        </Button>
        <Button variant="solid" label="Save" :loading="saving" @click="saveSettings" />
      </template>
    </LayoutHeader>

    <!-- Tabs -->
    <div class="border-b px-5">
      <div class="flex gap-1">
        <button
          v-for="tab in tabs" :key="tab.key"
          @click="activeTab = tab.key"
          class="px-4 py-2.5 text-sm font-medium transition-colors"
          :class="activeTab === tab.key
            ? 'border-b-2 border-ink-gray-9 text-ink-gray-9'
            : 'text-ink-gray-5 hover:text-ink-gray-9'"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Content Area -->
    <div class="flex-1 overflow-auto p-5">
      <div class="mx-auto max-w-4xl space-y-6">
          <!-- General Tab -->
          <template v-if="activeTab === 'general'">
            <div class="rounded-lg border border-outline-gray-2 bg-surface-cards p-6">
              <h2 class="mb-4 text-lg font-semibold text-ink-gray-9">Company & Defaults</h2>
              <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <FormControl
                  v-model="settings.company"
                  label="Default Company"
                  type="autocomplete"
                  :options="companyOptions"
                  placeholder="Select company"
                />
                <FormControl
                  v-model="settings.default_lead_source"
                  label="Default Lead Source"
                  type="text"
                  placeholder="e.g. Website, Marketing Hub"
                />
              </div>
            </div>

            <div class="rounded-lg border border-outline-gray-2 bg-surface-cards p-6">
              <h2 class="mb-4 text-lg font-semibold text-ink-gray-9">Attribution</h2>
              <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div class="space-y-3">
                  <div class="flex items-center justify-between">
                    <div>
                      <div class="font-medium text-ink-gray-9">Auto Attribution</div>
                      <div class="text-sm text-ink-gray-6">Attribute leads to campaigns via UTM params</div>
                    </div>
                    <Switch v-model="settings.enable_auto_attribution" />
                  </div>
                  <div class="flex items-center justify-between">
                    <div>
                      <div class="font-medium text-ink-gray-9">UTM Tracking</div>
                      <div class="text-sm text-ink-gray-6">Track UTM parameters on leads</div>
                    </div>
                    <Switch v-model="settings.enable_utm_tracking" />
                  </div>
                </div>
                <div class="space-y-4">
                  <FormControl
                    v-model="settings.attribution_window"
                    label="Attribution Window (Days)"
                    type="number"
                    placeholder="30"
                  />
                  <FormControl
                    v-model="settings.session_timeout_days"
                    label="Session Timeout (Days)"
                    type="number"
                    placeholder="30"
                  />
                </div>
              </div>
            </div>
          </template>

          <!-- Channels Tab -->
          <template v-if="activeTab === 'channels'">
            <div class="rounded-lg border border-outline-gray-2 bg-surface-cards p-6">
              <h2 class="mb-4 text-lg font-semibold text-ink-gray-9">Marketing Channels</h2>
              <div class="space-y-4">
                <div class="flex items-center justify-between">
                  <div>
                    <div class="font-medium text-ink-gray-9">Email Blasts</div>
                    <div class="text-sm text-ink-gray-6">Enable sending mass email campaigns</div>
                  </div>
                  <Switch v-model="settings.enable_email_blast" />
                </div>
                <div class="flex items-center justify-between">
                  <div>
                    <div class="font-medium text-ink-gray-9">SMS Blasts</div>
                    <div class="text-sm text-ink-gray-6">Enable sending SMS campaigns</div>
                  </div>
                  <Switch v-model="settings.enable_sms_blast" />
                </div>
                <div class="flex items-center justify-between">
                  <div>
                    <div class="font-medium text-ink-gray-9">WhatsApp Blasts</div>
                    <div class="text-sm text-ink-gray-6">Enable WhatsApp Business API campaigns</div>
                  </div>
                  <Switch v-model="settings.enable_whatsapp_blast" />
                </div>
              </div>
            </div>

            <div class="rounded-lg border border-outline-gray-2 bg-surface-cards p-6">
              <h2 class="mb-4 text-lg font-semibold text-ink-gray-9">Social Media</h2>
              <div class="space-y-4">
                <div class="flex items-center justify-between">
                  <div>
                    <div class="font-medium text-ink-gray-9">Auto Post</div>
                    <div class="text-sm text-ink-gray-6">Automatically publish scheduled social posts</div>
                  </div>
                  <Switch v-model="settings.enable_auto_post" />
                </div>
                <FormControl
                  v-model="settings.auto_post_interval_minutes"
                  label="Auto Post Check Interval (Minutes)"
                  type="number"
                  placeholder="15"
                />
                <div class="flex items-center justify-between">
                  <div>
                    <div class="font-medium text-ink-gray-9">Require Post Approval</div>
                    <div class="text-sm text-ink-gray-6">Posts must be approved before publishing</div>
                  </div>
                  <Switch v-model="settings.require_post_approval" />
                </div>
              </div>
            </div>
          </template>

          <!-- Analytics Tab -->
          <template v-if="activeTab === 'analytics'">
            <div class="rounded-lg border border-outline-gray-2 bg-surface-cards p-6">
              <h2 class="mb-4 text-lg font-semibold text-ink-gray-9">Analytics Sync</h2>
              <div class="space-y-4">
                <div class="flex items-center justify-between">
                  <div>
                    <div class="font-medium text-ink-gray-9">Enable Analytics Sync</div>
                    <div class="text-sm text-ink-gray-6">Periodically sync data from ad platforms</div>
                  </div>
                  <Switch v-model="settings.enable_analytics_sync" />
                </div>
                <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <FormControl
                    v-model="settings.sync_frequency"
                    label="Sync Frequency (Hours)"
                    type="number"
                    placeholder="24"
                  />
                  <div class="flex items-center justify-between">
                    <div>
                      <div class="font-medium text-ink-gray-9">Track Conversions</div>
                      <div class="text-sm text-ink-gray-6">Track campaign conversion events</div>
                    </div>
                    <Switch v-model="settings.track_conversions" />
                  </div>
                </div>
              </div>
            </div>

            <div class="rounded-lg border border-outline-gray-2 bg-surface-cards p-6">
              <h2 class="mb-4 text-lg font-semibold text-ink-gray-9">Google Ads Integration</h2>
              <div class="space-y-4">
                <FormControl
                  v-model="settings.google_ads_developer_token"
                  label="Developer Token"
                  type="password"
                  placeholder="Enter your Google Ads Developer Token"
                />
                <div class="rounded-md bg-surface-gray-2 p-3 text-sm text-ink-gray-6">
                  Configure OAuth credentials in the Ad Account doctype for each account.
                </div>
              </div>
            </div>
          </template>

          <!-- Content Tab -->
          <template v-if="activeTab === 'content'">
            <div class="rounded-lg border border-outline-gray-2 bg-surface-cards p-6">
              <h2 class="mb-4 text-lg font-semibold text-ink-gray-9">Content Library</h2>
              <div class="space-y-4">
                <div class="flex items-center justify-between">
                  <div>
                    <div class="font-medium text-ink-gray-9">Enable Content Library</div>
                    <div class="text-sm text-ink-gray-6">Centralized asset library for marketing content</div>
                  </div>
                  <Switch v-model="settings.enable_content_library" />
                </div>
                <div class="flex items-center justify-between">
                  <div>
                    <div class="font-medium text-ink-gray-9">Version Control</div>
                    <div class="text-sm text-ink-gray-6">Track content revisions and versions</div>
                  </div>
                  <Switch v-model="settings.enable_version_control" />
                </div>
                <div class="flex items-center justify-between">
                  <div>
                    <div class="font-medium text-ink-gray-9">Brand Guidelines</div>
                    <div class="text-sm text-ink-gray-6">Enforce brand guidelines for content</div>
                  </div>
                  <Switch v-model="settings.enable_brand_guidelines" />
                </div>
              </div>
            </div>
          </template>

          <!-- Notifications Tab -->
          <template v-if="activeTab === 'notifications'">
            <div class="rounded-lg border border-outline-gray-2 bg-surface-cards p-6">
              <h2 class="mb-4 text-lg font-semibold text-ink-gray-9">Notifications</h2>
              <div class="space-y-4">
                <div class="flex items-center justify-between">
                  <div>
                    <div class="font-medium text-ink-gray-9">Campaign Completion</div>
                    <div class="text-sm text-ink-gray-6">Notify when a campaign is completed</div>
                  </div>
                  <Switch v-model="settings.notify_campaign_completion" />
                </div>
                <div class="flex items-center justify-between">
                  <div>
                    <div class="font-medium text-ink-gray-9">Blast Execution</div>
                    <div class="text-sm text-ink-gray-6">Notify when an omni blast is executed</div>
                  </div>
                  <Switch v-model="settings.notify_blast_execution" />
                </div>
                <div class="flex items-center justify-between">
                  <div>
                    <div class="font-medium text-ink-gray-9">Analytics Sync</div>
                    <div class="text-sm text-ink-gray-6">Notify after analytics sync completes</div>
                  </div>
                  <Switch v-model="settings.notify_analytics_sync" />
                </div>
                <FormControl
                  v-model="settings.notification_recipients"
                  label="Notification Recipients"
                  type="text"
                  placeholder="Comma-separated email addresses"
                />
              </div>
            </div>
          </template>

          <!-- Actions already in header -->
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Breadcrumbs, Button, FormControl, Switch, toast } from 'frappe-ui'
import LayoutHeader from '@/components/LayoutHeader.vue'

import IconExternalLink from '~icons/lucide/external-link'

const saving = ref(false)
const activeTab = ref('general')
const companies = ref([])

const tabs = [
  { key: 'general', label: 'General' },
  { key: 'channels', label: 'Channels' },
  { key: 'analytics', label: 'Analytics' },
  { key: 'content', label: 'Content' },
  { key: 'notifications', label: 'Notifications' },
]

const companyOptions = computed(() =>
  companies.value.map(c => ({ label: c.name, value: c.name }))
)

// All settings fields exposed in portal
const settingsFields = [
  'company', 'default_lead_source', 'enable_auto_attribution', 'enable_utm_tracking',
  'session_timeout_days', 'attribution_window',
  'enable_email_blast', 'enable_sms_blast', 'enable_whatsapp_blast',
  'enable_auto_post', 'auto_post_interval_minutes', 'require_post_approval',
  'enable_analytics_sync', 'sync_frequency', 'track_conversions', 'google_ads_developer_token',
  'enable_content_library', 'enable_version_control', 'enable_brand_guidelines',
  'notify_campaign_completion', 'notify_blast_execution', 'notify_analytics_sync', 'notification_recipients',
]

const checkFields = [
  'enable_auto_attribution', 'enable_utm_tracking',
  'enable_email_blast', 'enable_sms_blast', 'enable_whatsapp_blast',
  'enable_auto_post', 'require_post_approval',
  'enable_analytics_sync', 'track_conversions',
  'enable_content_library', 'enable_version_control', 'enable_brand_guidelines',
  'notify_campaign_completion', 'notify_blast_execution', 'notify_analytics_sync',
]

const settings = ref({
  company: '',
  default_lead_source: '',
  enable_auto_attribution: true,
  enable_utm_tracking: true,
  session_timeout_days: 30,
  attribution_window: 30,
  enable_email_blast: true,
  enable_sms_blast: false,
  enable_whatsapp_blast: false,
  enable_auto_post: true,
  auto_post_interval_minutes: 15,
  require_post_approval: false,
  enable_analytics_sync: true,
  sync_frequency: 24,
  track_conversions: true,
  google_ads_developer_token: '',
  enable_content_library: true,
  enable_version_control: true,
  enable_brand_guidelines: false,
  notify_campaign_completion: true,
  notify_blast_execution: true,
  notify_analytics_sync: false,
  notification_recipients: '',
})

onMounted(async () => {
  // Load settings
  try {
    const doc = await window.frappe.call({
      method: "frappe.client.get_value",
      args: {
        doctype: "Marketing Hub Settings",
        fieldname: settingsFields
      }
    })
    if (doc.message) {
      const vals = doc.message
      for (const key of checkFields) {
        vals[key] = !!vals[key]
      }
      settings.value = { ...settings.value, ...vals }
    }
  } catch (error) {
    console.error("Error loading settings:", error)
  }

  // Load companies
  try {
    const res = await window.frappe.call({
      method: 'frappe.client.get_list',
      args: { doctype: 'Company', fields: ['name'], limit_page_length: 50 }
    })
    companies.value = res.message || []
  } catch (e) { /* ignore */ }
})

async function saveSettings() {
  saving.value = true
  try {
    const fieldname = {}
    for (const key of settingsFields) {
      if (checkFields.includes(key)) {
        fieldname[key] = settings.value[key] ? 1 : 0
      } else {
        fieldname[key] = settings.value[key]
      }
    }
    await window.frappe.call({
      method: "frappe.client.set_value",
      args: {
        doctype: "Marketing Hub Settings",
        name: "Marketing Hub Settings",
        fieldname
      }
    })
    toast({ title: "Success", text: "Settings saved successfully", icon: "check", iconClasses: "text-green-600" })
  } catch (error) {
    toast({ title: "Error", text: "Failed to save settings", icon: "x", iconClasses: "text-red-600" })
  } finally {
    saving.value = false
  }
}

function openFullSettings() {
  window.location.href = '/app/marketing-hub-settings'
}
</script>
