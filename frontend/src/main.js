import { createApp } from "vue"
import { FrappeUI, setConfig, frappeRequest } from "frappe-ui"
import App from "./App.vue"
import { router } from "./router"
import "./index.css"

setConfig("resourceFetcher", frappeRequest)

const app = createApp(App)
app.use(FrappeUI)
app.use(router)

function mount() {
  app.mount("#app")
  document.getElementById("splash")?.remove()
}

if (import.meta.env.DEV) {
  // In dev the Jinja page is not served, so fetch the same boot values it would inject.
  frappeRequest({ url: "/api/method/marketing_hub.www.marketing.index.get_context_for_dev" }).then((values) => {
    window.frappe = window.frappe || {}
    window.frappe.boot = { ...(window.frappe.boot || {}), user: { roles: values.user_roles || [] } }
    window.frappe.session = { user: values.user, user_fullname: values.user_fullname, user_image: values.user_image }
    mount()
  })
} else {
  mount()
}
