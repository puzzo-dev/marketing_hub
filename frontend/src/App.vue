<template>
  <FrappeUIProvider>
    <div v-if="userStore.isLoggedIn && configStore.isReady">
      <!-- Agency mode: admins get AdminLayout, agents get AgentLayout -->
      <!-- Operations mode: everyone gets AdminLayout -->
      <AgentLayout v-if="configStore.isAgencyMode && !userStore.isAdmin" />
      <AdminLayout v-else />
    </div>
    <div v-else class="flex h-screen items-center justify-center">
      <LoadingIndicator />
    </div>
  </FrappeUIProvider>
</template>

<script setup>
import { FrappeUIProvider, LoadingIndicator } from "frappe-ui";
import { useUserStore } from "@/stores/user";
import { useConfigStore } from "@/stores/config";
import AdminLayout from "@/layouts/AdminLayout.vue";
import AgentLayout from "@/layouts/AgentLayout.vue";

const userStore = useUserStore();
const configStore = useConfigStore();
</script>
