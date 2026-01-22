<template>
  <Dropdown :options="userOptions" placement="bottom-start" class="user-menu-dropdown">
    <template #default="{ open }">
      <button
        class="flex h-9 w-full items-center gap-2 rounded px-2 text-sm duration-200 ease-in-out"
        :class="open ? 'bg-white shadow-sm' : 'hover:bg-gray-100'"
      >
        <div class="flex h-6 w-6 items-center justify-center rounded bg-gray-600 text-white text-xs font-medium flex-shrink-0">
          {{ userInitials }}
        </div>
        <span v-show="isExpanded" class="flex-1 text-left text-gray-700 truncate">
          {{ userName }}
        </span>
        <component
          v-show="isExpanded"
          :is="IconChevronDown"
          class="h-3 w-3 text-gray-500 flex-shrink-0"
        />
      </button>
    </template>
  </Dropdown>
</template>

<script setup>
import { Dropdown } from "frappe-ui";
import { computed } from "vue";
import IconChevronDown from "~icons/lucide/chevron-down";

defineProps({
  isExpanded: {
    type: Boolean,
    default: true,
  },
});

const userName = computed(() =>
  (typeof frappe !== 'undefined' && frappe?.session?.user_fullname) || 'User'
);

const userInitials = computed(() => {
  const name = userName.value;
  const parts = name.split(' ');
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase();
  }
  return name.substring(0, 2).toUpperCase();
});

const userOptions = computed(() => [
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
        label: "Log Out",
        icon: "log-out",
        onClick: () => window.location.href = "/api/method/logout",
      },
    ],
  },
]);
</script>
