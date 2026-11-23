<template>
  <Dialog v-model:open="open" title="Schedule placement" :message="`${content.title} · ${content.campaign}`" size="md">
    <template #default>
      <form class="flex flex-col gap-4" @submit.prevent="send">
        <LinkSelect label="Channel" doctype="Social Media Network" v-model="channel" />
        <div class="grid grid-cols-2 gap-4">
          <FormControl label="Date" type="date" v-model="date" />
          <FormControl label="Time" type="time" v-model="time" />
        </div>
        <div class="flex items-start gap-2 rounded-5 bg-surface-gray-1 px-3 py-2 text-sm text-ink-gray-7">
          <span class="lucide-info mt-0.5 size-4 text-ink-gray-6" />
          This goes to the exercise's Brand Manager for approval first. It sends only after they approve.
        </div>
        <ErrorMessage :message="error" />
      </form>
    </template>
    <template #actions="{ close }">
      <Button variant="solid" label="Send for approval" :loading="sending" @click="send" />
      <Button label="Cancel" @click="close" />
    </template>
  </Dialog>
</template>

<script setup>
import { ref } from "vue"
import { Button, Dialog, ErrorMessage, FormControl, toast, useCall } from "frappe-ui"
import LinkSelect from "./LinkSelect.vue"

const props = defineProps({ content: { type: Object, required: true } })
const emit = defineEmits(["scheduled"])
const open = defineModel("open", { type: Boolean, default: false })
const channel = ref(null)
const date = ref(null)
const time = ref("09:00")
const error = ref("")
const sending = ref(false)

const insert = useCall({ url: "/api/v2/document/Placement", method: "POST", immediate: false })
async function send() {
  error.value = ""
  if (!channel.value || !date.value) return (error.value = "Pick a channel and a date.")
  sending.value = true
  try {
    await insert.submit({ campaign: props.content.campaign, content_item: props.content.name, channel: channel.value, scheduled_for: `${date.value} ${time.value}:00` })
    toast.success("Sent for approval")
    emit("scheduled")
    open.value = false
  } catch (e) {
    error.value = e?.message || "That could not be scheduled."
  } finally {
    sending.value = false
  }
}
</script>
