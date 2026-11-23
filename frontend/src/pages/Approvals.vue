<template>
  <PageHeader>
    <div class="flex items-center gap-2">
      <PageHeaderTitle title="Approvals" />
      <Badge v-if="rows.length" :label="`${rows.length} waiting`" theme="amber" />
    </div>
  </PageHeader>

  <div class="flex min-h-0 flex-1">
    <section aria-label="Waiting for you" class="flex w-[352px] shrink-0 flex-col overflow-y-auto border-e">
      <button v-for="row in rows" :key="row.name" type="button" class="flex h-[60px] items-center gap-3 border-b px-5 text-start hover:bg-surface-gray-1" :class="row.name === selected?.name && 'bg-surface-gray-2'" @click="selected = row">
        <Avatar :label="row.reference_doctype" size="sm" />
        <span class="flex min-w-0 flex-1 flex-col gap-1.5">
          <span class="truncate text-base text-ink-gray-8">{{ row.reference_name }}</span>
          <span class="truncate text-sm text-ink-gray-6">{{ row.reference_doctype }}</span>
        </span>
      </button>
      <ErrorState v-if="!isFetching && !rows.length" icon="lucide-circle-check" title="Nothing is waiting for you" text="Requests for your exercises appear here." />
    </section>

    <section aria-label="Request detail" class="min-w-0 flex-1 overflow-y-auto px-10 pb-20 pt-5">
      <div v-if="selected && doc" class="flex max-w-[700px] flex-col gap-6">
        <div class="flex flex-col gap-2">
          <div class="flex items-center gap-2 text-sm text-ink-gray-6">
            <Badge :label="selected.reference_doctype" /><span>{{ selected.reference_name }}</span>
          </div>
          <h2 class="text-xl-semibold text-ink-gray-9">{{ doc.reason || doc.name }}</h2>
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
      <ErrorState v-else-if="rows.length" icon="lucide-mouse-pointer-click" title="Pick a request" text="Choose one from the list to see what it changes." />
    </section>
  </div>
</template>

<script setup>
import { computed, ref, watch } from "vue"
import { Avatar, Badge, Button, ErrorMessage, PageHeader, PageHeaderTitle, toast, useCall, useList } from "frappe-ui"
import ErrorState from "./ErrorState.vue"

// The queue is Frappe's own Workflow Action list. Frappe sends an action only to
// users who hold the transition's role and can read the document, which is how a
// request reaches just the exercise's assigned Brand Manager.
const queue = useList({
  doctype: "Workflow Action",
  fields: ["name", "reference_doctype", "reference_name", "creation"],
  filters: { status: "Open" },
  orderBy: "creation desc",
  limit: 100,
})
const { data, isFetching } = queue
const rows = computed(() => data.value || [])
const selected = ref(null)
const doc = ref(null)
const acting = ref(false)
const actionError = ref("")

const getDoc = useCall({ url: "/api/method/frappe.client.get", method: "GET", immediate: false })
watch(selected, async (row) => {
  doc.value = null
  actionError.value = ""
  if (!row) return
  const res = await getDoc.submit({ doctype: row.reference_doctype, name: row.reference_name })
  doc.value = res?.message || res
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
