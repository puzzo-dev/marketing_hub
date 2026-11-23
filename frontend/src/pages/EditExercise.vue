<template>
  <AppHeader title="Edit exercise" :back="{ name: 'Exercise', params: { name } }"><template #title><Breadcrumbs :items="[{ label: 'Exercises', route: { name: 'Exercises' } }, { label: form.campaign_name || name, route: { name: 'Exercise', params: { name } } }, { label: 'Edit' }]" /></template></AppHeader>
  <div v-if="!loaded" class="flex flex-col gap-3 px-3 py-4 sm:px-5" aria-busy="true"><Skeleton class="h-8 w-64" /><Skeleton class="h-40 w-full" /></div>
  <form v-else class="flex max-w-xl flex-col gap-4 px-3 py-4 sm:px-5" @submit.prevent="save">
    <FormControl label="Exercise name" v-model="form.campaign_name" required />
    <FormControl label="Objective" type="textarea" v-model="form.objective" :rows="3" />
    <div class="grid grid-cols-2 gap-4">
      <FormControl label="Starts" type="date" v-model="form.start_date" />
      <FormControl label="Ends" type="date" v-model="form.end_date" />
    </div>
    <FormControl label="Planned budget (NGN)" type="number" v-model="form.budget" />
    <p class="text-sm text-ink-gray-6">Only the exercise's Brand Manager can change this directly. Everyone else asks through a change request.</p>
    <ErrorMessage :message="error" />
    <div class="flex items-center gap-2">
      <Button type="submit" variant="solid" label="Save changes" :loading="saving" />
      <Button label="Cancel" @click="$router.back()" />
    </div>
  </form>
</template>

<script setup>
import { reactive, ref, watch } from "vue"
import { useRouter } from "vue-router"
import { Breadcrumbs, Button, ErrorMessage, FormControl, Skeleton, toast, useCall, useDoc } from "frappe-ui"
import AppHeader from "@/components/AppHeader.vue"

const props = defineProps({ name: String })
const router = useRouter()
const form = reactive({ campaign_name: "", objective: "", start_date: null, end_date: null, budget: null })
const loaded = ref(false)
const saving = ref(false)
const error = ref("")
const { doc } = useDoc({ doctype: "Marketing Campaign", name: props.name })
watch(doc, (d) => {
  if (!d || loaded.value) return
  for (const k of Object.keys(form)) form[k] = d[k] ?? form[k]
  loaded.value = true
}, { immediate: true })

const setValue = useCall({ url: "/api/method/frappe.client.set_value", method: "POST", immediate: false })
async function save() {
  error.value = ""
  saving.value = true
  try {
    await setValue.submit({ doctype: "Marketing Campaign", name: props.name, fieldname: { ...form } })
    toast.success("Saved")
    router.replace({ name: "Exercise", params: { name: props.name } })
  } catch (e) {
    error.value = e?.message || "The changes could not be saved."
  } finally {
    saving.value = false
  }
}
</script>
