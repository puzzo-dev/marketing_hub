<template>
  <div class="flex h-full flex-col overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="[
          { label: 'Campaigns', route: { path: '/marketing/campaigns' } },
          { label: campaign.doc?.campaign_name || campaignName }
        ]" />
      </template>
      <template #right-header>
        <Badge v-if="campaign.doc" :label="campaign.doc.status || 'Draft'" variant="subtle"
          :theme="campaign.doc.status === 'Active' ? 'green' : campaign.doc.status === 'Completed' ? 'blue' : 'gray'"
        />
        <Button @click="openInDesk" variant="ghost">
          <template #prefix>
            <IconExternalLink class="h-4 w-4" />
          </template>
          Open in Desk
        </Button>
      </template>
    </LayoutHeader>

    <div v-if="campaign.doc" class="flex-1 overflow-auto">
      <div class="grid gap-6 p-5 lg:grid-cols-3">
        <!-- Main Content (2 cols) -->
        <div class="lg:col-span-2 space-y-5">
          <!-- Stats Row -->
          <div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div class="rounded-lg border border-outline-gray-1 bg-surface-white p-4">
              <div class="text-xs font-medium text-ink-gray-5">Budget</div>
              <div class="mt-1.5 text-lg font-semibold text-ink-gray-9">{{ formatCurrency(campaign.doc.budget || 0) }}</div>
            </div>
            <div class="rounded-lg border border-outline-gray-1 bg-surface-white p-4">
              <div class="text-xs font-medium text-ink-gray-5">Spend</div>
              <div class="mt-1.5 text-lg font-semibold text-ink-gray-9">{{ formatCurrency(metrics.spend) }}</div>
              <div v-if="campaign.doc.budget" class="mt-2">
                <div class="h-1 w-full rounded-full bg-surface-gray-2">
                  <div class="h-1 rounded-full transition-all"
                    :class="budgetPercent > 80 ? 'bg-ink-red-3' : budgetPercent > 60 ? 'bg-ink-orange-3' : 'bg-ink-green-3'"
                    :style="{ width: Math.min(budgetPercent, 100) + '%' }"
                  />
                </div>
                <p class="mt-1 text-[11px] text-ink-gray-5">{{ budgetPercent.toFixed(0) }}% utilized</p>
              </div>
            </div>
            <div class="rounded-lg border border-outline-gray-1 bg-surface-white p-4">
              <div class="text-xs font-medium text-ink-gray-5">Revenue</div>
              <div class="mt-1.5 text-lg font-semibold text-ink-green-3">{{ formatCurrency(metrics.revenue) }}</div>
            </div>
            <div class="rounded-lg border border-outline-gray-1 bg-surface-white p-4">
              <div class="text-xs font-medium text-ink-gray-5">ROAS</div>
              <div class="mt-1.5 text-lg font-semibold" :class="metrics.roas >= 3 ? 'text-ink-green-3' : metrics.roas >= 1 ? 'text-ink-orange-3' : 'text-ink-red-3'">
                {{ (metrics.roas || 0).toFixed(2) }}x
              </div>
            </div>
          </div>

          <!-- Campaign Activities -->
          <div class="rounded-lg border border-outline-gray-1 bg-surface-white">
            <div class="border-b border-outline-gray-1 px-5 py-3">
              <h4 class="text-sm font-medium text-ink-gray-9">Campaign Activities</h4>
            </div>
            <div v-if="activities.data?.length" class="divide-y divide-outline-gray-1">
              <div v-for="act in activities.data" :key="act.name"
                class="flex cursor-pointer items-center justify-between px-5 py-3 transition-colors hover:bg-surface-gray-2"
                @click="window.location.href = '/app/campaign-activity/' + act.name"
              >
                <div>
                  <p class="text-sm font-medium text-ink-gray-9">{{ act.subject || act.name }}</p>
                  <p class="mt-0.5 text-xs text-ink-gray-5">{{ act.channel || 'Multi-channel' }} · {{ act.scheduled_date || 'Not scheduled' }}</p>
                </div>
                <Badge :label="act.status || 'Draft'" variant="subtle" />
              </div>
            </div>
            <div v-else class="flex flex-col items-center gap-2 py-10">
              <IconActivity class="h-6 w-6 text-ink-gray-4" />
              <p class="text-sm text-ink-gray-5">No activities for this campaign</p>
            </div>
          </div>

          <!-- Leads Section -->
          <div class="rounded-lg border border-outline-gray-1 bg-surface-white">
            <div class="border-b border-outline-gray-1 px-5 py-3">
              <h4 class="text-sm font-medium text-ink-gray-9">Attributed Leads</h4>
            </div>
            <div v-if="leads.data?.length" class="divide-y divide-outline-gray-1">
              <div v-for="lead in leads.data" :key="lead.name"
                class="flex cursor-pointer items-center justify-between px-5 py-3 transition-colors hover:bg-surface-gray-2"
                @click="window.location.href = '/app/lead/' + lead.name"
              >
                <div>
                  <p class="text-sm font-medium text-ink-gray-9">{{ lead.lead_name || lead.name }}</p>
                  <p class="mt-0.5 text-xs text-ink-gray-5">{{ lead.company_name || 'No company' }} · {{ lead.source || 'Direct' }}</p>
                </div>
                <Badge :label="lead.status || 'Open'" variant="subtle" />
              </div>
            </div>
            <div v-else class="flex flex-col items-center gap-2 py-10">
              <IconUsers class="h-6 w-6 text-ink-gray-4" />
              <p class="text-sm text-ink-gray-5">No leads attributed yet</p>
            </div>
          </div>
        </div>

        <!-- Sidebar (1 col) -->
        <div class="space-y-5">
          <div class="rounded-lg border border-outline-gray-1 bg-surface-white p-5">
            <h4 class="mb-4 text-sm font-medium text-ink-gray-5">Details</h4>
            <dl class="space-y-3">
              <div>
                <dt class="text-xs text-ink-gray-5">Status</dt>
                <dd class="mt-0.5">
                  <Badge :label="campaign.doc.status || 'Draft'" variant="subtle"
                    :theme="campaign.doc.status === 'Active' ? 'green' : campaign.doc.status === 'Completed' ? 'blue' : 'gray'" />
                </dd>
              </div>
              <div v-if="campaign.doc.start_date">
                <dt class="text-xs text-ink-gray-5">Start Date</dt>
                <dd class="mt-0.5 text-sm text-ink-gray-9">{{ campaign.doc.start_date }}</dd>
              </div>
              <div v-if="campaign.doc.end_date">
                <dt class="text-xs text-ink-gray-5">End Date</dt>
                <dd class="mt-0.5 text-sm text-ink-gray-9">{{ campaign.doc.end_date }}</dd>
              </div>
              <div v-if="campaign.doc.company">
                <dt class="text-xs text-ink-gray-5">Company</dt>
                <dd class="mt-0.5 text-sm text-ink-gray-9">{{ campaign.doc.company }}</dd>
              </div>
            </dl>
          </div>
          <div class="rounded-lg border border-outline-gray-1 bg-surface-white p-5">
            <h4 class="mb-4 text-sm font-medium text-ink-gray-5">Actions</h4>
            <div class="space-y-2">
              <Button class="w-full" variant="subtle" label="Edit in Desk" @click="openInDesk">
                <template #prefix><IconExternalLink class="h-4 w-4" /></template>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-else-if="campaign.loading" class="flex flex-1 items-center justify-center">
      <LoadingIndicator class="h-6 w-6" />
    </div>

    <!-- Error State -->
    <div v-else class="flex flex-1 items-center justify-center">
      <div class="flex flex-col items-center gap-3">
        <IconAlertCircle class="h-7 w-7 text-ink-red-3" />
        <span class="text-sm text-ink-red-3">Campaign not found</span>
        <Button @click="$router.push('/marketing/campaigns')" variant="subtle" label="Back to Campaigns" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { Breadcrumbs, LoadingIndicator, createDocumentResource, createListResource, createResource } from "frappe-ui";
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import LayoutHeader from "@/components/LayoutHeader.vue";

import IconExternalLink from '~icons/lucide/external-link'
import IconActivity from '~icons/lucide/activity'
import IconUsers from '~icons/lucide/users'
import IconAlertCircle from '~icons/lucide/alert-circle'

const route = useRoute();
const campaignName = computed(() => route.params.name);

const campaign = createDocumentResource({
  doctype: "Marketing Campaign",
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

// Fetch real metrics from API
const campaignMetrics = ref({ spend: 0, revenue: 0, roas: 0 });

const metricsResource = createResource({
  url: "marketing_hub.api.campaigns.get_campaign_metrics",
  params: { campaign: campaignName.value },
  auto: true,
  onSuccess(data) {
    if (data) {
      campaignMetrics.value = data;
    }
  }
});

const metrics = computed(() => campaignMetrics.value);

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
  window.location.href = `/app/marketing-campaign/${campaignName.value}`;
}
</script>
