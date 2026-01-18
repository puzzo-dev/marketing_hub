<template>
  <nav class="border-b bg-white shadow-sm">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="flex h-16 items-center justify-between">
        <div class="flex items-center">
          <router-link to="/marketing" class="flex items-center space-x-3">
            <div class="flex h-8 w-8 items-center justify-center rounded bg-blue-600 text-white">
              <FeatherIcon name="trending-up" class="h-5 w-5" />
            </div>
            <span class="text-xl font-semibold text-gray-900">Marketing Hub</span>
          </router-link>

          <div class="ml-10 flex space-x-4">
            <router-link
              v-for="item in navigation"
              :key="item.name"
              :to="item.href"
              class="rounded-md px-3 py-2 text-sm font-medium transition-colors"
              :class="[
                $route.path === item.href
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900',
              ]"
            >
              {{ item.name }}
            </router-link>
          </div>
        </div>

        <div class="flex items-center space-x-4">
          <Dropdown :options="userMenuOptions">
            <template #default="{ open }">
              <Button
                variant="ghost"
                class="flex items-center space-x-2"
              >
                <FeatherIcon name="grid" class="h-5 w-5" />
              </Button>
            </template>
          </Dropdown>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { Dropdown } from "frappe-ui";

const navigation = [
  { name: "Dashboard", href: "/marketing" },
  { name: "Campaigns", href: "/marketing/campaigns" },
  { name: "Social", href: "/marketing/social" },
  { name: "Analytics", href: "/marketing/analytics" },
];

const userMenuOptions = [
  {
    label: "Desk",
    icon: "monitor",
    onClick: () => (window.location.href = "/app"),
  },
  {
    label: "Settings",
    icon: "settings",
    onClick: () => (window.location.href = "/app/user"),
  },
];
</script>
