<template>
  <div class="flex min-h-0 flex-1 flex-col">
  <AppHeader :title="doc?.campaign_name || name" :back="{ name: 'Exercises' }">
      <template #title><Breadcrumbs :items="[{ label: 'Exercises', route: { name: 'Exercises' } }, { label: doc?.campaign_name || name }]" /></template>
      <template #actions>
        <Button v-if="canEditDirectly" label="Edit" icon-left="lucide-pencil" :route="{ name: 'EditExercise', params: { name } }" />
        <Button v-else-if="canRequest" variant="solid" label="Request a change" @click="showRequest = true" />
        <Button v-else-if="isOOH" variant="solid" label="New booking" icon-left="lucide-plus" :route="{ name: 'NewOOHBooking' }" />
      </template>
    </AppHeader>
  <div class="min-h-0 flex-1 overflow-y-auto">

  <div v-if="!doc && !error" class="flex flex-col gap-3 px-3 py-4 sm:px-5" aria-busy="true"><Skeleton class="h-8 w-64" /><Skeleton class="h-40 w-full" /></div>

  <ErrorState v-else-if="error" icon="lucide-lock" title="You do not have access to this" text="It belongs to another brand or exercise. Ask its Brand Manager to add you." action-label="Back to exercises" @action="$router.push({ name: 'Exercises' })" />

  <div v-else-if="doc" class="flex flex-col">
    <Tabs v-model="tab" :tabs="tabs" variant="underline" class="px-3 sm:px-5" />
    <div class="flex flex-col gap-6 px-3 pb-10 pt-5 sm:px-5">
      <template v-if="tab === 'overview'">
        <FieldRows :rows="[['Brand', doc.brand], ['Brand Manager', doc.brand_manager], ['Dates', `${doc.start_date} to ${doc.end_date}`], ['Status', doc.status], ['Objective', doc.objective]]" />
        <StatStrip :items="[{ label: 'Tasks done', value: taskCount('Completed') }, { label: 'In progress', value: taskCount('Working') + taskCount('Open') }, { label: 'Tasks in all', value: tasks.length }]" />
      </template>
      <DataList v-else-if="tab === 'content'" :loading="contentList.isFetching?.value" :rows="content" empty="No content for this exercise yet." :route="(r) => ({ name: 'ContentDetail', params: { name: r.name } })"
        :columns="[{ key: 'title', label: 'Title' }, { key: 'type', label: 'Type', width: '8rem' }, { key: 'due_date', label: 'Due', width: '9rem' }, { key: 'status', label: 'Status', width: '9rem', badge: true }]" />
      <DataList v-else-if="tab === 'placements'" :loading="placementList.isFetching?.value" :rows="placements" empty="No placements for this exercise yet." :route="(r) => ({ name: 'Placement', params: { name: r.name } })"
        :columns="[{ key: 'content_item', label: 'Content' }, { key: 'channel', label: 'Channel', width: '9rem' }, { key: 'scheduled_for', label: 'Send time', width: '11rem' }, { key: 'approval_state', label: 'Approval', width: '9rem', badge: true }, { key: 'status', label: 'Status', width: '8rem', badge: true }]" />
      <DataList v-else-if="tab === 'ooh'" :loading="bookingList.isFetching?.value" :rows="bookings" empty="No billboards booked for this exercise yet." :route="(r) => ({ name: 'OOHBooking', params: { name: r.name } })"
        :columns="[{ key: 'site', label: 'Site' }, { key: 'start_date', label: 'Starts', width: '9rem' }, { key: 'end_date', label: 'Ends', width: '9rem' }, { key: 'status', label: 'Status', width: '9rem', badge: true }]" />
      <DataList v-else-if="tab === 'plan'" :loading="tasksLoading" :rows="tasks" empty="No tasks yet. Tasks live on the exercise's ERPNext Project."
        :columns="[{ key: 'subject', label: 'Task' }, { key: 'status', label: 'Status', width: '9rem', badge: true }, { key: 'exp_end_date', label: 'Due', width: '9rem' }]" />
      <template v-else-if="tab === 'budget'">
        <StatStrip :items="[{ label: 'Planned budget', value: money(doc.budget) }, { label: 'Spent so far', value: money(doc.total_spent) }, { label: 'Left', value: money((doc.budget || 0) - (doc.total_spent || 0)) }]" />
        <p class="text-sm text-ink-gray-6">Spend is read from the ledger against the exercise's Project.</p>
      </template>
      <DataList v-else-if="tab === 'changes'" :loading="changesLoading" :rows="changes" empty="No change requests."
        :columns="[{ key: 'name', label: 'Request', width: '10rem' }, { key: 'reason', label: 'Reason' }, { key: 'workflow_state', label: 'State', width: '9rem', badge: true }]" />
      <template v-else-if="tab === 'email'">
        <p class="max-w-xl text-sm text-ink-gray-6">These are ERPNext Email Campaigns started from this exercise. ERPNext sends each one once a day on its start date, with one message for every recipient.</p>
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
import { Breadcrumbs, Button, Skeleton, Tabs, useDoc, useList } from "frappe-ui"
import AppHeader from "@/components/AppHeader.vue"
import DataList from "@/components/DataList.vue"
import FieldRows from "@/components/FieldRows.vue"
import StatStrip from "@/components/StatStrip.vue"
import ErrorState from "./ErrorState.vue"
import RequestChangeDialog from "@/components/RequestChangeDialog.vue"
import { hasRole, primaryRole, ROLES } from "@/lib/session"

const props = defineProps({ name: String })
// Each role sees the tabs it works with, and nothing else.
const TABS = {
  overview: "Overview", plan: "Plan", content: "Content", placements: "Placements", ooh: "Out of home", email: "Email", changes: "Changes", budget: "Budget",
}
const BY_ROLE = {
  [ROLES.manager]: ["overview", "plan", "content", "placements", "ooh", "email", "changes", "budget"],
  [ROLES.head]: ["overview", "budget", "changes"],
  [ROLES.planner]: ["overview", "plan", "content"],
  [ROLES.contentLead]: ["overview", "plan", "content"],
  [ROLES.publisher]: ["overview", "plan", "content"],
  [ROLES.ooh]: ["overview", "ooh"],
}
const tabs = (BY_ROLE[primaryRole.value] || ["overview"]).map((value) => ({ value, label: TABS[value] }))
const tab = ref("overview")
const isOOH = primaryRole.value === ROLES.ooh
const canRequest = [ROLES.planner, ROLES.contentLead, ROLES.publisher].includes(primaryRole.value)

const { doc: docRef, error } = useDoc({ doctype: "Marketing Campaign", name: props.name })
const doc = computed(() => docRef.value || docRef)
const showRequest = ref(false)
const canEditDirectly = hasRole(ROLES.manager)

const { data: taskData, isFetching: tasksLoading } = useList({
  doctype: "Task",
  fields: ["name", "subject", "status", "exp_end_date"],
  filters: () => ({ project: doc.value?.project || "-" }),
})
const tasks = computed(() => taskData.value || [])
const taskCount = (status) => tasks.value.filter((t) => t.status === status).length
const forExercise = () => ({ campaign: props.name })
const contentList = useList({ doctype: "Content Item", fields: ["name", "title", "type", "due_date", "status"], filters: forExercise, orderBy: "due_date asc" })
const content = computed(() => contentList.data.value || [])
const placementList = useList({ doctype: "Placement", fields: ["name", "content_item", "channel", "scheduled_for", "approval_state", "status"], filters: forExercise, orderBy: "scheduled_for asc" })
const placements = computed(() => placementList.data.value || [])
const bookingList = useList({ doctype: "OOH Booking", fields: ["name", "site", "start_date", "end_date", "status"], filters: forExercise, orderBy: "start_date asc" })
const bookings = computed(() => bookingList.data.value || [])
const changeList = useList({
  doctype: "Campaign Change Request",
  fields: ["name", "reason", "workflow_state"],
  filters: { campaign: props.name },
})
const changes = computed(() => changeList.data.value || [])
const changesLoading = computed(() => !!changeList.isFetching?.value)
const money = (v) => (v == null ? "—" : new Intl.NumberFormat(undefined, { style: "currency", currency: "NGN", maximumFractionDigits: 0 }).format(v))
</script>
