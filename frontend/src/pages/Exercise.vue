<template>
  <PageHeader>
    <Breadcrumbs :items="[{ label: 'Exercises', route: { name: 'Exercises' } }, { label: doc?.campaign_name || name }]" />
    <Button v-if="!canEditDirectly" label="Request a change" @click="showRequest = true" />
  </PageHeader>

  <ErrorState v-if="error" icon="lucide-lock" title="You do not have access to this" text="It belongs to another brand or exercise. Ask its Brand Manager to add you." action-label="Back to exercises" @action="$router.push({ name: 'Exercises' })" />

  <div v-else-if="doc" class="flex flex-col">
    <Tabs v-model="tab" :tabs="tabs" variant="underline" class="px-3 sm:px-5" />
    <div class="flex max-w-4xl flex-col gap-4 p-5">
      <template v-if="tab === 'plan'">
        <Row v-for="t in tasks" :key="t.name" :a="t.subject" :b="t.status" :c="t.exp_end_date" />
        <p v-if="!tasks.length" class="text-base text-ink-gray-6">No tasks yet. Tasks live on the exercise's ERPNext Project.</p>
      </template>
      <template v-else-if="tab === 'budget'">
        <Row a="Planned budget" :b="money(doc.budget)" />
        <Row a="Spent so far" :b="money(doc.total_spent)" />
        <p class="text-sm text-ink-gray-5">Spend is read from the ledger against the exercise's Project.</p>
      </template>
      <template v-else-if="tab === 'changes'">
        <Row v-for="c in changes" :key="c.name" :a="c.name" :b="c.reason" :c="c.workflow_state" />
        <p v-if="!changes.length" class="text-base text-ink-gray-6">No change requests.</p>
      </template>
      <template v-else-if="tab === 'email'">
        <p class="max-w-xl text-sm text-ink-gray-5">These are ERPNext Email Campaigns started from this exercise. ERPNext sends each one once a day on its start date, with one message for every recipient.</p>
        <Row v-for="e in doc.email_campaigns" :key="e.name" :a="e.email_campaign" :b="e.activity" :c="e.start_date" />
        <p v-if="!doc.email_campaigns?.length" class="text-base text-ink-gray-6">No email campaigns yet.</p>
      </template>
    </div>
  </div>

  <RequestChangeDialog v-if="doc" v-model:open="showRequest" :campaign="doc" :approver="doc.brand_manager" @sent="changeList.reload?.()" />
</template>

<script setup>
import { computed, h, ref } from "vue"
import { Breadcrumbs, Button, PageHeader, Tabs, useDoc, useList } from "frappe-ui"
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

// A three-cell row, kept here because only this page uses it.
const Row = (p) =>
  h("div", { class: "grid min-h-11 grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)_140px] items-center gap-3 border-b px-3 text-base" }, [
    h("span", { class: "truncate text-ink-gray-8" }, p.a),
    h("span", { class: "truncate text-ink-gray-6" }, p.b),
    h("span", { class: "truncate text-ink-gray-6" }, p.c),
  ])
Row.props = ["a", "b", "c"]
</script>
