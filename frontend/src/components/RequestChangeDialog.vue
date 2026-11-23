<template>
  <Dialog v-model:open="open" title="Request a change" :message="`This goes to ${approver || 'the Brand Manager'} for approval first. Nothing changes until they approve.`" size="md">
    <template #default>
      <form class="flex flex-col gap-4" @submit.prevent="send">
        <FormControl label="What should change" type="select" v-model="fieldname" :options="fields" />
        <FormControl label="New value" v-model="newValue" />
        <FormControl label="Why" type="textarea" v-model="reason" :rows="3" />
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

const props = defineProps({ campaign: { type: Object, required: true }, approver: String })
const emit = defineEmits(["sent"])
const open = defineModel("open", { type: Boolean, default: false })

// The fields a requester may ask to change. Everything else stays with the Brand Manager.
const fields = [
  { label: "Planned budget", value: "budget" },
  { label: "Start date", value: "start_date" },
  { label: "End date", value: "end_date" },
  { label: "Objective", value: "objective" },
]
const fieldname = ref("budget")
const newValue = ref("")
const reason = ref("")
const error = ref("")
const sending = ref(false)

// target_modified lets the apply step refuse if the exercise changed after the request.
const insert = useCall({ url: "/api/v2/document/Campaign Change Request", method: "POST", immediate: false })
async function send() {
  error.value = ""
  if (!newValue.value || !reason.value) return (error.value = "Say what the new value is and why.")
  sending.value = true
  try {
    await insert.submit({
      brand: props.campaign.brand,
      campaign: props.campaign.name,
      reason: reason.value,
      target_modified: props.campaign.modified,
      items: [{ fieldname: fieldname.value, old_value: String(props.campaign[fieldname.value] ?? ""), new_value: newValue.value }],
    })
    toast.success("Sent for approval")
    emit("sent")
    open.value = false
  } catch (e) {
    error.value = e?.message || "The request could not be sent."
  } finally {
    sending.value = false
  }
}
</script>
