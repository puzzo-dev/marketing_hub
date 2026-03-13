<template>
  <div v-if="brandLogo">
    <img :src="brandLogo" class="h-full w-full object-cover" />
  </div>
  <MarketingHubLogo v-else class="h-8 w-8 shrink-0 rounded" />
</template>

<script setup>
import { computed } from 'vue'
import { useConfigStore } from '@/stores/config'
import MarketingHubLogo from '@/components/Icons/MarketingHubLogo.vue'

const configStore = useConfigStore()
const brandLogo = computed(() => configStore.settings.brand_logo)
</script>
