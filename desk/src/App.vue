<template>
  <FrappeUIProvider>
    <div v-if="userStore.isLoggedIn">
      <AdminLayout v-if="userStore.role === 'Admin'" />
      <AgentLayout v-else />
    </div>
    <div v-else class="flex h-screen items-center justify-center">
      <LoadingIndicator />
    </div>
  </FrappeUIProvider>
</template>

<script setup>
import { FrappeUIProvider, LoadingIndicator } from "frappe-ui";
import { useUserStore } from "@/stores/user";
import AdminLayout from "@/layouts/AdminLayout.vue";
import AgentLayout from "@/layouts/AgentLayout.vue";

const userStore = useUserStore();
</script>
