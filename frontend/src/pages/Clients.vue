<template>
  <div class="flex h-full flex-col overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="[{ label: 'Marketing Hub' }, { label: 'Clients' }]" />
      </template>
      <template #right-header>
        <Button @click="openNewClient" variant="solid" label="Add Client">
          <template #prefix>
            <IconPlus class="h-4 w-4" />
          </template>
        </Button>
      </template>
    </LayoutHeader>

    <!-- Filter Bar -->
    <div class="flex items-center gap-3 border-b px-5 py-3">
      <div class="relative flex-1 max-w-xs">
        <IconSearch class="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-gray-4" />
        <FormControl
          type="text"
          :modelValue="searchQuery"
          @update:modelValue="searchQuery = $event; debouncedSearch()"
          placeholder="Search clients..."
          class="pl-8"
        />
      </div>
    </div>

    <!-- Content Area -->
    <div class="flex-1 overflow-auto p-5">
      <!-- Client Grid -->
      <div v-if="clients.length" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div v-for="client in clients" :key="client.name"
          class="cursor-pointer rounded-lg border border-outline-gray-1 bg-surface-white p-4 shadow-sm transition-shadow hover:shadow"
          @click="$router.push('/marketing/clients/' + encodeURIComponent(client.name))"
        >
          <div class="mb-3 flex items-start justify-between">
            <div>
              <h4 class="text-base font-medium text-ink-gray-9 line-clamp-1">{{ client.customer_name }}</h4>
              <p class="mt-0.5 text-xs text-ink-gray-5">{{ client.customer_group || client.territory || '' }}</p>
            </div>
            <Badge
              :label="client.subscription ? 'Active' : 'No Sub'"
              variant="subtle"
              :theme="client.subscription ? 'green' : 'gray'"
            />
          </div>

          <!-- Subscription info -->
          <div v-if="client.subscription" class="mb-3 rounded-md bg-surface-gray-1 px-3 py-2 text-xs">
            <div class="flex items-center justify-between">
              <span class="text-ink-gray-6">{{ client.subscription.package_name }}</span>
              <span class="text-ink-gray-5">Exp: {{ formatDate(client.subscription.end_date) }}</span>
            </div>
          </div>

          <!-- Stats row -->
          <div class="grid grid-cols-3 gap-2 text-sm">
            <div>
              <div class="text-xs text-ink-gray-5">Campaigns</div>
              <div class="font-medium text-ink-gray-9">{{ client.active_campaigns }}/{{ client.total_campaigns }}</div>
            </div>
            <div>
              <div class="text-xs text-ink-gray-5">Projects</div>
              <div class="font-medium text-ink-gray-9">{{ client.projects || 0 }}</div>
            </div>
            <div>
              <div class="text-xs text-ink-gray-5">Spend</div>
              <div class="font-medium text-ink-gray-9">{{ formatCurrency(client.total_spend) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Load More -->
      <div v-if="hasMore" class="mt-6 text-center">
        <Button @click="loadMore" :loading="clientsResource.loading" variant="subtle" label="Load More" />
      </div>

      <!-- Empty State -->
      <div v-if="!clients.length && !clientsResource.loading" class="relative flex h-full w-full justify-center">
        <div class="absolute left-1/2 flex w-4/12 -translate-x-1/2 flex-col items-center gap-3" style="top: 35%">
          <IconBuilding class="h-7 w-7 text-ink-gray-5" />
          <span class="text-base font-medium text-ink-gray-8">
            {{ searchQuery ? 'No clients match your search' : 'No clients yet' }}
          </span>
          <span class="text-center text-sm text-ink-gray-6">
            {{ searchQuery ? 'Try adjusting your search' : 'Add a client and create a subscription to get started.' }}
          </span>
          <Button v-if="!searchQuery" @click="openNewClient" variant="solid" label="Add Client">
            <template #prefix>
              <IconPlus class="h-4 w-4" />
            </template>
          </Button>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="clientsResource.loading && !clients.length" class="flex items-center justify-center py-20">
        <LoadingIndicator class="h-6 w-6" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { Breadcrumbs, FormControl, LoadingIndicator, createResource } from "frappe-ui"
import { computed, ref } from "vue"
import LayoutHeader from "@/components/LayoutHeader.vue"

import IconPlus from '~icons/lucide/plus'
import IconSearch from '~icons/lucide/search'
import IconBuilding from '~icons/lucide/building'

const searchQuery = ref("")
const currentOffset = ref(0)
const pageSize = 20

const clientsResource = createResource({
  url: "marketing_hub.api.agency.get_clients",
  params: { filters: {}, limit: pageSize, offset: 0 },
  auto: true,
})

const clients = computed(() => clientsResource.data?.clients || [])
const hasMore = computed(() => clientsResource.data?.has_more || false)

let searchTimeout = null
function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => fetchClients(), 300)
}

function fetchClients() {
  currentOffset.value = 0
  const filters = {}
  if (searchQuery.value) filters.search = searchQuery.value
  clientsResource.fetch({ filters: JSON.stringify(filters), limit: pageSize, offset: 0 })
}

function loadMore() {
  currentOffset.value += pageSize
  const filters = {}
  if (searchQuery.value) filters.search = searchQuery.value
  clientsResource.fetch({ filters: JSON.stringify(filters), limit: pageSize, offset: currentOffset.value })
}

function openNewClient() {
  window.location.href = '/app/customer/new?customer_type=Company'
}

function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency", currency: "USD", maximumFractionDigits: 0
  }).format(value || 0)
}

function formatDate(date) {
  if (!date) return ''
  return new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}
</script>
