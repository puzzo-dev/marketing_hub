<template>
  <AppHeader title="Overview" />
  <div class="flex flex-col px-3 py-4 sm:px-5">
    <router-link v-for="e in rows" :key="e.name" :to="{ name: 'Exercise', params: { name: e.name } }" class="flex h-12 items-center gap-3 border-b px-3 hover:bg-surface-gray-1">
      <span class="min-w-0 flex-1 truncate text-base text-ink-gray-8">{{ e.campaign_name }}</span>
      <span class="text-sm text-ink-gray-6">{{ e.start_date }} to {{ e.end_date }}</span><Badge :label="e.status" :theme="badgeTheme(e.status)" />
    </router-link>
    <p v-if="!rows.length" class="text-base text-ink-gray-6">Your agency has not shared an exercise with you yet.</p>
  </div>
</template>

<script setup>
import { computed } from "vue"
import { Badge, useCall } from "frappe-ui"
import AppHeader from "@/components/AppHeader.vue"
import { badgeTheme } from "@/lib/status"

const call = useCall({ url: "/api/method/marketing_hub.api.client.exercises" })
const rows = computed(() => call.data.value?.message ?? call.data.value ?? [])
</script>
