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
              class="w-full rounded-md border border-outline-gray-2 p-4 text-sm focus:border-outline-gray-4 focus:outline-none focus:ring-1 focus:ring-outline-gray-4"
              placeholder="Write your content here..."
            ></textarea>
            <p class="mt-1 text-sm text-ink-gray-5 flex justify-between">
              <span>Supports basic text content for emails and posts.</span>
              <span>{{ formData.content_text?.length || 0 }} chars</span>
            </p>
          </div>

          <div v-else class="rounded-lg border-2 border-dashed border-outline-gray-3 p-10 text-center">
            <div v-if="formData.file_url" class="flex items-center justify-between rounded-md bg-surface-gray-1 p-3">
              <div class="flex items-center gap-2">
                <FeatherIcon :name="formData.content_type === 'Video' ? 'video' : 'image'" class="h-5 w-5 text-ink-gray-5" />
                <span class="text-sm text-ink-gray-7">{{ uploadedFileName || formData.file_url }}</span>
              </div>
              <Button variant="ghost" size="sm" @click="removeFile">
                <FeatherIcon name="x" class="h-4 w-4" />
              </Button>
            </div>
            <div v-else-if="fileUploading" class="py-4">
              <LoadingIndicator class="mx-auto h-6 w-6" />
              <p class="mt-2 text-sm text-ink-gray-6">Uploading...</p>
            </div>
            <div v-else>
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
import { createResource, Breadcrumbs, Button, FormControl, FeatherIcon, LoadingIndicator, call } from 'frappe-ui'
import { toast } from '@/utils/toast'
import LayoutHeader from '@/components/LayoutHeader.vue'

const route = useRoute()
const router = useRouter()
const fileInput = ref(null)

const isNew = computed(() => !route.params.name)
const saving = ref(false)
const fileUploading = ref(false)
const uploadedFileName = ref('')

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
      if (data.doc.file_url || data.doc.file_attachment) {
        uploadedFileName.value = (data.doc.file_url || data.doc.file_attachment || '').split('/').pop()
      }
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

async function handleFileSelect(event) {
  const file = event.target.files[0]
  if (!file) return

  fileUploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    fd.append('is_private', '0')
    fd.append('folder', 'Home/Marketing Hub')

    const response = await fetch('/api/method/upload_file', {
      method: 'POST',
      body: fd,
      headers: { 'X-Frappe-CSRF-Token': window.csrf_token },
    })
    const result = await response.json()

    if (result.message) {
      formData.value.file_url = result.message.file_url
      uploadedFileName.value = result.message.file_name || file.name
      toast({ title: 'Uploaded', text: 'File uploaded successfully', icon: 'check', iconClasses: 'text-ink-green-3' })
    }
  } catch (error) {
    toast({ title: 'Error', text: 'Failed to upload file', icon: 'x', iconClasses: 'text-ink-red-3' })
  } finally {
    fileUploading.value = false
  }
}

function removeFile() {
  formData.value.file_url = null
  uploadedFileName.value = ''
}

async function saveContent() {
  if (!formData.value.asset_name) {
    toast({ title: 'Error', text: 'Name is required', icon: 'x', iconClasses: 'text-ink-red-3' })
    return
  }

  saving.value = true
  try {
    if (isNew.value) {
      await call('frappe.client.insert', {
        doc: {
          doctype: 'Content Asset',
          asset_name: formData.value.asset_name,
          content_type: formData.value.content_type,
          content_text: formData.value.content_text,
          campaign: formData.value.campaign,
          status: formData.value.status,
          file_attachment: formData.value.file_url || undefined,
        }
      })
      toast({ title: 'Success', text: 'Content created', icon: 'check', iconClasses: 'text-ink-green-3' })
      router.push({ name: 'Content' })
    } else {
      await call('frappe.client.set_value', {
        doctype: 'Content Asset',
        name: route.params.name,
        fieldname: {
          asset_name: formData.value.asset_name,
          content_type: formData.value.content_type,
          content_text: formData.value.content_text,
          campaign: formData.value.campaign,
          status: formData.value.status,
          file_attachment: formData.value.file_url || undefined,
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
