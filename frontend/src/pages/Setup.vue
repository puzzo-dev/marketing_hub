<template>
  <div class="flex justify-center px-6 py-12" style="min-height: 100%">
    <div class="flex w-full max-w-4xl gap-12">
      <div class="flex flex-col gap-6">
        <span class="text-base font-medium text-ink-gray-8">Marketing Hub</span>
        <ol class="flex w-56 shrink-0 flex-col gap-1" aria-label="Setup steps">
          <li v-for="(s, i) in STEPS" :key="s" class="flex h-8 items-center gap-2.5 rounded-4 px-2 text-base" :class="i === step ? 'bg-surface-gray-2 text-ink-gray-9' : i < step ? 'text-ink-gray-7' : 'text-ink-gray-6'">
            <span class="flex size-5 items-center justify-center rounded-full text-sm" :class="i < step ? 'bg-surface-gray-10 text-ink-white' : i === step ? 'border border-outline-gray-8' : 'border border-outline-gray-3'">{{ i < step ? "✓" : i + 1 }}</span>{{ s }}
          </li>
        </ol>
      </div>
      <form class="flex min-w-0 flex-1 flex-col gap-5" @submit.prevent="next">
        <div class="flex flex-col gap-1.5"><h1 class="text-2xl font-semibold text-ink-gray-9">{{ TITLES[step] }}</h1><p class="text-base text-ink-gray-6">{{ HINTS[step] }}</p></div>
        <template v-if="step === 0">
          <FormControl label="Brand name" v-model="brand.brand_name" required />
          <LinkSelect label="Company" doctype="Company" v-model="brand.company" />
        </template>
        <template v-else-if="step === 1">
          <div v-for="(m, i) in team" :key="i" class="grid grid-cols-[1fr_12rem_auto] items-end gap-3">
            <LinkSelect label="Person" doctype="User" label-field="full_name" v-model="m.user" />
            <FormControl label="Role" type="select" v-model="m.brand_role" :options="ROLES" />
            <Button variant="ghost" icon="lucide-x" aria-label="Remove" @click="team.splice(i, 1)" />
          </div>
          <Button class="self-start" label="Add a person" icon-left="lucide-plus" @click="team.push({ user: null, brand_role: 'Media Planner' })" />
        </template>
        <template v-else-if="step === 2">
          <p class="text-base text-ink-gray-8">Email goes through ERPNext Campaigns and SMS through your site's SMS gateway, so there is nothing to connect for them. Accounts you post from are added on the Channels page.</p>
          <Button class="self-start" label="Open Channels" :route="{ name: 'Channels' }" />
        </template>
        <template v-else><p class="text-base text-ink-gray-8">Creating an exercise also creates its ERPNext Project.</p></template>
        <ErrorMessage :message="error" />
        <div class="flex items-center justify-between pt-2">
          <Button label="Back" :disabled="step === 0" @click="step--" />
          <div class="flex gap-2">
            <Button v-if="step === 1 || step === 2" label="Skip for now" @click="step++" />
            <Button type="submit" variant="solid" :loading="saving" :label="step === 3 ? 'Plan the first exercise' : 'Continue'" />
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue"
import { useRouter } from "vue-router"
import { Button, ErrorMessage, FormControl, useCall } from "frappe-ui"
import LinkSelect from "@/components/LinkSelect.vue"

const router = useRouter()
const STEPS = ["Your brand", "Team and roles", "Channels", "First exercise"]
const TITLES = ["Set up your brand", "Who works on this brand", "Connect your channels", "Plan your first exercise"]
const HINTS = ["A brand groups its exercises, team and accounts.", "Every brand has one or more Brand Managers. Each exercise has one.", "You can skip this and add accounts later.", "You can change all of it later."]
const ROLES = ["Brand Manager", "Media Planner", "Content Lead", "Publisher", "OOH Coordinator", "Client"]
const step = ref(0)
const saving = ref(false)
const error = ref("")
const brand = reactive({ brand_name: "", company: null })
const team = reactive([{ user: null, brand_role: "Brand Manager" }])
const insert = useCall({ url: "/api/method/frappe.client.insert", method: "POST", immediate: false })
const saved = ref(null)

// The brand is saved once, with its team, when the person leaves step two.
async function next() {
  error.value = ""
  if (step.value === 0 && !brand.brand_name) return (error.value = "Give the brand a name.")
  if (step.value === 3) return router.push({ name: "NewExercise", query: { brand: saved.value || brand.brand_name } })
  if (step.value === 1 && !saved.value) {
    saving.value = true
    try {
      const doc = { doctype: "Brand", brand_name: brand.brand_name, company: brand.company, team: team.filter((m) => m.user) }
      const res = await insert.submit({ doc })
      saved.value = (res?.message || res)?.name
    } catch (e) {
      error.value = e?.message || "The brand could not be saved."
      saving.value = false
      return
    }
    saving.value = false
  }
  step.value++
}
</script>
