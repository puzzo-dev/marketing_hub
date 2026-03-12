<template>
  <div class="flex h-full flex-col overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="[
          { label: 'Clients', route: { path: '/marketing/clients' } },
          { label: clientName }
        ]" />
      </template>
      <template #right-header>
        <Button variant="ghost" label="Open in Desk" @click="openInDesk">
          <template #prefix>
            <IconExternalLink class="h-4 w-4" />
          </template>
        </Button>
      </template>
    </LayoutHeader>

    <div v-if="detail.loading && !data" class="flex flex-1 items-center justify-center">
      <LoadingIndicator class="h-6 w-6" />
    </div>

    <div v-else-if="data" class="flex-1 overflow-auto p-5">
      <div class="mx-auto max-w-5xl space-y-6">

        <!-- Client Header -->
        <div class="flex items-start justify-between rounded-lg border border-outline-gray-1 bg-surface-cards p-6">
          <div>
            <h2 class="text-xl font-semibold text-ink-gray-9">{{ data.customer.customer_name }}</h2>
            <p class="mt-1 text-sm text-ink-gray-5">{{ data.customer.territory || '' }}</p>
          </div>
          <div class="text-right">
            <Badge
              :label="data.subscription ? 'Subscribed' : 'No Subscription'"
              :theme="data.subscription ? 'green' : 'gray'"
              variant="subtle"
              size="lg"
            />
            <div v-if="data.subscription" class="mt-1 text-xs text-ink-gray-5">
              {{ data.package?.package_name }} · Expires {{ formatDate(data.subscription.end_date) }}
            </div>
          </div>
        </div>

        <!-- Stats -->
        <div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <StatCard label="Active Campaigns" :value="data.active_campaigns" />
          <StatCard label="Total Spend" :value="formatCurrency(data.total_spend)" />
          <StatCard label="Total Revenue" :value="formatCurrency(data.total_revenue)" />
          <StatCard label="Projects" :value="data.projects?.length || 0" />
        </div>

        <!-- Package Limits (if subscription) -->
        <div v-if="data.package" class="rounded-lg border border-outline-gray-1 bg-surface-cards p-6">
          <h3 class="mb-4 text-base font-medium text-ink-gray-9">Package Limits</h3>
          <div class="grid grid-cols-2 gap-4 sm:grid-cols-3">
            <div>
              <div class="text-xs text-ink-gray-5">Campaign Limit</div>
              <div class="text-sm font-medium text-ink-gray-9">
                {{ data.campaigns?.length || 0 }} / {{ data.package.campaign_limit || '∞' }}
              </div>
            </div>
            <div>
              <div class="text-xs text-ink-gray-5">Blast Limit (Monthly)</div>
              <div class="text-sm font-medium text-ink-gray-9">{{ data.package.blast_limit || '∞' }}</div>
            </div>
            <div>
              <div class="text-xs text-ink-gray-5">Channels</div>
              <div class="text-sm font-medium text-ink-gray-9">
                {{ data.package.included_channels?.filter(c => c).join(', ') || 'All' }}
              </div>
            </div>
          </div>
        </div>

        <!-- Campaigns -->
        <div class="rounded-lg border border-outline-gray-1 bg-surface-cards p-6">
          <div class="mb-4 flex items-center justify-between">
            <h3 class="text-base font-medium text-ink-gray-9">Campaigns</h3>
            <Button
              @click="$router.push({ path: '/marketing/campaigns/new', query: { customer: clientId } })"
              variant="subtle" size="sm" label="New Campaign"
            >
              <template #prefix><IconPlus class="h-3.5 w-3.5" /></template>
            </Button>
          </div>
          <div v-if="data.campaigns?.length" class="divide-y divide-outline-gray-1">
            <div v-for="c in data.campaigns" :key="c.name"
              class="flex cursor-pointer items-center justify-between py-3 transition-colors hover:bg-surface-gray-1 -mx-2 px-2 rounded"
              @click="$router.push('/marketing/campaigns/' + c.name)"
            >
              <div>
                <div class="text-sm font-medium text-ink-gray-9">{{ c.campaign_name }}</div>
                <div class="mt-0.5 flex items-center gap-2 text-xs text-ink-gray-5">
                  <Badge :label="c.status" variant="subtle" size="sm"
                    :theme="c.status === 'Active' ? 'green' : c.status === 'Completed' ? 'blue' : 'gray'"
                  />
                  <span v-if="c.project">Project: {{ c.project }}</span>
                </div>
              </div>
              <div class="text-right text-sm">
                <div class="font-medium text-ink-gray-9">{{ formatCurrency(c.budget || 0) }}</div>
                <div class="text-xs text-ink-gray-5">budget</div>
              </div>
            </div>
          </div>
          <div v-else class="py-6 text-center text-sm text-ink-gray-5">No campaigns for this client</div>
        </div>

        <!-- Projects -->
        <div class="rounded-lg border border-outline-gray-1 bg-surface-cards p-6">
          <div class="mb-4 flex items-center justify-between">
            <h3 class="text-base font-medium text-ink-gray-9">Projects</h3>
            <Button @click="openNewProject" variant="subtle" size="sm" label="New Project">
              <template #prefix><IconPlus class="h-3.5 w-3.5" /></template>
            </Button>
          </div>
          <div v-if="data.projects?.length" class="divide-y divide-outline-gray-1">
            <div v-for="p in data.projects" :key="p.name"
              class="flex cursor-pointer items-center justify-between py-3 transition-colors hover:bg-surface-gray-1 -mx-2 px-2 rounded"
              @click="openProject(p.name)"
            >
              <div>
                <div class="text-sm font-medium text-ink-gray-9">{{ p.project_name }}</div>
                <div class="mt-0.5 flex items-center gap-2 text-xs text-ink-gray-5">
                  <Badge :label="p.status" variant="subtle" size="sm"
                    :theme="p.status === 'Open' ? 'green' : p.status === 'Completed' ? 'blue' : 'gray'"
                  />
                  <Badge v-if="p.priority" :label="p.priority" variant="outline" size="sm" />
                </div>
              </div>
              <div v-if="p.estimated_costing" class="text-right text-sm">
                <div class="font-medium text-ink-gray-9">{{ formatCurrency(p.estimated_costing) }}</div>
                <div class="text-xs text-ink-gray-5">est. cost</div>
              </div>
            </div>
          </div>
          <div v-else class="py-6 text-center text-sm text-ink-gray-5">No projects linked to this client</div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Breadcrumbs, Button, LoadingIndicator, createResource } from 'frappe-ui'
import LayoutHeader from '@/components/LayoutHeader.vue'
import StatCard from '@/components/StatCard.vue'

import IconExternalLink from '~icons/lucide/external-link'
import IconPlus from '~icons/lucide/plus'

const route = useRoute()
const clientId = computed(() => decodeURIComponent(route.params.name))
const clientName = computed(() => data.value?.customer?.customer_name || clientId.value)

const detail = createResource({
  url: 'marketing_hub.api.agency.get_client_detail',
  params: { client: clientId.value },
  auto: true,
})

const data = computed(() => detail.data)

function openInDesk() {
  window.location.href = `/app/customer/${encodeURIComponent(clientId.value)}`
}

function openProject(name) {
  window.location.href = `/app/project/${encodeURIComponent(name)}`
}

function openNewProject() {
  window.location.href = `/app/project/new?customer=${encodeURIComponent(clientId.value)}`
}

function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value || 0)
}

function formatDate(date) {
  if (!date) return ''
  return new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}
</script>
