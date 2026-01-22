<template>
  <div
    class="flex h-full select-none flex-col border-r border-gray-100 bg-gray-50 p-3 text-base duration-300 ease-in-out"
    :style="{
      'min-width': width,
      'max-width': width,
    }"
  >
    <AppSwitcher class="mb-3" :is-expanded="isExpanded" />

    <SidebarLink
      label="Dashboard"
      class="my-0.5"
      :icon="IconLayoutDashboard"
      to="/marketing"
      :is-active="isActiveTab('/marketing')"
      :is-expanded="isExpanded"
    />

    <div class="mb-3">
      <SidebarLink
        label="Campaigns"
        class="my-0.5"
        :icon="IconMegaphone"
        to="/marketing/campaigns"
        :is-active="isActiveTab('/marketing/campaigns')"
        :is-expanded="isExpanded"
      />

      <SidebarLink
        label="Social Media"
        class="my-0.5"
        :icon="IconShare2"
        to="/marketing/social"
        :is-active="isActiveTab('/marketing/social')"
        :is-expanded="isExpanded"
      />

      <SidebarLink
        label="Analytics"
        class="my-0.5"
        :icon="IconBarChart3"
        to="/marketing/analytics"
        :is-active="isActiveTab('/marketing/analytics')"
        :is-expanded="isExpanded"
      />
    </div>

    <div class="mt-auto flex flex-col gap-1">
      <button
        class="flex h-8 cursor-pointer items-center rounded px-2 text-gray-700 duration-200 ease-in-out hover:bg-gray-100"
        :class="{
          'w-full justify-start': isExpanded,
          'w-8 justify-center': !isExpanded,
        }"
        @click="toggle()"
        :title="isExpanded ? 'Collapse sidebar' : 'Expand sidebar'"
      >
        <component
          :is="isExpanded ? IconPanelLeftClose : IconPanelLeftOpen"
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
import { useRoute } from "vue-router";
import { useSidebar } from "@/stores/sidebar";
import AppSwitcher from "./AppSwitcher.vue";
import SidebarLink from "./SidebarLink.vue";
import IconLayoutDashboard from "~icons/lucide/layout-dashboard";
import IconMegaphone from "~icons/lucide/megaphone";
import IconShare2 from "~icons/lucide/share-2";
import IconBarChart3 from "~icons/lucide/bar-chart-2";
import IconGrid3x3 from "~icons/lucide/grid-3x3";
import IconPanelLeftClose from "~icons/lucide/panel-left-close";
import IconPanelLeftOpen from "~icons/lucide/panel-left-open";

const route = useRoute();
const { isExpanded, width, toggle } = useSidebar();

function isActiveTab(path) {
  return route.path === path || route.path.startsWith(path + '/');
}
</script>
