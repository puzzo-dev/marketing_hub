<template>
  <div class="flex h-full flex-col overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="breadcrumbs" />
      </template>
      <template #right-header>
        <div class="flex items-center gap-2">
          <Badge v-if="post.doc?.platform" :label="post.doc.platform" variant="subtle" theme="blue" />
          <Badge v-if="post.doc" :label="post.doc.status || 'Draft'" variant="subtle"
            :theme="post.doc.status === 'Published' ? 'green' : post.doc.status === 'Failed' ? 'red' : post.doc.status === 'Scheduled' ? 'orange' : 'gray'"
          />
          <Button v-if="post.doc?.status === 'Draft'" @click="publishPost" variant="solid" theme="green">
            <template #prefix><IconSend class="h-4 w-4" /></template>
            Publish Now
          </Button>
          <Button @click="openInDesk" variant="ghost">
            <template #prefix><IconExternalLink class="h-4 w-4" /></template>
            Open in Desk
          </Button>
        </div>
      </template>
    </LayoutHeader>

    <div v-if="post.doc" class="flex-1 overflow-auto">
      <div class="grid gap-6 p-5 lg:grid-cols-3">
        <!-- Content Preview (2 cols) -->
        <div class="lg:col-span-2 space-y-5">
          <!-- Post Content -->
          <div class="rounded-lg border border-outline-gray-1 bg-surface-white">
            <div class="border-b border-outline-gray-1 px-5 py-3">
              <h3 class="text-sm font-medium text-ink-gray-5">Content</h3>
            </div>
            <div class="px-5 py-4">
              <div v-if="post.doc.content" class="prose max-w-none text-sm text-ink-gray-9" v-html="sanitizedContent"></div>
              <p v-else class="text-sm text-ink-gray-5 italic">No content written yet</p>
            </div>
          </div>

          <!-- Media -->
          <div v-if="post.doc.media_attachment" class="rounded-lg border border-outline-gray-1 bg-surface-white">
            <div class="border-b border-outline-gray-1 px-5 py-3">
              <h3 class="text-sm font-medium text-ink-gray-5">Media</h3>
            </div>
            <div class="p-5">
              <img :src="post.doc.media_attachment" class="rounded-lg max-h-96 w-full object-cover" alt="Post media" />
            </div>
          </div>

          <!-- Engagement Stats -->
          <div v-if="post.doc.status === 'Published'" class="rounded-lg border border-outline-gray-1 bg-surface-white">
            <div class="border-b border-outline-gray-1 px-5 py-3">
              <h3 class="text-sm font-medium text-ink-gray-5">Engagement</h3>
            </div>
            <div class="grid grid-cols-2 gap-4 p-5 sm:grid-cols-3 lg:grid-cols-6">
              <div v-for="stat in engagementStats" :key="stat.label" class="text-center">
                <p class="text-lg font-semibold text-ink-gray-9">{{ stat.value }}</p>
                <p class="text-xs text-ink-gray-5 mt-1">{{ stat.label }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Sidebar Info (1 col) -->
        <div class="space-y-5">
          <!-- Post Details -->
          <div class="rounded-lg border border-outline-gray-1 bg-surface-white p-5">
            <h3 class="mb-4 text-sm font-medium text-ink-gray-5">Details</h3>
            <dl class="space-y-3">
              <div>
                <dt class="text-xs text-ink-gray-5">Platform</dt>
                <dd class="text-sm font-medium text-ink-gray-9">{{ post.doc.platform || 'Not set' }}</dd>
              </div>
              <div>
                <dt class="text-xs text-ink-gray-5">Campaign</dt>
                <dd class="text-sm font-medium text-ink-gray-9">
                  <router-link v-if="post.doc.campaign" :to="'/marketing/campaigns/' + post.doc.campaign" class="text-ink-blue-3 hover:underline">
                    {{ post.doc.campaign }}
                  </router-link>
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
          <div class="rounded-lg border border-outline-gray-1 bg-surface-white p-5">
            <h3 class="mb-4 text-sm font-medium text-ink-gray-5">Actions</h3>
            <div class="space-y-2">
              <Button class="w-full" variant="subtle" label="Edit in Desk" @click="openInDesk">
                <template #prefix><IconSquarePen class="h-4 w-4" /></template>
              </Button>
              <Button v-if="post.doc.status === 'Draft'" class="w-full" variant="subtle" label="Schedule"
                @click="post.setValue.submit({ status: 'Scheduled' })">
                <template #prefix><IconCalendar class="h-4 w-4" /></template>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-else-if="post.loading" class="flex flex-1 items-center justify-center">
      <LoadingIndicator class="h-6 w-6 text-ink-gray-5" />
    </div>

    <!-- Error -->
    <div v-else class="relative flex h-full w-full justify-center">
      <div class="absolute left-1/2 -translate-x-1/2 flex flex-col items-center gap-3" style="top: 35%">
        <IconAlertCircle class="h-10 w-10 text-ink-gray-4" />
        <span class="text-base text-ink-gray-5">Post not found</span>
        <Button label="Back to Social" variant="solid" @click="$router.push('/marketing/social')" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { Breadcrumbs, LoadingIndicator, createDocumentResource } from "frappe-ui";
import { computed } from "vue";
import { useRoute } from "vue-router";
import LayoutHeader from "../components/LayoutHeader.vue";
import IconSend from "~icons/lucide/send";
import IconExternalLink from "~icons/lucide/external-link";
import IconSquarePen from "~icons/lucide/square-pen";
import IconCalendar from "~icons/lucide/calendar";
import IconAlertCircle from "~icons/lucide/alert-circle";

const route = useRoute();
const postName = computed(() => route.params.name);

const post = createDocumentResource({
  doctype: "Social Post",
  name: postName.value,
});

const breadcrumbs = computed(() => [
  { label: "Social Media", route: { path: "/marketing/social" } },
  { label: post.doc?.post_title || postName.value },
]);

const sanitizedContent = computed(() => {
  if (!post.doc?.content) return "";
  const div = document.createElement("div");
  div.textContent = post.doc.content;
  return div.innerHTML;
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
