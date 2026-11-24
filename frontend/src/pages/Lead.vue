<template>
  <RecordPage :name="name" :title="doc?.lead_name" parent-label="Leads" :back="{ name: 'Leads' }" :state="state" error-title="You cannot open this lead">
    <template #badges><Badge v-if="doc?.status" :label="doc.status" :theme="badgeTheme(doc.status)" /></template>
    <FieldRows :rows="rows" />
    <template #aside>
      <AttachmentList doctype="Lead" :name="name" empty="No files attached." />
      <AsideSection title="Details"><FieldRows compact :rows="[['Last changed', doc?.modified], ['Created by', doc?.owner]]" /></AsideSection>
    </template>
  </RecordPage>
</template>

<script setup>
import { computed } from "vue"
import { Badge, useDoc } from "frappe-ui"
import RecordPage from "@/components/RecordPage.vue"
import AsideSection from "@/components/AsideSection.vue"
import AttachmentList from "@/components/AttachmentList.vue"
import FieldRows from "@/components/FieldRows.vue"
import { badgeTheme } from "@/lib/status"

const props = defineProps({ name: String })
const { doc: docRef, error: err } = useDoc({ doctype: "Lead", name: props.name })
const doc = computed(() => docRef.value || null)
const state = computed(() => (err?.value ? "error" : doc.value ? "ready" : "loading"))
const rows = computed(() => [
  ["Source", doc.value?.source],
  ["Email", doc.value?.email_id],
  ["Phone", doc.value?.mobile_no],
  ["Exercise", doc.value?.mkt_campaign],
  ["Captured", doc.value?.creation],
])
</script>
