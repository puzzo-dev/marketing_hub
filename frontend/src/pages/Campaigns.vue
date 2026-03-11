<template>
  <div class="flex h-full flex-col overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="[{ label: 'Marketing Hub' }, { label: 'Campaigns' }]" />
      </template>
      <template #right-header>
        <Button @click="$router.push('/marketing/campaigns/new')" variant="solid" label="Create">
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
          <Button v-if="!searchQuery && !selectedStatus" @click="$router.push('/marketing/campaigns/new')" variant="solid" label="Create Campaign">
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
  </div>
</template>

<script setup>
import { Breadcrumbs, FormControl, LoadingIndicator, createResource } from "frappe-ui";
import { computed, ref, watch } from "vue";
import LayoutHeader from "@/components/LayoutHeader.vue";

import IconPlus from '~icons/lucide/plus'
import IconSearch from '~icons/lucide/search'
import IconTarget from '~icons/lucide/target'

const searchQuery = ref("");
const selectedStatus = ref("");
const currentOffset = ref(0);
const pageSize = 20;

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
