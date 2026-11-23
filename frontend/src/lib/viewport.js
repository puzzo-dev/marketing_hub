import { onBeforeUnmount, ref } from "vue"

// One answer to "is this a phone", shared by the layout and every page header, so the
// shell and the header never disagree.
const query = window.matchMedia("(max-width: 639px)")
export const isMobile = ref(query.matches)
query.addEventListener("change", (e) => (isMobile.value = e.matches))
export const useIsMobile = () => isMobile
