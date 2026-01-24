<template>
  <div class="flex h-full flex-col overflow-auto bg-surface-gray-1">
    <!-- Onboarding Component -->
    <Onboarding :mode="userRole" />

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
          {{ stats.leads }}
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
    <div class="grid gap-6 sm:grid-cols-2 lg:grid-cols-5">
      <router-link
        to="/marketing/campaigns"
        class="stat-card flex flex-col items-center text-center"
      >
        <FeatherIcon name="target" class="mb-2 h-10 w-10 text-blue-600" />
        <h4 class="font-semibold text-gray-900">Campaigns</h4>
        <p class="mt-1 text-sm text-gray-500">Manage campaigns</p>
      </router-link>
      <router-link
        to="/marketing/blast/new"
        class="stat-card flex flex-col items-center text-center"
      >
        <FeatherIcon name="send" class="mb-2 h-10 w-10 text-purple-600" />
        <h4 class="font-semibold text-gray-900">Omni Blast</h4>
        <p class="mt-1 text-sm text-gray-500">Create blast</p>
      </router-link>
      <router-link
        to="/marketing/segments"
        class="stat-card flex flex-col items-center text-center"
      >
        <FeatherIcon name="users" class="mb-2 h-10 w-10 text-green-600" />
        <h4 class="font-semibold text-gray-900">Segments</h4>
        <p class="mt-1 text-sm text-gray-500">Manage audiences</p>
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
import Onboarding from "@/components/Onboarding.vue";

// Determine user role for onboarding
const userRole = computed(() => {
  const roles = window.frappe?.boot?.user?.roles || [];
  return roles.includes('System Manager') || roles.includes('Marketing Manager') ? 'admin' : 'agent';
});

const dashboard = createResource({
  url: "marketing_hub.www.marketing.index.get_dashboard_data",
  auto: true,
});

const stats = computed(() => {
  if (!dashboard.data) return {
    active_campaigns: 0,
    total_spend: 0,
    leads_generated: 0,
    roi: 0,
    avg_roas: 0
  };
  
  return {
    active_campaigns: dashboard.data.active_campaigns || 0,
    total_spend: dashboard.data.total_spend || 0,
    spend_change: dashboard.data.spend_change || 0,
    leads_generated: dashboard.data.leads_generated || 0,
    leads_change: dashboard.data.leads_change || 0,
    roi: dashboard.data.roi || 0,
    avg_roas: dashboard.data.avg_roas || 0
  };
});

const campaigns = computed(() => dashboard.data?.top_campaigns || []);
const activities = computed(() => dashboard.data?.recent_activities || []);

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
