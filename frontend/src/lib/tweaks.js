import { ref, watch } from "vue"

// The few layout choices the person can flip from the Tweak panel. Kept per browser.
const KEY = "mh_density"
const read = () => { try { return localStorage.getItem(KEY) === "compact" ? "compact" : "relaxed" } catch { return "relaxed" } }
export const density = ref(read())
watch(density, (v) => { try { localStorage.setItem(KEY, v) } catch { /* private mode */ } })
// Row heights for two-line list rows and plain rows.
export const rowHeight = (twoLine) => (density.value === "compact" ? (twoLine ? 52 : 40) : twoLine ? 60 : 48)
