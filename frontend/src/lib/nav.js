// The sidebar for each role. Items name a route; the router decides who may open it.
import { ROLES } from "./session"

const I = (label, icon, route) => ({ label, icon: `lucide-${icon}`, route })

export const NAV = {
  [ROLES.manager]: [
    { items: [I("Home", "house", "Home"), I("Approvals", "circle-check", "Approvals")] },
    { label: "Plan", items: [I("Exercises", "folder", "Exercises"), I("Content", "file-text", "Content"), I("Calendar", "calendar", "Calendar")] },
    { label: "Deliver", items: [I("Placements", "send", "Placements"), I("Out of home", "map-pin", "OutOfHome"), I("Leads", "inbox", "Leads")] },
    { label: "Measure", items: [I("Reports", "chart-column", "Reports")] },
    { label: "Setup", items: [I("Channels", "plug", "Channels")] },
  ],
  [ROLES.head]: [
    { items: [I("Home", "house", "Home"), I("Approvals", "circle-check", "Approvals")] },
    { label: "Plan", items: [I("Exercises", "folder", "Exercises")] },
    { label: "Measure", items: [I("Cross-brand report", "chart-column", "CrossBrand")] },
  ],
  [ROLES.planner]: [{ items: [I("Exercises", "folder", "Exercises"), I("Content", "file-text", "Content")] }],
  [ROLES.contentLead]: [{ items: [I("Exercises", "folder", "Exercises"), I("Content", "file-text", "Content")] }],
  [ROLES.publisher]: [{ items: [I("Placements", "send", "Placements"), I("Content", "file-text", "Content")] }],
  [ROLES.ooh]: [
    { label: "Deliver", items: [I("Out of home", "map-pin", "OutOfHome"), I("Vendors", "building-2", "Vendors"), I("Purchase orders", "receipt", "PurchaseOrders"), I("Exercises", "folder", "Exercises")] },
  ],
  [ROLES.client]: [
    { items: [I("Overview", "house", "Home"), I("Exercises", "folder", "Exercises")] },
  ],
}
