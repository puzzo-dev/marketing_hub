<template>
  <div class="flex h-full flex-col overflow-auto bg-surface-gray-1">
    <div class="flex-1 px-5 py-5 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-5 flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-semibold text-ink-gray-9">Campaigns</h1>
          <p class="mt-1 text-sm text-ink-gray-6">Manage your marketing initiatives</p>
        </div>
        <Button @click="$router.push('/marketing/campaigns/new')" variant="solid">
          <template #prefix>
            <FeatherIcon name="plus" class="h-4 w-4" />
          </template>
          New Campaign
        </Button>
      </div>

      <!-- Search + Filter Bar -->
      <div class="mb-5 flex flex-wrap items-center gap-3">
        <div class="relative flex-1 min-w-[200px] max-w-md">
          <FeatherIcon name="search" class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-gray-4" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search campaigns..."
            class="w-full rounded-lg border border-outline-gray-2 bg-surface-cards py-2 pl-9 pr-4 text-sm text-ink-gray-9 placeholder-ink-gray-4 focus:border-ink-blue-3 focus:outline-none focus:ring-1 focus:ring-ink-blue-3"
            @input="debouncedSearch"
          />
        </div>
        <div class="flex gap-2">
          <button
            v-for="status in statusFilters"
            :key="status.value"
            @click="selectedStatus = status.value"
            class="rounded-lg px-3 py-2 text-sm font-medium transition-colors"
            :class="selectedStatus === status.value
              ? 'bg-ink-gray-9 text-white'
              : 'bg-surface-cards border border-outline-gray-2 text-ink-gray-6 hover:bg-surface-gray-2'"
          >
            {{ status.label }}
          </button>
        </div>
      </div>

      <!-- Campaign Grid -->
      <div v-if="campaigns.length" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div v-for="campaign in campaigns" :key="campaign.name"
          class="rounded-lg border border-outline-gray-1 bg-surface-cards p-5 shadow-sm transition-all hover:shadow-md cursor-pointer"
          @click="$router.push('/marketing/campaigns/' + campaign.name)"
        >
          <div class="mb-3 flex items-start justify-between">
            <h3 class="font-semibold text-ink-gray-9 line-clamp-1">{{ campaign.campaign_name }}</h3>
            <Badge :label="campaign.status || 'Draft'" variant="subtle"
              :theme="campaign.status === 'Active' ? 'green' : campaign.status === 'Completed' ? 'blue' : campaign.status === 'Cancelled' ? 'orange' : 'gray'"
            />
          </div>

          <p v-if="campaign.description" class="mb-3 text-sm text-ink-gray-6 line-clamp-2">{{ campaign.description }}</p>

          <!-- Budget Bar -->
          <div v-if="campaign.budget" class="mb-3">
            <div class="flex items-center justify-between text-xs text-ink-gray-5 mb-1">
              <span>Budget</span>
              <span>{{ formatCurrency(campaign.spend || 0) }} / {{ formatCurrency(campaign.budget) }}</span>
            </div>
            <div class="h-1.5 w-full rounded-full bg-surface-gray-2">
              <div class="h-1.5 rounded-full transition-all"
                :class="campaign.budget_utilization > 80 ? 'bg-red-500' : campaign.budget_utilization > 60 ? 'bg-orange-400' : 'bg-green-500'"
                :style="{ width: Math.min(campaign.budget_utilization || 0, 100) + '%' }"
              ></div>
            </div>
          </div>

          <div class="grid grid-cols-3 gap-2 text-sm">
            <div>
              <div class="text-ink-gray-5 text-xs">Leads</div>
              <div class="font-semibold text-ink-gray-9">{{ campaign.leads_count || 0 }}</div>
            </div>
            <div>
              <div class="text-ink-gray-5 text-xs">Spend</div>
              <div class="font-semibold text-ink-gray-9">{{ formatCurrency(campaign.spend) }}</div>
            </div>
            <div>
              <div class="text-ink-gray-5 text-xs">ROAS</div>
              <div class="font-semibold"
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
        <Button @click="loadMore" :loading="campaignsResource.loading" variant="subtle">
          Load More
        </Button>
      </div>

      <!-- Empty State -->
      <div v-if="!campaigns.length && !campaignsResource.loading" class="rounded-lg border-2 border-dashed border-outline-gray-2 bg-surface-cards p-12 text-center">
        <FeatherIcon name="target" class="mx-auto h-12 w-12 text-ink-gray-4" />
        <h3 class="mt-2 text-sm font-medium text-ink-gray-9">
          {{ searchQuery || selectedStatus ? 'No campaigns match your filters' : 'No campaigns yet' }}
        </h3>
        <p class="mt-1 text-sm text-ink-gray-5">
          {{ searchQuery || selectedStatus ? 'Try adjusting your search or filters' : 'Create your first marketing campaign to get started.' }}
        </p>
        <Button v-if="!searchQuery && !selectedStatus" class="mt-4" @click="$router.push('/marketing/campaigns/new')" variant="solid">
          <template #prefix>
            <FeatherIcon name="plus" class="h-4 w-4" />
          </template>
          Create Campaign
        </Button>
      </div>

      <!-- Loading State -->
      <div v-if="campaignsResource.loading && !campaigns.length" class="flex items-center justify-center py-20">
        <div class="h-8 w-8 animate-spin rounded-full border-2 border-ink-gray-3 border-t-transparent"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { createResource } from "frappe-ui";
import { computed, ref } from "vue";

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
  url: "marketing_hub.www.marketing.api.get_campaign_list",
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
import { watch } from "vue";
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
