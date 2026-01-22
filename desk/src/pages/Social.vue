<template>
  <div class="flex h-full flex-col overflow-auto bg-white">
    <div class="flex-1 px-5 py-5 sm:px-6 lg:px-8">
      <div class="mb-5 flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">Social Media Posts</h1>
        <p class="mt-1 text-sm text-gray-600">Manage your social media content</p>
      </div>
      <Button @click="$router.push('/marketing/social/new')">
        <template #prefix>
          <FeatherIcon name="plus" class="h-4 w-4" />
        </template>
        Create Post
      </Button>
    </div>

    <!-- Stats -->
    <div class="mb-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
      <div class="stat-card">
        <div class="text-sm font-medium text-gray-500">Total Posts</div>
        <div class="mt-2 text-3xl font-bold text-gray-900">
          {{ stats.total_posts }}
        </div>
      </div>
      <div class="stat-card">
        <div class="text-sm font-medium text-gray-500">Scheduled</div>
        <div class="mt-2 text-3xl font-bold text-orange-600">
          {{ stats.scheduled }}
        </div>
      </div>
      <div class="stat-card">
        <div class="text-sm font-medium text-gray-500">Published</div>
        <div class="mt-2 text-3xl font-bold text-green-600">
          {{ stats.published }}
        </div>
      </div>
      <div class="stat-card">
        <div class="text-sm font-medium text-gray-500">Engagement Rate</div>
        <div class="mt-2 text-3xl font-bold text-gray-900">
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
    <div v-if="filteredPosts.length" class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      <div v-for="post in filteredPosts" :key="post.name" class="post-card">
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

        <h3 class="mb-1 font-semibold text-gray-900">{{ post.post_title }}</h3>
        <p class="mb-3 text-sm text-gray-600">
          {{ post.content.slice(0, 120) }}
          {{ post.content.length > 120 ? "..." : "" }}
        </p>

        <img
          v-if="post.media_attachment"
          :src="post.media_attachment"
          alt="Post media"
          class="mb-3 rounded"
        />

        <div class="space-y-1 text-sm text-gray-500">
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
          class="mt-3 grid grid-cols-2 gap-2 border-t pt-3 text-sm"
        >
          <div>
            <div class="text-gray-500">Impressions</div>
            <div class="font-semibold">{{ formatNumber(post.impressions) }}</div>
          </div>
          <div>
            <div class="text-gray-500">Engagement</div>
            <div class="font-semibold">{{ post.engagement_rate }}%</div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="rounded-lg border-2 border-dashed p-12 text-center">
      <FeatherIcon name="share-2" class="mx-auto h-12 w-12 text-gray-400" />
      <h3 class="mt-2 text-sm font-medium text-gray-900">No social posts yet</h3>
      <p class="mt-1 text-sm text-gray-500">
        Create your first post to start engaging with your audience
      </p>
      <Button class="mt-4" @click="$router.push('/marketing/social/new')">
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

const socialResource = createResource({
  url: "marketing_hub.www.marketing.social.index.get_context",
  auto: true,
});

const stats = computed(() => socialResource.data?.stats || {
  total_posts: 0,
  scheduled: 0,
  published: 0,
  engagement_rate: 0,
});

const posts = computed(() => socialResource.data?.posts || []);

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
</script>
