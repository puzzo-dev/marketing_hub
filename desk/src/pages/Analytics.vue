<template>
  <div class="flex h-full flex-col overflow-auto bg-white">
    <div class="flex-1 px-5 py-5 sm:px-6 lg:px-8">
      <div class="mb-5">
      <h1 class="text-2xl font-semibold text-gray-900">Analytics</h1>
      <p class="mt-1 text-sm text-gray-600">
        Performance breakdown by channel (Last 30 Days)
      </p>
    </div>

    <!-- Connectors Status -->
    <div class="mb-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
      <div v-for="connector in connectors" :key="connector.name" class="stat-card">
        <h6 class="mb-1 font-semibold text-gray-900">{{ connector.platform }}</h6>
        <div class="mb-2 text-sm text-gray-500">{{ connector.connector_name }}</div>
        <div class="flex items-center justify-between">
          <Badge
            :label="connector.sync_status"
            :variant="connector.sync_status === 'Active' ? 'success' : 'subtle'"
          />
          <span class="text-xs text-gray-500">
            {{ formatDate(connector.last_sync_date) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Performance Table -->
    <div class="rounded-lg border border-gray-100 bg-white shadow-sm">
      <div class="border-b px-6 py-4">
        <h5 class="font-semibold text-gray-900">Channel Performance</h5>
      </div>
      <div v-if="analytics.length" class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th
                class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500"
              >
                Channel
              </th>
              <th
                class="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500"
              >
                Spend
              </th>
              <th
                class="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500"
              >
                Revenue
              </th>
              <th
                class="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500"
              >
                ROAS
              </th>
              <th
                class="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500"
              >
                CTR
              </th>
              <th
                class="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500"
              >
                Conv.
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 bg-white">
            <tr v-for="row in analytics" :key="row.channel" class="hover:bg-gray-50">
              <td class="whitespace-nowrap px-6 py-4 font-medium text-gray-900">
                {{ row.channel }}
              </td>
              <td class="whitespace-nowrap px-6 py-4 text-right text-gray-900">
                {{ formatCurrency(row.spend) }}
              </td>
              <td class="whitespace-nowrap px-6 py-4 text-right text-gray-900">
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
              <td class="whitespace-nowrap px-6 py-4 text-right text-gray-900">
                {{ row.ctr.toFixed(2) }}%
              </td>
              <td class="whitespace-nowrap px-6 py-4 text-right text-gray-900">
                {{ row.conversions }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="p-12 text-center text-gray-500">
        No analytics data found for the last 30 days.
      </div>
    </div>
    </div>
  </div>
</template>

<script setup>
import { createResource } from "frappe-ui";
import { computed } from "vue";

const analyticsResource = createResource({
  url: "marketing_hub.www.marketing.analytics.get_context",
  auto: true,
});

const connectors = computed(() => analyticsResource.data?.connectors || []);
const analytics = computed(() => analyticsResource.data?.analytics || []);

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
</script>
