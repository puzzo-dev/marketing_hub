<template>
  <AppHeader title="Channels" />
  <div class="flex max-w-3xl flex-col gap-6 p-5">
    <div class="flex flex-col">
      <h3 class="pb-2 text-lg-medium text-ink-gray-9">Built in</h3>
      <div v-for="c in builtIn" :key="c.name" class="flex min-h-14 items-center gap-3 border-b">
        <span class="min-w-0 flex-1"><div class="text-base text-ink-gray-8">{{ c.name }}</div><div class="text-sm text-ink-gray-6">{{ c.note }}</div></span>
        <Badge label="Set up in Desk" /><Button label="Open Desk" @click="desk(c.route)" />
      </div>
    </div>
    <div class="flex flex-col">
      <h3 class="pb-2 text-lg-medium text-ink-gray-9">Connected accounts</h3>
      <div v-for="c in channels" :key="c.name" class="flex min-h-14 items-center gap-3 border-b">
        <span class="min-w-0 flex-1"><div class="text-base text-ink-gray-8">{{ c.name }}</div><div class="text-sm text-ink-gray-6">{{ c.network_type }}</div></span>
        <Badge :label="c.has_sender ? 'Can send' : 'No sender installed'" :theme="c.has_sender ? 'green' : 'amber'" />
      </div>
      <p v-if="!channels.length" class="pt-2 text-base text-ink-gray-6">No channels yet. Add a Social Media Network in Desk, or install an app that provides one.</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"
import { Badge, Button, useCall } from "frappe-ui"
import AppHeader from "@/components/AppHeader.vue"

// Email goes through ERPNext Campaigns and SMS through SMS Settings, so neither is connected here.
const builtIn = [
  { name: "Email", note: "Sent by ERPNext Campaigns from your site's email account", route: "/app/email-account" },
  { name: "SMS", note: "Sent through your site's SMS gateway", route: "/app/sms-settings" },
]
const call = useCall({ url: "/api/method/marketing_hub.utils.omni_blast.list_channels" })
const channels = computed(() => call.data.value?.message ?? call.data.value ?? [])
const desk = (route) => (window.location.href = route)
</script>
