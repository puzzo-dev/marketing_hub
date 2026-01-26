<template>
  <div class="flex h-full flex-col overflow-auto bg-surface-gray-1">
    <!-- Onboarding Component -->
    <Onboarding :mode="userRole" />

    <div class="flex-1 px-5 py-5 sm:px-6 lg:px-8">
      <!-- Header Section -->
      <div class="mb-6">
        <h1 class="text-3xl font-bold text-ink-gray-9">Marketing Dashboard</h1>
        <p class="mt-1 text-sm text-ink-gray-6">
          Overview for {{ stats.month_name || new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' }) }}
        </p>
      </div>

      <!-- Stats Grid -->
      <div class="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Total Spend"
          :value="formatCurrency(stats.spend)"
          icon="dollar-sign"
          :change="stats.spend_change"
        />
        <StatCard
          label="Active Campaigns"
          :value="stats.active_campaigns"
          icon="target"
        />
        <StatCard
          label="Leads Generated"
          :value="stats.leads"
          icon="users"
          :change="stats.leads_change"
        />
        <StatCard
          label="ROAS"
          :value="(stats.avg_roas || 0).toFixed(2) + 'x'"
          icon="trending-up"
          subtext="Return on Ad Spend"
        />
      </div>

    <!-- Active Campaigns -->
      <div class="mb-6">
        <div class="mb-4 flex items-center justify-between">
          <h2 class="text-xl font-semibold text-ink-gray-9">Active Campaigns</h2>
          <Button @click="$router.push('/marketing/campaigns/new')" variant="solid">
            <template #prefix>
              <FeatherIcon name="plus" class="h-4 w-4" />
            </template>
            New Campaign
          </Button>
        </div>

        <div v-if="campaigns.length" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div 
            v-for="campaign in campaigns" 
            :key="campaign.name" 
            class="rounded-lg border border-outline-gray-1 bg-surface-cards p-5 shadow-sm transition-all hover:shadow-md cursor-pointer"
            @click="openCampaign(campaign.name)"
          >
            <div class="mb-3 flex items-start justify-between">
              <h3 class="font-semibold text-ink-gray-9 line-clamp-1">{{ campaign.campaign_name }}</h3>
              <Badge :label="campaign.status" variant="subtle" />
            </div>
            <p v-if="campaign.description" class="mb-3 text-sm text-ink-gray-6 line-clamp-2">
              {{ campaign.description }}
            </p>
            <div class="grid grid-cols-2 gap-3 text-sm">
              <div class="space-y-1">
                <div class="text-ink-gray-5">Leads</div>
                <div class="font-semibold text-ink-gray-9">{{ campaign.leads_count || 0 }}</div>
              </div>
              <div class="space-y-1">
                <div class="text-ink-gray-5">Spend</div>
                <div class="font-semibold text-ink-gray-9">{{ formatCurrency(campaign.total_spend || 0) }}</div>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="rounded-lg border-2 border-dashed border-outline-gray-2 bg-surface-cards p-12 text-center">
          <FeatherIcon name="target" class="mx-auto h-12 w-12 text-ink-gray-4" />
          <h3 class="mt-2 text-sm font-semibold text-ink-gray-9">No active campaigns</h3>
          <p class="mt-1 text-sm text-ink-gray-5">Get started by creating a new campaign.</p>
          <Button class="mt-4" @click="$router.push('/marketing/campaigns/new')" variant="solid">
            <template #prefix>
              <FeatherIcon name="plus" class="h-4 w-4" />
            </template>
            New Campaign
          </Button>
        </div>
      </div>

      <!-- Quick Links Grid -->
      <div class="mb-6">
        <h2 class="mb-4 text-xl font-semibold text-ink-gray-9">Quick Actions</h2>
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <router-link
            to="/marketing/campaigns"
            class="group rounded-lg border border-outline-gray-1 bg-surface-cards p-6 shadow-sm transition-all hover:shadow-md hover:border-blue-200"
          >
            <div class="flex flex-col items-center text-center">
              <div class="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-blue-50 group-hover:bg-blue-100 transition-colors">
                <FeatherIcon name="target" class="h-6 w-6 text-blue-600" />
              </div>
              <h4 class="font-semibold text-ink-gray-9">Campaigns</h4>
              <p class="mt-1 text-sm text-ink-gray-5">Manage campaigns</p>
            </div>
          </router-link>
          
          <router-link
            to="/marketing/blast/new"
            class="group rounded-lg border border-outline-gray-1 bg-surface-cards p-6 shadow-sm transition-all hover:shadow-md hover:border-purple-200"
          >
            <div class="flex flex-col items-center text-center">
              <div class="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-purple-50 group-hover:bg-purple-100 transition-colors">
                <FeatherIcon name="send" class="h-6 w-6 text-purple-600" />
              </div>
              <h4 class="font-semibold text-ink-gray-9">Omni Blast</h4>
              <p class="mt-1 text-sm text-ink-gray-5">Multi-channel blast</p>
            </div>
          </router-link>
          
          <router-link
            to="/marketing/social"
            class="group rounded-lg border border-outline-gray-1 bg-surface-cards p-6 shadow-sm transition-all hover:shadow-md hover:border-blue-200"
          >
            <div class="flex flex-col items-center text-center">
              <div class="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-blue-50 group-hover:bg-blue-100 transition-colors">
                <FeatherIcon name="share-2" class="h-6 w-6 text-blue-600" />
              </div>
              <h4 class="font-semibold text-ink-gray-9">Social Media</h4>
              <p class="mt-1 text-sm text-ink-gray-5">Schedule posts</p>
            </div>
          </router-link>
          
          <router-link
            to="/marketing/analytics"
            class="group rounded-lg border border-outline-gray-1 bg-surface-cards p-6 shadow-sm transition-all hover:shadow-md hover:border-green-200"
          >
            <div class="flex flex-col items-center text-center">
              <div class="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-green-50 group-hover:bg-green-100 transition-colors">
                <FeatherIcon name="bar-chart-2" class="h-6 w-6 text-green-600" />
              </div>
              <h4 class="font-semibold text-ink-gray-9">Analytics</h4>
              <p class="mt-1 text-sm text-ink-gray-5">View metrics</p>
            </div>
          </router-link>
          
          <router-link
            to="/marketing/content"
            class="group rounded-lg border border-outline-gray-1 bg-surface-cards p-6 shadow-sm transition-all hover:shadow-md hover:border-orange-200"
          >
            <div class="flex flex-col items-center text-center">
              <div class="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-orange-50 group-hover:bg-orange-100 transition-colors">
                <FeatherIcon name="image" class="h-6 w-6 text-orange-600" />
              </div>
              <h4 class="font-semibold text-ink-gray-9">Content</h4>
              <p class="mt-1 text-sm text-ink-gray-5">Assets & templates</p>
            </div>
          </router-link>
          
          <router-link
            to="/marketing/segments"
            class="group rounded-lg border border-outline-gray-1 bg-surface-cards p-6 shadow-sm transition-all hover:shadow-md hover:border-green-200"
          >
            <div class="flex flex-col items-center text-center">
              <div class="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-green-50 group-hover:bg-green-100 transition-colors">
                <FeatherIcon name="users" class="h-6 w-6 text-green-600" />
              </div>
              <h4 class="font-semibold text-ink-gray-9">Segments</h4>
              <p class="mt-1 text-sm text-ink-gray-5">Manage audiences</p>
            </div>
          </router-link>
          
          <router-link
            to="/marketing/expenses"
            class="group rounded-lg border border-outline-gray-1 bg-surface-cards p-6 shadow-sm transition-all hover:shadow-md hover:border-red-200"
          >
            <div class="flex flex-col items-center text-center">
              <div class="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-red-50 group-hover:bg-red-100 transition-colors">
                <FeatherIcon name="dollar-sign" class="h-6 w-6 text-red-600" />
              </div>
              <h4 class="font-semibold text-ink-gray-9">Expenses</h4>
              <p class="mt-1 text-sm text-ink-gray-5">Track spending</p>
            </div>
          </router-link>
          
          <router-link
            to="/marketing/settings"
            class="group rounded-lg border border-outline-gray-1 bg-surface-cards p-6 shadow-sm transition-all hover:shadow-md hover:border-gray-300"
          >
            <div class="flex flex-col items-center text-center">
              <div class="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-gray-50 group-hover:bg-gray-100 transition-colors">
                <FeatherIcon name="settings" class="h-6 w-6 text-gray-600" />
              </div>
              <h4 class="font-semibold text-ink-gray-9">Settings</h4>
              <p class="mt-1 text-sm text-ink-gray-5">Configure hub</p>
            </div>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { createResource } from "frappe-ui";
import { computed } from "vue";
import Onboarding from "@/components/Onboarding.vue";
import StatCard from "@/components/StatCard.vue";
import { useUserStore } from "@/stores/user";

const userStore = useUserStore();
const userRole = computed(() => userStore.role === 'Admin' ? 'admin' : 'agent');

const dashboard = createResource({
  url: "marketing_hub.www.marketing.api.get_dashboard_data",
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
