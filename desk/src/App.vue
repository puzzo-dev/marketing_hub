<template>
  <FrappeUIProvider>
    <div class="min-h-screen">
      <Navbar />
      <main class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <router-view />
      </main>
    </div>
  </FrappeUIProvider>
</template>

<script setup>
import { FrappeUIProvider } from "frappe-ui";
import Navbar from "@/components/Navbar.vue";
</script>
