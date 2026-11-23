<template>
  <div class="flex h-full gap-3 overflow-x-auto p-3 sm:p-5">
    <section v-for="s in statuses" :key="s" class="flex w-72 shrink-0 flex-col gap-2 rounded-6 bg-surface-gray-1 p-2">
      <div class="flex items-center gap-2 px-1 py-1"><span class="text-base font-medium text-ink-gray-8">{{ s }}</span><span class="text-sm text-ink-gray-6">{{ by[s].length }}</span></div>
      <router-link v-for="c in by[s]" :key="c.name" :to="{ name: 'ContentDetail', params: { name: c.name } }" class="flex flex-col gap-2 rounded-5 bg-surface-base p-3 shadow-sm hover:bg-surface-gray-2">
        <span class="text-base text-ink-gray-8">{{ c.title }}</span>
        <span class="text-sm text-ink-gray-6">{{ c.campaign }}</span>
        <span class="flex items-center justify-between pt-1 text-sm text-ink-gray-6"><span>{{ c.type }}</span><span>{{ c.due_date }}</span></span>
      </router-link>
      <p v-if="!by[s].length" class="px-1 py-3 text-sm text-ink-gray-6">Nothing here.</p>
    </section>
  </div>
</template>

<script setup>
import { computed } from "vue"
const props = defineProps({ items: Array, statuses: Array })
const by = computed(() => Object.fromEntries(props.statuses.map((s) => [s, props.items.filter((i) => i.status === s)])))
</script>
