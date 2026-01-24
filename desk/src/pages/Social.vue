<template>
  <div class="flex h-full flex-col overflow-auto bg-surface-gray-1">
    <div class="flex-1 px-5 py-5 sm:px-6 lg:px-8">
      <div class="mb-5 flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-ink-gray-9">Social Media Posts</h1>
        <p class="mt-1 text-sm text-ink-gray-6">Manage your social media content</p>
      </div>
      <Button @click="createNewPost">
        <template #prefix>
          <FeatherIcon name="plus" class="h-4 w-4" />
        </template>
        Create Post
      </Button>
    </div>

    <!-- Stats -->
    <div class="mb-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
      <div class="rounded-lg border border-outline-gray-1 bg-surface-cards p-5 shadow-sm">
        <div class="text-sm font-medium text-ink-gray-5">Total Posts</div>
        <div class="mt-2 text-3xl font-bold text-ink-gray-9">
          {{ stats.total_posts }}
        </div>
      </div>
      <div class="rounded-lg border border-outline-gray-1 bg-surface-cards p-5 shadow-sm">
        <div class="text-sm font-medium text-ink-gray-5">Scheduled</div>
        <div class="mt-2 text-3xl font-bold text-ink-amber-2">
          {{ stats.scheduled }}
        </div>
      </div>
      <div class="rounded-lg border border-outline-gray-1 bg-surface-cards p-5 shadow-sm">
        <div class="text-sm font-medium text-ink-gray-5">Published</div>
        <div class="mt-2 text-3xl font-bold text-ink-green-2">
          {{ stats.published }}
        </div>
      </div>
      <div class="rounded-lg border border-outline-gray-1 bg-surface-cards p-5 shadow-sm">
        <div class="text-sm font-medium text-ink-gray-5">Engagement Rate</div>
        <div class="mt-2 text-3xl font-bold text-ink-gray-9">
          {{ stats.engagement_rate }}%
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="mb-4 flex space-x-2">
      <Button
        v-for="filter in filters"
        :key="filter.value"
        :variant="activeFilter === filter.value ? 'solid' : 'ghost'"
        size="sm"
        @click="activeFilter = filter.value"
      >
        {{ filter.label }}
      </Button>
    </div>

    <!-- Posts -->
    <div v-if="postsResource.loading" class="flex items-center justify-center py-12">
      <div class="text-center">
        <div class="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-ink-gray-3 border-t-red-600"></div>
        <p class="mt-2 text-sm text-ink-gray-5">Loading posts...</p>
      </div>
    </div>

    <div v-else-if="filteredPosts.length" class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      <div v-for="post in filteredPosts" :key="post.name" class="rounded-lg border border-outline-gray-1 bg-surface-cards p-5 shadow-sm transition-shadow hover:shadow-md">
        <div class="mb-2 flex items-start justify-between">
          <div class="flex space-x-2">
            <Badge :label="post.platform" variant="subtle" theme="blue" />
            <Badge
              :label="post.status"
              :variant="
                post.status === 'Published'
                  ? 'success'
                  : post.status === 'Scheduled'
                  ? 'warning'
                  : 'subtle'
              "
            />
          </div>
          <Button variant="ghost" size="sm" @click="editPost(post.name)">
            <FeatherIcon name="edit-2" class="h-4 w-4" />
          </Button>
        </div>

        <h3 class="mb-1 font-semibold text-ink-gray-9">{{ post.post_title }}</h3>
        <p class="mb-3 text-sm text-ink-gray-6">
          {{ post.content.slice(0, 120) }}
          {{ post.content.length > 120 ? "..." : "" }}
        </p>

        <img
          v-if="post.media_attachment"
          :src="post.media_attachment"
          alt="Post media"
          class="mb-3 rounded"
        />

        <div class="space-y-1 text-sm text-ink-gray-5">
          <div v-if="post.scheduled_time" class="flex items-center">
            <FeatherIcon name="clock" class="mr-1 h-4 w-4" />
            {{ formatDateTime(post.scheduled_time) }}
          </div>
          <div v-if="post.campaign" class="flex items-center">
            <FeatherIcon name="target" class="mr-1 h-4 w-4" />
            {{ post.campaign }}
          </div>
        </div>

        <div
          v-if="post.status === 'Published' && post.impressions"
          class="mt-3 grid grid-cols-2 gap-2 border-t border-outline-gray-1 pt-3 text-sm"
        >
          <div>
            <div class="text-ink-gray-5">Impressions</div>
            <div class="font-semibold text-ink-gray-9">{{ formatNumber(post.impressions) }}</div>
          </div>
          <div>
            <div class="text-ink-gray-5">Engagement</div>
            <div class="font-semibold text-ink-gray-9">{{ post.engagement_rate }}%</div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="rounded-lg border-2 border-dashed border-outline-gray-2 bg-surface-cards p-12 text-center">
      <FeatherIcon name="share-2" class="mx-auto h-12 w-12 text-gray-400" />
      <h3 class="mt-2 text-sm font-medium text-gray-900">No social posts yet</h3>
      <p class="mt-1 text-sm text-gray-500">
        Create your first post to start engaging with your audience
      </p>
      <Button class="mt-4" @click="createNewPost">
        <template #prefix>
          <FeatherIcon name="plus" class="h-4 w-4" />
        </template>
        Create Post
      </Button>
    </div>
    </div>
  </div>
</template>

<script setup>
import { createResource } from "frappe-ui";
import { computed, ref } from "vue";

// Fetch social posts
const postsResource = createResource({
  url: "marketing_hub.www.marketing.index.get_social_posts",
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
  window.location.href = `/app/social-post/${name}`;
}

function createNewPost() {
  window.location.href = `/app/social-post/new`;
}
</script>
