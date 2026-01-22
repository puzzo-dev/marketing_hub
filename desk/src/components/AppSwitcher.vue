<template>
  <Dropdown :options="appOptions" placement="bottom-start" class="app-switcher-dropdown">
    <template #default="{ open }">
      <button
        class="flex h-12 w-full items-center gap-2 rounded px-2 duration-200 ease-in-out"
        :class="open ? 'bg-white shadow-sm' : 'hover:bg-gray-100'"
        title="Switch Apps"
      >
        <BrandLogo />
        <div v-if="isExpanded" class="flex flex-1 flex-col text-left">
          <span class="text-sm font-medium text-gray-900">Marketing Hub</span>
        </div>
        <component
          v-if="isExpanded"
          :is="IconChevronDown"
          class="h-4 w-4 text-gray-500 flex-shrink-0"
        />
      </button>
    </template>
  </Dropdown>
</template>

<script setup>
import { Dropdown } from "frappe-ui";
import BrandLogo from "./BrandLogo.vue";
import { computed } from "vue";
import IconChevronDown from "~icons/lucide/chevron-down";

const props = defineProps({
  isExpanded: {
    type: Boolean,
    default: true,
  },
});

const installedApps = computed(() => window.installed_apps || []);

const appConfig = {
  frappe: { label: "Frappe Desk", icon: "grid", url: "/app" },
  erpnext: { label: "ERPNext", icon: "package", url: "/app" },
  crm: { label: "CRM", icon: "users", url: "/crm" },
  helpdesk: { label: "Helpdesk", icon: "life-buoy", url: "/helpdesk" },
  marketing_hub: { label: "Marketing Hub", icon: "megaphone", url: "/marketing" },
  hrms: { label: "HR", icon: "user-check", url: "/app" },
  insights: { label: "Insights", icon: "bar-chart", url: "/insights" },
};

const appOptions = computed(() => {
  const apps = installedApps.value
    .map(app => {
      const config = appConfig[app] || { 
        label: app.charAt(0).toUpperCase() + app.slice(1), 
        icon: "box",
        url: "/app"
      };
      return {
        label: config.label,
        icon: config.icon,
        onClick: () => window.location.href = config.url,
      };
    })
    .filter(Boolean);

  return [
    {
      group: "Installed Apps",
      hideLabel: false,
      items: apps,
    },
    {
      group: "Account",
      hideLabel: false,
      items: [
        {
          label: "My Settings",
          icon: "settings",
          onClick: () => window.location.href = "/app/user/" + frappe.session.user,
        },
        {
          label: "Switch to Desk",
          icon: "grid",
          onClick: () => window.location.href = "/app",
        },
      ],
    },
    {
      group: "Help",
      hideLabel: false,
      items: [
        {
          label: "Documentation",
          icon: "book-open",
          onClick: () => window.open("https://docs.erpnext.com", "_blank"),
        },
        {
          label: "Support",
          icon: "help-circle",
          onClick: () => window.open("https://discuss.erpnext.com", "_blank"),
        },
      ],
    },
    {
      group: "",
      hideLabel: true,
      items: [
        {
          label: "Logout",
          icon: "log-out",
          onClick: () => window.location.href = "/api/method/logout",
        },
      ],
    },
  ];
});
</script>
