<template>
  <div class="flex min-h-0 flex-1 flex-col">
  <PaneHeader :title="doc?.campaign_name || name" :close="{ name: 'Exercises' }">
      <template v-if="!canEditDirectly" #actions><Button label="Request a change" @click="showRequest = true" /></template>
    </PaneHeader>
  <div class="min-h-0 flex-1 overflow-y-auto">

  <div v-if="!doc && !error" class="flex flex-col gap-3 px-3 py-4 sm:px-5" aria-busy="true"><Skeleton class="h-8 w-64" /><Skeleton class="h-40 w-full" /></div>

  <ErrorState v-else-if="error" icon="lucide-lock" title="You do not have access to this" text="It belongs to another brand or exercise. Ask its Brand Manager to add you." action-label="Back to exercises" @action="$router.push({ name: 'Exercises' })" />

  <div v-else-if="doc" class="flex flex-col">
    <Tabs v-model="tab" :tabs="tabs" variant="underline" class="px-3 sm:px-5" />
    <div class="flex flex-col gap-6 px-3 pb-10 pt-5 sm:px-5">
      <FieldRows v-if="tab === 'plan'" :rows="[['Brand', doc.brand], ['Brand Manager', doc.brand_manager], ['Dates', `${doc.start_date} to ${doc.end_date}`], ['Status', doc.status], ['Objective', doc.objective]]" />
      <DataList v-if="tab === 'plan'" :rows="tasks" empty="No tasks yet. Tasks live on the exercise's ERPNext Project."
        :columns="[{ key: 'subject', label: 'Task' }, { key: 'status', label: 'Status', width: '9rem', badge: true }, { key: 'exp_end_date', label: 'Due', width: '9rem' }]" />
      <template v-else-if="tab === 'budget'">
        <StatStrip :items="[{ label: 'Planned budget', value: money(doc.budget) }, { label: 'Spent so far', value: money(doc.total_spent) }, { label: 'Left', value: money((doc.budget || 0) - (doc.total_spent || 0)) }]" />
        <p class="text-sm text-ink-gray-5">Spend is read from the ledger against the exercise's Project.</p>
      </template>
      <DataList v-else-if="tab === 'changes'" :rows="changes" empty="No change requests."
        :columns="[{ key: 'name', label: 'Request', width: '10rem' }, { key: 'reason', label: 'Reason' }, { key: 'workflow_state', label: 'State', width: '9rem', badge: true }]" />
      <template v-else-if="tab === 'email'">
        <p class="max-w-xl text-sm text-ink-gray-5">These are ERPNext Email Campaigns started from this exercise. ERPNext sends each one once a day on its start date, with one message for every recipient.</p>
        <DataList :rows="doc.email_campaigns || []" empty="No email campaigns yet." :columns="[{ key: 'email_campaign', label: 'Email Campaign' }, { key: 'activity', label: 'Activity', width: '12rem' }, { key: 'start_date', label: 'Starts', width: '9rem' }]" />
      </template>
    </div>
  </div>

  <RequestChangeDialog v-if="doc" v-model:open="showRequest" :campaign="doc" :approver="doc.brand_manager" @sent="changeList.reload?.()" />
  </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue"
import { Button, Skeleton, Tabs, useDoc, useList } from "frappe-ui"
import PaneHeader from "@/components/PaneHeader.vue"
import DataList from "@/components/DataList.vue"
import FieldRows from "@/components/FieldRows.vue"
import StatStrip from "@/components/StatStrip.vue"
import ErrorState from "./ErrorState.vue"
import RequestChangeDialog from "@/components/RequestChangeDialog.vue"
import { hasRole, ROLES } from "@/lib/session"

const props = defineProps({ name: String })
const tab = ref("plan")
const tabs = [
  { value: "plan", label: "Plan" },
  { value: "budget", label: "Budget" },
  { value: "changes", label: "Changes" },
  { value: "email", label: "Email", condition: () => hasRole(ROLES.manager, ROLES.head) },
]

const { doc: docRef, error } = useDoc({ doctype: "Marketing Campaign", name: props.name })
const doc = computed(() => docRef.value || docRef)
const showRequest = ref(false)
const canEditDirectly = hasRole(ROLES.manager)

const { data: taskData } = useList({
  doctype: "Task",
  fields: ["name", "subject", "status", "exp_end_date"],
  filters: () => ({ project: doc.value?.project || "-" }),
})
const tasks = computed(() => taskData.value || [])
const changeList = useList({
  doctype: "Campaign Change Request",
  fields: ["name", "reason", "workflow_state"],
  filters: { campaign: props.name },
})
const changes = computed(() => changeList.data.value || [])
const money = (v) => (v == null ? "—" : new Intl.NumberFormat(undefined, { style: "currency", currency: "NGN", maximumFractionDigits: 0 }).format(v))
</script>
