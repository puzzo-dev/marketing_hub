<template>
  <div class="flex h-full flex-col overflow-auto bg-surface-gray-1">
    <div class="flex-1 px-5 py-5 sm:px-6 lg:px-8">
      <!-- Back Button + Header -->
      <div class="mb-6">
        <button @click="$router.push('/marketing/campaigns')" class="mb-4 flex items-center gap-1 text-sm text-ink-gray-5 hover:text-ink-gray-9 transition-colors">
          <FeatherIcon name="arrow-left" class="h-4 w-4" />
          Back to Campaigns
        </button>
        
        <div v-if="campaign.doc" class="flex items-start justify-between">
          <div>
            <h1 class="text-2xl font-bold text-ink-gray-9">{{ campaign.doc.campaign_name }}</h1>
            <p v-if="campaign.doc.description" class="mt-1 text-sm text-ink-gray-6">{{ campaign.doc.description }}</p>
          </div>
          <div class="flex items-center gap-3">
            <Badge :label="campaign.doc.status || 'Draft'" variant="subtle" 
              :theme="campaign.doc.status === 'Running' ? 'green' : campaign.doc.status === 'Completed' ? 'blue' : 'gray'" 
            />
            <Button @click="openInDesk" variant="subtle" size="sm">
              <template #prefix>
                <FeatherIcon name="external-link" class="h-3.5 w-3.5" />
              </template>
              Open in Desk
            </Button>
          </div>
        </div>
      </div>

      <div v-if="campaign.doc" class="space-y-6">
        <!-- Stats Row -->
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div class="rounded-lg border border-outline-gray-1 bg-surface-cards p-4 shadow-sm">
            <p class="text-xs font-medium text-ink-gray-5 uppercase tracking-wider">Budget</p>
            <p class="mt-1 text-xl font-bold text-ink-gray-9">{{ formatCurrency(campaign.doc.budget || 0) }}</p>
          </div>
          <div class="rounded-lg border border-outline-gray-1 bg-surface-cards p-4 shadow-sm">
            <p class="text-xs font-medium text-ink-gray-5 uppercase tracking-wider">Spend</p>
            <p class="mt-1 text-xl font-bold text-ink-gray-9">{{ formatCurrency(metrics.spend) }}</p>
            <div v-if="campaign.doc.budget" class="mt-2">
              <div class="h-1.5 w-full rounded-full bg-surface-gray-2">
                <div class="h-1.5 rounded-full transition-all" 
                  :class="budgetPercent > 80 ? 'bg-red-500' : budgetPercent > 60 ? 'bg-orange-400' : 'bg-green-500'"
                  :style="{ width: Math.min(budgetPercent, 100) + '%' }"
                ></div>
              </div>
              <p class="mt-1 text-xs text-ink-gray-5">{{ budgetPercent.toFixed(0) }}% utilized</p>
            </div>
          </div>
          <div class="rounded-lg border border-outline-gray-1 bg-surface-cards p-4 shadow-sm">
            <p class="text-xs font-medium text-ink-gray-5 uppercase tracking-wider">Revenue</p>
            <p class="mt-1 text-xl font-bold text-ink-green-3">{{ formatCurrency(metrics.revenue) }}</p>
          </div>
          <div class="rounded-lg border border-outline-gray-1 bg-surface-cards p-4 shadow-sm">
            <p class="text-xs font-medium text-ink-gray-5 uppercase tracking-wider">ROAS</p>
            <p class="mt-1 text-xl font-bold" :class="metrics.roas >= 3 ? 'text-ink-green-3' : metrics.roas >= 1 ? 'text-ink-orange-3' : 'text-ink-red-3'">
              {{ (metrics.roas || 0).toFixed(2) }}x
            </p>
          </div>
        </div>

        <!-- Campaign Activities -->
        <div>
          <h2 class="mb-3 text-lg font-semibold text-ink-gray-9">Campaign Activities</h2>
          <div v-if="activities.data?.length" class="space-y-3">
            <div v-for="act in activities.data" :key="act.name"
              class="flex items-center justify-between rounded-lg border border-outline-gray-1 bg-surface-cards p-4 shadow-sm cursor-pointer hover:shadow-md transition-shadow"
              @click="window.location.href = '/app/campaign-activity/' + act.name"
            >
              <div>
                <p class="font-medium text-ink-gray-9">{{ act.subject || act.name }}</p>
                <p class="text-xs text-ink-gray-5 mt-1">{{ act.channel || 'Multi-channel' }} · {{ act.scheduled_date || 'Not scheduled' }}</p>
              </div>
              <Badge :label="act.status || 'Draft'" variant="subtle" />
            </div>
          </div>
          <div v-else class="rounded-lg border border-dashed border-outline-gray-2 bg-surface-cards p-8 text-center">
            <FeatherIcon name="activity" class="mx-auto h-8 w-8 text-ink-gray-4" />
            <p class="mt-2 text-sm text-ink-gray-5">No activities for this campaign</p>
          </div>
        </div>

        <!-- Leads Section -->
        <div>
          <h2 class="mb-3 text-lg font-semibold text-ink-gray-9">Attributed Leads</h2>
          <div v-if="leads.data?.length" class="rounded-lg border border-outline-gray-1 bg-surface-cards shadow-sm">
            <div class="divide-y divide-outline-gray-1">
              <div v-for="lead in leads.data" :key="lead.name" 
                class="flex items-center justify-between p-4 hover:bg-surface-gray-1 cursor-pointer transition-colors"
                @click="window.location.href = '/app/lead/' + lead.name"
              >
                <div>
                  <p class="font-medium text-ink-gray-9">{{ lead.lead_name || lead.name }}</p>
                  <p class="text-xs text-ink-gray-5">{{ lead.company_name || 'No company' }} · {{ lead.source || 'Direct' }}</p>
                </div>
                <Badge :label="lead.status || 'Open'" variant="subtle" />
              </div>
            </div>
          </div>
          <div v-else class="rounded-lg border border-dashed border-outline-gray-2 bg-surface-cards p-8 text-center">
            <FeatherIcon name="users" class="mx-auto h-8 w-8 text-ink-gray-4" />
            <p class="mt-2 text-sm text-ink-gray-5">No leads attributed to this campaign yet</p>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-else-if="campaign.loading" class="flex items-center justify-center py-20">
        <div class="text-center">
          <div class="h-8 w-8 animate-spin rounded-full border-2 border-ink-gray-3 border-t-transparent mx-auto"></div>
          <p class="mt-3 text-sm text-ink-gray-5">Loading campaign...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else class="rounded-lg border border-outline-red-1 bg-surface-red-1 p-8 text-center">
        <FeatherIcon name="alert-circle" class="mx-auto h-8 w-8 text-ink-red-3" />
        <p class="mt-2 text-sm text-ink-red-3">Campaign not found</p>
        <Button class="mt-4" @click="$router.push('/marketing/campaigns')" variant="subtle">
          Back to Campaigns
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { createDocumentResource, createListResource } from "frappe-ui";
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const campaignName = computed(() => route.params.name);

const campaign = createDocumentResource({
  doctype: "Campaign",
  name: campaignName.value,
});

// Get campaign activities
const activities = createListResource({
  doctype: "Campaign Activity",
  fields: ["name", "subject", "status", "channel", "scheduled_date"],
  filters: { campaign: campaignName.value },
  orderBy: "scheduled_date desc",
  pageLength: 10,
  auto: true,
});

// Get attributed leads
const leads = createListResource({
  doctype: "Lead",
  fields: ["name", "lead_name", "company_name", "status", "source"],
  filters: { campaign_name: campaignName.value },
  orderBy: "creation desc",
  pageLength: 10,
  auto: true,
});

// Calculate metrics from Analytics Daily Log
const metrics = computed(() => {
  // For now use basic campaign data; can be enhanced with API call
  return {
    spend: 0,
    revenue: 0,
    roas: 0,
  };
});

const budgetPercent = computed(() => {
  if (!campaign.doc?.budget) return 0;
  return (metrics.value.spend / campaign.doc.budget) * 100;
});

function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value || 0);
}

function openInDesk() {
  window.location.href = `/app/campaign/${campaignName.value}`;
}
</script>
