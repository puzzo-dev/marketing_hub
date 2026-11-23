<template>
  <div class="flex min-h-0 flex-1 flex-col">
    <PaneHeader :title="doc?.content_item || name" :close="{ name: 'Placements' }">
      <template #actions>
        <Badge v-if="doc?.status" :label="doc.status" :theme="badgeTheme(doc.status)" />
        <template v-if="canDecide">
          <Button label="Reject" :loading="busy" @click="decide('Reject')" />
          <Button variant="solid" label="Approve" icon-left="lucide-check" :loading="busy" @click="decide('Approve')" />
        </template>
      </template>
    </PaneHeader>
    <div class="min-h-0 flex-1 overflow-y-auto">
      <div v-if="error" class="px-3 py-5 sm:px-5"><ErrorMessage :message="error" /></div>
      <div v-else-if="!doc" class="flex flex-col gap-3 px-3 py-4 sm:px-5" aria-busy="true"><Skeleton class="h-8 w-64" /><Skeleton class="h-24 w-full" /></div>
      <div v-else class="flex flex-col gap-6 px-3 pb-10 pt-5 sm:px-5">
        <FieldRows :rows="rows" />
        <p v-if="doc.approval_state === 'Pending'" class="text-sm text-ink-gray-6">Only the exercise's Brand Manager can approve. It sends after they do.</p>

      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue"
import { Badge, Button, ErrorMessage, Skeleton, toast, useCall, useDoc } from "frappe-ui"
import PaneHeader from "@/components/PaneHeader.vue"
import FieldRows from "@/components/FieldRows.vue"
import { badgeTheme } from "@/lib/status"
import { hasRole, ROLES, user } from "@/lib/session"

const props = defineProps({ name: String })
const { doc: docRef, error: err, reload } = useDoc({ doctype: "Placement", name: props.name })
const doc = computed(() => docRef.value || null)
const error = computed(() => err?.value?.message || "")
const rows = computed(() => [
  ["Exercise", doc.value.campaign],
  ["Channel", doc.value.channel],
  ["Scheduled for", doc.value.scheduled_for],
  ["Approval", doc.value.approval_state],
  ["Approver", doc.value.approver],
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
    reload?.()
  } catch (e) {
    toast.error(e?.message || "That did not go through.")
  } finally {
    busy.value = false
  }
}
</script>
