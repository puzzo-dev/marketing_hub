import { ref, computed } from "vue";

const isExpanded = ref(localStorage.getItem('sidebar_is_expanded') !== 'false');

export function useSidebar() {
  const width = computed(() => {
    return isExpanded.value ? "224px" : "50px";
  });

  function toggle(state) {
    isExpanded.value = state ?? !isExpanded.value;
    localStorage.setItem('sidebar_is_expanded', isExpanded.value);
  }

  return {
    isExpanded,
    toggle,
    width,
  };
}
