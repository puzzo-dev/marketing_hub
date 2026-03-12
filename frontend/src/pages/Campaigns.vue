<template>
  <div class="flex h-full flex-col overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="[{ label: 'Marketing Hub' }, { label: 'Campaigns' }]" />
      </template>
      <template #right-header>
        <Button @click="openCreateDialog" variant="solid" label="Create">
          <template #prefix>
            <IconPlus class="h-4 w-4" />
          </template>
        </Button>
      </template>
    </LayoutHeader>

    <!-- Filter Bar -->
    <div class="flex items-center gap-3 border-b px-5 py-3">
      <div class="relative flex-1 max-w-xs">
        <IconSearch class="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-gray-4" />
        <FormControl
          type="text"
          :modelValue="searchQuery"
          @update:modelValue="searchQuery = $event; debouncedSearch()"
          placeholder="Search campaigns..."
          class="pl-8"
        />
      </div>
      <div class="-ml-1 h-[70%] border-l border-outline-gray-2" />
      <div class="flex gap-1.5">
        <Button
          v-for="status in statusFilters"
          :key="status.value"
          @click="selectedStatus = status.value"
          :variant="selectedStatus === status.value ? 'subtle' : 'ghost'"
          size="sm"
          :label="status.label"
        />
      </div>
    </div>

    <!-- Content Area -->
    <div class="flex-1 overflow-auto p-5">
      <!-- Campaign Grid -->
      <div v-if="campaigns.length" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div v-for="campaign in campaigns" :key="campaign.name"
          class="cursor-pointer rounded-lg border border-outline-gray-1 bg-surface-white p-4 shadow-sm transition-shadow hover:shadow"
          @click="$router.push('/marketing/campaigns/' + campaign.name)"
        >
          <div class="mb-3 flex items-start justify-between">
            <h4 class="text-base font-medium text-ink-gray-9 line-clamp-1">{{ campaign.campaign_name }}</h4>
            <Badge :label="campaign.status || 'Draft'" variant="subtle"
              :theme="campaign.status === 'Active' ? 'green' : campaign.status === 'Completed' ? 'blue' : campaign.status === 'Cancelled' ? 'orange' : 'gray'"
            />
          </div>

          <p v-if="campaign.description" class="mb-3 text-sm text-ink-gray-6 line-clamp-2">{{ campaign.description }}</p>

          <!-- Client tag (agency mode) -->
          <div v-if="configStore.isAgencyMode && campaign.customer" class="mb-3 flex items-center gap-1.5">
            <span class="inline-flex items-center rounded bg-surface-purple-1 px-2 py-0.5 text-xs font-medium text-ink-purple-3">
              {{ campaign.customer }}
            </span>
            <span v-if="campaign.project" class="inline-flex items-center rounded bg-surface-gray-2 px-2 py-0.5 text-xs text-ink-gray-6">
              {{ campaign.project }}
            </span>
          </div>

          <!-- Budget Bar -->
          <div v-if="campaign.budget" class="mb-3">
            <div class="mb-1 flex items-center justify-between text-xs text-ink-gray-5">
              <span>Budget</span>
              <span>{{ formatCurrency(campaign.spend || 0) }} / {{ formatCurrency(campaign.budget) }}</span>
            </div>
            <div class="h-1.5 w-full rounded-full bg-surface-gray-2">
              <div class="h-1.5 rounded-full transition-all"
                :class="campaign.budget_utilization > 80 ? 'bg-ink-red-3' : campaign.budget_utilization > 60 ? 'bg-ink-orange-3' : 'bg-ink-green-3'"
                :style="{ width: Math.min(campaign.budget_utilization || 0, 100) + '%' }"
              ></div>
            </div>
          </div>

          <div class="grid grid-cols-3 gap-2 text-sm">
            <div>
              <div class="text-xs text-ink-gray-5">Leads</div>
              <div class="font-medium text-ink-gray-9">{{ campaign.leads_count || 0 }}</div>
            </div>
            <div>
              <div class="text-xs text-ink-gray-5">Spend</div>
              <div class="font-medium text-ink-gray-9">{{ formatCurrency(campaign.spend) }}</div>
            </div>
            <div>
              <div class="text-xs text-ink-gray-5">ROAS</div>
              <div class="font-medium"
                :class="(campaign.roas || 0) >= 3 ? 'text-ink-green-3' : (campaign.roas || 0) >= 1 ? 'text-ink-orange-3' : 'text-ink-gray-9'"
              >
                {{ (campaign.roas || 0).toFixed(1) }}x
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Load More -->
      <div v-if="hasMore" class="mt-6 text-center">
        <Button @click="loadMore" :loading="campaignsResource.loading" variant="subtle" label="Load More" />
      </div>

      <!-- Empty State -->
      <div v-if="!campaigns.length && !campaignsResource.loading" class="relative flex h-full w-full justify-center">
        <div class="absolute left-1/2 flex w-4/12 -translate-x-1/2 flex-col items-center gap-3" style="top: 35%">
          <IconTarget class="h-7 w-7 text-ink-gray-5" />
          <span class="text-base font-medium text-ink-gray-8">
            {{ searchQuery || selectedStatus ? 'No campaigns match your filters' : 'No campaigns yet' }}
          </span>
          <span class="text-center text-sm text-ink-gray-6">
            {{ searchQuery || selectedStatus ? 'Try adjusting your search or filters' : 'Create your first marketing campaign to get started.' }}
          </span>
          <Button v-if="!searchQuery && !selectedStatus" @click="openCreateDialog" variant="solid" label="Create Campaign">
            <template #prefix>
              <IconPlus class="h-4 w-4" />
            </template>
          </Button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="campaignsResource.loading && !campaigns.length" class="flex items-center justify-center py-20">
        <LoadingIndicator class="h-6 w-6" />
      </div>
    </div>

    <!-- Create Campaign Dialog -->
    <Dialog
      v-model="showCreateDialog"
      :options="{ title: 'Create Campaign', size: '3xl' }"
      :disableOutsideClickToClose="true"
    >
      <template #body-content>
        <div class="space-y-5">
          <!-- Basic Info -->
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
              <label class="mb-1.5 block text-sm font-medium text-ink-gray-9">Description</label>
              <textarea
                v-model="form.description"
                rows="3"
                class="w-full rounded-md border border-outline-gray-2 p-3 text-sm focus:border-outline-gray-4 focus:outline-none focus:ring-1 focus:ring-outline-gray-4"
                placeholder="Describe your campaign objectives..."
              ></textarea>
            </div>
          </div>

          <!-- Schedule & Budget -->
          <div>
            <h3 class="mb-3 text-sm font-medium text-ink-gray-5">Schedule & Budget</h3>
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <FormControl v-model="form.start_date" label="Start Date" type="date" />
              <FormControl v-model="form.end_date" label="End Date" type="date" />
              <FormControl v-model="form.budget" label="Budget" type="number" placeholder="0.00" />
            </div>
          </div>

          <!-- Channels -->
          <div>
            <div class="mb-3 flex items-center justify-between">
              <h3 class="text-sm font-medium text-ink-gray-5">Channels</h3>
              <div class="flex items-center gap-2">
                <span class="text-sm text-ink-gray-7">Omni Campaign</span>
                <Switch v-model="form.is_omni_campaign" />
              </div>
            </div>
            <div v-if="form.is_omni_campaign && networks.length" class="grid grid-cols-2 gap-2 sm:grid-cols-3">
              <label
                v-for="net in networks" :key="net.name"
                class="flex cursor-pointer items-center gap-2 rounded-md border border-outline-gray-1 p-2.5 transition-colors hover:bg-surface-gray-1"
                :class="{'border-blue-400 bg-blue-50': selectedChannels.includes(net.name)}"
              >
                <input type="checkbox" :value="net.name" v-model="selectedChannels" class="h-4 w-4 rounded border-outline-gray-3" />
                <span class="text-sm text-ink-gray-9">{{ net.network_name || net.name }}</span>
              </label>
            </div>
          </div>

          <!-- CRM Link -->
          <FormControl
            v-model="form.email_campaign"
            label="Linked Email Campaign (CRM)"
            type="autocomplete"
            :options="crmCampaignOptions"
            placeholder="Link to ERPNext CRM Campaign"
          />

          <!-- Agency: Client & Project -->
          <div v-if="configStore.isAgencyMode">
            <h3 class="mb-3 flex items-center gap-1.5 text-sm font-medium text-ink-purple-3">
              <IconBuilding class="h-3.5 w-3.5" /> Client & Project
            </h3>
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <FormControl
                v-model="form.customer"
                label="Client"
                type="autocomplete"
                :options="customerOptions"
                placeholder="Select client"
              />
              <FormControl
                v-model="form.project"
                label="Project"
                type="autocomplete"
                :options="projectOptions"
                placeholder="Link to ERPNext Project"
              />
            </div>
          </div>
        </div>
      </template>
      <template #actions="{ close }">
        <div class="flex w-full justify-end gap-2">
          <Button variant="ghost" @click="close">Cancel</Button>
          <Button variant="solid" :loading="saving" @click="createCampaign">Create Campaign</Button>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { Breadcrumbs, FormControl, LoadingIndicator, createResource, Dialog, Button, Switch, call } from "frappe-ui";
import { toast } from '@/utils/toast'
import { computed, ref, watch, onMounted } from "vue";
import { useRouter } from "vue-router";
import LayoutHeader from "@/components/LayoutHeader.vue";
import { useConfigStore } from "@/stores/config";

import IconPlus from '~icons/lucide/plus'
import IconSearch from '~icons/lucide/search'
import IconTarget from '~icons/lucide/target'
import IconBuilding from '~icons/lucide/building'

const router = useRouter()
const configStore = useConfigStore()

const searchQuery = ref("");
const selectedStatus = ref("");
const currentOffset = ref(0);
const pageSize = 20;

// Create dialog state
const showCreateDialog = ref(false)
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
  customer: '',
  project: '',
})
const selectedChannels = ref([])
const networks = ref([])
const companies = ref([])
const crmCampaigns = ref([])
const customers = ref([])
const projects = ref([])

const companyOptions = computed(() => companies.value.map(c => ({ label: c.name, value: c.name })))
const crmCampaignOptions = computed(() => crmCampaigns.value.map(c => ({ label: c.name, value: c.name })))
const customerOptions = computed(() => customers.value.map(c => ({ label: c.customer_name, value: c.name })))
const projectOptions = computed(() => projects.value.map(p => ({ label: p.project_name, value: p.name })))

watch(() => form.value.customer, (newVal) => {
  if (configStore.isAgencyMode) loadProjects(newVal)
})

async function loadProjects(customer) {
  try {
    const data = await call('marketing_hub.api.agency.get_project_options', {
      customer: customer || undefined
    })
    projects.value = data || []
  } catch (e) { /* ignore */ }
}

async function openCreateDialog() {
  showCreateDialog.value = true
  // Reset form
  form.value = {
    campaign_name: '', company: '', status: 'Draft', description: '',
    start_date: '', end_date: '', budget: 0, is_omni_campaign: true,
    email_campaign: '', customer: '', project: '',
  }
  selectedChannels.value = []

  // Load form data
  try {
    const [netData, compData, crmData] = await Promise.all([
      call('frappe.client.get_list', { doctype: 'Social Media Network', filters: { is_active: 1 }, fields: ['name', 'network_name'], limit_page_length: 50 }),
      call('frappe.client.get_list', { doctype: 'Company', fields: ['name'], limit_page_length: 50 }),
      call('frappe.client.get_list', { doctype: 'Campaign', fields: ['name'], limit_page_length: 100 }),
    ])
    networks.value = netData || []
    companies.value = compData || []
    if (companies.value.length === 1) form.value.company = companies.value[0].name
    crmCampaigns.value = crmData || []
  } catch (e) { /* ignore */ }

  if (configStore.isAgencyMode) {
    try {
      const data = await call('marketing_hub.api.agency.get_customer_options', {})
      customers.value = data || []
    } catch (e) { /* ignore */ }
    loadProjects(form.value.customer)
  }
}

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
      customer: form.value.customer || undefined,
      project: form.value.project || undefined,
    }
    if (form.value.is_omni_campaign && selectedChannels.value.length) {
      doc.channels = selectedChannels.value.map(ch => ({ doctype: 'Marketing Campaign Channel', channel: ch }))
    }
    const newDoc = await call('frappe.client.insert', { doc })
    toast({ title: 'Success', text: 'Campaign created successfully', icon: 'check', iconClasses: 'text-ink-green-3' })
    showCreateDialog.value = false
    router.push(`/marketing/campaigns/${newDoc.name}`)
  } catch (error) {
    toast({ title: 'Error', text: error.message || 'Failed to create campaign', icon: 'x', iconClasses: 'text-ink-red-3' })
  } finally {
    saving.value = false
  }
}

const statusFilters = [
  { label: "All", value: "" },
  { label: "Active", value: "Active" },
  { label: "Draft", value: "Draft" },
  { label: "Completed", value: "Completed" },
  { label: "Cancelled", value: "Cancelled" },
];

const campaignsResource = createResource({
  url: "marketing_hub.api.campaigns.get_campaign_list",
  params: {
    filters: {},
    limit: pageSize,
    offset: 0,
  },
  auto: true,
});

const campaigns = computed(() => campaignsResource.data?.campaigns || []);
const hasMore = computed(() => campaignsResource.data?.has_more || false);

let searchTimeout = null;
function debouncedSearch() {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    fetchCampaigns();
  }, 300);
}

function fetchCampaigns() {
  currentOffset.value = 0;
  const filters = {};
  if (searchQuery.value) filters.campaign_name = searchQuery.value;
  if (selectedStatus.value) filters.status = selectedStatus.value;

  campaignsResource.fetch({
    filters: JSON.stringify(filters),
    limit: pageSize,
    offset: 0,
  });
}

function loadMore() {
  currentOffset.value += pageSize;
  const filters = {};
  if (searchQuery.value) filters.campaign_name = searchQuery.value;
  if (selectedStatus.value) filters.status = selectedStatus.value;

  campaignsResource.fetch({
    filters: JSON.stringify(filters),
    limit: pageSize,
    offset: currentOffset.value,
  });
}

// Watch status filter changes
watch(selectedStatus, () => {
  fetchCampaigns();
});

function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value || 0);
}
</script>
