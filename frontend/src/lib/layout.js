import { ref, watch } from "vue"

// Full width or a centered column, the same choice Desk calls "Toggle Full Width".
// Kept per browser; the default is full width.
const KEY = "mh_full_width"
const read = () => { try { return localStorage.getItem(KEY) !== "0" } catch { return true } }
export const fullWidth = ref(read())
watch(fullWidth, (v) => { try { localStorage.setItem(KEY, v ? "1" : "0") } catch { /* private mode */ } })
