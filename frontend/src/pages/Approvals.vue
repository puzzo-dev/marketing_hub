<template>
  <div class="flex min-h-0 flex-1">
    <section v-if="!(isMobile && selected)" aria-label="Waiting for you" class="flex min-h-0 flex-col" :class="selected && !isMobile ? 'w-[400px] shrink-0 border-e' : 'min-w-0 flex-1'">
      <PaneHeader title="Approvals">
        <template #title><PageHeaderTitle title="Approvals" /><Badge v-if="rows.length" :label="`${rows.length} waiting`" theme="amber" /></template>
      </PaneHeader>
      <div class="min-h-0 flex-1 overflow-y-auto">
        <div v-if="isFetching && !rows.length" class="flex flex-col gap-2 px-3 py-3 sm:px-5" aria-busy="true"><Skeleton v-for="n in 5" :key="n" class="h-[60px] w-full" /></div>
        <ErrorState v-else-if="queueError" icon="lucide-triangle-alert" title="Something went wrong on our side" text="Nothing was lost. Try again." action-label="Try again" @action="queue.reload?.()" />
        <ErrorState v-else-if="!rows.length" icon="lucide-circle-check" title="Nothing is waiting for you" text="Requests for your exercises appear here as they come in." />
        <List v-else class="list-row-px-3 px-3 pb-10 pt-3 sm:px-5" :row-height="rowHeight(true)" :active="selected?.name">
          <ListRows :items="rows" row-key="name" v-slot="{ item, value }">
            <ListRow :value="value" @click="selected = item">
              <ListCell><Avatar :label="item.reference_doctype" size="md" /></ListCell>
              <ListCell>
                <div class="min-w-0">
                  <div class="truncate text-base text-ink-gray-8">{{ item.reference_name }}</div>
                  <div class="mt-1.5 truncate text-sm text-ink-gray-5">{{ item.reference_doctype }}</div>
                </div>
              </ListCell>
              <ListCell class="justify-end"><span class="text-sm text-ink-gray-5">{{ ago(item.creation) }}</span></ListCell>
            </ListRow>
          </ListRows>
        </List>
      </div>
    </section>

    <section v-if="selected" aria-label="Request detail" class="flex min-h-0 min-w-0 flex-1 flex-col">
      <PaneHeader :title="selected.reference_doctype">
        <template #actions><Button variant="ghost" icon="lucide-x" aria-label="Close" @click="selected = null" /></template>
      </PaneHeader>
      <div class="min-h-0 flex-1 overflow-y-auto px-3 py-4 sm:px-5">
      <div v-if="selected && !doc && !docError" class="flex flex-col gap-3" aria-busy="true"><Skeleton class="h-6 w-1/2" /><Skeleton class="h-32 w-full" /></div>
      <ErrorState v-else-if="selected && docError" icon="lucide-lock" title="You cannot open this request" text="It may belong to another exercise." />
      <div v-else-if="selected && doc" class="flex flex-col gap-6">
        <div class="flex flex-col gap-2">
          <div class="flex items-center gap-2 text-sm text-ink-gray-6">
            <Badge :label="selected.reference_doctype" /><span>{{ selected.reference_name }}</span>
          </div>
          <h2 class="text-xl-semibold text-ink-gray-9">{{ doc.reason || doc.name }}</h2>
        </div>

        <div v-if="summary.length" class="flex flex-col">
          <div v-for="[k, v] in summary" :key="k" class="flex min-h-9 items-center gap-4"><span class="w-32 shrink-0 text-sm text-ink-gray-6">{{ k }}</span><span class="min-w-0 flex-1 text-base text-ink-gray-8">{{ v }}</span></div>
        </div>

        <div v-if="doc.items?.length" class="flex flex-col gap-2">
          <h3 class="text-lg-medium text-ink-gray-9">What changes</h3>
          <div class="grid h-8 grid-cols-[9rem_minmax(0,1fr)_minmax(0,1fr)] items-center gap-3 rounded-4 bg-surface-gray-2 px-3 text-sm text-ink-gray-6"><span>Field</span><span>Now</span><span>Requested</span></div>
          <div v-for="r in doc.items" :key="r.name" class="grid min-h-10 grid-cols-[9rem_minmax(0,1fr)_minmax(0,1fr)] items-center gap-3 border-b px-3">
            <span class="text-ink-gray-6">{{ r.fieldname }}</span><span class="text-ink-gray-6">{{ r.old_value }}</span><span class="text-ink-gray-8">{{ r.new_value }}</span>
          </div>
        </div>

        <ErrorMessage v-if="actionError" :message="actionError" />
        <div class="flex items-center gap-2">
          <Button variant="solid" label="Approve and apply" :loading="acting" @click="act('Approve')" />
          <Button label="Reject" :disabled="acting" @click="act('Reject')" />
        </div>
      </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, ref, watch } from "vue"
import { Avatar, Badge, Button, ErrorMessage, PageHeaderTitle, Skeleton, toast, useCall, useList } from "frappe-ui"
import { List, ListCell, ListRow, ListRows } from "frappe-ui/list"
import { rowHeight } from "@/lib/tweaks"
import PaneHeader from "@/components/PaneHeader.vue"
import { isMobile } from "@/lib/viewport"
import ErrorState from "./ErrorState.vue"

// The queue is Frappe's own Workflow Action list. Frappe sends an action only to
// users who hold the transition's role and can read the document, which is how a
// request reaches just the exercise's assigned Brand Manager.
const ago = (t) => {
  const m = Math.max(0, Math.round((Date.now() - new Date(t.replace(" ", "T")).getTime()) / 60000))
  return m < 60 ? `${m} m` : m < 1440 ? `${Math.round(m / 60)} h` : `${Math.round(m / 1440)} d`
}
const queue = useList({
  doctype: "Workflow Action",
  fields: ["name", "reference_doctype", "reference_name", "creation"],
  filters: { status: "Open" },
  orderBy: "creation desc",
  limit: 100,
})
const { data, isFetching, error: queueError } = queue
const rows = computed(() => data.value || [])
const selected = ref(null)
const doc = ref(null)
const acting = ref(false)
const actionError = ref("")

const docError = ref(false)
// The few fields that say what a request is about, whichever kind of document it is.
const SUMMARY = [["campaign", "Exercise"], ["content_item", "Content"], ["channel", "Channel"], ["scheduled_for", "Scheduled for"], ["booking", "Booking"], ["target_name", "Changes"], ["owner", "Requested by"]]
const summary = computed(() => SUMMARY.filter(([f]) => doc.value?.[f]).map(([f, label]) => [label, doc.value[f]]))
const getDoc = useCall({ url: "/api/method/frappe.client.get", method: "GET", immediate: false })
watch(selected, async (row) => {
  doc.value = null
  actionError.value = ""
  if (!row) return
  docError.value = false
  try {
    const res = await getDoc.submit({ doctype: row.reference_doctype, name: row.reference_name })
    doc.value = res?.message || res
  } catch {
    docError.value = true
  }
})

const apply = useCall({ url: "/api/method/frappe.model.workflow.apply_workflow", method: "POST", immediate: false })
async function act(action) {
  acting.value = true
  actionError.value = ""
  try {
    // The workflow's transition names are "Approve" and "Reject".
    await apply.submit({ doc: JSON.stringify(doc.value), action })
    toast.success(action === "Approve" ? "Approved and applied" : "Rejected")
    selected.value = null
    queue.reload?.()
  } catch (e) {
    actionError.value = e?.message || "That did not go through."
  } finally {
    acting.value = false
  }
}
</script>
