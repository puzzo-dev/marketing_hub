<template>
  <ErrorState icon="lucide-lock" title="You do not have access to this" text="It belongs to another brand or exercise. Ask its Brand Manager to add you." action-label="Back to home" @action="$router.push({ name: 'Home' })" />
</template>

<script setup>
import ErrorState from "./ErrorState.vue"
</script>
