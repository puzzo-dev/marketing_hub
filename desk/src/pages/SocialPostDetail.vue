<template>
  <div class="flex h-full flex-col overflow-auto bg-surface-gray-1">
    <div class="flex-1 px-5 py-5 sm:px-6 lg:px-8">
      <!-- Back Button + Header -->
      <div class="mb-6">
        <button @click="$router.push('/marketing/social')" class="mb-4 flex items-center gap-1 text-sm text-ink-gray-5 hover:text-ink-gray-9 transition-colors">
          <FeatherIcon name="arrow-left" class="h-4 w-4" />
          Back to Social Posts
        </button>

        <div v-if="post.doc" class="flex items-start justify-between">
          <div>
            <h1 class="text-2xl font-bold text-ink-gray-9">{{ post.doc.post_title || 'Untitled Post' }}</h1>
            <div class="mt-2 flex items-center gap-3">
              <Badge v-if="post.doc.platform" :label="post.doc.platform" variant="subtle" theme="blue" />
              <Badge :label="post.doc.status || 'Draft'" variant="subtle"
                :theme="post.doc.status === 'Published' ? 'green' : post.doc.status === 'Failed' ? 'red' : post.doc.status === 'Scheduled' ? 'orange' : 'gray'"
              />
              <span v-if="post.doc.post_type" class="text-xs text-ink-gray-5">{{ post.doc.post_type }}</span>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <Button v-if="post.doc.status === 'Draft'" @click="publishPost" variant="solid" theme="green" size="sm">
              <template #prefix>
                <FeatherIcon name="send" class="h-3.5 w-3.5" />
              </template>
              Publish Now
            </Button>
            <Button @click="openInDesk" variant="subtle" size="sm">
              <template #prefix>
                <FeatherIcon name="external-link" class="h-3.5 w-3.5" />
              </template>
              Open in Desk
            </Button>
          </div>
        </div>
      </div>

      <div v-if="post.doc" class="grid gap-6 lg:grid-cols-3">
        <!-- Content Preview (2 cols) -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Post Content -->
          <div class="rounded-lg border border-outline-gray-1 bg-surface-cards p-6 shadow-sm">
            <h3 class="mb-3 text-sm font-semibold text-ink-gray-5 uppercase tracking-wider">Content</h3>
            <div v-if="post.doc.content" class="prose max-w-none text-sm text-ink-gray-9" v-html="post.doc.content"></div>
            <p v-else class="text-sm text-ink-gray-5 italic">No content written yet</p>
          </div>

          <!-- Media -->
          <div v-if="post.doc.media_attachment" class="rounded-lg border border-outline-gray-1 bg-surface-cards p-6 shadow-sm">
            <h3 class="mb-3 text-sm font-semibold text-ink-gray-5 uppercase tracking-wider">Media</h3>
            <img :src="post.doc.media_attachment" class="rounded-lg max-h-96 w-full object-cover" alt="Post media" />
          </div>

          <!-- Engagement Stats -->
          <div v-if="post.doc.status === 'Published'" class="rounded-lg border border-outline-gray-1 bg-surface-cards p-6 shadow-sm">
            <h3 class="mb-4 text-sm font-semibold text-ink-gray-5 uppercase tracking-wider">Engagement</h3>
            <div class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
              <div v-for="stat in engagementStats" :key="stat.label" class="text-center">
                <p class="text-xl font-bold text-ink-gray-9">{{ stat.value }}</p>
                <p class="text-xs text-ink-gray-5 mt-1">{{ stat.label }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Sidebar Info (1 col) -->
        <div class="space-y-6">
          <!-- Post Details -->
          <div class="rounded-lg border border-outline-gray-1 bg-surface-cards p-6 shadow-sm">
            <h3 class="mb-4 text-sm font-semibold text-ink-gray-5 uppercase tracking-wider">Details</h3>
            <dl class="space-y-3">
              <div>
                <dt class="text-xs text-ink-gray-5">Platform</dt>
                <dd class="text-sm font-medium text-ink-gray-9">{{ post.doc.platform || 'Not set' }}</dd>
              </div>
              <div>
                <dt class="text-xs text-ink-gray-5">Campaign</dt>
                <dd class="text-sm font-medium text-ink-gray-9">
                  <a v-if="post.doc.campaign" :href="'/marketing/campaigns/' + post.doc.campaign" class="text-ink-blue-3 hover:underline">
                    {{ post.doc.campaign }}
                  </a>
                  <span v-else class="text-ink-gray-5">None</span>
                </dd>
              </div>
              <div>
                <dt class="text-xs text-ink-gray-5">Scheduled</dt>
                <dd class="text-sm font-medium text-ink-gray-9">{{ post.doc.scheduled_time || 'Not scheduled' }}</dd>
              </div>
              <div>
                <dt class="text-xs text-ink-gray-5">Published</dt>
                <dd class="text-sm font-medium text-ink-gray-9">{{ post.doc.published_time || 'Not yet' }}</dd>
              </div>
              <div v-if="post.doc.engagement_rate">
                <dt class="text-xs text-ink-gray-5">Engagement Rate</dt>
                <dd class="text-sm font-bold text-ink-green-3">{{ post.doc.engagement_rate }}%</dd>
              </div>
            </dl>
          </div>

          <!-- Actions -->
          <div class="rounded-lg border border-outline-gray-1 bg-surface-cards p-6 shadow-sm">
            <h3 class="mb-4 text-sm font-semibold text-ink-gray-5 uppercase tracking-wider">Actions</h3>
            <div class="space-y-2">
              <Button class="w-full" variant="subtle" @click="openInDesk">
                <template #prefix><FeatherIcon name="edit-2" class="h-4 w-4" /></template>
                Edit in Desk
              </Button>
              <Button v-if="post.doc.status === 'Draft'" class="w-full" variant="subtle" 
                @click="post.setValue.submit({ status: 'Scheduled' })">
                <template #prefix><FeatherIcon name="calendar" class="h-4 w-4" /></template>
                Schedule
              </Button>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading -->
      <div v-else-if="post.loading" class="flex items-center justify-center py-20">
        <div class="h-8 w-8 animate-spin rounded-full border-2 border-ink-gray-3 border-t-transparent"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { createDocumentResource } from "frappe-ui";
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const postName = computed(() => route.params.name);

const post = createDocumentResource({
  doctype: "Social Post",
  name: postName.value,
});

const engagementStats = computed(() => {
  if (!post.doc) return [];
  return [
    { label: "Impressions", value: post.doc.impressions || 0 },
    { label: "Reach", value: post.doc.reach || 0 },
    { label: "Clicks", value: post.doc.clicks || 0 },
    { label: "Likes", value: post.doc.likes || 0 },
    { label: "Comments", value: post.doc.comments_count || 0 },
    { label: "Shares", value: post.doc.shares || 0 },
  ];
});

function publishPost() {
  post.setValue.submit({ status: 'Published' });
}

function openInDesk() {
  window.location.href = `/app/social-post/${postName.value}`;
}
</script>
