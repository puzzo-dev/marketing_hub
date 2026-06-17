<template>
  <div class="flex h-full flex-col overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="[{ label: 'Marketing Hub' }, { label: 'Activities' }]" />
      </template>
    </LayoutHeader>

    <!-- Filter Bar -->
    <div class="flex items-center gap-3 border-b px-5 py-3">
      <div class="relative flex-1 max-w-xs">
        <IconSearch class="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-gray-4" />
        <FormControl
          type="text"
          :modelValue="searchQuery"
          @update:modelValue="searchQuery = $event"
          placeholder="Search activities..."
          class="pl-8"
        />
      </div>
      <div class="flex gap-1.5">
        <Button
          v-for="status in statusFilters"
          :key="status.value"
          @click="selectedStatus = status.value"
          :variant="selectedStatus === status.value ? 'subtle' : 'ghost'"
          size="sm"
          :label="status.label"
        />
      </div>
    </div>

    <!-- Content Area -->
    <div class="flex-1 overflow-auto p-5">
      <div v-if="activitiesResource.loading" class="flex items-center justify-center py-12">
        <LoadingIndicator class="h-6 w-6" />
      </div>

      <div v-else-if="filteredActivities.length === 0" class="relative flex h-full w-full justify-center">
        <div class="absolute left-1/2 flex w-4/12 -translate-x-1/2 flex-col items-center gap-3" style="top: 35%">
          <IconActivity class="h-7 w-7 text-ink-gray-5" />
          <span class="text-base font-medium text-ink-gray-8">No activities</span>
          <span class="text-center text-sm text-ink-gray-6">Campaign activities will appear here</span>
        </div>
      </div>

      <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="activity in filteredActivities"
          :key="activity.name"
          class="cursor-pointer rounded-lg border border-outline-gray-1 bg-surface-white p-4 shadow-sm transition-shadow hover:shadow"
          @click="$router.push('/marketing/activities/' + activity.name)"
        >
          <div class="mb-3 flex items-start justify-between">
            <h4 class="text-base font-medium text-ink-gray-9 line-clamp-1">{{ activity.activity_name || activity.name }}</h4>
            <Badge :label="activity.status || 'Draft'" variant="subtle"
              :theme="statusTheme(activity.status)"
            />
          </div>

          <div class="mb-2 text-sm text-ink-gray-6">
            {{ activity.activity_type }} · {{ activity.campaign || 'No campaign' }}
          </div>

          <div v-if="activity.scheduled_date" class="mb-3 text-xs text-ink-gray-5">
            <IconCalendar class="inline h-3 w-3 mr-1" />
            {{ formatDate(activity.scheduled_date) }}
          </div>

          <!-- Metrics -->
          <div v-if="activity.sent_count !== undefined" class="mt-2 grid grid-cols-3 gap-2 text-xs">
            <div class="rounded bg-surface-gray-1 p-1.5 text-center">
              <div class="font-medium text-ink-gray-9">{{ activity.sent_count || 0 }}</div>
              <div class="text-ink-gray-5">Sent</div>
            </div>
            <div class="rounded bg-surface-gray-1 p-1.5 text-center">
              <div class="font-medium text-ink-green-3">{{ activity.delivered_count || 0 }}</div>
              <div class="text-ink-gray-5">Delivered</div>
            </div>
            <div class="rounded bg-surface-gray-1 p-1.5 text-center">
              <div class="font-medium text-ink-red-3">{{ activity.failed_count || 0 }}</div>
              <div class="text-ink-gray-5">Failed</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Breadcrumbs, createResource, Button, FormControl, LoadingIndicator, Badge } from 'frappe-ui'
import LayoutHeader from '@/components/LayoutHeader.vue'

import IconSearch from '~icons/lucide/search'
import IconActivity from '~icons/lucide/activity'
import IconCalendar from '~icons/lucide/calendar'

const searchQuery = ref('')
const selectedStatus = ref('All')

const statusFilters = [
  { label: 'All', value: 'All' },
  { label: 'Scheduled', value: 'Scheduled' },
  { label: 'In Progress', value: 'In Progress' },
  { label: 'Completed', value: 'Completed' },
  { label: 'Failed', value: 'Failed' },
]

const activitiesResource = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'Campaign Activity',
    fields: ['name', 'activity_name', 'campaign', 'activity_type', 'status', 'scheduled_date', 'sent_count', 'delivered_count', 'failed_count', 'creation'],
    limit_page_length: 100,
    order_by: 'creation desc',
  },
  auto: true,
})

const activities = computed(() => activitiesResource.data || [])

const filteredActivities = computed(() => {
  let result = activities.value
  if (selectedStatus.value !== 'All') {
    result = result.filter(a => a.status === selectedStatus.value)
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(a =>
      (a.activity_name || '').toLowerCase().includes(q) ||
      (a.campaign || '').toLowerCase().includes(q) ||
      (a.activity_type || '').toLowerCase().includes(q)
    )
  }
  return result
})

function statusTheme(status) {
  if (status === 'Completed') return 'green'
  if (status === 'In Progress') return 'blue'
  if (status === 'Scheduled') return 'orange'
  if (status === 'Failed') return 'red'
  return 'gray'
}

function formatDate(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleString()
}
</script>
