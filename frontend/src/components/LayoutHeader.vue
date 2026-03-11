<template>
  <Teleport to="#app-header" v-if="showHeader">
    <slot>
      <header class="flex h-[45px] items-center justify-between px-5 py-2.5">
        <div class="flex items-center gap-2">
          <slot name="left-header" />
        </div>
        <div class="flex items-center gap-2">
          <slot name="right-header" />
        </div>
      </header>
    </slot>
  </Teleport>
</template>

<script setup>
import { ref, nextTick } from 'vue'

const showHeader = ref(false)

nextTick(() => {
  showHeader.value = true
})
</script>
