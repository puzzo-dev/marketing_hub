<template>
  <div class="flex h-full flex-col overflow-auto bg-surface-gray-1">
    <!-- Onboarding Component -->
    <Onboarding :mode="userRole" />

    <div class="flex-1 px-5 py-5 sm:px-6 lg:px-8">
      <!-- Header Section -->
      <div class="mb-6 flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-ink-gray-9">Marketing Dashboard</h1>
          <p class="mt-1 text-sm text-ink-gray-6">
            Overview for {{ new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' }) }}
          </p>
        </div>
        <div class="flex items-center gap-3">
          <span v-if="lastUpdated" class="text-xs text-ink-gray-5">
            Updated {{ lastUpdated }}
          </span>
          <Button @click="refreshDashboard" size="sm" variant="subtle" :loading="dashboard.loading">
            <template #prefix>
              <FeatherIcon name="refresh-cw" class="h-3.5 w-3.5" />
            </template>
            Refresh
          </Button>
        </div>
      </div>

      <!-- Stats Grid -->
      <div class="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Total Spend"
          :value="formatCurrency(stats.total_spend)"
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
          :value="stats.leads_generated"
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

      <!-- ROI Banner -->
      <div v-if="stats.roi > 0" class="mb-6 rounded-lg border border-outline-green-1 bg-surface-green-1 p-4">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-full bg-surface-green-2">
            <FeatherIcon name="trending-up" class="h-5 w-5 text-ink-green-3" />
          </div>
          <div>
            <p class="text-sm font-semibold text-ink-green-3">Return on Investment: {{ stats.roi.toFixed(1) }}%</p>
            <p class="text-xs text-ink-gray-6">Revenue exceeds marketing spend by {{ stats.roi.toFixed(1) }}%</p>
          </div>
        </div>
      </div>

      <!-- Active Campaigns + Recent Activities -->
      <div class="mb-6 grid gap-6 lg:grid-cols-3">
        <!-- Active Campaigns (2 cols) -->
        <div class="lg:col-span-2">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-xl font-semibold text-ink-gray-9">Active Campaigns</h2>
            <Button @click="$router.push('/marketing/campaigns/new')" variant="solid">
              <template #prefix>
                <FeatherIcon name="plus" class="h-4 w-4" />
              </template>
              New Campaign
            </Button>
          </div>

          <div v-if="campaigns.length" class="grid gap-4 sm:grid-cols-2">
            <div 
              v-for="campaign in campaigns" 
              :key="campaign.campaign_name" 
              class="rounded-lg border border-outline-gray-1 bg-surface-cards p-5 shadow-sm transition-all hover:shadow-md cursor-pointer"
              @click="openCampaign(campaign.campaign_name)"
            >
              <div class="mb-3 flex items-start justify-between">
                <h3 class="font-semibold text-ink-gray-9 line-clamp-1">{{ campaign.title || campaign.campaign_name }}</h3>
                <Badge v-if="campaign.roas" :label="campaign.roas.toFixed(1) + 'x'" 
                  :variant="campaign.roas >= 3 ? 'solid' : 'subtle'" 
                  :theme="campaign.roas >= 3 ? 'green' : campaign.roas >= 1 ? 'orange' : 'red'" 
                />
              </div>
              <div class="grid grid-cols-2 gap-3 text-sm">
                <div class="space-y-1">
                  <div class="text-ink-gray-5">Spend</div>
                  <div class="font-semibold text-ink-gray-9">{{ formatCurrency(campaign.spend || 0) }}</div>
                </div>
                <div class="space-y-1">
                  <div class="text-ink-gray-5">Revenue</div>
                  <div class="font-semibold text-ink-gray-9">{{ formatCurrency(campaign.revenue || 0) }}</div>
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

        <!-- Recent Activities (1 col) -->
        <div>
          <h2 class="mb-4 text-xl font-semibold text-ink-gray-9">Recent Activity</h2>
          <div class="rounded-lg border border-outline-gray-1 bg-surface-cards shadow-sm">
            <div v-if="activities.length" class="divide-y divide-outline-gray-1">
              <div 
                v-for="activity in activities" 
                :key="activity.name"
                class="flex items-start gap-3 p-4 transition-colors hover:bg-surface-gray-1 cursor-pointer"
                @click="openActivity(activity.name)"
              >
                <div class="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full"
                  :class="{
                    'bg-surface-green-1': activity.status === 'Completed',
                    'bg-surface-blue-1': activity.status === 'In Progress',
                    'bg-surface-orange-1': activity.status === 'Scheduled',
                    'bg-surface-gray-2': !['Completed', 'In Progress', 'Scheduled'].includes(activity.status)
                  }"
                >
                  <FeatherIcon 
                    :name="activity.status === 'Completed' ? 'check-circle' : activity.status === 'In Progress' ? 'clock' : 'calendar'" 
                    class="h-4 w-4"
                    :class="{
                      'text-ink-green-3': activity.status === 'Completed',
                      'text-ink-blue-3': activity.status === 'In Progress',
                      'text-ink-orange-3': activity.status === 'Scheduled',
                      'text-ink-gray-5': !['Completed', 'In Progress', 'Scheduled'].includes(activity.status)
                    }"
                  />
                </div>
                <div class="min-w-0 flex-1">
                  <p class="text-sm font-medium text-ink-gray-9 line-clamp-1">{{ activity.subject || activity.name }}</p>
                  <p class="text-xs text-ink-gray-5 mt-0.5">
                    {{ activity.campaign || 'No campaign' }} · 
                    <Badge :label="activity.status" variant="subtle" size="sm" />
                  </p>
                </div>
              </div>
            </div>
            <div v-else class="p-8 text-center">
              <FeatherIcon name="activity" class="mx-auto h-8 w-8 text-ink-gray-4" />
              <p class="mt-2 text-sm text-ink-gray-5">No recent activities</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Links Grid -->
      <div class="mb-6">
        <h2 class="mb-4 text-xl font-semibold text-ink-gray-9">Quick Actions</h2>
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <router-link
            v-for="action in quickActions"
            :key="action.route"
            :to="action.route"
            class="group rounded-lg border border-outline-gray-1 bg-surface-cards p-6 shadow-sm transition-all hover:shadow-md hover:border-outline-gray-3"
          >
            <div class="flex flex-col items-center text-center">
              <div class="mb-3 flex h-12 w-12 items-center justify-center rounded-full transition-colors"
                :class="action.bgClass"
              >
                <FeatherIcon :name="action.icon" class="h-6 w-6" :class="action.iconClass" />
              </div>
              <h4 class="font-semibold text-ink-gray-9">{{ action.label }}</h4>
              <p class="mt-1 text-sm text-ink-gray-5">{{ action.description }}</p>
            </div>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { createResource } from "frappe-ui";
import { computed, ref, onMounted, onUnmounted } from "vue";
import Onboarding from "@/components/Onboarding.vue";
import StatCard from "@/components/StatCard.vue";
import { useUserStore } from "@/stores/user";

const userStore = useUserStore();
const userRole = computed(() => userStore.role === 'Admin' ? 'admin' : 'agent');

const lastUpdated = ref(null);
let autoRefreshInterval = null;

const dashboard = createResource({
  url: "marketing_hub.www.marketing.api.get_dashboard_data",
  auto: true,
  onSuccess() {
    lastUpdated.value = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  },
});

const stats = computed(() => {
  if (!dashboard.data) return {
    active_campaigns: 0,
    total_spend: 0,
    leads_generated: 0,
    roi: 0,
    avg_roas: 0,
    spend_change: 0,
    leads_change: 0,
  };
  
  return {
    active_campaigns: dashboard.data.active_campaigns || 0,
    total_spend: dashboard.data.total_spend || 0,
    spend_change: dashboard.data.spend_change || 0,
    leads_generated: dashboard.data.leads_generated || 0,
    leads_change: dashboard.data.leads_change || 0,
    roi: dashboard.data.roi || 0,
    avg_roas: dashboard.data.avg_roas || 0,
  };
});

const campaigns = computed(() => dashboard.data?.top_campaigns || []);
const activities = computed(() => dashboard.data?.recent_activities || []);

const quickActions = [
  { route: '/marketing/campaigns', label: 'Campaigns', description: 'Manage campaigns', icon: 'target', bgClass: 'bg-surface-blue-1 group-hover:bg-surface-blue-2', iconClass: 'text-ink-blue-3' },
  { route: '/marketing/blast/new', label: 'Omni Blast', description: 'Multi-channel blast', icon: 'send', bgClass: 'bg-surface-purple-1 group-hover:bg-surface-purple-2', iconClass: 'text-ink-purple-3' },
  { route: '/marketing/social', label: 'Social Media', description: 'Schedule posts', icon: 'share-2', bgClass: 'bg-surface-blue-1 group-hover:bg-surface-blue-2', iconClass: 'text-ink-blue-3' },
  { route: '/marketing/analytics', label: 'Analytics', description: 'View metrics', icon: 'bar-chart-2', bgClass: 'bg-surface-green-1 group-hover:bg-surface-green-2', iconClass: 'text-ink-green-3' },
  { route: '/marketing/content', label: 'Content', description: 'Assets & templates', icon: 'image', bgClass: 'bg-surface-orange-1 group-hover:bg-surface-orange-2', iconClass: 'text-ink-orange-3' },
  { route: '/marketing/segments', label: 'Segments', description: 'Manage audiences', icon: 'users', bgClass: 'bg-surface-green-1 group-hover:bg-surface-green-2', iconClass: 'text-ink-green-3' },
  { route: '/marketing/expenses', label: 'Expenses', description: 'Track spending', icon: 'credit-card', bgClass: 'bg-surface-red-1 group-hover:bg-surface-red-2', iconClass: 'text-ink-red-3' },
  { route: '/marketing/settings', label: 'Settings', description: 'Configure hub', icon: 'settings', bgClass: 'bg-surface-gray-2 group-hover:bg-surface-gray-3', iconClass: 'text-ink-gray-5' },
];

function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value || 0);
}

function openCampaign(name) {
  window.location.href = `/app/campaign/${name}`;
}

function openActivity(name) {
  window.location.href = `/app/campaign-activity/${name}`;
}

function refreshDashboard() {
  dashboard.reload();
}

// Auto-refresh every 30 seconds
onMounted(() => {
  autoRefreshInterval = setInterval(() => {
    dashboard.reload();
  }, 30000);
});

onUnmounted(() => {
  if (autoRefreshInterval) {
    clearInterval(autoRefreshInterval);
  }
});
</script>
