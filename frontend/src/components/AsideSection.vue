<template>
  <section class="flex flex-col gap-2">
    <div class="flex h-7 items-center"><h2 class="text-sm font-semibold text-ink-gray-8">{{ title }}</h2></div>
    <slot />
  </section>
</template>

<script setup>
defineProps({ title: { type: String, required: true } })
</script>
