<template>
  <div class="flex h-full flex-col overflow-auto bg-surface-gray-1">
    <div class="flex-1 px-5 py-5 sm:px-6 lg:px-8">
      <div class="mb-5 flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-ink-gray-9">Campaigns</h1>
        <p class="mt-1 text-sm text-ink-gray-6">Manage your marketing initiatives</p>
      </div>
      <Button @click="$router.push('/marketing/campaigns/new')">
        <template #prefix>
          <FeatherIcon name="plus" class="h-4 w-4" />
        </template>
        New Campaign
      </Button>
    </div>

    <div v-if="campaigns.length" class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      <div v-for="campaign in campaigns" :key="campaign.name" class="rounded-lg border border-outline-gray-1 bg-surface-cards p-5 shadow-sm transition-shadow hover:shadow-md">
        <div class="mb-2 flex items-start justify-between">
          <h3 class="font-semibold text-ink-gray-9">{{ campaign.campaign_name }}</h3>
          <Badge
            :label="campaign.status"
            :variant="campaign.status === 'In Progress' ? 'success' : 'subtle'"
          />
        </div>

        <div class="mb-3 flex items-center text-sm text-ink-gray-5">
          <FeatherIcon name="calendar" class="mr-1 h-4 w-4" />
          {{ formatDate(campaign.start_date) }}
          <span v-if="campaign.end_date"> - {{ formatDate(campaign.end_date) }}</span>
        </div>

        <div class="grid grid-cols-3 gap-2 text-sm">
          <div>
            <div class="text-ink-gray-5">Spend</div>
            <div class="font-semibold text-ink-gray-9">{{ formatCurrency(campaign.spend) }}</div>
          </div>
          <div>
            <div class="text-ink-gray-5">Revenue</div>
            <div class="font-semibold text-ink-gray-9">{{ formatCurrency(campaign.revenue) }}</div>
          </div>
          <div>
            <div class="text-ink-gray-5">ROAS</div>
            <div
              class="font-semibold"
              :class="{
                'text-ink-green-2': campaign.roas >= 2,
                'text-ink-amber-2': campaign.roas >= 1 && campaign.roas < 2,
              }"
            >
              {{ campaign.roas.toFixed(2) }}x
            </div>
          </div>
        </div>

        <Button
          variant="ghost"
          class="mt-3 w-full"
          @click="openCampaign(campaign.name)"
        >
          View Details
        </Button>
      </div>
    </div>

    <div v-else class="rounded-lg border-2 border-dashed border-outline-gray-2 bg-surface-cards p-12 text-center">
      <FeatherIcon name="target" class="mx-auto h-12 w-12 text-ink-gray-4" />
      <h3 class="mt-2 text-sm font-medium text-ink-gray-9">No campaigns yet</h3>
      <p class="mt-1 text-sm text-ink-gray-5">
        Create your first marketing campaign to get started.
      </p>
      <Button class="mt-4" @click="$router.push('/marketing/campaigns/new')">
        <template #prefix>
          <FeatherIcon name="plus" class="h-4 w-4" />
        </template>
        Create Campaign
      </Button>
    </div>
    </div>
  </div>
</template>

<script setup>
import { createResource } from "frappe-ui";
import { computed } from "vue";

const campaignsResource = createResource({
  url: "marketing_hub.www.marketing.index.get_campaign_list",
  params: {
    filters: {},
    limit: 20,
    offset: 0
  },
  auto: true,
});

const campaigns = computed(() => campaignsResource.data?.campaigns || []);

function formatDate(date) {
  return new Date(date).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value || 0);
}

function openCampaign(name) {
  window.location.href = `/app/campaign/${name}`;
}
</script>
