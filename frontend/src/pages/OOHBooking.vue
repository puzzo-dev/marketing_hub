<template>
  <RecordPage :name="name" :title="doc?.site" parent-label="Out of home" :back="{ name: 'OutOfHome' }" :state="state"
    error-title="You cannot open this booking" error-text="It belongs to another exercise, or it has been removed.">
    <template v-if="next && canAdvance" #actions>
      <Button variant="solid" :label="next === 'Approved' ? 'Approve' : `Move to ${next}`" :icon-left="next === 'Approved' ? 'lucide-check' : undefined" :loading="busy" @click="advance" />
    </template>
    <template #badges><Badge v-if="doc?.status" :label="doc.status" :theme="badgeTheme(doc.status)" /></template>
    <ol class="flex flex-wrap gap-2" aria-label="Progress">
      <li v-for="s in STEPS" :key="s" class="flex h-7 items-center rounded-4 px-2 text-sm" :class="STEPS.indexOf(s) <= STEPS.indexOf(doc?.status) ? 'bg-surface-gray-7 text-ink-white' : 'bg-surface-gray-2 text-ink-gray-6'">{{ s }}</li>
    </ol>
    <FieldRows :rows="rows" />
    <router-link v-if="doc?.purchase_order" :to="{ name: 'PurchaseOrder', params: { name: doc.purchase_order } }" class="text-base text-ink-gray-8 underline">Purchase order {{ doc.purchase_order }}</router-link>
    <ErrorMessage :message="error" />
    <template #aside>
      <AttachmentList doctype="OOH Booking" :name="name" title="Proof photos" empty="No proof photos yet." />
      <AsideSection title="Details"><FieldRows compact :rows="[['Created', doc?.creation], ['Last changed', doc?.modified], ['Created by', doc?.owner]]" /></AsideSection>
    </template>
  </RecordPage>
</template>

<script setup>
import { computed, ref } from "vue"
import { Badge, Button, ErrorMessage, useCall, useDoc } from "frappe-ui"
import RecordPage from "@/components/RecordPage.vue"
import AsideSection from "@/components/AsideSection.vue"
import AttachmentList from "@/components/AttachmentList.vue"
import FieldRows from "@/components/FieldRows.vue"
import { badgeTheme } from "@/lib/status"
import { isAdmin, user } from "@/lib/session"

const STEPS = ["Proposed", "Approved", "Production", "Live", "Ended"]
const props = defineProps({ name: String })
const { doc: docRef, reload, error: loadErr } = useDoc({ doctype: "OOH Booking", name: props.name })
const doc = computed(() => docRef.value || null)
const state = computed(() => (loadErr?.value ? "error" : doc.value ? "ready" : "loading"))
const next = computed(() => STEPS[STEPS.indexOf(doc.value?.status) + 1])
const rows = computed(() => [["Exercise", doc.value?.campaign], ["Dates", `${doc.value?.start_date} to ${doc.value?.end_date}`], ["Agreed rate", doc.value?.agreed_rate], ["Approved by", doc.value?.approver]])
// Approving is the exercise's Brand Manager only; the coordinator moves every later step.
const canAdvance = computed(() => next.value !== "Approved" || doc.value?.approver === user.value.id || isAdmin())
const busy = ref(false)
const error = ref("")
const run = useCall({ url: "/api/method/run_doc_method", method: "POST", immediate: false })
async function advance() {
  busy.value = true
  error.value = ""
  try {
    await run.submit({ docs: JSON.stringify(doc.value), method: "advance" })
    await reload?.()
  } catch (e) {
    error.value = e?.message || "That step did not go through."
  } finally {
    busy.value = false
  }
}
</script>
