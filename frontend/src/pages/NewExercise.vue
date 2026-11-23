<template>
  <PageHeader>
    <Breadcrumbs :items="[{ label: 'Exercises', route: { name: 'Exercises' } }, { label: 'New exercise' }]" />
  </PageHeader>

  <form class="flex max-w-xl flex-col gap-4 p-5" @submit.prevent="save">
    <FormControl label="Exercise name" v-model="form.campaign_name" required />
    <LinkSelect label="Brand" doctype="Brand" label-field="brand_name" v-model="form.brand" />
    <FormControl label="Type" type="select" v-model="form.campaign_type" :options="['Campaign', 'OOH Flight', 'Activation', 'Content Series']" />
    <FormControl label="Objective" type="textarea" v-model="form.objective" :rows="3" />
    <div class="grid grid-cols-2 gap-4">
      <FormControl label="Starts" type="date" v-model="form.start_date" />
      <FormControl label="Ends" type="date" v-model="form.end_date" />
    </div>
    <FormControl label="Planned budget (NGN)" type="number" v-model="form.budget" />
    <LinkSelect label="Brand Manager" doctype="User" label-field="full_name" v-model="form.brand_manager" />
    <p class="text-sm text-ink-gray-5">Creating an exercise also creates its ERPNext Project. The Brand Manager you pick approves every change to it.</p>
    <ErrorMessage :message="error" />
    <div class="flex items-center gap-2">
      <Button type="submit" variant="solid" label="Create exercise" :loading="saving" />
      <Button label="Cancel" @click="$router.back()" />
    </div>
  </form>
</template>

<script setup>
import { reactive, ref } from "vue"
import { useRouter } from "vue-router"
import { Breadcrumbs, Button, ErrorMessage, FormControl, PageHeader, toast, useNewDoc } from "frappe-ui"
import LinkSelect from "@/components/LinkSelect.vue"

const router = useRouter()
const form = reactive({ campaign_name: "", brand: null, campaign_type: "Campaign", objective: "", start_date: null, end_date: null, budget: null, brand_manager: null })
const saving = ref(false)
const error = ref("")

const { submit } = useNewDoc("Marketing Campaign", form)
async function save() {
  error.value = ""
  if (!form.campaign_name || !form.brand) return (error.value = "Give the exercise a name and pick its brand.")
  saving.value = true
  try {
    const created = await submit()
    toast.success("Exercise created")
    router.replace({ name: "Exercise", params: { name: created.name } })
  } catch (e) {
    error.value = e?.message || "The exercise could not be created."
  } finally {
    saving.value = false
  }
}
</script>
