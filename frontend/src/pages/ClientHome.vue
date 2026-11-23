<template>
  <AppHeader title="Overview" />
  <div class="px-3 pb-10 pt-5 sm:px-5">
    <DataList :rows="rows" :route="(e) => ({ name: 'Exercise', params: { name: e.name } })" empty="Your agency has not shared an exercise with you yet."
      :columns="[{ key: 'campaign_name', label: 'Exercise' }, { key: 'dates', label: 'Dates', width: '14rem' }, { key: 'status', label: 'Status', width: '8rem', badge: true }]" />
  </div>
</template>

<script setup>
import { computed } from "vue"
import { Badge, useCall } from "frappe-ui"
import DataList from "@/components/DataList.vue"
import AppHeader from "@/components/AppHeader.vue"
import { badgeTheme } from "@/lib/status"

const call = useCall({ url: "/api/method/marketing_hub.api.client.exercises" })
const rows = computed(() => (call.data.value?.message ?? call.data.value ?? []).map((e) => ({ ...e, dates: `${e.start_date} to ${e.end_date}` })))
</script>
