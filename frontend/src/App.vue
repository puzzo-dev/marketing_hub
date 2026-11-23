<template>
  <FrappeUIProvider>
    <AppLayout />
    <Dialogs />
  </FrappeUIProvider>
</template>

<script setup>
import { Dialogs, FrappeUIProvider } from "frappe-ui"
import AppLayout from "@/layouts/AppLayout.vue"
</script>
