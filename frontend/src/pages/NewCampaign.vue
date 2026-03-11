<template>
  <div class="flex h-full flex-col overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="[
          { label: 'Campaigns', route: { path: '/marketing/campaigns' } },
          { label: 'New Campaign' }
        ]" />
      </template>
      <template #right-header>
        <Button variant="ghost" @click="$router.push('/marketing/campaigns')">Cancel</Button>
        <Button variant="solid" :loading="saving" @click="createCampaign">Create Campaign</Button>
      </template>
    </LayoutHeader>

    <div class="flex-1 overflow-auto">
      <div class="mx-auto max-w-3xl px-5 py-6">

        <div class="space-y-6">
          <!-- Basic Info -->
          <div class="rounded-lg border border-outline-gray-1 bg-surface-cards p-6 shadow-sm">
            <h2 class="mb-4 text-base font-medium text-ink-gray-9">Campaign Details</h2>
            <div class="space-y-4">
              <FormControl
                v-model="form.campaign_name"
                label="Campaign Name"
                type="text"
                placeholder="e.g. Summer Sale 2025"
                :required="true"
              />
              <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <FormControl
                  v-model="form.company"
                  label="Company"
                  type="autocomplete"
                  :options="companyOptions"
                  placeholder="Select company"
                  :required="true"
                />
                <FormControl
                  v-model="form.status"
                  label="Status"
                  type="select"
                  :options="[
                    { label: 'Draft', value: 'Draft' },
                    { label: 'Active', value: 'Active' },
                  ]"
                />
              </div>
              <div>
                <label class="mb-2 block text-sm font-medium text-ink-gray-9">Description</label>
                <textarea
                  v-model="form.description"
                  rows="4"
                  class="w-full rounded-md border border-outline-gray-2 p-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  placeholder="Describe your campaign objectives..."
                ></textarea>
              </div>
            </div>
          </div>

          <!-- Schedule & Budget -->
          <div class="rounded-lg border border-outline-gray-1 bg-surface-cards p-6 shadow-sm">
            <h2 class="mb-4 text-base font-medium text-ink-gray-9">Schedule & Budget</h2>
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <FormControl
                v-model="form.start_date"
                label="Start Date"
                type="date"
              />
              <FormControl
                v-model="form.end_date"
                label="End Date"
                type="date"
              />
              <FormControl
                v-model="form.budget"
                label="Budget"
                type="number"
                placeholder="0.00"
              />
            </div>
          </div>

          <!-- Channel Settings -->
          <div class="rounded-lg border border-outline-gray-1 bg-surface-cards p-6 shadow-sm">
            <h2 class="mb-4 text-base font-medium text-ink-gray-9">Channels</h2>
            <div class="mb-4 flex items-center justify-between">
              <div>
                <div class="font-medium text-ink-gray-9">Omni Campaign</div>
                <div class="text-sm text-ink-gray-6">Publish across multiple channels simultaneously</div>
              </div>
              <Switch v-model="form.is_omni_campaign" />
            </div>
            <div v-if="form.is_omni_campaign && networks.length" class="space-y-2">
              <label class="block text-sm font-medium text-ink-gray-9">Select Channels</label>
              <div class="grid grid-cols-2 gap-2 sm:grid-cols-3">
                <label
                  v-for="net in networks"
                  :key="net.name"
                  class="flex cursor-pointer items-center gap-2 rounded-md border border-outline-gray-1 p-3 transition-colors hover:bg-surface-gray-1"
                  :class="{'border-blue-400 bg-blue-50': selectedChannels.includes(net.name)}"
                >
                  <input
                    type="checkbox"
                    :value="net.name"
                    v-model="selectedChannels"
                    class="h-4 w-4 rounded border-outline-gray-3"
                  />
                  <span class="text-sm text-ink-gray-9">{{ net.network_name || net.name }}</span>
                </label>
              </div>
            </div>
          </div>

          <!-- CRM Link -->
          <div class="rounded-lg border border-outline-gray-1 bg-surface-cards p-6 shadow-sm">
            <h2 class="mb-4 text-base font-medium text-ink-gray-9">CRM Integration</h2>
            <FormControl
              v-model="form.email_campaign"
              label="Linked Email Campaign (CRM)"
              type="autocomplete"
              :options="crmCampaignOptions"
              placeholder="Link to ERPNext CRM Campaign for email blasts"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Breadcrumbs, Button, FormControl, Switch, createResource, toast } from 'frappe-ui'
import LayoutHeader from '@/components/LayoutHeader.vue'

const router = useRouter()
const saving = ref(false)

const form = ref({
  campaign_name: '',
  company: '',
  status: 'Draft',
  description: '',
  start_date: '',
  end_date: '',
  budget: 0,
  is_omni_campaign: true,
  email_campaign: '',
})

const selectedChannels = ref([])
const networks = ref([])
const companies = ref([])
const crmCampaigns = ref([])

const companyOptions = computed(() =>
  companies.value.map(c => ({ label: c.name, value: c.name }))
)
const crmCampaignOptions = computed(() =>
  crmCampaigns.value.map(c => ({ label: c.name, value: c.name }))
)

onMounted(async () => {
  // Load networks
  try {
    const res = await window.frappe.call({
      method: 'frappe.client.get_list',
      args: { doctype: 'Social Media Network', filters: { is_active: 1 }, fields: ['name', 'network_name'], limit_page_length: 50 }
    })
    networks.value = res.message || []
  } catch (e) { /* ignore */ }

  // Load companies
  try {
    const res = await window.frappe.call({
      method: 'frappe.client.get_list',
      args: { doctype: 'Company', fields: ['name'], limit_page_length: 50 }
    })
    companies.value = res.message || []
    if (companies.value.length === 1) {
      form.value.company = companies.value[0].name
    }
  } catch (e) { /* ignore */ }

  // Load CRM campaigns
  try {
    const res = await window.frappe.call({
      method: 'frappe.client.get_list',
      args: { doctype: 'Campaign', fields: ['name'], limit_page_length: 100 }
    })
    crmCampaigns.value = res.message || []
  } catch (e) { /* ignore */ }
})

async function createCampaign() {
  if (!form.value.campaign_name) {
    toast({ title: 'Error', text: 'Campaign name is required', icon: 'x', iconClasses: 'text-ink-red-3' })
    return
  }
  if (!form.value.company) {
    toast({ title: 'Error', text: 'Company is required', icon: 'x', iconClasses: 'text-ink-red-3' })
    return
  }

  saving.value = true
  try {
    const doc = {
      doctype: 'Marketing Campaign',
      campaign_name: form.value.campaign_name,
      company: form.value.company,
      status: form.value.status,
      description: form.value.description,
      start_date: form.value.start_date || undefined,
      end_date: form.value.end_date || undefined,
      budget: form.value.budget || 0,
      is_omni_campaign: form.value.is_omni_campaign ? 1 : 0,
      email_campaign: form.value.email_campaign || undefined,
    }

    // Add channels as child table rows
    if (form.value.is_omni_campaign && selectedChannels.value.length) {
      doc.channels = selectedChannels.value.map(ch => ({
        doctype: 'Marketing Campaign Channel',
        channel: ch
      }))
    }

    const res = await window.frappe.call({
      method: 'frappe.client.insert',
      args: { doc }
    })

    toast({ title: 'Success', text: 'Campaign created successfully', icon: 'check', iconClasses: 'text-ink-green-3' })
    router.push(`/marketing/campaigns/${res.message.name}`)
  } catch (error) {
    toast({ title: 'Error', text: error.message || 'Failed to create campaign', icon: 'x', iconClasses: 'text-ink-red-3' })
  } finally {
    saving.value = false
  }
}
</script>
