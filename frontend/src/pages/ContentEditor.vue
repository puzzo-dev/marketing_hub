<template>
  <div class="flex h-full flex-col">
    <!-- Header -->
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="[
          { label: 'Content', route: { path: '/marketing/content' } },
          { label: isNew ? 'New Asset' : formData.asset_name || 'Edit' }
        ]" />
      </template>
      <template #right-header>
        <Button variant="ghost" @click="$router.back()">Cancel</Button>
        <Button variant="solid" :loading="saving" @click="saveContent">Save</Button>
      </template>
    </LayoutHeader>

    <!-- Main Body -->
    <div class="flex-1 flex overflow-hidden">
      <!-- Editor Column (Left) -->
      <div class="flex-1 border-r border-outline-gray-1 overflow-y-auto">
        <div class="max-w-3xl mx-auto p-6 space-y-6">
          <FormControl
            label="Name / Title"
            v-model="formData.asset_name"
            :required="true"
            placeholder="e.g. Summer Campaign Banner"
          />

          <div v-if="formData.content_type === 'Text'">
            <label class="block text-sm font-medium text-ink-gray-9 mb-2">Content</label>
            <textarea
              v-model="formData.content_text"
              rows="15"
              class="w-full rounded-md border border-outline-gray-2 p-4 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              placeholder="Write your content here..."
            ></textarea>
            <p class="mt-1 text-sm text-ink-gray-5 flex justify-between">
              <span>Supports basic text content for emails and posts.</span>
              <span>{{ formData.content_text?.length || 0 }} chars</span>
            </p>
          </div>

          <div v-else class="rounded-lg border-2 border-dashed border-outline-gray-3 p-10 text-center">
            <div class="flex justify-center mb-4">
              <FeatherIcon name="image" class="h-10 w-10 text-ink-gray-4" />
            </div>
            <p class="text-ink-gray-6 mb-4">Upload {{ formData.content_type }} Asset</p>
            <Button variant="outline" @click="triggerUpload">Choose File</Button>
            <input
              ref="fileInput"
              type="file"
              class="hidden"
              @change="handleFileSelect"
            />
            <div v-if="formData.file_url" class="mt-4 p-2 bg-surface-gray-1 rounded text-sm text-ink-gray-7">
              Selected: {{ formData.file_url }}
            </div>
          </div>
        </div>
      </div>

      <!-- Settings Column (Right) -->
      <div class="w-80 bg-surface-gray-1 p-6 overflow-y-auto">
        <h3 class="text-sm font-medium text-ink-gray-5 mb-4">Settings</h3>
        
        <div class="space-y-6">
          <FormControl
            type="select"
            label="Type"
            v-model="formData.content_type"
            :options="[
              { label: 'Text', value: 'Text' },
              { label: 'Image', value: 'Image' },
              { label: 'Video', value: 'Video' },
            ]"
          />

          <FormControl
            type="link"
            label="Campaign"
            v-model="formData.campaign"
            doctype="Marketing Campaign"
          />

          <FormControl
            type="select"
            label="Status"
            v-model="formData.status"
            :options="[
              { label: 'Draft', value: 'Draft' },
              { label: 'Approved', value: 'Approved' },
              { label: 'Archived', value: 'Archived' },
            ]"
          />
        </div>

        <hr class="my-6 border-outline-gray-2" />

        <!-- Preview Section -->
        <div>
          <h3 class="text-sm font-medium text-ink-gray-5 mb-2">Preview</h3>
          <div class="bg-surface-white border border-outline-gray-1 rounded-lg p-4 text-sm text-ink-gray-6 min-h-[100px]">
            <div v-if="formData.content_type === 'Text'">
              {{ formData.content_text || 'No content yet...' }}
            </div>
            <div v-else class="flex items-center justify-center h-full text-ink-gray-4">
              Media Preview
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createResource, Breadcrumbs, Button, FormControl, FeatherIcon, toast } from 'frappe-ui'
import LayoutHeader from '@/components/LayoutHeader.vue'

const route = useRoute()
const router = useRouter()
const fileInput = ref(null)

const isNew = computed(() => !route.params.name)
const saving = ref(false)

const formData = ref({
  asset_name: '',
  content_type: 'Text',
  content_text: '',
  campaign: '',
  status: 'Draft',
  file_url: null
})

// Fetch existing data
const contentResource = createResource({
  url: 'marketing_hub.api.content.get_content_details',
  auto: false,
  onSuccess(data) {
    if (data.success && data.doc) {
      formData.value = { ...data.doc }
    }
  }
})

onMounted(() => {
  if (!isNew.value) {
    contentResource.fetch({ name: route.params.name })
  }
})

function triggerUpload() {
  fileInput.value.click()
}

function handleFileSelect(event) {
  const file = event.target.files[0]
  if (file) {
    formData.value.file_url = file.name
    toast({
      title: 'File Selected',
      text: 'File upload logic needed here',
      icon: 'info'
    })
  }
}

async function saveContent() {
  if (!formData.value.asset_name) {
    toast({ title: 'Error', text: 'Name is required', icon: 'x', iconClasses: 'text-ink-red-3' })
    return
  }

  saving.value = true
  try {
    if (isNew.value) {
      await window.frappe.call({
        method: 'frappe.client.insert',
        args: {
          doc: {
            doctype: 'Content Asset',
            ...formData.value
          }
        }
      })
      toast({ title: 'Success', text: 'Content created', icon: 'check', iconClasses: 'text-ink-green-3' })
      router.push({ name: 'Content' })
    } else {
      await window.frappe.call({
        method: 'frappe.client.set_value',
        args: {
          doctype: 'Content Asset',
          name: route.params.name,
          fieldname: {
            asset_name: formData.value.asset_name,
            content_type: formData.value.content_type,
            content_text: formData.value.content_text,
            campaign: formData.value.campaign,
            status: formData.value.status
          }
        }
      })
      toast({ title: 'Saved', text: 'Changes saved', icon: 'check', iconClasses: 'text-ink-green-3' })
    }
  } catch (error) {
    toast({ title: 'Error', text: error.message, icon: 'x', iconClasses: 'text-ink-red-3' })
  } finally {
    saving.value = false
  }
}
</script>
