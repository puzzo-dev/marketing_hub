<template>
  <Dialog v-model="open" :options="{ title: 'Add a channel', size: 'lg' }">
    <template #body-content>
      <div class="flex flex-col gap-3">
        <p class="text-sm text-ink-gray-6">Pick a channel to connect. Email and SMS come from your site, so they are not listed.</p>
        <FormControl v-model="q" type="text" placeholder="Search channels" />
        <div v-for="g in groups" :key="g.type" class="flex flex-col">
          <div class="flex h-7 items-center text-sm font-medium text-ink-gray-7">{{ g.type }}</div>
          <div v-for="c in g.items" :key="c.network_name" class="flex min-h-14 items-center gap-3 border-b">
            <span class="flex min-w-0 flex-1 flex-col gap-1.5"><span class="truncate text-base text-ink-gray-8">{{ c.network_name }}</span><span class="truncate text-sm text-ink-gray-6">{{ c.has_sender ? "Ready to send" : "No sender installed yet" }}</span></span>
            <Button :label="c.has_sender ? 'Connect' : 'See how'" @click="go(c)" />
          </div>
        </div>
        <p v-if="!groups.length" class="py-6 text-center text-base text-ink-gray-6">No channel matches "{{ q }}".</p>
        <p class="text-sm text-ink-gray-6">Do not see yours? A developer can add a channel to the app, and it will show here.</p>
      </div>
    </template>
    <template #actions><Button label="Close" @click="open = false" /></template>
  </Dialog>
</template>

<script setup>
import { computed, ref } from "vue"
import { Button, Dialog, FormControl } from "frappe-ui"

const props = defineProps({ channels: { type: Array, default: () => [] } })
const open = defineModel({ type: Boolean })
const q = ref("")
const groups = computed(() => {
  const by = {}
  for (const c of props.channels) {
    if (q.value && !c.network_name.toLowerCase().includes(q.value.toLowerCase())) continue
    ;(by[c.network_type || "Other"] ||= []).push(c)
  }
  return Object.entries(by).map(([type, items]) => ({ type, items }))
})
// A channel is connected on its Social Media Network record in Desk.
const go = (c) => (window.location.href = `/app/social-media-network/${encodeURIComponent(c.network_name)}`)
</script>
