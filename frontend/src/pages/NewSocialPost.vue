<template>
  <div class="flex h-full flex-col overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="[
          { label: 'Social Media', route: { path: '/marketing/social' } },
          { label: 'New Post' }
        ]" />
      </template>
      <template #right-header>
        <Button variant="ghost" @click="$router.push('/marketing/social')">Cancel</Button>
        <Button variant="subtle" :loading="saving" @click="createPost('Draft')">Save as Draft</Button>
        <Button variant="solid" :loading="saving" @click="createPost('Scheduled')" :disabled="!form.scheduled_time">
          Schedule
        </Button>
      </template>
    </LayoutHeader>

    <div class="flex-1 overflow-auto">
      <div class="mx-auto max-w-4xl px-5 py-6">
        <div class="grid gap-6 lg:grid-cols-3">
          <!-- Content Column (2 cols) -->
          <div class="lg:col-span-2 space-y-6">
            <!-- Basic Info -->
            <div class="rounded-lg border border-outline-gray-1 bg-surface-cards p-6">
              <h2 class="mb-4 text-base font-medium text-ink-gray-9">Post Details</h2>
              <div class="space-y-4">
                <FormControl
                  v-model="form.post_title"
                  label="Post Title"
                  type="text"
                  placeholder="Give your post a title"
                  :required="true"
                />
                <div>
                  <label class="mb-2 block text-sm font-medium text-ink-gray-9">Content <span class="text-red-500">*</span></label>
                  <textarea
                    v-model="form.content"
                    rows="6"
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
              </div>
            </div>

            <!-- Media -->
            <div class="rounded-lg border border-outline-gray-1 bg-surface-cards p-6">
              <h2 class="mb-4 text-base font-medium text-ink-gray-9">Media</h2>
              <div class="rounded-lg border-2 border-dashed border-outline-gray-3 p-8 text-center">
                <FeatherIcon name="image" class="mx-auto h-10 w-10 text-ink-gray-4" />
                <p class="mt-2 text-sm text-ink-gray-6">Attach an image or video</p>
                <Button variant="outline" class="mt-3" @click="$refs.fileInput.click()">Choose File</Button>
                <input ref="fileInput" type="file" class="hidden" accept="image/*,video/*" @change="handleFileSelect" />
                <div v-if="form.media_attachment" class="mt-3 rounded bg-surface-gray-1 p-2 text-sm text-ink-gray-7">
                  {{ form.media_attachment }}
                </div>
              </div>
            </div>

            <!-- Targeting -->
            <div class="rounded-lg border border-outline-gray-1 bg-surface-cards p-6">
              <h2 class="mb-4 text-base font-medium text-ink-gray-9">Targeting & Tags</h2>
              <div class="space-y-4">
                <FormControl
                  v-model="form.hashtags"
                  label="Hashtags"
                  type="text"
                  placeholder="#marketing, #digital, #growth"
                />
                <FormControl
                  v-model="form.mentions"
                  label="Mentions"
                  type="text"
                  placeholder="@username1, @username2"
                />
                <FormControl
                  v-model="form.target_audience"
                  label="Target Audience"
                  type="text"
                  placeholder="Age 25-45, interests: technology"
                />
              </div>
            </div>
          </div>

          <!-- Settings Column (1 col) -->
          <div class="space-y-6">
            <!-- Platform & Campaign -->
            <div class="rounded-lg border border-outline-gray-1 bg-surface-cards p-6">
              <h3 class="mb-4 text-sm font-medium text-ink-gray-5">Publishing</h3>
              <div class="space-y-4">
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
            </div>

            <!-- Schedule -->
            <div class="rounded-lg border border-outline-gray-1 bg-surface-cards p-6">
              <h3 class="mb-4 text-sm font-medium text-ink-gray-5">Schedule</h3>
              <FormControl
                v-model="form.scheduled_time"
                label="Schedule Date & Time"
                type="datetime-local"
              />
            </div>

            <!-- Options -->
            <div class="rounded-lg border border-outline-gray-1 bg-surface-cards p-6">
              <h3 class="mb-4 text-sm font-medium text-ink-gray-5">Options</h3>
              <div class="space-y-3">
                <div class="flex items-center justify-between">
                  <span class="text-sm text-ink-gray-9">Enable Comments</span>
                  <Switch v-model="form.enable_comments" />
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-sm text-ink-gray-9">Enable Sharing</span>
                  <Switch v-model="form.enable_sharing" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Breadcrumbs, Button, FormControl, Switch, FeatherIcon, call } from 'frappe-ui'
import { toast } from '@/utils/toast'
import LayoutHeader from '@/components/LayoutHeader.vue'

const router = useRouter()
const saving = ref(false)
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
const campaigns = ref([])
const accounts = ref([])

const platformOptions = computed(() =>
  platforms.value.map(p => ({ label: p.network_name || p.name, value: p.name }))
)
const postTypeOptions = computed(() =>
  postTypes.value.map(p => ({ label: p.name, value: p.name }))
)
const campaignOptions = computed(() =>
  campaigns.value.map(c => ({ label: c.campaign_name || c.name, value: c.name }))
)
const accountOptions = computed(() =>
  accounts.value.map(a => ({ label: a.account_name || a.name, value: a.name }))
)

onMounted(async () => {
  // Load platforms
  try {
    const data = await call('frappe.client.get_list', {
      doctype: 'Social Media Network', filters: { is_active: 1 }, fields: ['name', 'network_name', 'max_character_limit'], limit_page_length: 50
    })
    platforms.value = data || []
  } catch (e) { /* ignore */ }

  // Load post types
  try {
    const data = await call('frappe.client.get_list', {
      doctype: 'Post Type', fields: ['name'], limit_page_length: 50
    })
    postTypes.value = data || []
  } catch (e) { /* ignore */ }

  // Load campaigns
  try {
    const data = await call('frappe.client.get_list', {
      doctype: 'Marketing Campaign', filters: { status: ['in', ['Draft', 'Active']] }, fields: ['name', 'campaign_name'], limit_page_length: 100
    })
    campaigns.value = data || []
  } catch (e) { /* ignore */ }

  // Load ad accounts
  try {
    const data = await call('frappe.client.get_list', {
      doctype: 'Ad Account', fields: ['name', 'account_name'], limit_page_length: 50
    })
    accounts.value = data || []
  } catch (e) { /* ignore */ }
})

function onPlatformChange() {
  const platform = platforms.value.find(p => p.name === form.value.platform)
  maxChars.value = platform?.max_character_limit || 0
}

function updateCharCount() {
  charCount.value = (form.value.content || '').length
}

function handleFileSelect(event) {
  const file = event.target.files[0]
  if (file) {
    form.value.media_attachment = file.name
    if (file.type.startsWith('video/')) {
      form.value.media_type = 'Video'
    } else if (file.type.startsWith('image/')) {
      form.value.media_type = 'Image'
    }
  }
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

  saving.value = true
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
      hashtags: form.value.hashtags || undefined,
      mentions: form.value.mentions || undefined,
      target_audience: form.value.target_audience || undefined,
      enable_comments: form.value.enable_comments ? 1 : 0,
      enable_sharing: form.value.enable_sharing ? 1 : 0,
    }

    const newDoc = await call('frappe.client.insert', { doc })

    toast({ title: 'Success', text: `Post ${status === 'Scheduled' ? 'scheduled' : 'saved as draft'}`, icon: 'check', iconClasses: 'text-ink-green-3' })
    router.push(`/marketing/social/${newDoc.name}`)
  } catch (error) {
    toast({ title: 'Error', text: error.message || 'Failed to create post', icon: 'x', iconClasses: 'text-ink-red-3' })
  } finally {
    saving.value = false
  }
}
</script>
