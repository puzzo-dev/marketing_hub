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
import { useUserStore } from '@/stores/user'
import { useConfigStore } from '@/stores/config'

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
import IconSend from '~icons/lucide/send'
import IconUsers from '~icons/lucide/users'
import IconFileText from '~icons/lucide/file-text'
import IconBuilding from '~icons/lucide/building-2'
import IconCreditCard from '~icons/lucide/credit-card'

const route = useRoute()
const router = useRouter()
const { isExpanded: isCollapsed } = useSidebar()
const userStore = useUserStore()
const configStore = useConfigStore()

// Get installed apps with their full metadata (logo, title, route)
// We still rely on window.installed_apps injection from index.py for now as it's boot data
const installedApps = computed(() => window.installed_apps || [])

// Get Marketing Hub logo from the installed apps
const marketingHubLogo = computed(() => {
  const marketingHub = installedApps.value.find(app => app.name === 'marketing_hub')
  return marketingHub?.logo || null
})

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
  subtitle: userStore.name,
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
const sidebarSections = computed(() => {
  const sections = [
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
          label: 'Omni Blast',
          icon: IconSend,
          to: '/marketing/blast/new',
          isActive: isActiveRoute('/marketing/blast'),
          onClick: () => router.push('/marketing/blast/new'),
        },
        {
          label: 'Segments',
          icon: IconUsers,
          to: '/marketing/segments',
          isActive: isActiveRoute('/marketing/segments'),
          onClick: () => router.push('/marketing/segments'),
        },
        {
          label: 'Content',
          icon: IconFileText,
          to: '/marketing/content',
          isActive: isActiveRoute('/marketing/content'),
          onClick: () => router.push('/marketing/content'),
        },
        {
          label: 'Expenses',
          icon: IconBarChart3,
          to: '/marketing/expenses',
          isActive: isActiveRoute('/marketing/expenses'),
          onClick: () => router.push('/marketing/expenses'),
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
  ]

  // Agency mode: show Clients & Subscriptions section for admins
  if (configStore.isAgencyMode) {
    sections.push({
      label: 'Agency',
      items: [
        {
          label: 'Clients',
          icon: IconBuilding,
          to: '/marketing/clients',
          isActive: isActiveRoute('/marketing/clients'),
          onClick: () => router.push('/marketing/clients'),
        },
        {
          label: 'Subscriptions',
          icon: IconCreditCard,
          to: '/marketing/subscriptions',
          isActive: isActiveRoute('/marketing/subscriptions'),
          onClick: () => router.push('/marketing/subscriptions'),
        },
      ],
    })
  }

  sections.push({
    label: 'System',
    items: [
      {
        label: 'Settings',
        icon: IconSettings,
        to: '/marketing/settings',
        isActive: isActiveRoute('/marketing/settings'),
        onClick: () => router.push('/marketing/settings'),
      },
    ],
  })

  return sections
})
</script>
