<template>
  <AppHeader title="Channels" />
  <div class="flex flex-col gap-8 px-3 pb-10 pt-5 sm:px-5">
    <section class="flex flex-col gap-2">
      <div class="flex h-7 items-center"><h3 class="text-sm font-semibold text-ink-gray-8">Built in</h3></div>
      <div v-for="c in builtIn" :key="c.name" class="flex min-h-[60px] items-center gap-3 border-b">
        <span class="min-w-0 flex-1"><div class="truncate text-base text-ink-gray-8">{{ c.name }}</div><div class="mt-1.5 truncate text-sm text-ink-gray-5">{{ c.note }}</div></span>
        <Button label="Open in Desk" @click="desk(c.route)" />
      </div>
    </section>
    <section class="flex flex-col gap-2">
      <div class="flex h-7 items-center"><h3 class="text-sm font-semibold text-ink-gray-8">Connected accounts</h3></div>
      <DataList :rows="connected" :columns="[{ key: 'name', label: 'Account' }, { key: 'network_type', label: 'Network', width: '12rem' }, { key: 'state', label: 'Status', width: '12rem', badge: true }]" empty="No channels yet. Add a Social Media Network in Desk, or install an app that provides one." />
    </section>
  </div>
</template>

<script setup>
import { computed } from "vue"
import { Badge, Button, useCall } from "frappe-ui"
import DataList from "@/components/DataList.vue"
import AppHeader from "@/components/AppHeader.vue"

// Email goes through ERPNext Campaigns and SMS through SMS Settings, so neither is connected here.
const builtIn = [
  { name: "Email", note: "Sent by ERPNext Campaigns from your site's email account", route: "/app/email-account" },
  { name: "SMS", note: "Sent through your site's SMS gateway", route: "/app/sms-settings" },
]
const call = useCall({ url: "/api/method/marketing_hub.utils.omni_blast.list_channels" })
const channels = computed(() => call.data.value?.message ?? call.data.value ?? [])
const connected = computed(() => channels.value.map((c) => ({ ...c, state: c.has_sender ? "Can send" : "No sender installed" })))
const desk = (route) => (window.location.href = route)
</script>
