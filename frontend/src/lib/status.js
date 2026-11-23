// One place that decides a status badge's colour, so every list agrees.
const THEMES = {
  gray: ["draft", "ended", "closed", "archived", "cancelled"],
  blue: ["scheduled", "proposed", "production", "to receive", "open", "in review", "planned"],
  amber: ["pending", "needs approval", "sending", "on hold", "waiting", "awaiting approval"],
  green: ["live", "approved", "completed", "posted", "billed", "active", "published", "done"],
  red: ["rejected", "failed", "overdue", "error"],
}
export function badgeTheme(status) {
  const s = String(status || "").toLowerCase()
  return Object.keys(THEMES).find((t) => THEMES[t].includes(s)) || "gray"
}
