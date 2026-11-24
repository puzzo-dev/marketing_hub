<template>
  <RecordPage :name="name" :title="doc?.content_item" parent-label="Placements" :back="{ name: 'Placements' }" :state="state"
    error-title="You cannot open this placement">
    <template #actions>
      <template v-if="canDecide">
        <Button label="Reject" :loading="busy" @click="decide('Reject')" />
        <Button variant="solid" label="Approve" icon-left="lucide-check" :loading="busy" @click="decide('Approve')" />
      </template>
    </template>
    <template #badges>
      <Badge v-if="doc?.status" :label="doc.status" :theme="badgeTheme(doc.status)" />
      <Badge v-if="doc?.approval_state" :label="doc.approval_state" :theme="badgeTheme(doc.approval_state)" />
    </template>
    <FieldRows :rows="rows" />
    <p v-if="doc?.approval_state === 'Pending'" class="text-sm text-ink-gray-6">Only the exercise's Brand Manager can approve. It sends after they do.</p>
    <template #aside>
      <AttachmentList doctype="Content Item" :name="doc?.content_item" title="Content assets" empty="No assets on this content." />
      <AsideSection title="Details"><FieldRows compact :rows="[['Created', doc?.creation], ['Last changed', doc?.modified], ['Created by', doc?.owner]]" /></AsideSection>
    </template>
  </RecordPage>
</template>

<script setup>
import { computed, ref } from "vue"
import { Badge, Button, toast, useCall, useDoc } from "frappe-ui"
import RecordPage from "@/components/RecordPage.vue"
import AsideSection from "@/components/AsideSection.vue"
import AttachmentList from "@/components/AttachmentList.vue"
import FieldRows from "@/components/FieldRows.vue"
import { badgeTheme } from "@/lib/status"
import { hasRole, ROLES, user } from "@/lib/session"

const props = defineProps({ name: String })
const { doc: docRef, error: err, reload } = useDoc({ doctype: "Placement", name: props.name })
const doc = computed(() => docRef.value || null)
const state = computed(() => (err?.value ? "error" : doc.value ? "ready" : "loading"))
const rows = computed(() => [
  ["Exercise", doc.value?.campaign],
  ["Channel", doc.value?.channel],
  ["Scheduled for", doc.value?.scheduled_for],
  ["Approval", doc.value?.approval_state],
  ["Approver", doc.value?.approver],
])

// The assigned Brand Manager decides; a Marketing Head can cover when they are away.
const canDecide = computed(() => doc.value?.approval_state === "Pending" && (doc.value.approver === user.value.id || hasRole(ROLES.head)))
const busy = ref(false)
const apply = useCall({ url: "/api/method/frappe.model.workflow.apply_workflow", method: "POST", immediate: false })
async function decide(action) {
  busy.value = true
  try {
    await apply.submit({ doc: JSON.stringify(doc.value), action })
    toast.success(action === "Approve" ? "Approved" : "Rejected")
    await reload?.()
  } catch (e) {
    toast.error(e?.message || "That did not go through.")
  } finally {
    busy.value = false
  }
}
</script>
