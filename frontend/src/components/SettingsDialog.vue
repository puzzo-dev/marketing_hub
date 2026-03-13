<template>
  <Dialog v-model="show" :options="{ size: '4xl' }">
    <template #body>
      <div class="flex h-[calc(100vh_-_8rem)]">
        <!-- Left sidebar with tabs -->
        <div class="flex flex-col p-1 w-48 shrink-0 bg-surface-menu-bar overflow-y-auto border-r border-outline-gray-1">
          <template v-for="(section, i) in sections" :key="section.label">
            <div v-if="i !== 0" class="border-t mx-1 mb-2 mt-[11px]" />
            <div class="h-7.5 px-2 py-[7px] my-[3px]">
              <span class="text-xs font-medium uppercase text-ink-gray-5">{{ section.label }}</span>
            </div>
            <nav class="space-y-[3px] px-1">
              <button
                v-for="item in section.items"
                :key="item.key"
                class="flex w-full items-center gap-2 rounded px-2 py-1.5 text-sm"
                :class="
                  activeTab === item.key
                    ? 'bg-surface-selected text-ink-gray-9 font-medium'
                    : 'text-ink-gray-7 hover:bg-surface-gray-3'
                "
                @click="activeTab = item.key"
              >
                <component :is="item.icon" class="h-4 w-4" />
                <span>{{ item.label }}</span>
              </button>
            </nav>
          </template>
        </div>

        <!-- Right content area -->
        <div class="flex flex-1 flex-col overflow-y-auto bg-surface-modal p-6">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-lg font-semibold text-ink-gray-9">{{ activeSection?.label }}</h2>
            <Button variant="subtle" size="sm" @click="openFullSettings">
              Open in Desk
            </Button>
          </div>

          <!-- General -->
          <div v-if="activeTab === 'general'" class="space-y-6">
            <SettingsCard title="Company & Defaults">
              <div class="grid grid-cols-2 gap-4">
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
                  placeholder="e.g. Website"
                />
              </div>
            </SettingsCard>
            <SettingsCard title="Attribution">
              <div class="space-y-3">
                <SettingsToggle
                  v-model="settings.enable_auto_attribution"
                  label="Auto Attribution"
                  description="Attribute leads to campaigns via UTM params"
                />
                <SettingsToggle
                  v-model="settings.enable_utm_tracking"
                  label="UTM Tracking"
                  description="Track UTM parameters on leads"
                />
              </div>
            </SettingsCard>
            <SettingsCard title="Branding">
              <div class="space-y-4">
                <FormControl
                  v-model="settings.brand_name"
                  label="Brand Name"
                  type="text"
                  placeholder="Marketing Hub"
                />
                <div>
                  <label class="mb-1.5 block text-sm font-medium text-ink-gray-8">Brand Logo</label>
                  <p class="mb-2 text-xs text-ink-gray-5">Custom logo for the portal sidebar. Leave empty to use default.</p>
                  <div class="flex items-center gap-4">
                    <img v-if="settings.brand_logo" :src="settings.brand_logo" class="h-10 w-10 rounded object-cover" />
                    <FormControl
                      v-model="settings.brand_logo"
                      type="text"
                      placeholder="/assets/marketing_hub/images/logo.svg"
                    />
                  </div>
                </div>
              </div>
            </SettingsCard>
          </div>

          <!-- Channels -->
          <div v-if="activeTab === 'channels'" class="space-y-6">
            <SettingsCard title="Marketing Channels">
              <div class="space-y-3">
                <SettingsToggle v-model="settings.enable_email_blast" label="Email Blasts" description="Enable sending mass email campaigns" />
                <SettingsToggle v-model="settings.enable_sms_blast" label="SMS Blasts" description="Enable sending SMS campaigns" />
                <SettingsToggle v-model="settings.enable_whatsapp_blast" label="WhatsApp Blasts" description="Enable WhatsApp Business API campaigns" />
              </div>
            </SettingsCard>
            <SettingsCard title="Social Media">
              <div class="space-y-3">
                <SettingsToggle v-model="settings.enable_auto_post" label="Auto Post" description="Automatically publish scheduled social posts" />
                <SettingsToggle v-model="settings.require_post_approval" label="Require Post Approval" description="Posts must be approved before publishing" />
              </div>
            </SettingsCard>
          </div>

          <!-- Analytics -->
          <div v-if="activeTab === 'analytics'" class="space-y-6">
            <SettingsCard title="Analytics Sync">
              <div class="space-y-3">
                <SettingsToggle v-model="settings.enable_analytics_sync" label="Enable Analytics Sync" description="Periodically sync data from ad platforms" />
                <FormControl
                  v-model="settings.sync_frequency"
                  label="Sync Frequency (Hours)"
                  type="number"
                  placeholder="24"
                />
              </div>
            </SettingsCard>
          </div>

          <!-- Content -->
          <div v-if="activeTab === 'content'" class="space-y-6">
            <SettingsCard title="Content Library">
              <div class="space-y-3">
                <SettingsToggle v-model="settings.enable_content_library" label="Content Library" description="Centralized asset library for marketing content" />
                <SettingsToggle v-model="settings.enable_version_control" label="Version Control" description="Track content revisions and versions" />
                <SettingsToggle v-model="settings.enable_brand_guidelines" label="Brand Guidelines" description="Enforce brand guidelines for content" />
              </div>
            </SettingsCard>
          </div>

          <!-- Notifications -->
          <div v-if="activeTab === 'notifications'" class="space-y-6">
            <SettingsCard title="Notification Preferences">
              <div class="space-y-3">
                <SettingsToggle v-model="settings.notify_campaign_completion" label="Campaign Completion" description="Notify when a campaign is completed" />
                <SettingsToggle v-model="settings.notify_blast_execution" label="Blast Execution" description="Notify when an omni blast is executed" />
                <SettingsToggle v-model="settings.notify_analytics_sync" label="Analytics Sync" description="Notify after analytics sync completes" />
              </div>
            </SettingsCard>
          </div>

          <!-- Save button -->
          <div class="mt-6 flex justify-end">
            <Button variant="solid" :loading="saving" @click="saveSettings">
              Save Changes
            </Button>
          </div>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch, h } from 'vue'
import { Dialog, Button, FormControl, Switch, call } from 'frappe-ui'
import { toast } from '@/utils/toast'
import IconSettings from '~icons/lucide/settings'
import IconMegaphone from '~icons/lucide/megaphone'
import IconBarChart from '~icons/lucide/bar-chart-2'
import IconFileText from '~icons/lucide/file-text'
import IconBell from '~icons/lucide/bell'

const show = defineModel({ type: Boolean, default: false })

const activeTab = ref('general')
const saving = ref(false)
const companies = ref([])

const sections = [
  {
    label: 'Configuration',
    items: [
      { key: 'general', label: 'General', icon: IconSettings },
      { key: 'channels', label: 'Channels', icon: IconMegaphone },
      { key: 'analytics', label: 'Analytics', icon: IconBarChart },
      { key: 'content', label: 'Content', icon: IconFileText },
      { key: 'notifications', label: 'Notifications', icon: IconBell },
    ],
  },
]

const activeSection = computed(() => {
  for (const section of sections) {
    const item = section.items.find((i) => i.key === activeTab.value)
    if (item) return item
  }
  return null
})

const companyOptions = computed(() =>
  companies.value.map((c) => ({ label: c.name, value: c.name }))
)

const settingsFields = [
  'company', 'default_lead_source', 'brand_name', 'brand_logo',
  'enable_auto_attribution', 'enable_utm_tracking',
  'enable_email_blast', 'enable_sms_blast', 'enable_whatsapp_blast',
  'enable_auto_post', 'require_post_approval',
  'enable_analytics_sync', 'sync_frequency',
  'enable_content_library', 'enable_version_control', 'enable_brand_guidelines',
  'notify_campaign_completion', 'notify_blast_execution', 'notify_analytics_sync',
]

const checkFields = [
  'enable_auto_attribution', 'enable_utm_tracking',
  'enable_email_blast', 'enable_sms_blast', 'enable_whatsapp_blast',
  'enable_auto_post', 'require_post_approval',
  'enable_analytics_sync',
  'enable_content_library', 'enable_version_control', 'enable_brand_guidelines',
  'notify_campaign_completion', 'notify_blast_execution', 'notify_analytics_sync',
]

const settings = ref({
  company: '',
  default_lead_source: '',
  brand_name: '',
  brand_logo: '',
  enable_auto_attribution: true,
  enable_utm_tracking: true,
  enable_email_blast: true,
  enable_sms_blast: false,
  enable_whatsapp_blast: false,
  enable_auto_post: true,
  require_post_approval: false,
  enable_analytics_sync: true,
  sync_frequency: 24,
  enable_content_library: true,
  enable_version_control: true,
  enable_brand_guidelines: false,
  notify_campaign_completion: true,
  notify_blast_execution: true,
  notify_analytics_sync: false,
})

watch(show, async (val) => {
  if (val) {
    await loadSettings()
    await loadCompanies()
  }
})

async function loadSettings() {
  try {
    const vals = await call('frappe.client.get_value', {
      doctype: 'Marketing Hub Settings', fieldname: settingsFields,
    })
    if (vals) {
      for (const key of checkFields) vals[key] = Number(vals[key]) === 1
      settings.value = { ...settings.value, ...vals }
    }
  } catch (e) {
    console.error('Error loading settings:', e)
  }
}

async function loadCompanies() {
  try {
    const data = await call('frappe.client.get_list', {
      doctype: 'Company', fields: ['name'], limit_page_length: 50,
    })
    companies.value = data || []
  } catch (e) { /* ignore */ }
}

async function saveSettings() {
  saving.value = true
  try {
    const fieldname = {}
    for (const key of settingsFields) {
      fieldname[key] = checkFields.includes(key)
        ? settings.value[key] ? 1 : 0
        : settings.value[key]
    }
    await call('frappe.client.set_value', {
      doctype: 'Marketing Hub Settings', name: 'Marketing Hub Settings', fieldname,
    })
    toast({ title: 'Settings saved', icon: 'check', iconClasses: 'text-green-600' })
  } catch (e) {
    toast({ title: 'Failed to save settings', icon: 'x', iconClasses: 'text-red-600' })
  } finally {
    saving.value = false
  }
}

function openFullSettings() {
  window.location.href = '/app/marketing-hub-settings'
}

// Sub-components
const SettingsCard = {
  props: { title: String },
  setup(props, { slots }) {
    return () =>
      h('div', { class: 'rounded-lg border border-outline-gray-2 bg-surface-white p-5' }, [
        h('h3', { class: 'mb-4 text-sm font-semibold text-ink-gray-9' }, props.title),
        slots.default?.(),
      ])
  },
}

const SettingsToggle = {
  props: { modelValue: Boolean, label: String, description: String },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    return () =>
      h('div', { class: 'flex items-center justify-between py-1' }, [
        h('div', {}, [
          h('div', { class: 'text-sm font-medium text-ink-gray-9' }, props.label),
          h('div', { class: 'text-xs text-ink-gray-5' }, props.description),
        ]),
        h(Switch, {
          modelValue: props.modelValue,
          'onUpdate:modelValue': (v) => emit('update:modelValue', v),
        }),
      ])
  },
}
</script>
