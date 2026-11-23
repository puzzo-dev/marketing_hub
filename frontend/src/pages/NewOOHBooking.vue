<template>
  <AppHeader title="New booking" :back="{ name: 'OutOfHome' }"><template #title><Breadcrumbs :items="[{ label: 'Out of home', route: { name: 'OutOfHome' } }, { label: 'New booking' }]" /></template></AppHeader>
  <form class="flex max-w-xl flex-col gap-4 px-3 py-4 sm:px-5" @submit.prevent="save">
    <LinkSelect label="Exercise" doctype="Marketing Campaign" label-field="campaign_name" v-model="form.campaign" />
    <LinkSelect label="Site" doctype="OOH Site" v-model="form.site" />
    <div class="grid grid-cols-2 gap-4">
      <FormControl label="Starts" type="date" v-model="form.start_date" />
      <FormControl label="Ends" type="date" v-model="form.end_date" />
    </div>
    <FormControl label="Agreed rate (NGN)" type="number" v-model="form.agreed_rate" />
    <p class="text-sm text-ink-gray-5">The booking goes to the exercise's Brand Manager. A purchase order is created once, when it is approved.</p>
    <ErrorMessage :message="error" />
    <div class="flex gap-2"><Button type="submit" variant="solid" label="Create booking" :loading="saving" /><Button label="Cancel" @click="$router.back()" /></div>
  </form>
</template>

<script setup>
import { reactive, ref } from "vue"
import { useRouter } from "vue-router"
import { Breadcrumbs, Button, ErrorMessage, FormControl, useNewDoc } from "frappe-ui"
import AppHeader from "@/components/AppHeader.vue"
import LinkSelect from "@/components/LinkSelect.vue"

const router = useRouter()
const form = reactive({ campaign: null, site: null, start_date: null, end_date: null, agreed_rate: null })
const saving = ref(false)
const error = ref("")
const { submit } = useNewDoc("OOH Booking", form)
async function save() {
  error.value = ""
  if (!form.campaign || !form.site || !form.start_date || !form.end_date) return (error.value = "Pick an exercise, a site and both dates.")
  saving.value = true
  try {
    const created = await submit()
    router.replace({ name: "OOHBooking", params: { name: created.name } })
  } catch (e) {
    error.value = e?.message || "The booking could not be created."
  } finally {
    saving.value = false
  }
}
</script>
