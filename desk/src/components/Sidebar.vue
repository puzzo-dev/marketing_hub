<template>
  <Sidebar
    :header="sidebarHeader"
    :sections="sidebarSections"
    v-model:collapsed="isCollapsed"
  >
    <template #header-logo>
      <MarketingHubLogo class="h-full w-full rounded" />
    </template>
  </Sidebar>
</template>

<script setup>
import { Sidebar } from 'frappe-ui'
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MarketingHubLogo from './Icons/MarketingHubLogo.vue'
import { useSidebar } from '@/stores/sidebar'

import IconLayoutDashboard from '~icons/lucide/layout-dashboard'
import IconMegaphone from '~icons/lucide/megaphone'
import IconShare2 from '~icons/lucide/share-2'
import IconBarChart3 from '~icons/lucide/bar-chart-2'
import IconSettings from '~icons/lucide/settings'
import IconGrid from '~icons/lucide/grid'
import IconBookOpen from '~icons/lucide/book-open'
import IconHelpCircle from '~icons/lucide/help-circle'
import IconLogOut from '~icons/lucide/log-out'

const route = useRoute()
const router = useRouter()
const { isExpanded: isCollapsed } = useSidebar()

// Get installed apps
const installedApps = computed(() => window.installed_apps || [])

// App configuration
const appConfig = {
  frappe: { label: 'Frappe Desk', icon: IconGrid, url: '/app' },
  erpnext: { label: 'ERPNext', icon: IconGrid, url: '/app' },
  crm: { label: 'CRM', icon: IconGrid, url: '/crm' },
  helpdesk: { label: 'Helpdesk', icon: IconGrid, url: '/helpdesk' },
  marketing_hub: { label: 'Marketing Hub', icon: IconMegaphone, url: '/marketing' },
  hrms: { label: 'HR', icon: IconGrid, url: '/app' },
  insights: { label: 'Insights', icon: IconGrid, url: '/insights' },
}

// User data
const userName = computed(() =>
  (typeof frappe !== 'undefined' && frappe?.session?.user_fullname) || 'User'
)

// Sidebar header with app switcher
const sidebarHeader = computed(() => ({
  title: 'Marketing Hub',
  subtitle: userName.value,
  logo: MarketingHubLogo,
  menuItems: [
    {
      group: 'Installed Apps',
      hideLabel: false,
      items: installedApps.value
        .map(app => {
          const config = appConfig[app]
          if (!config) return null
          return {
            label: config.label,
            icon: config.icon,
            onClick: () => window.location.href = config.url,
          }
        })
        .filter(Boolean),
    },
    {
      group: 'Account',
      hideLabel: false,
      items: [
        {
          label: 'My Settings',
          icon: IconSettings,
          onClick: () => window.location.href = '/app/user/' + frappe.session.user,
        },
        {
          label: 'Switch to Desk',
          icon: IconGrid,
          onClick: () => window.location.href = '/app',
        },
      ],
    },
    {
      group: 'Help',
      hideLabel: false,
      items: [
        {
          label: 'Documentation',
          icon: IconBookOpen,
          onClick: () => window.open('https://docs.erpnext.com', '_blank'),
        },
        {
          label: 'Support',
          icon: IconHelpCircle,
          onClick: () => window.open('https://discuss.erpnext.com', '_blank'),
        },
      ],
    },
    {
      group: '',
      hideLabel: true,
      items: [
        {
          label: 'Logout',
          icon: IconLogOut,
          onClick: () => window.location.href = '/api/method/logout',
        },
      ],
    },
  ],
}))

// Check if route is active
function isActiveRoute(path) {
  return route.path === path || route.path.startsWith(path + '/')
}

// Sidebar sections
const sidebarSections = computed(() => [
  {
    label: '',
    items: [
      {
        label: 'Dashboard',
        icon: IconLayoutDashboard,
        to: '/marketing',
        isActive: isActiveRoute('/marketing') && route.path === '/marketing',
        onClick: () => router.push('/marketing'),
      },
    ],
  },
  {
    label: 'Marketing',
    items: [
      {
        label: 'Campaigns',
        icon: IconMegaphone,
        to: '/marketing/campaigns',
        isActive: isActiveRoute('/marketing/campaigns'),
        onClick: () => router.push('/marketing/campaigns'),
      },
      {
        label: 'Social Media',
        icon: IconShare2,
        to: '/marketing/social',
        isActive: isActiveRoute('/marketing/social'),
        onClick: () => router.push('/marketing/social'),
      },
      {
        label: 'Analytics',
        icon: IconBarChart3,
        to: '/marketing/analytics',
        isActive: isActiveRoute('/marketing/analytics'),
        onClick: () => router.push('/marketing/analytics'),
      },
    ],
  },
])
</script>
