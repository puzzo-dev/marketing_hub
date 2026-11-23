<template>
  <div class="min-h-0 flex-1 overflow-y-auto"><router-view v-if="$route.name === 'Exercise'" /><ClientHome v-else /></div>
</template>

<script setup>
import ClientHome from "./ClientHome.vue"
</script>
