<template>
  <AppHeader :title="doc?.title || name" :back="{ name: 'Content' }">
    <template #title><Breadcrumbs :items="[{ label: 'Content', route: { name: 'Content' } }, { label: doc?.title || name }]" /></template>
    <template #actions>
      <Button v-if="canApprove && doc?.status !== 'Approved'" label="Approve latest version" @click="approve" :loading="busy" />
      <Button variant="solid" label="Schedule" @click="showSchedule = true" />
    </template>
  </AppHeader>

  <div v-if="!doc && !error" class="flex flex-col gap-3 p-5" aria-busy="true"><Skeleton class="h-8 w-64" /><Skeleton class="h-40 w-full" /></div>
  <ErrorState v-else-if="error" icon="lucide-lock" title="You do not have access to this" text="It belongs to another exercise." action-label="Back to content" @action="$router.push({ name: 'Content' })" />
  <div v-else-if="doc" class="flex max-w-3xl flex-col gap-6 p-5">
    <div class="flex items-center gap-2"><h2 class="text-xl-semibold text-ink-gray-9">{{ doc.title }}</h2><Badge :label="doc.status" :theme="badgeTheme(doc.status)" /></div>
    <div class="flex flex-col">
      <div v-for="v in [...(doc.versions || [])].reverse()" :key="v.name" class="flex flex-col gap-1 border-b py-3">
        <div class="flex items-center gap-2 text-sm text-ink-gray-6"><span>Version {{ v.version_no }}</span><Badge v-if="v.approved_on" label="Approved" theme="green" /></div>
        <p class="whitespace-pre-wrap text-base text-ink-gray-8">{{ v.body }}</p>
      </div>
      <p v-if="!doc.versions?.length" class="text-base text-ink-gray-6">No version yet.</p>
    </div>
    <SchedulePlacementDialog v-model:open="showSchedule" :content="doc" />
  </div>
</template>

<script setup>
import { computed, ref } from "vue"
import { Badge, Breadcrumbs, Button, Skeleton, toast, useCall, useDoc } from "frappe-ui"
import AppHeader from "@/components/AppHeader.vue"
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
