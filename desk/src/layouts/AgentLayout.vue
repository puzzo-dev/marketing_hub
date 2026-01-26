<template>
  <div class="flex h-screen w-screen flex-col overflow-hidden bg-gray-50">
    <!-- Simple Topbar for Agents -->
    <div class="flex h-14 items-center justify-between border-b bg-white px-5 shadow-sm">
      <div class="flex items-center gap-2">
        <div class="h-8 w-8 rounded bg-blue-600 flex items-center justify-center text-white font-bold">MH</div>
        <span class="font-semibold text-gray-900">Marketing Hub</span>
        <span class="ml-2 rounded bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-800">Agent Portal</span>
      </div>
      <div class="flex items-center gap-4">
        <router-link to="/marketing" class="text-sm font-medium text-gray-600 hover:text-gray-900">Dashboard</router-link>
        <router-link to="/marketing/campaigns" class="text-sm font-medium text-gray-600 hover:text-gray-900">Campaigns</router-link>
        <div class="h-8 w-8 rounded-full bg-gray-200 overflow-hidden">
           <!-- User Avatar Fallback -->
           <img v-if="userStore.image" :src="userStore.image" class="h-full w-full object-cover" />
           <div v-else class="h-full w-full flex items-center justify-center text-xs text-gray-500 font-bold">
             {{ userStore.name[0] }}
           </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="flex-1 overflow-auto">
      <div class="mx-auto max-w-5xl p-6">
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
import { useUserStore } from '@/stores/user'
const userStore = useUserStore()
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
