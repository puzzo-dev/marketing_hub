<template>
  <div class="flex h-full flex-col overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="[{ label: 'Marketing Hub' }, { label: 'Social Media' }]" />
      </template>
      <template #right-header>
        <Button @click="createNewPost" variant="solid" label="Create Post">
          <template #prefix>
            <IconPlus class="h-4 w-4" />
          </template>
        </Button>
      </template>
    </LayoutHeader>

    <!-- Stats + Filter Bar -->
    <div class="flex items-center justify-between border-b px-5 py-3">
      <div class="flex items-center gap-5 text-sm">
        <div><span class="text-ink-gray-5">Total</span> <span class="ml-1 font-medium text-ink-gray-9">{{ stats.total_posts }}</span></div>
        <div><span class="text-ink-gray-5">Scheduled</span> <span class="ml-1 font-medium text-ink-orange-3">{{ stats.scheduled }}</span></div>
        <div><span class="text-ink-gray-5">Published</span> <span class="ml-1 font-medium text-ink-green-3">{{ stats.published }}</span></div>
        <div><span class="text-ink-gray-5">Engagement</span> <span class="ml-1 font-medium text-ink-gray-9">{{ stats.engagement_rate }}%</span></div>
      </div>
      <div class="flex gap-1.5">
        <Button
          v-for="filter in filters"
          :key="filter.value"
          :variant="activeFilter === filter.value ? 'subtle' : 'ghost'"
          size="sm"
          :label="filter.label"
          @click="activeFilter = filter.value"
        />
      </div>
    </div>

    <!-- Content Area -->
    <div class="flex-1 overflow-auto p-5">
      <!-- Loading -->
      <div v-if="postsResource.loading" class="flex items-center justify-center py-12">
        <LoadingIndicator class="h-6 w-6" />
      </div>

      <!-- Posts Grid -->
      <div v-else-if="filteredPosts.length" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div v-for="post in filteredPosts" :key="post.name"
          class="cursor-pointer rounded-lg border border-outline-gray-1 bg-surface-white p-4 shadow-sm transition-shadow hover:shadow"
          @click="editPost(post.name)"
        >
          <div class="mb-2 flex items-start justify-between">
            <div class="flex gap-1.5">
              <Badge :label="post.platform" variant="subtle" theme="blue" />
              <Badge :label="post.status" variant="subtle"
                :theme="post.status === 'Published' ? 'green' : post.status === 'Scheduled' ? 'orange' : 'gray'"
              />
            </div>
          </div>

          <h4 class="mb-1 text-base font-medium text-ink-gray-9">{{ post.post_title }}</h4>
          <p class="mb-3 text-sm text-ink-gray-6 line-clamp-2">{{ post.content }}</p>

          <img v-if="post.media_attachment" :src="post.media_attachment" alt="" class="mb-3 rounded" />

          <div class="space-y-1 text-sm text-ink-gray-5">
            <div v-if="post.scheduled_time" class="flex items-center gap-1">
              <IconClock class="h-3.5 w-3.5" />
              {{ formatDateTime(post.scheduled_time) }}
            </div>
            <div v-if="post.campaign" class="flex items-center gap-1">
              <IconTarget class="h-3.5 w-3.5" />
              {{ post.campaign }}
            </div>
          </div>

          <div v-if="post.status === 'Published' && post.impressions"
            class="mt-3 grid grid-cols-2 gap-2 border-t border-outline-gray-1 pt-3 text-sm"
          >
            <div>
              <div class="text-xs text-ink-gray-5">Impressions</div>
              <div class="font-medium text-ink-gray-9">{{ formatNumber(post.impressions) }}</div>
            </div>
            <div>
              <div class="text-xs text-ink-gray-5">Engagement</div>
              <div class="font-medium text-ink-gray-9">{{ post.engagement_rate }}%</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="relative flex h-full w-full justify-center">
        <div class="absolute left-1/2 flex w-4/12 -translate-x-1/2 flex-col items-center gap-3" style="top: 35%">
          <IconShare2 class="h-7 w-7 text-ink-gray-5" />
          <span class="text-lg font-medium text-ink-gray-8">No social posts yet</span>
          <span class="text-center text-sm text-ink-gray-6">Create your first post to start engaging with your audience</span>
          <Button @click="createNewPost" variant="solid" label="Create Post">
            <template #prefix>
              <IconPlus class="h-4 w-4" />
            </template>
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Breadcrumbs, createResource, LoadingIndicator } from "frappe-ui";
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import LayoutHeader from "@/components/LayoutHeader.vue";

import IconPlus from '~icons/lucide/plus'
import IconClock from '~icons/lucide/clock'
import IconTarget from '~icons/lucide/target'
import IconShare2 from '~icons/lucide/share-2'

const router = useRouter();

// Fetch social posts
const postsResource = createResource({
  url: "marketing_hub.api.social.get_social_posts",
  params: {
    filters: {},
    limit: 20,
    offset: 0
  },
  auto: true,
});

const posts = computed(() => postsResource.data?.posts || []);

// Calculate stats from posts
const stats = computed(() => {
  const allPosts = posts.value;
  const scheduled = allPosts.filter(p => p.status === "Scheduled").length;
  const published = allPosts.filter(p => p.status === "Published").length;
  const totalEngagement = allPosts
    .filter(p => p.engagement_rate)
    .reduce((sum, p) => sum + (parseFloat(p.engagement_rate) || 0), 0);
  const avgEngagement = allPosts.filter(p => p.engagement_rate).length > 0
    ? (totalEngagement / allPosts.filter(p => p.engagement_rate).length).toFixed(1)
    : 0;

  return {
    total_posts: allPosts.length,
    scheduled,
    published,
    engagement_rate: avgEngagement,
  };
});

const activeFilter = ref("all");
const filters = [
  { label: "All", value: "all" },
  { label: "Draft", value: "Draft" },
  { label: "Scheduled", value: "Scheduled" },
  { label: "Published", value: "Published" },
];

const filteredPosts = computed(() => {
  if (activeFilter.value === "all") return posts.value;
  return posts.value.filter((p) => p.status === activeFilter.value);
});

function formatDateTime(datetime) {
  if (!datetime) return "";
  return new Date(datetime).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function formatNumber(num) {
  return new Intl.NumberFormat("en-US").format(num || 0);
}

function editPost(name) {
  router.push('/marketing/social/' + name);
}

function createNewPost() {
  router.push('/marketing/social/new');
}
</script>
