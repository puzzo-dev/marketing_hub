<template>
  <div class="flex min-h-0 flex-1 flex-col">
  <PaneHeader :title="doc?.title || name" :close="{ name: 'Content' }">
      <template #actions>
      <Button v-if="canApprove && doc?.status !== 'Approved'" label="Approve latest version" @click="approve" :loading="busy" />
      <Button variant="solid" label="Schedule" @click="showSchedule = true" />
    </template>
    </PaneHeader>
  <div class="min-h-0 flex-1 overflow-y-auto">

  <div v-if="!doc && !error" class="flex flex-col gap-3 px-3 py-4 sm:px-5" aria-busy="true"><Skeleton class="h-8 w-64" /><Skeleton class="h-40 w-full" /></div>
  <ErrorState v-else-if="error" icon="lucide-lock" title="You do not have access to this" text="It belongs to another exercise." action-label="Back to content" @action="$router.push({ name: 'Content' })" />
  <div v-else-if="doc" class="flex flex-col gap-6 px-3 pb-10 pt-5 sm:px-5">
    <div class="flex items-center gap-2"><Badge :label="doc.status" :theme="badgeTheme(doc.status)" /></div>
    <FieldRows :rows="[['Exercise', doc.campaign], ['Type', doc.type], ['Due', doc.due_date]]" />
    <section class="flex flex-col gap-2">
      <div class="flex h-7 items-center"><h3 class="text-sm font-semibold text-ink-gray-8">Versions</h3></div>
      <div v-for="v in [...(doc.versions || [])].reverse()" :key="v.name" class="flex flex-col gap-1.5 border-b py-3">
        <div class="flex items-center gap-2 text-sm text-ink-gray-5"><span>Version {{ v.version_no }}</span><Badge v-if="v.approved_on" label="Approved" theme="green" /></div>
        <p class="whitespace-pre-wrap text-base text-ink-gray-8">{{ v.body }}</p>
      </div>
      <p v-if="!doc.versions?.length" class="text-base text-ink-gray-6">No version yet.</p>
    </section>
    <SchedulePlacementDialog v-model:open="showSchedule" :content="doc" />
  </div>
  </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue"
import { Badge, Button, Skeleton, toast, useCall, useDoc } from "frappe-ui"
import PaneHeader from "@/components/PaneHeader.vue"
import FieldRows from "@/components/FieldRows.vue"
import ErrorState from "./ErrorState.vue"
import SchedulePlacementDialog from "@/components/SchedulePlacementDialog.vue"
import { badgeTheme } from "@/lib/status"
import { hasRole, ROLES } from "@/lib/session"

const props = defineProps({ name: String })
const { doc: docRef, error } = useDoc({ doctype: "Content Item", name: props.name })
const doc = computed(() => docRef.value || docRef)
const showSchedule = ref(false)
const busy = ref(false)
const canApprove = hasRole(ROLES.manager)

const run = useCall({ url: "/api/method/run_doc_method", method: "POST", immediate: false })
async function approve() {
  busy.value = true
  try {
    await run.submit({ docs: JSON.stringify(doc.value), method: "approve_latest" })
    toast.success("Approved")
    location.reload()
  } catch (e) {
    toast.error(e?.message || "Only the exercise's Brand Manager can approve.")
  } finally {
    busy.value = false
  }
}
</script>
