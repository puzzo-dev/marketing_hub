<template>
  <div class="flex h-full flex-col bg-white">
    <!-- Header -->
    <div class="h-16 border-b flex items-center justify-between px-5 bg-white shrink-0">
      <div class="flex items-center gap-2">
        <Button variant="ghost" @click="$router.back()">
          <template #prefix>
            <FeatherIcon name="arrow-left" class="h-4 w-4" />
          </template>
        </Button>
        <h1 class="text-xl font-semibold text-gray-900">
          {{ isNew ? 'New Content Asset' : formData.asset_name }}
        </h1>
      </div>
      <div class="flex gap-2">
        <Button
          variant="solid"
          :loading="saving"
          @click="saveContent"
        >
          Save
        </Button>
      </div>
    </div>

    <!-- Main Body -->
    <div class="flex-1 flex overflow-hidden">
      <!-- Editor Column (Left) -->
      <div class="flex-1 border-r p-6 overflow-y-auto">
        <div class="max-w-3xl mx-auto space-y-6">
          <FormControl
            label="Name / Title"
            v-model="formData.asset_name"
            :required="true"
            placeholder="e.g. Summer Campaign Banner"
          />

          <div v-if="formData.content_type === 'Text'">
            <label class="block text-sm font-medium text-gray-700 mb-2">Content</label>
            <textarea
              v-model="formData.content_text"
              rows="15"
              class="w-full rounded-md border border-gray-300 p-4 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="Write your content here..."
            ></textarea>
            <p class="mt-1 text-sm text-gray-500 flex justify-between">
              <span>Supports basic text content for emails and posts.</span>
              <span>{{ formData.content_text?.length || 0 }} chars</span>
            </p>
          </div>

          <div v-else class="rounded-lg border-2 border-dashed border-gray-300 p-10 text-center">
            <div class="flex justify-center mb-4">
              <FeatherIcon name="image" class="h-10 w-10 text-gray-400" />
            </div>
            <p class="text-gray-600 mb-4">Upload {{ formData.content_type }} Asset</p>
            <Button variant="outline" @click="triggerUpload">Choose File</Button>
            <input
              ref="fileInput"
              type="file"
              class="hidden"
              @change="handleFileSelect"
            />
            <div v-if="formData.file_url" class="mt-4 p-2 bg-gray-50 rounded text-sm text-gray-700">
              Selected: {{ formData.file_url }}
            </div>
          </div>
        </div>
      </div>

      <!-- Settings Column (Right) -->
      <div class="w-80 bg-gray-50 p-6 overflow-y-auto">
        <h3 class="font-semibold text-gray-900 mb-4">Settings</h3>
        
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
            doctype="Campaign"
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

        <hr class="my-6 border-gray-200" />

        <!-- Preview Section -->
        <div>
          <h3 class="font-semibold text-gray-900 mb-2">Preview</h3>
          <div class="bg-white border rounded p-4 text-sm text-gray-600 min-h-[100px]">
            <div v-if="formData.content_type === 'Text'">
              {{ formData.content_text || 'No content yet...' }}
            </div>
            <div v-else class="flex items-center justify-center h-full text-gray-400">
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
import { createResource, Button, FormControl, FeatherIcon, toast } from 'frappe-ui'

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
  url: 'marketing_hub.www.marketing.api.get_content_details',
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
    // In a real app, upload this file first
    formData.value.file_url = file.name // Placeholder
    toast({
      title: 'File Selected',
      text: 'File upload logic needed here',
      icon: 'info'
    })
  }
}

async function saveContent() {
  if (!formData.value.asset_name) {
    toast({ title: 'Error', text: 'Name is required', icon: 'x', iconClasses: 'text-red-600' })
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
      toast({ title: 'Success', text: 'Content created', icon: 'check', iconClasses: 'text-green-600' })
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
      toast({ title: 'Saved', text: 'Changes saved', icon: 'check', iconClasses: 'text-green-600' })
    }
  } catch (error) {
    toast({ title: 'Error', text: error.message, icon: 'x', iconClasses: 'text-red-600' })
  } finally {
    saving.value = false
  }
}
</script>
