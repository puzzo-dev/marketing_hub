<template>
  <div class="flex h-full flex-col overflow-auto">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="[{ label: 'Marketing Hub' }, { label: 'Dashboard' }]" />
      </template>
      <template #right-header>
        <span v-if="lastUpdated" class="text-xs text-ink-gray-5">
          Updated {{ lastUpdated }}
        </span>
        <Button @click="refreshDashboard" variant="ghost" :loading="dashboard.loading">
          <template #icon>
            <IconRefreshCw class="h-4 w-4" />
          </template>
        </Button>
      </template>
    </LayoutHeader>

    <!-- Onboarding Component -->
    <Onboarding :mode="userRole" />

    <div class="flex-1 p-5">
      <!-- Stats Grid -->
      <div class="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Total Spend"
          :value="formatCurrency(stats.total_spend)"
          :change="stats.spend_change"
        />
        <StatCard
          label="Active Campaigns"
          :value="stats.active_campaigns"
        />
        <StatCard
          label="Leads Generated"
          :value="stats.leads_generated"
          :change="stats.leads_change"
        />
        <StatCard
          label="ROAS"
          :value="(stats.avg_roas || 0).toFixed(2) + 'x'"
          subtext="Return on Ad Spend"
        />
      </div>

      <!-- ROI Banner -->
      <div v-if="stats.roi > 0" class="mb-6 flex items-center gap-3 rounded-lg border border-outline-green-1 bg-surface-green-1 p-4">
        <div class="flex h-10 w-10 items-center justify-center rounded-full bg-surface-green-2">
          <IconTrendingUp class="h-5 w-5 text-ink-green-3" />
        </div>
        <div>
          <p class="text-sm font-semibold text-ink-green-3">Return on Investment: {{ stats.roi.toFixed(1) }}%</p>
          <p class="text-xs text-ink-gray-6">Revenue exceeds marketing spend by {{ stats.roi.toFixed(1) }}%</p>
        </div>
      </div>

      <!-- Active Campaigns + Recent Activities -->
      <div class="mb-6 grid gap-6 lg:grid-cols-3">
        <!-- Active Campaigns (2 cols) -->
        <div class="lg:col-span-2">
          <div class="mb-3 flex items-center justify-between">
            <h3 class="text-base font-medium text-ink-gray-9">Active Campaigns</h3>
            <Button @click="$router.push('/marketing/campaigns/new')" variant="solid" label="New Campaign">
              <template #prefix>
                <IconPlus class="h-4 w-4" />
              </template>
            </Button>
          </div>

          <div v-if="campaigns.length" class="grid gap-4 sm:grid-cols-2">
            <div
              v-for="campaign in campaigns"
              :key="campaign.campaign_name"
              class="cursor-pointer rounded-lg border border-outline-gray-1 bg-surface-white p-4 shadow-sm transition-shadow hover:shadow"
              @click="openCampaign(campaign.campaign_name)"
            >
              <div class="mb-3 flex items-start justify-between">
                <h4 class="text-base font-medium text-ink-gray-9 line-clamp-1">{{ campaign.title || campaign.campaign_name }}</h4>
                <Badge v-if="campaign.roas" :label="campaign.roas.toFixed(1) + 'x'"
                  :variant="campaign.roas >= 3 ? 'solid' : 'subtle'"
                  :theme="campaign.roas >= 3 ? 'green' : campaign.roas >= 1 ? 'orange' : 'red'"
                />
              </div>
              <div class="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <div class="text-ink-gray-5">Spend</div>
                  <div class="font-medium text-ink-gray-9">{{ formatCurrency(campaign.spend || 0) }}</div>
                </div>
                <div>
                  <div class="text-ink-gray-5">Revenue</div>
                  <div class="font-medium text-ink-gray-9">{{ formatCurrency(campaign.revenue || 0) }}</div>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="relative flex h-40 w-full items-center justify-center">
            <div class="flex flex-col items-center gap-3">
              <IconTarget class="h-7 w-7 text-ink-gray-5" />
              <span class="text-base font-medium text-ink-gray-8">No active campaigns</span>
              <Button @click="$router.push('/marketing/campaigns/new')" variant="solid" label="New Campaign">
                <template #prefix>
                  <IconPlus class="h-4 w-4" />
                </template>
              </Button>
            </div>
          </div>
        </div>

        <!-- Recent Activities (1 col) -->
        <div>
          <h3 class="mb-3 text-base font-medium text-ink-gray-9">Recent Activity</h3>
          <div class="rounded-lg border border-outline-gray-1">
            <div v-if="activities.length" class="divide-y divide-outline-gray-1">
              <div
                v-for="activity in activities"
                :key="activity.name"
                class="flex cursor-pointer items-start gap-3 px-4 py-3 transition-colors hover:bg-surface-gray-2"
                @click="openActivity(activity.name)"
              >
                <div class="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full"
                  :class="{
                    'bg-surface-green-1': activity.status === 'Completed',
                    'bg-surface-blue-1': activity.status === 'In Progress',
                    'bg-surface-orange-1': activity.status === 'Scheduled',
                    'bg-surface-gray-2': !['Completed', 'In Progress', 'Scheduled'].includes(activity.status)
                  }"
                >
                  <component
                    :is="activity.status === 'Completed' ? IconCheckCircle : activity.status === 'In Progress' ? IconClock : IconCalendar"
                    class="h-3.5 w-3.5"
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
                  <p class="mt-0.5 text-xs text-ink-gray-5">
                    {{ activity.campaign || 'No campaign' }} ·
                    <Badge :label="activity.status" variant="subtle" size="sm" />
                  </p>
                </div>
              </div>
            </div>
            <div v-else class="flex flex-col items-center gap-2 p-8">
              <IconActivity class="h-7 w-7 text-ink-gray-5" />
              <p class="text-sm text-ink-gray-6">No recent activities</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Links Grid -->
      <div>
        <h3 class="mb-3 text-base font-medium text-ink-gray-9">Quick Actions</h3>
        <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <router-link
            v-for="action in quickActions"
            :key="action.route"
            :to="action.route"
            class="group flex items-center gap-3 rounded-lg border border-outline-gray-1 bg-surface-white px-4 py-3 transition-shadow hover:shadow"
          >
            <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg transition-colors"
              :class="action.bgClass"
            >
              <component :is="action.icon" class="h-4.5 w-4.5" :class="action.iconClass" />
            </div>
            <div>
              <h4 class="text-sm font-medium text-ink-gray-9">{{ action.label }}</h4>
              <p class="text-xs text-ink-gray-6">{{ action.description }}</p>
            </div>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Breadcrumbs, createResource } from "frappe-ui";
import { computed, ref, onMounted, onUnmounted } from "vue";
import LayoutHeader from "@/components/LayoutHeader.vue";
import Onboarding from "@/components/Onboarding.vue";
import StatCard from "@/components/StatCard.vue";
import { useUserStore } from "@/stores/user";

import IconRefreshCw from '~icons/lucide/refresh-cw'
import IconTrendingUp from '~icons/lucide/trending-up'
import IconPlus from '~icons/lucide/plus'
import IconTarget from '~icons/lucide/target'
import IconCheckCircle from '~icons/lucide/check-circle'
import IconClock from '~icons/lucide/clock'
import IconCalendar from '~icons/lucide/calendar'
import IconActivity from '~icons/lucide/activity'
import IconMegaphone from '~icons/lucide/megaphone'
import IconSend from '~icons/lucide/send'
import IconShare2 from '~icons/lucide/share-2'
import IconBarChart from '~icons/lucide/bar-chart-2'
import IconFileText from '~icons/lucide/file-text'
import IconUsers from '~icons/lucide/users'
import IconWallet from '~icons/lucide/wallet'
import IconSettings from '~icons/lucide/settings'

const userStore = useUserStore();
const userRole = computed(() => userStore.role === 'Admin' ? 'admin' : 'agent');

const lastUpdated = ref(null);
let autoRefreshInterval = null;

const dashboard = createResource({
  url: "marketing_hub.api.dashboard.get_dashboard_data",
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
  { route: '/marketing/campaigns', label: 'Campaigns', description: 'Manage campaigns', icon: IconMegaphone, bgClass: 'bg-surface-blue-1 group-hover:bg-surface-blue-2', iconClass: 'text-ink-blue-3' },
  { route: '/marketing/blast/new', label: 'Omni Blast', description: 'Multi-channel blast', icon: IconSend, bgClass: 'bg-surface-purple-1 group-hover:bg-surface-purple-2', iconClass: 'text-ink-purple-3' },
  { route: '/marketing/social', label: 'Social Media', description: 'Schedule posts', icon: IconShare2, bgClass: 'bg-surface-blue-1 group-hover:bg-surface-blue-2', iconClass: 'text-ink-blue-3' },
  { route: '/marketing/analytics', label: 'Analytics', description: 'View metrics', icon: IconBarChart, bgClass: 'bg-surface-green-1 group-hover:bg-surface-green-2', iconClass: 'text-ink-green-3' },
  { route: '/marketing/content', label: 'Content', description: 'Assets & templates', icon: IconFileText, bgClass: 'bg-surface-orange-1 group-hover:bg-surface-orange-2', iconClass: 'text-ink-orange-3' },
  { route: '/marketing/segments', label: 'Segments', description: 'Manage audiences', icon: IconUsers, bgClass: 'bg-surface-green-1 group-hover:bg-surface-green-2', iconClass: 'text-ink-green-3' },
  { route: '/marketing/expenses', label: 'Expenses', description: 'Track spending', icon: IconWallet, bgClass: 'bg-surface-red-1 group-hover:bg-surface-red-2', iconClass: 'text-ink-red-3' },
  { route: '/marketing/settings', label: 'Settings', description: 'Configure hub', icon: IconSettings, bgClass: 'bg-surface-gray-2 group-hover:bg-surface-gray-3', iconClass: 'text-ink-gray-5' },
];

function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value || 0);
}

import { useRouter } from 'vue-router'

const router = useRouter()

function openCampaign(name) {
  router.push(`/marketing/campaigns/${name}`)
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
