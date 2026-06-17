<template>
  <div class="flex h-full flex-col overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="[{ label: 'Marketing Hub' }, { label: 'Omni Blasts' }]" />
      </template>
      <template #right-header>
        <Button @click="$router.push('/marketing/blast/new')" variant="solid" label="New Blast">
          <template #prefix><IconPlus class="h-4 w-4" /></template>
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
          @update:modelValue="searchQuery = $event"
          placeholder="Search blasts..."
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
      <div v-if="blastsResource.loading" class="flex items-center justify-center py-12">
        <LoadingIndicator class="h-6 w-6" />
      </div>

      <div v-else-if="filteredBlasts.length === 0" class="relative flex h-full w-full justify-center">
        <div class="absolute left-1/2 flex w-4/12 -translate-x-1/2 flex-col items-center gap-3" style="top: 35%">
          <IconMegaphone class="h-7 w-7 text-ink-gray-5" />
          <span class="text-base font-medium text-ink-gray-8">No blasts yet</span>
          <Button @click="$router.push('/marketing/blast/new')" variant="solid" label="Create Blast" />
        </div>
      </div>

      <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="blast in filteredBlasts"
          :key="blast.name"
          class="rounded-lg border border-outline-gray-1 bg-surface-white p-4 shadow-sm"
        >
          <div class="mb-3 flex items-start justify-between">
            <h4 class="text-base font-medium text-ink-gray-9 line-clamp-1">{{ blast.blast_title || blast.name }}</h4>
            <Badge :label="blast.status || 'Draft'" variant="subtle"
              :theme="statusTheme(blast.status)"
            />
          </div>

          <div class="mb-2 text-sm text-ink-gray-6">
            {{ blast.blast_type }} · {{ blast.campaign || 'No campaign' }}
          </div>

          <div v-if="blast.scheduled_time" class="mb-3 text-xs text-ink-gray-5">
            <IconCalendar class="inline h-3 w-3 mr-1" />
            {{ formatDate(blast.scheduled_time) }}
          </div>

          <div class="flex gap-2">
            <Button size="sm" variant="outline" @click="openInDesk(blast.name)">
              <template #prefix><IconExternalLink class="h-3.5 w-3.5" /></template>
              View
            </Button>
            <Button v-if="blast.status === 'Scheduled'" size="sm" variant="solid" @click="executeBlast(blast.name)" :loading="executing === blast.name">
              <template #prefix><IconPlay class="h-3.5 w-3.5" /></template>
              Publish
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Breadcrumbs, createResource, Button, FormControl, LoadingIndicator, Badge, call } from 'frappe-ui'
import LayoutHeader from '@/components/LayoutHeader.vue'
import { toast } from '@/utils/toast'

import IconSearch from '~icons/lucide/search'
import IconPlus from '~icons/lucide/plus'
import IconMegaphone from '~icons/lucide/megaphone'
import IconCalendar from '~icons/lucide/calendar'
import IconExternalLink from '~icons/lucide/external-link'
import IconPlay from '~icons/lucide/play'

const searchQuery = ref('')
const selectedStatus = ref('All')
const executing = ref(null)

const statusFilters = [
  { label: 'All', value: 'All' },
  { label: 'Draft', value: 'Draft' },
  { label: 'Scheduled', value: 'Scheduled' },
  { label: 'Publishing', value: 'Publishing' },
  { label: 'Published', value: 'Published' },
  { label: 'Failed', value: 'Failed' },
]

const blastsResource = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'Omni Blast',
    fields: ['name', 'blast_title', 'campaign', 'blast_type', 'status', 'scheduled_time', 'creation'],
    limit_page_length: 100,
    order_by: 'creation desc',
  },
  auto: true,
})

const blasts = computed(() => blastsResource.data || [])

const filteredBlasts = computed(() => {
  let result = blasts.value
  if (selectedStatus.value !== 'All') {
    result = result.filter(b => b.status === selectedStatus.value)
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(b =>
      (b.blast_title || '').toLowerCase().includes(q) ||
      (b.campaign || '').toLowerCase().includes(q)
    )
  }
  return result
})

function statusTheme(status) {
  if (status === 'Published') return 'green'
  if (status === 'Publishing') return 'blue'
  if (status === 'Scheduled') return 'orange'
  if (status === 'Failed') return 'red'
  return 'gray'
}

function formatDate(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleString()
}

function openInDesk(name) {
  window.open(`/app/omni-blast/${name}`, '_blank')
}

async function executeBlast(name) {
  executing.value = name
  try {
    await call('frappe.client.submit', {
      doctype: 'Omni Blast',
      name: name,
    })
    toast({ title: 'Success', text: 'Blast published', icon: 'check', iconClasses: 'text-green-600' })
    blastsResource.reload()
  } catch (error) {
    toast({ title: 'Error', text: error.message || 'Publish failed', icon: 'x', iconClasses: 'text-red-600' })
  } finally {
    executing.value = null
  }
}
</script>
