<template>
  <div class="flex h-full flex-col overflow-auto bg-surface-gray-1">
    <div class="flex-1 px-5 py-5 sm:px-6 lg:px-8">
      <div class="mb-5">
        <h1 class="text-2xl font-semibold text-ink-gray-9">Analytics</h1>
        <p class="mt-1 text-sm text-ink-gray-6">
          Performance breakdown by channel (Last 30 Days)
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="analyticsResource.loading" class="flex items-center justify-center py-12">
        <div class="text-center">
          <div class="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-ink-gray-3 border-t-red-600"></div>
          <p class="mt-2 text-sm text-ink-gray-5">Loading analytics...</p>
        </div>
      </div>

      <template v-else>
        <!-- Connectors Status -->
        <div v-if="connectors.length" class="mb-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <div v-for="connector in connectors" :key="connector.name" 
               class="rounded-lg border border-outline-gray-1 bg-surface-cards p-5 shadow-sm">
            <h6 class="mb-1 font-semibold text-ink-gray-9">{{ connector.platform }}</h6>
            <div class="mb-2 text-sm text-ink-gray-5">{{ connector.connector_name }}</div>
            <div class="flex items-center justify-between">
              <Badge
                :label="connector.sync_status || 'Inactive'"
                :variant="connector.sync_status === 'Active' ? 'success' : 'subtle'"
              />
              <span v-if="connector.last_sync_date" class="text-xs text-ink-gray-5">
                {{ formatDate(connector.last_sync_date) }}
              </span>
            </div>
          </div>
        </div>

        <!-- Performance Chart -->
        <div v-if="dailyMetrics.length" class="mb-8 rounded-lg border border-outline-gray-1 bg-surface-cards p-6 shadow-sm">
          <h5 class="mb-4 font-semibold text-ink-gray-9">Performance Trend</h5>
          <AxisChart
            title="Sales and Growth Rate"
            subtitle="Bar and line combination"
            :data="chartData"
            :colors="['#EF4444', '#10B981']"
            :axisOptions="{
              xAxisMode: 'tick',
              xIsSeries: true
            }"
            :tooltipOptions="{
              formatTooltipY: (d) => formatCurrency(d)
            }"
            type="line"
          />
        </div>

        <!-- Channel Performance Table -->
        <div class="rounded-lg border border-outline-gray-1 bg-surface-cards shadow-sm">
          <div class="border-b border-outline-gray-1 px-6 py-4">
            <h5 class="font-semibold text-ink-gray-9">Channel Performance</h5>
          </div>
          <div v-if="channelPerformance.length" class="overflow-x-auto">
            <table class="min-w-full divide-y divide-outline-gray-1">
              <thead class="bg-surface-gray-1">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-ink-gray-5">
                    Channel
                  </th>
                  <th class="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-ink-gray-5">
                    Spend
                  </th>
                  <th class="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-ink-gray-5">
                    Revenue
                  </th>
                  <th class="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-ink-gray-5">
                    ROAS
                  </th>
                  <th class="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-ink-gray-5">
                    CTR
                  </th>
                  <th class="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-ink-gray-5">
                    Conversions
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-outline-gray-1 bg-surface-cards">
                <tr v-for="row in channelPerformance" :key="row.channel" class="hover:bg-surface-gray-1 transition-colors">
                  <td class="whitespace-nowrap px-6 py-4 font-medium text-ink-gray-9">
                    {{ row.channel || 'Unknown' }}
                  </td>
                  <td class="whitespace-nowrap px-6 py-4 text-right text-ink-gray-9">
                    {{ formatCurrency(row.spend) }}
                  </td>
                  <td class="whitespace-nowrap px-6 py-4 text-right text-ink-gray-9">
                    {{ formatCurrency(row.revenue) }}
                  </td>
                  <td class="whitespace-nowrap px-6 py-4 text-right">
                    <span
                      class="font-semibold"
                      :class="{
                        'text-green-600': row.roas >= 2,
                        'text-orange-600': row.roas >= 1 && row.roas < 2,
                        'text-red-600': row.roas < 1,
                      }"
                    >
                      {{ row.roas.toFixed(2) }}x
                    </span>
                  </td>
                  <td class="whitespace-nowrap px-6 py-4 text-right text-ink-gray-9">
                    {{ row.ctr.toFixed(2) }}%
                  </td>
                  <td class="whitespace-nowrap px-6 py-4 text-right text-ink-gray-9">
                    {{ row.conversions || 0 }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="p-12 text-center">
            <FeatherIcon name="bar-chart-2" class="mx-auto h-12 w-12 text-ink-gray-4" />
            <h3 class="mt-2 text-sm font-medium text-ink-gray-9">No analytics data</h3>
            <p class="mt-1 text-sm text-ink-gray-5">
              Connect your analytics platforms to start tracking performance
            </p>
            <Button class="mt-4" @click="goToConnectors">
              <template #prefix>
                <FeatherIcon name="plus" class="h-4 w-4" />
              </template>
              Add Connector
            </Button>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { createResource, AxisChart } from "frappe-ui";
import { computed } from "vue";

const analyticsResource = createResource({
  url: "marketing_hub.www.marketing.analytics.get_analytics_data",
  auto: true,
});

const connectors = computed(() => analyticsResource.data?.connectors || []);
const channelPerformance = computed(() => analyticsResource.data?.channel_performance || []);
const dailyMetrics = computed(() => analyticsResource.data?.daily_metrics || []);

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
