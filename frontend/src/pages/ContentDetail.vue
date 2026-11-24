<template>
  <RecordPage :name="name" :title="doc?.title" parent-label="Content" :back="{ name: 'Content' }" :state="state"
    error-title="You do not have access to this" error-text="It belongs to another exercise.">
    <template #actions>
      <Button v-if="canApprove && doc?.status !== 'Approved'" label="Approve latest version" @click="approve" :loading="busy" />
      <Button v-if="canSend && doc?.status === 'Draft'" variant="solid" label="Send for approval" :loading="busy" @click="sendForApproval" />
      <Button v-if="canSchedule && doc?.status === 'Approved'" variant="solid" label="Schedule placement" @click="showSchedule = true" />
    </template>
    <template #badges><Badge v-if="doc?.status" :label="doc.status" :theme="badgeTheme(doc.status)" /></template>
    <FieldRows :rows="[['Exercise', doc?.campaign], ['Type', doc?.type], ['Due', doc?.due_date]]" />
    <section class="flex flex-col gap-2">
      <div class="flex h-7 items-center"><h2 class="text-sm font-semibold text-ink-gray-8">Versions</h2></div>
      <div v-for="v in [...(doc?.versions || [])].reverse()" :key="v.name" class="flex flex-col gap-1.5 border-b py-3">
        <div class="flex items-center gap-2 text-sm text-ink-gray-6"><span>Version {{ v.version_no }}</span><Badge v-if="v.approved_on" label="Approved" theme="green" /></div>
        <p class="whitespace-pre-wrap text-base text-ink-gray-8">{{ v.body }}</p>
      </div>
      <p v-if="!doc?.versions?.length" class="text-base text-ink-gray-6">No version yet.</p>
    </section>
    <template #aside>
      <AttachmentList doctype="Content Item" :name="name" title="Assets" empty="No images or files attached yet." />
      <AsideSection title="Details"><FieldRows compact :rows="[['Created', doc?.creation], ['Last changed', doc?.modified], ['Created by', doc?.owner]]" /></AsideSection>
    </template>
    <SchedulePlacementDialog v-if="doc" v-model:open="showSchedule" :content="doc" />
  </RecordPage>
</template>

<script setup>
import { computed, ref } from "vue"
import { Badge, Button, toast, useCall, useDoc } from "frappe-ui"
import RecordPage from "@/components/RecordPage.vue"
import AsideSection from "@/components/AsideSection.vue"
import AttachmentList from "@/components/AttachmentList.vue"
import FieldRows from "@/components/FieldRows.vue"
import SchedulePlacementDialog from "@/components/SchedulePlacementDialog.vue"
import { badgeTheme } from "@/lib/status"
import { hasRole, ROLES } from "@/lib/session"

const props = defineProps({ name: String })
const { doc: docRef, error, reload } = useDoc({ doctype: "Content Item", name: props.name })
const doc = computed(() => docRef.value || null)
const state = computed(() => (error?.value ? "error" : doc.value ? "ready" : "loading"))
const showSchedule = ref(false)
const busy = ref(false)
const canApprove = hasRole(ROLES.manager)
// Only approved content can be scheduled; the publisher and the Brand Manager do it.
const canSchedule = hasRole(ROLES.manager, ROLES.publisher)

const canSend = hasRole(ROLES.planner, ROLES.contentLead)
const setValue = useCall({ url: "/api/method/frappe.client.set_value", method: "POST", immediate: false })
async function sendForApproval() {
  busy.value = true
  try {
    await setValue.submit({ doctype: "Content Item", name: props.name, fieldname: "status", value: "In review" })
    toast.success("Sent for approval")
    await reload?.()
  } catch (e) {
    toast.error(e?.message || "That did not go through.")
  } finally {
    busy.value = false
  }
}

const run = useCall({ url: "/api/method/run_doc_method", method: "POST", immediate: false })
async function approve() {
  busy.value = true
  try {
    await run.submit({ docs: JSON.stringify(doc.value), method: "approve_latest" })
    toast.success("Approved")
    await reload?.()
  } catch (e) {
    toast.error(e?.message || "Only the exercise's Brand Manager can approve.")
  } finally {
    busy.value = false
  }
}
</script>
