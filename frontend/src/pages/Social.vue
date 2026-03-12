<template>
  <div class="flex h-full flex-col overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="[{ label: 'Marketing Hub' }, { label: 'Social Media' }]" />
      </template>
      <template #right-header>
        <Button @click="openCreateDialog" variant="solid" label="Create Post">
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

      <!-- Loading State -->
      <div v-if="postsResource.loading" class="flex items-center justify-center py-12">
        <LoadingIndicator class="h-6 w-6" />
      </div>

      <!-- Empty State -->
      <div v-else-if="!filteredPosts.length" class="relative flex h-full w-full justify-center">
        <div class="absolute left-1/2 flex w-4/12 -translate-x-1/2 flex-col items-center gap-3" style="top: 35%">
          <IconShare2 class="h-7 w-7 text-ink-gray-5" />
          <span class="text-base font-medium text-ink-gray-8">No social posts yet</span>
          <span class="text-center text-sm text-ink-gray-6">Create your first post to start engaging with your audience</span>
          <Button @click="openCreateDialog" variant="solid" label="Create Post">
            <template #prefix>
              <IconPlus class="h-4 w-4" />
            </template>
          </Button>
        </div>
      </div>
    </div>

    <!-- Create Social Post Dialog -->
    <Dialog
      v-model="showCreateDialog"
      :options="{ title: 'Create Social Post', size: '3xl' }"
      :disableOutsideClickToClose="true"
    >
      <template #body-content>
        <div class="space-y-5">
          <!-- Post Title -->
          <FormControl
            v-model="form.post_title"
            label="Post Title"
            type="text"
            placeholder="Give your post a title"
            :required="true"
          />

          <!-- Content -->
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink-gray-9">Content <span class="text-red-500">*</span></label>
            <textarea
              v-model="form.content"
              rows="5"
              class="w-full rounded-md border border-outline-gray-2 p-3 text-sm focus:border-outline-gray-4 focus:outline-none focus:ring-1 focus:ring-outline-gray-4"
              placeholder="Write your post content..."
              @input="updateCharCount"
            ></textarea>
            <div class="mt-1 flex justify-between text-xs text-ink-gray-5">
              <span v-if="maxChars">{{ charCount }}/{{ maxChars }} characters</span>
              <span v-else>{{ charCount }} characters</span>
              <span v-if="maxChars && charCount > maxChars" class="text-ink-red-3">Exceeds limit</span>
            </div>
          </div>

          <!-- Platform & Type -->
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <FormControl
              v-model="form.platform"
              label="Platform"
              type="autocomplete"
              :options="platformOptions"
              placeholder="Select platform"
              :required="true"
              @change="onPlatformChange"
            />
            <FormControl
              v-model="form.post_type"
              label="Post Type"
              type="autocomplete"
              :options="postTypeOptions"
              placeholder="Select type"
              :required="true"
            />
          </div>

          <!-- Campaign & Account -->
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <FormControl
              v-model="form.campaign"
              label="Campaign"
              type="autocomplete"
              :options="campaignOptions"
              placeholder="Link to campaign (optional)"
            />
            <FormControl
              v-model="form.account"
              label="Account"
              type="autocomplete"
              :options="accountOptions"
              placeholder="Select ad account"
            />
          </div>

          <!-- Media Upload (Frappe file upload) -->
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink-gray-9">Media Attachment</label>
            <div class="rounded-lg border-2 border-dashed border-outline-gray-3 p-5 text-center">
              <div v-if="form.media_attachment" class="flex items-center justify-between rounded-md bg-surface-gray-1 p-3">
                <div class="flex items-center gap-2">
                  <FeatherIcon :name="form.media_type === 'Video' ? 'video' : 'image'" class="h-5 w-5 text-ink-gray-5" />
                  <span class="text-sm text-ink-gray-7">{{ uploadedFileName }}</span>
                </div>
                <Button variant="ghost" size="sm" @click="removeMedia">
                  <FeatherIcon name="x" class="h-4 w-4" />
                </Button>
              </div>
              <div v-else-if="uploading" class="py-2">
                <LoadingIndicator class="mx-auto h-5 w-5" />
                <p class="mt-1 text-sm text-ink-gray-6">Uploading...</p>
              </div>
              <div v-else>
                <FeatherIcon name="image" class="mx-auto h-8 w-8 text-ink-gray-4" />
                <p class="mt-1 text-sm text-ink-gray-6">Attach an image or video</p>
                <Button variant="outline" size="sm" class="mt-2" @click="$refs.fileInputSocial.click()">Choose File</Button>
                <input ref="fileInputSocial" type="file" class="hidden" accept="image/*,video/*" @change="handleFileUpload" />
              </div>
            </div>
          </div>

          <!-- Schedule -->
          <FormControl
            v-model="form.scheduled_time"
            label="Schedule Date & Time"
            type="datetime-local"
          />

          <!-- Targeting -->
          <div>
            <h3 class="mb-3 text-sm font-medium text-ink-gray-5">Targeting & Tags</h3>
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <FormControl v-model="form.hashtags" label="Hashtags" type="text" placeholder="#marketing, #digital" />
              <FormControl v-model="form.mentions" label="Mentions" type="text" placeholder="@username1" />
              <FormControl v-model="form.target_audience" label="Target Audience" type="text" placeholder="Age 25-45" />
            </div>
          </div>

          <!-- Options -->
          <div class="flex items-center gap-6">
            <div class="flex items-center gap-2">
              <span class="text-sm text-ink-gray-9">Comments</span>
              <Switch v-model="form.enable_comments" />
            </div>
            <div class="flex items-center gap-2">
              <span class="text-sm text-ink-gray-9">Sharing</span>
              <Switch v-model="form.enable_sharing" />
            </div>
          </div>
        </div>
      </template>
      <template #actions="{ close }">
        <div class="flex w-full justify-end gap-2">
          <Button variant="ghost" @click="close">Cancel</Button>
          <Button variant="subtle" :loading="savingPost" @click="createPost('Draft')">Save as Draft</Button>
          <Button variant="solid" :loading="savingPost" @click="createPost('Scheduled')" :disabled="!form.scheduled_time">Schedule</Button>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { Breadcrumbs, createResource, LoadingIndicator, Dialog, Button, FormControl, Switch, FeatherIcon, call } from "frappe-ui";
import { toast } from '@/utils/toast'
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

// === Create Post Dialog ===
const showCreateDialog = ref(false)
const savingPost = ref(false)
const uploading = ref(false)
const uploadedFileName = ref('')
const charCount = ref(0)
const maxChars = ref(0)

const form = ref({
  post_title: '',
  content: '',
  platform: '',
  post_type: '',
  campaign: '',
  account: '',
  scheduled_time: '',
  media_attachment: null,
  media_type: '',
  hashtags: '',
  mentions: '',
  target_audience: '',
  enable_comments: true,
  enable_sharing: true,
})

const platforms = ref([])
const postTypes = ref([])
const dialogCampaigns = ref([])
const accounts = ref([])

const platformOptions = computed(() => platforms.value.map(p => ({ label: p.network_name || p.name, value: p.name })))
const postTypeOptions = computed(() => postTypes.value.map(p => ({ label: p.name, value: p.name })))
const campaignOptions = computed(() => dialogCampaigns.value.map(c => ({ label: c.campaign_name || c.name, value: c.name })))
const accountOptions = computed(() => accounts.value.map(a => ({ label: a.account_name || a.name, value: a.name })))

function onPlatformChange() {
  const platform = platforms.value.find(p => p.name === form.value.platform)
  maxChars.value = platform?.max_character_limit || 0
}

function updateCharCount() {
  charCount.value = (form.value.content || '').length
}

async function openCreateDialog() {
  showCreateDialog.value = true
  form.value = {
    post_title: '', content: '', platform: '', post_type: '', campaign: '',
    account: '', scheduled_time: '', media_attachment: null, media_type: '',
    hashtags: '', mentions: '', target_audience: '',
    enable_comments: true, enable_sharing: true,
  }
  charCount.value = 0
  maxChars.value = 0
  uploadedFileName.value = ''

  try {
    const [platData, typeData, campData, acctData] = await Promise.all([
      call('frappe.client.get_list', { doctype: 'Social Media Network', filters: { is_active: 1 }, fields: ['name', 'network_name', 'max_character_limit'], limit_page_length: 50 }),
      call('frappe.client.get_list', { doctype: 'Post Type', fields: ['name'], limit_page_length: 50 }),
      call('frappe.client.get_list', { doctype: 'Marketing Campaign', filters: { status: ['in', ['Draft', 'Active']] }, fields: ['name', 'campaign_name'], limit_page_length: 100 }),
      call('frappe.client.get_list', { doctype: 'Ad Account', fields: ['name', 'account_name'], limit_page_length: 50 }),
    ])
    platforms.value = platData || []
    postTypes.value = typeData || []
    dialogCampaigns.value = campData || []
    accounts.value = acctData || []
  } catch (e) { /* ignore */ }
}

async function handleFileUpload(event) {
  const file = event.target.files[0]
  if (!file) return

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('is_private', '0')
    formData.append('folder', 'Home/Marketing Hub')

    const response = await fetch('/api/method/upload_file', {
      method: 'POST',
      body: formData,
      headers: { 'X-Frappe-CSRF-Token': window.csrf_token },
    })
    const result = await response.json()

    if (result.message) {
      form.value.media_attachment = result.message.file_url
      uploadedFileName.value = result.message.file_name || file.name
      if (file.type.startsWith('video/')) {
        form.value.media_type = 'Video'
      } else if (file.type.startsWith('image/')) {
        form.value.media_type = 'Image'
      }
      toast({ title: 'Uploaded', text: 'File uploaded successfully', icon: 'check', iconClasses: 'text-ink-green-3' })
    }
  } catch (error) {
    toast({ title: 'Error', text: 'Failed to upload file', icon: 'x', iconClasses: 'text-ink-red-3' })
  } finally {
    uploading.value = false
  }
}

function removeMedia() {
  form.value.media_attachment = null
  form.value.media_type = ''
  uploadedFileName.value = ''
}

async function createPost(status) {
  if (!form.value.post_title) {
    toast({ title: 'Error', text: 'Post title is required', icon: 'x', iconClasses: 'text-ink-red-3' })
    return
  }
  if (!form.value.content) {
    toast({ title: 'Error', text: 'Post content is required', icon: 'x', iconClasses: 'text-ink-red-3' })
    return
  }
  if (!form.value.platform) {
    toast({ title: 'Error', text: 'Platform is required', icon: 'x', iconClasses: 'text-ink-red-3' })
    return
  }
  if (!form.value.post_type) {
    toast({ title: 'Error', text: 'Post type is required', icon: 'x', iconClasses: 'text-ink-red-3' })
    return
  }
  if (status === 'Scheduled' && !form.value.scheduled_time) {
    toast({ title: 'Error', text: 'Schedule time is required', icon: 'x', iconClasses: 'text-ink-red-3' })
    return
  }

  savingPost.value = true
  try {
    const doc = {
      doctype: 'Social Post',
      post_title: form.value.post_title,
      content: form.value.content,
      platform: form.value.platform,
      post_type: form.value.post_type,
      status: status,
      campaign: form.value.campaign || undefined,
      account: form.value.account || undefined,
      scheduled_time: form.value.scheduled_time || undefined,
      media_attachment: form.value.media_attachment || undefined,
      media_type: form.value.media_type || undefined,
      hashtags: form.value.hashtags || undefined,
      mentions: form.value.mentions || undefined,
      target_audience: form.value.target_audience || undefined,
      enable_comments: form.value.enable_comments ? 1 : 0,
      enable_sharing: form.value.enable_sharing ? 1 : 0,
    }

    const newDoc = await call('frappe.client.insert', { doc })
    toast({ title: 'Success', text: `Post ${status === 'Scheduled' ? 'scheduled' : 'saved as draft'}`, icon: 'check', iconClasses: 'text-ink-green-3' })
    showCreateDialog.value = false
    postsResource.fetch()
    router.push(`/marketing/social/${newDoc.name}`)
  } catch (error) {
    toast({ title: 'Error', text: error.message || 'Failed to create post', icon: 'x', iconClasses: 'text-ink-red-3' })
  } finally {
    savingPost.value = false
  }
}
</script>
