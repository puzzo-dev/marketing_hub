<template>
  <div class="flex h-full flex-col overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="[
          { label: 'Activities', route: { path: '/marketing/activities' } },
          { label: activity.doc?.activity_name || activityName }
        ]" />
      </template>
      <template #right-header>
        <Badge v-if="activity.doc" :label="activity.doc.status || 'Draft'" variant="subtle"
          :theme="statusTheme(activity.doc.status)"
        />
        <Button variant="ghost" @click="openInDesk">
          <template #prefix>
            <IconExternalLink class="h-4 w-4" />
          </template>
          Open in Desk
        </Button>
      </template>
    </LayoutHeader>

    <div v-if="activity.doc" class="flex-1 overflow-auto p-5">
      <div class="mx-auto max-w-4xl space-y-5">
        <!-- Header Card -->
        <div class="rounded-lg border border-outline-gray-1 bg-surface-white p-5 shadow-sm">
          <h2 class="text-lg font-semibold text-ink-gray-9">{{ activity.doc.activity_name }}</h2>
          <p class="mt-1 text-sm text-ink-gray-6">{{ activity.doc.activity_type }} · {{ activity.doc.campaign || 'No campaign' }}</p>
          <div v-if="activity.doc.error_log" class="mt-3 rounded-md bg-surface-red-1 p-3 text-sm text-ink-red-3">
            {{ activity.doc.error_log }}
          </div>
        </div>

        <!-- Metrics -->
        <div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div class="rounded-lg border border-outline-gray-1 bg-surface-white p-4 text-center">
            <div class="text-xs font-medium text-ink-gray-5">Sent</div>
            <div class="mt-1.5 text-lg font-semibold text-ink-gray-9">{{ activity.doc.sent_count || 0 }}</div>
          </div>
          <div class="rounded-lg border border-outline-gray-1 bg-surface-white p-4 text-center">
            <div class="text-xs font-medium text-ink-gray-5">Delivered</div>
            <div class="mt-1.5 text-lg font-semibold text-ink-green-3">{{ activity.doc.delivered_count || 0 }}</div>
          </div>
          <div class="rounded-lg border border-outline-gray-1 bg-surface-white p-4 text-center">
            <div class="text-xs font-medium text-ink-gray-5">Failed</div>
            <div class="mt-1.5 text-lg font-semibold text-ink-red-3">{{ activity.doc.failed_count || 0 }}</div>
          </div>
          <div class="rounded-lg border border-outline-gray-1 bg-surface-white p-4 text-center">
            <div class="text-xs font-medium text-ink-gray-5">Opened</div>
            <div class="mt-1.5 text-lg font-semibold text-ink-gray-9">{{ activity.doc.opened_count || 0 }}</div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex gap-2">
          <Button v-if="activity.doc.status === 'Failed' && canRetry" variant="solid" @click="retryActivity" :loading="retrying">
            <template #prefix><IconRefreshCw class="h-4 w-4" /></template>
            Retry
          </Button>
          <Button v-if="activity.doc.status === 'Scheduled'" variant="solid" @click="executeActivity" :loading="executing">
            <template #prefix><IconPlay class="h-4 w-4" /></template>
            Execute Now
          </Button>
        </div>
      </div>
    </div>

    <div v-else-if="activity.loading" class="flex flex-1 items-center justify-center">
      <LoadingIndicator class="h-6 w-6" />
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { Breadcrumbs, Badge, Button, LoadingIndicator, getDocResource, call } from 'frappe-ui'
import LayoutHeader from '@/components/LayoutHeader.vue'
import { toast } from '@/utils/toast'

import IconExternalLink from '~icons/lucide/external-link'
import IconRefreshCw from '~icons/lucide/refresh-cw'
import IconPlay from '~icons/lucide/play'

const route = useRoute()
const activityName = route.params.name

const activity = getDocResource({
  doctype: 'Campaign Activity',
  name: activityName,
  auto: true,
})

const canRetry = computed(() => {
  const doc = activity.doc
  if (!doc) return false
  return (doc.retry_count || 0) < (doc.max_retries || 3)
})

const retrying = ref(false)
const executing = ref(false)

function statusTheme(status) {
  if (status === 'Completed') return 'green'
  if (status === 'In Progress') return 'blue'
  if (status === 'Scheduled') return 'orange'
  if (status === 'Failed') return 'red'
  return 'gray'
}

function openInDesk() {
  window.open(`/app/campaign-activity/${activityName}`, '_blank')
}

async function retryActivity() {
  retrying.value = true
  try {
    await call('marketing_hub.marketing_hub.doctype.campaign_activity.campaign_activity.retry_activity', {
      activity_name: activityName,
    })
    toast({ title: 'Success', text: 'Activity retry enqueued', icon: 'check', iconClasses: 'text-green-600' })
    activity.reload()
  } catch (error) {
    toast({ title: 'Error', text: error.message || 'Retry failed', icon: 'x', iconClasses: 'text-red-600' })
  } finally {
    retrying.value = false
  }
}

async function executeActivity() {
  executing.value = true
  try {
    await call('marketing_hub.marketing_hub.doctype.campaign_activity.campaign_activity.execute_activity', {
      activity_name: activityName,
    })
    toast({ title: 'Success', text: 'Activity execution enqueued', icon: 'check', iconClasses: 'text-green-600' })
    activity.reload()
  } catch (error) {
    toast({ title: 'Error', text: error.message || 'Execution failed', icon: 'x', iconClasses: 'text-red-600' })
  } finally {
    executing.value = false
  }
}
</script>
