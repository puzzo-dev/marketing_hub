<template>
  <div class="flex h-screen w-screen">
    <AgentSidebar />
    <div class="flex-1 flex flex-col h-full overflow-hidden bg-surface-white">
      <div class="flex border-b pr-5">
        <div id="app-header" class="flex-1"></div>
      </div>
      <div class="flex-1 overflow-auto">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </div>
  </div>
</template>

<script setup>
import AgentSidebar from '@/components/AgentSidebar.vue'
</script>
