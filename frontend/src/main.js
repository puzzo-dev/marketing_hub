import { createApp } from "vue";
import { createPinia } from "pinia";
import {
  Badge,
  Button,
  Dialog,
  ErrorMessage,
  FeatherIcon,
  FormControl,
  frappeRequest,
  FrappeUI,
  Input,
  setConfig,
  TextInput,
  toast,
} from "frappe-ui";
import App from "./App.vue";
import "./index.css";
import { router } from "./router";

const globalComponents = {
  Badge,
  Button,
  Dialog,
  ErrorMessage,
  FeatherIcon,
  FormControl,
  Input,
  TextInput,
};

setConfig("resourceFetcher", frappeRequest);

// Configure socket.io to use the correct port from Frappe's boot data
// In production, socketio runs on the same port as the web server (behind nginx)
// In dev, it's on the port specified by window.socketio_port (typically 9000)
if (window.frappe?.boot?.socketio_port) {
  setConfig("socketio_port", window.frappe.boot.socketio_port);
}

const app = createApp(App);

// Register Pinia BEFORE any component that uses defineStore is mounted
const pinia = createPinia();
app.use(pinia);

app.use(FrappeUI);
app.use(router);

for (const c in globalComponents) {
  app.component(c, globalComponents[c]);
}

if (import.meta.env.DEV) {
  frappeRequest({
    url: "/api/method/marketing_hub.www.marketing.index.get_context_for_dev",
  }).then((values) => {
    for (let key in values) {
      window[key] = values[key];
    }
    // Ensure boot.user.roles is populated for dev mode
    if (values.user_roles) {
      window.frappe = window.frappe || {};
      window.frappe.boot = window.frappe.boot || {};
      window.frappe.boot.user = window.frappe.boot.user || {};
      window.frappe.boot.user.roles = values.user_roles;
    }
    app.mount("#app");
    document.getElementById('splash')?.remove();
  });
} else {
  app.mount("#app");
  document.getElementById('splash')?.remove();
}
