<template>
  <Sidebar
    :header="sidebarHeader"
    :sections="sidebarSections"
    v-model:collapsed="isCollapsed"
  >
    <template #header-logo>
      <img 
        v-if="marketingHubLogo" 
        :src="marketingHubLogo" 
        class="h-full w-full rounded object-contain" 
        alt="Marketing Hub"
      />
      <MarketingHubLogo v-else class="h-full w-full rounded" />
    </template>
  </Sidebar>
</template>

<script setup>
import { Sidebar } from 'frappe-ui'
import { computed, h } from 'vue'
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
import IconChevronRight from '~icons/lucide/chevron-right'

const route = useRoute()
const router = useRouter()
const { isExpanded: isCollapsed } = useSidebar()

// Get installed apps with their full metadata (logo, title, route)
const installedApps = computed(() => window.installed_apps || [])

// Get Marketing Hub logo from the installed apps
const marketingHubLogo = computed(() => {
  const marketingHub = installedApps.value.find(app => app.name === 'marketing_hub')
  return marketingHub?.logo || null
})

// User data
const userName = computed(() =>
  (typeof frappe !== 'undefined' && frappe?.session?.user_fullname) || 'User'
)

// Create app icon component using h() render function
const createAppIcon = (logoUrl) => {
  if (!logoUrl) return IconGrid
  
  // Return a functional component using h()
  return {
    name: 'AppIcon',
    render() {
      return h('img', {
        src: logoUrl,
        class: 'h-4 w-4 object-contain',
        alt: 'App icon'
      })
    }
  }
}

// Sidebar header with app switcher
const sidebarHeader = computed(() => ({
  title: 'Marketing Hub',
  subtitle: userName.value,
  logo: MarketingHubLogo,
  menuItems: [
    {
      label: 'Apps',
      icon: IconGrid,
      submenu: installedApps.value.map(app => ({
        label: app.title,
        icon: createAppIcon(app.logo),
        onClick: () => window.location.href = app.route,
      })),
    },
    {
      label: 'Settings',
      icon: IconSettings,
      onClick: () => window.location.href = '/app/user/' + frappe.session.user,
    },
    {
      label: 'Help',
      icon: IconHelpCircle,
      submenu: [
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
      label: 'Logout',
      icon: IconLogOut,
      onClick: () => window.location.href = '/api/method/logout',
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
