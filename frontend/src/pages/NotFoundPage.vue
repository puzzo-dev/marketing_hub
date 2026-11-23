<template>
  <ErrorState title="This page does not exist" text="The exercise may have been deleted, or the link may be wrong." action-label="Back to exercises" @action="$router.push({ name: 'Exercises' })" />
</template>

<script setup>
import ErrorState from "./ErrorState.vue"
</script>
