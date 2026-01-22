import { computed } from "vue";
import { defineStore } from "pinia";
import { useStorage } from "@vueuse/core";

export const useSidebarStore = defineStore("sidebar", () => {
  const isExpanded = useStorage("sidebar_is_expanded", true);
  const width = computed(() => {
    return isExpanded.value ? "224px" : "50px";
  });

  function toggle(state) {
    isExpanded.value = state ?? !isExpanded.value;
  }

  return {
    isExpanded,
    toggle,
    width,
  };
});
