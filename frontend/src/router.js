import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/marketing",
    name: "Dashboard",
    component: () => import("@/pages/Dashboard.vue"),
  },
  {
    path: "/marketing/campaigns",
    name: "Campaigns",
    component: () => import("@/pages/Campaigns.vue"),
  },
  {
    path: "/marketing/campaigns/new",
    name: "NewCampaign",
    component: () => import("@/pages/NewCampaign.vue"),
  },
  {
    path: "/marketing/campaigns/:name",
    name: "CampaignDetail",
    component: () => import("@/pages/CampaignDetail.vue"),
  },
  {
    path: "/marketing/social",
    name: "Social",
    component: () => import("@/pages/Social.vue"),
  },
  {
    path: "/marketing/social/new",
    name: "NewSocialPost",
    component: () => import("@/pages/NewSocialPost.vue"),
  },
  {
    path: "/marketing/social/:name",
    name: "SocialPostDetail",
    component: () => import("@/pages/SocialPostDetail.vue"),
  },
  {
    path: "/marketing/analytics",
    name: "Analytics",
    component: () => import("@/pages/Analytics.vue"),
  },
  {
    path: "/marketing/connectors",
    name: "AnalyticsConnectors",
    component: () => import("@/pages/AnalyticsConnectors.vue"),
  },
  {
    path: "/marketing/connectors/:name",
    name: "AnalyticsConnectorDetail",
    component: () => import("@/pages/AnalyticsConnectorDetail.vue"),
  },
  {
    path: "/marketing/activities",
    name: "Activities",
    component: () => import("@/pages/Activities.vue"),
  },
  {
    path: "/marketing/activities/:name",
    name: "ActivityDetail",
    component: () => import("@/pages/ActivityDetail.vue"),
  },
  {
    path: "/marketing/blasts",
    name: "Blasts",
    component: () => import("@/pages/Blasts.vue"),
  },
  {
    path: "/marketing/blast/new",
    name: "OmniBlast",
    component: () => import("@/pages/OmniBlast.vue"),
  },
  {
    path: "/marketing/segments",
    name: "Segments",
    component: () => import("@/pages/Segments.vue"),
  },
  {
    path: "/marketing/content",
    name: "Content",
    component: () => import("@/pages/Content.vue"),
  },
  {
    path: "/marketing/content/new",
    name: "NewContent",
    component: () => import("@/pages/ContentEditor.vue"),
  },
  {
    path: "/marketing/content/:name",
    name: "EditContent",
    component: () => import("@/pages/ContentEditor.vue"),
  },
  {
    path: "/marketing/expenses",
    name: "Expenses",
    component: () => import("@/pages/Expenses.vue"),
  },
  {
    path: "/marketing/tracking",
    name: "TrackingLinks",
    component: () => import("@/pages/TrackingLinks.vue"),
  },
  {
    path: "/marketing/leads",
    name: "Leads",
    component: () => import("@/pages/Leads.vue"),
  },
  {
    path: "/marketing/clients",
    name: "Clients",
    component: () => import("@/pages/Clients.vue"),
  },
  {
    path: "/marketing/clients/:name",
    name: "ClientDetail",
    component: () => import("@/pages/ClientDetail.vue"),
  },
  {
    path: "/marketing/settings",
    name: "Settings",
    component: () => import("@/pages/Settings.vue"),
  },
  // Catch-all: redirect unknown paths to dashboard
  {
    path: "/marketing/:pathMatch(.*)*",
    redirect: "/marketing",
  },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});
