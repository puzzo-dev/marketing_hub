<template>
  <AppHeader title="New content" :back="{ name: 'Content' }"><template #title><Breadcrumbs :items="[{ label: 'Content', route: { name: 'Content' } }, { label: 'New content' }]" /></template></AppHeader>
  <form class="flex max-w-xl flex-col gap-4 px-3 py-4 sm:px-5" @submit.prevent="save">
    <FormControl label="Title" v-model="form.title" required />
    <LinkSelect label="Exercise" doctype="Marketing Campaign" label-field="campaign_name" v-model="form.campaign" />
    <div class="grid grid-cols-2 gap-4">
      <FormControl label="Type" type="select" v-model="form.type" :options="['Post', 'Story', 'Video', 'Banner', 'Broadcast', 'Other']" />
      <FormControl label="Due" type="date" v-model="form.due_date" />
    </div>
    <FormControl label="Brief" type="textarea" v-model="brief" :rows="4" />
    <p class="text-sm text-ink-gray-6">It starts as a draft. Send it for approval when it is ready; only the exercise's Brand Manager approves.</p>
    <ErrorMessage :message="error" />
    <div class="flex items-center gap-2">
      <Button type="submit" variant="solid" label="Create content" :loading="saving" />
      <Button label="Cancel" @click="$router.back()" />
    </div>
  </form>
</template>

<script setup>
import { reactive, ref } from "vue"
import { useRouter } from "vue-router"
import { Breadcrumbs, Button, ErrorMessage, FormControl, toast, useCall } from "frappe-ui"
import AppHeader from "@/components/AppHeader.vue"
import LinkSelect from "@/components/LinkSelect.vue"

const router = useRouter()
const form = reactive({ title: "", campaign: null, type: "Post", due_date: null })
const brief = ref("")
const saving = ref(false)
const error = ref("")
const getValue = useCall({ url: "/api/method/frappe.client.get_value", method: "GET", immediate: false })
const insert = useCall({ url: "/api/method/frappe.client.insert", method: "POST", immediate: false })

async function save() {
  error.value = ""
  if (!form.title || !form.campaign) return (error.value = "Give the content a title and pick its exercise.")
  saving.value = true
  try {
    const res = await getValue.submit({ doctype: "Marketing Campaign", filters: JSON.stringify({ name: form.campaign }), fieldname: "brand" })
    const brand = (res?.message || res)?.brand
    const doc = { doctype: "Content Item", ...form, brand, status: "Draft" }
    if (brief.value) doc.versions = [{ version_no: 1, body: brief.value }]
    const out = await insert.submit({ doc: JSON.stringify(doc) })
    toast.success("Content created")
    router.replace({ name: "ContentDetail", params: { name: (out?.message || out).name } })
  } catch (e) {
    error.value = e?.message || "The content could not be created."
  } finally {
    saving.value = false
  }
}
</script>
