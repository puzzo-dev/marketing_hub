<template>
  <dl class="flex flex-col">
    <div v-for="[label, value] in rows" :key="label" class="flex min-h-9 items-center gap-4">
      <dt class="w-36 shrink-0 text-sm text-ink-gray-6">{{ label }}</dt>
      <dd class="min-w-0 flex-1 text-base text-ink-gray-8">{{ value || "—" }}</dd>
    </div>
  </dl>
</template>

<script setup>
defineProps({ rows: { type: Array, required: true } })
</script>
