<template>
  <div
    class="flex h-8 cursor-pointer items-center gap-2 rounded px-2 text-ink-gray-7 duration-200 ease-in-out"
    :class="{
      'justify-start': isExpanded,
      'justify-center w-8': !isExpanded,
      'bg-surface-cards shadow-sm': isActive,
      'hover:bg-surface-gray-1': !isActive,
    }"
    @click="handleNavigation"
  >
    <Tooltip v-if="!isExpanded" :text="label" placement="right">
      <span class="flex-shrink-0 text-ink-gray-6">
        <component :is="icon" class="h-4 w-4" />
      </span>
    </Tooltip>
    
    <template v-else>
      <span class="flex-shrink-0 text-ink-gray-6">
        <component :is="icon" class="h-4 w-4" />
      </span>
      <div class="flex flex-1 items-center justify-between text-sm">
        {{ label }}
        <slot name="right" />
      </div>
    </template>
  </div>
</template>

<script setup>
import { Tooltip } from "frappe-ui";
import { useRouter } from "vue-router";

const props = defineProps({
  icon: {
    type: Object,
    required: false,
  },
  label: {
    type: String,
    required: true,
  },
  isExpanded: {
    type: Boolean,
    default: true,
  },
  isActive: {
    type: Boolean,
    default: false,
  },
  onClick: {
    type: Function,
    default: () => () => true,
  },
  to: {
    type: [String, Object],
    default: "",
  },
});

const router = useRouter();

function handleNavigation() {
  props.onClick();
  if (!props.to) return;

  if (typeof props.to === "string") {
    router.push(props.to);
    return;
  }
  router.push(props.to);
}
</script>
