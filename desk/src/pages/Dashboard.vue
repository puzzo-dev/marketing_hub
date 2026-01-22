<template>
  <div class="flex h-full flex-col overflow-auto bg-surface-gray-1">
    <div class="flex-1 px-5 py-5 sm:px-6 lg:px-8">
      <div class="mb-5">
        <h1 class="text-2xl font-semibold text-ink-gray-9">Marketing Dashboard</h1>
        <p class="mt-1 text-sm text-ink-gray-6">Overview for {{ stats.month_name }}</p>
      </div>

    <!-- Stats Grid -->
    <div class="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div class="rounded-lg border border-outline-gray-1 bg-surface-cards p-5 shadow-sm">
        <div class="text-sm font-medium text-ink-gray-6">Total Spend</div>
        <div class="mt-2 text-2xl font-semibold text-ink-gray-9">
          {{ formatCurrency(stats.spend) }}
        </div>
      </div>
      <div class="rounded-lg border border-outline-gray-1 bg-surface-cards p-5 shadow-sm">
        <div class="text-sm font-medium text-ink-gray-6">Active Campaigns</div>
        <div class="mt-2 text-2xl font-semibold text-ink-gray-9">
          {{ stats.active_campaigns }}
        </div>
      </div>
      <div class="rounded-lg border border-outline-gray-1 bg-surface-cards p-5 shadow-sm">
        <div class="text-sm font-medium text-ink-gray-6">Leads Generated</div>
        <div class="mt-2 text-2xl font-semibold text-ink-gray-9">
          {{ stats.total_leads }}
        </div>
      </div>
      <div class="rounded-lg border border-outline-gray-1 bg-surface-cards p-5 shadow-sm">
        <div class="text-sm font-medium text-ink-gray-6">Revenue</div>
        <div class="mt-2 text-2xl font-semibold text-ink-gray-9">
          {{ formatCurrency(stats.revenue) }}
        </div>
      </div>
    </div>

    <!-- Active Campaigns -->
    <div class="mb-6">
      <div class="mb-4 flex items-center justify-between">
        <h2 class="text-lg font-semibold text-ink-gray-9">Active Campaigns</h2>
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
            <Badge :label="campaign.status" variant="subtle" />
          </div>
          <p v-if="campaign.description" class="mb-3 text-sm text-ink-gray-6">
            {{ campaign.description.slice(0, 100) }}
            {{ campaign.description.length > 100 ? "..." : "" }}
          </p>
          <div class="text-sm text-ink-gray-5">
            <div>Leads: <strong>{{ campaign.leads_count || 0 }}</strong></div>
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
        <h3 class="mt-2 text-sm font-medium text-ink-gray-9">No active campaigns</h3>
        <p class="mt-1 text-sm text-ink-gray-5">Get started by creating a new campaign.</p>
        <Button class="mt-4" @click="$router.push('/marketing/campaigns/new')">
          <template #prefix>
            <FeatherIcon name="plus" class="h-4 w-4" />
          </template>
          New Campaign
        </Button>
      </div>
    </div>

    <!-- Quick Links -->
    <div class="grid gap-6 sm:grid-cols-3">
      <router-link
        to="/marketing/campaigns"
        class="stat-card flex flex-col items-center text-center"
      >
        <FeatherIcon name="target" class="mb-2 h-10 w-10 text-blue-600" />
        <h4 class="font-semibold text-gray-900">Campaigns</h4>
        <p class="mt-1 text-sm text-gray-500">Manage campaigns</p>
      </router-link>
      <router-link
        to="/marketing/social"
        class="stat-card flex flex-col items-center text-center"
      >
        <FeatherIcon name="share-2" class="mb-2 h-10 w-10 text-blue-600" />
        <h4 class="font-semibold text-gray-900">Social Media</h4>
        <p class="mt-1 text-sm text-gray-500">Schedule posts</p>
      </router-link>
      <router-link
        to="/marketing/analytics"
        class="stat-card flex flex-col items-center text-center"
      >
        <FeatherIcon name="bar-chart-2" class="mb-2 h-10 w-10 text-blue-600" />
        <h4 class="font-semibold text-gray-900">Analytics</h4>
        <p class="mt-1 text-sm text-gray-500">View metrics</p>
      </router-link>
    </div>
    </div>
  </div>
</template>

<script setup>
import { createResource } from "frappe-ui";
import { computed } from "vue";

const dashboard = createResource({
  url: "marketing_hub.www.marketing.index.get_dashboard_data",
  auto: true,
});

const stats = computed(() => dashboard.data?.stats || {
  spend: 0,
  active_campaigns: 0,
  total_leads: 0,
  revenue: 0,
  month_name: "Current Month",
});

const campaigns = computed(() => dashboard.data?.active_campaigns || []);

function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value || 0);
}

function openCampaign(name) {
  window.location.href = `/app/campaign/${name}`;
}
</script>
