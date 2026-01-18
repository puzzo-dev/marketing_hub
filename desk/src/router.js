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
    path: "/marketing/analytics",
    name: "Analytics",
    component: () => import("@/pages/Analytics.vue"),
  },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});
