<template>
  <div class="flex h-full flex-col overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="[{ label: 'Marketing Hub' }, { label: 'Analytics' }]" />
      </template>
      <template #right-header>
        <Button @click="analyticsResource.reload()" variant="ghost" :loading="analyticsResource.loading">
          <template #icon>
            <IconRefreshCw class="h-4 w-4" />
          </template>
        </Button>
      </template>
    </LayoutHeader>

    <!-- Content Area -->
    <div class="flex-1 overflow-auto p-5">
      <!-- Loading State -->
      <div v-if="analyticsResource.loading" class="flex items-center justify-center py-12">
        <LoadingIndicator class="h-6 w-6" />
      </div>

      <template v-else>
        <!-- Connectors Status -->
        <div v-if="connectors.length" class="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div v-for="connector in connectors" :key="connector.name"
            class="rounded-lg border border-outline-gray-1 bg-surface-white p-4 shadow-sm"
          >
            <div class="text-sm font-medium text-ink-gray-9">{{ connector.platform }}</div>
            <div class="mb-2 text-xs text-ink-gray-5">{{ connector.connector_name }}</div>
            <div class="flex items-center justify-between">
              <Badge
                :label="connector.sync_status || 'Inactive'"
                variant="subtle"
                :theme="connector.sync_status === 'Active' ? 'green' : 'gray'"
              />
              <span v-if="connector.last_sync_date" class="text-xs text-ink-gray-5">
                {{ formatDate(connector.last_sync_date) }}
              </span>
            </div>
          </div>
        </div>

        <!-- Performance Chart -->
        <div v-if="dailyMetrics.length" class="mb-6 rounded-lg border border-outline-gray-1 bg-surface-white p-5 shadow-sm">
          <h4 class="mb-4 text-base font-medium text-ink-gray-9">Performance Trend</h4>
          <AxisChart
            title="Sales and Growth Rate"
            subtitle="Bar and line combination"
            :data="chartData"
            :colors="['#EF4444', '#10B981']"
            :axisOptions="{ xAxisMode: 'tick', xIsSeries: true }"
            :tooltipOptions="{ formatTooltipY: (d) => formatCurrency(d) }"
            type="line"
          />
        </div>

        <!-- Channel Performance Table -->
        <div class="rounded-lg border border-outline-gray-1 bg-surface-white shadow-sm">
          <div class="border-b border-outline-gray-1 px-5 py-3">
            <h4 class="text-base font-medium text-ink-gray-9">Channel Performance</h4>
          </div>
          <div v-if="channelPerformance.length" class="overflow-x-auto">
            <table class="min-w-full divide-y divide-outline-gray-1">
              <thead>
                <tr>
                  <th class="px-5 py-2.5 text-left text-xs font-medium uppercase text-ink-gray-5">Channel</th>
                  <th class="px-5 py-2.5 text-right text-xs font-medium uppercase text-ink-gray-5">Spend</th>
                  <th class="px-5 py-2.5 text-right text-xs font-medium uppercase text-ink-gray-5">Revenue</th>
                  <th class="px-5 py-2.5 text-right text-xs font-medium uppercase text-ink-gray-5">ROAS</th>
                  <th class="px-5 py-2.5 text-right text-xs font-medium uppercase text-ink-gray-5">CTR</th>
                  <th class="px-5 py-2.5 text-right text-xs font-medium uppercase text-ink-gray-5">Conversions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-outline-gray-1">
                <tr v-for="row in channelPerformance" :key="row.channel" class="transition-colors hover:bg-surface-gray-2">
                  <td class="whitespace-nowrap px-5 py-3 text-sm font-medium text-ink-gray-9">{{ row.channel || 'Unknown' }}</td>
                  <td class="whitespace-nowrap px-5 py-3 text-right text-sm text-ink-gray-9">{{ formatCurrency(row.spend) }}</td>
                  <td class="whitespace-nowrap px-5 py-3 text-right text-sm text-ink-gray-9">{{ formatCurrency(row.revenue) }}</td>
                  <td class="whitespace-nowrap px-5 py-3 text-right text-sm font-medium"
                    :class="row.roas >= 2 ? 'text-ink-green-3' : row.roas >= 1 ? 'text-ink-orange-3' : 'text-ink-red-3'"
                  >{{ row.roas.toFixed(2) }}x</td>
                  <td class="whitespace-nowrap px-5 py-3 text-right text-sm text-ink-gray-9">{{ row.ctr.toFixed(2) }}%</td>
                  <td class="whitespace-nowrap px-5 py-3 text-right text-sm text-ink-gray-9">{{ row.conversions || 0 }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="relative flex h-40 w-full justify-center">
            <div class="absolute left-1/2 flex -translate-x-1/2 flex-col items-center gap-3" style="top: 25%">
              <IconBarChart class="h-7 w-7 text-ink-gray-5" />
              <span class="text-base font-medium text-ink-gray-8">No analytics data</span>
              <span class="text-center text-sm text-ink-gray-6">Connect your analytics platforms to start tracking</span>
              <Button @click="goToConnectors" variant="solid" label="Add Connector">
                <template #prefix>
                  <IconPlus class="h-4 w-4" />
                </template>
              </Button>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { Breadcrumbs, createResource, AxisChart, LoadingIndicator } from "frappe-ui";
import { computed } from "vue";
import LayoutHeader from "@/components/LayoutHeader.vue";

import IconRefreshCw from '~icons/lucide/refresh-cw'
import IconBarChart from '~icons/lucide/bar-chart-2'
import IconPlus from '~icons/lucide/plus'

const analyticsResource = createResource({
  url: "marketing_hub.api.dashboard.get_analytics_data",
  params: {
    from_date: null,  // Will default to 30 days ago
    to_date: null     // Will default to today
  },
  auto: true,
});

const dailyMetrics = computed(() => analyticsResource.data?.daily_metrics || []);
const channelBreakdown = computed(() => analyticsResource.data?.channel_breakdown || []);
const connectors = computed(() => analyticsResource.data?.connectors || []);
const channelPerformance = computed(() => channelBreakdown.value);

// Prepare chart data for Frappe UI LineChart
const chartData = computed(() => {
  if (!dailyMetrics.value || dailyMetrics.value.length === 0) {
    return { labels: [], datasets: [] };
  }

  const labels = dailyMetrics.value.map(d => formatDate(d.date));
  
  return {
    labels,
    datasets: [
      {
        name: 'Spend',
        values: dailyMetrics.value.map(d => d.spend || 0),
      },
      {
        name: 'Revenue',
        values: dailyMetrics.value.map(d => d.revenue || 0),
      },
    ],
  };
});

function formatDate(date) {
  if (!date) return "";
  return new Date(date).toLocaleDateString("en-US", {
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

function goToConnectors() {
  window.location.href = "/app/analytics-connector";
}
</script>
