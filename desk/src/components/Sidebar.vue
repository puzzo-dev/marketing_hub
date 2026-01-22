<template>
  <div
    class="flex h-full select-none flex-col border-r border-gray-200 bg-gray-50 p-3 text-base duration-300 ease-in-out"
    :style="{
      'min-width': width,
      'max-width': width,
    }"
  >
    <UserMenu class="mb-3" :options="profileSettings" :is-expanded="isExpanded" />

    <SidebarLink
      label="Dashboard"
      class="my-0.5"
      :icon="LucideLayoutDashboard"
      to="/marketing"
      :is-active="isActiveTab('/marketing')"
      :is-expanded="isExpanded"
    />

    <div class="mb-3">
      <SidebarLink
        label="Campaigns"
        class="my-0.5"
        :icon="LucideMegaphone"
        to="/marketing/campaigns"
        :is-active="isActiveTab('/marketing/campaigns')"
        :is-expanded="isExpanded"
      />

      <SidebarLink
        label="Social Media"
        class="my-0.5"
        :icon="LucideShare2"
        to="/marketing/social"
        :is-active="isActiveTab('/marketing/social')"
        :is-expanded="isExpanded"
      />

      <SidebarLink
        label="Analytics"
        class="my-0.5"
        :icon="LucideBarChart3"
        to="/marketing/analytics"
        :is-active="isActiveTab('/marketing/analytics')"
        :is-expanded="isExpanded"
      />
    </div>

    <div class="mt-auto flex flex-col gap-1">
      <SidebarLink
        label="Switch to Desk"
        class="my-0.5"
        :icon="LucideGrid3x3"
        :on-click="() => open('/app')"
        :is-expanded="isExpanded"
      />

      <button
        class="flex h-8 cursor-pointer items-center rounded px-2 text-gray-700 duration-200 ease-in-out hover:bg-gray-100"
        :class="{
          'w-full justify-start': isExpanded,
          'w-8 justify-center': !isExpanded,
        }"
        @click="sidebarStore.toggle()"
        :title="isExpanded ? 'Collapse sidebar' : 'Expand sidebar'"
      >
        <component
          :is="isExpanded ? LucidePanelLeftClose : LucidePanelLeftOpen"
          class="h-4 w-4 flex-shrink-0 text-gray-600"
        />
        <span
          v-show="isExpanded"
          class="ml-2 text-sm"
        >
          Collapse
        </span>
      </button>
    </div>
  </div>
</template>

<script setup>
import {
  LucideLayoutDashboard,
  LucideMegaphone,
  LucideShare2,
  LucideBarChart3,
  LucideGrid3x3,
  LucidePanelLeftClose,
  LucidePanelLeftOpen,
} from "lucide-vue-next";
import { useRoute } from "vue-router";
import { storeToRefs } from "pinia";
import { useSidebarStore } from "@/stores/sidebar";
import UserMenu from "./UserMenu.vue";
import SidebarLink from "./SidebarLink.vue";

const route = useRoute();
const sidebarStore = useSidebarStore();
const { isExpanded, width } = storeToRefs(sidebarStore);

const profileSettings = [
  {
    label: "Installed Apps",
    icon: "grid",
    onClick: () => null,
    children: [
      {
        label: "Marketing Hub",
        icon: "layers",
        onClick: () => window.location.href = "/marketing",
      },
      {
        label: "CRM",
        icon: "users",
        onClick: () => window.location.href = "/crm",
        condition: () => window.installed_apps?.includes?.('crm'),
      },
      {
        label: "Helpdesk",
        icon: "life-buoy",
        onClick: () => window.location.href = "/helpdesk",
        condition: () => window.installed_apps?.includes?.('helpdesk'),
      },
    ].filter(item => !item.condition || item.condition()),
  },
  {
    label: "Switch to Desk",
    icon: "grid",
    onClick: () => open("/app"),
  },
  {
    label: "Logout",
    icon: "log-out",
    onClick: () => logout(),
  },
];

function isActiveTab(path) {
  return route.path === path || route.path.startsWith(path + '/');
}

function open(url) {
  window.location.href = url;
}

function logout() {
  window.location.href = "/api/method/logout";
}
</script>
