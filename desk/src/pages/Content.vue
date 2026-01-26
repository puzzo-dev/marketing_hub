<template>
  <div class="flex h-full flex-col">
    <!-- Header -->
    <div class="border-b px-6 py-4">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-semibold text-gray-900">Content Library</h1>
          <p class="mt-1 text-sm text-gray-600">Manage your marketing assets and templates</p>
        </div>
        <div class="flex gap-2">
          <Button @click="showUploadDialog = true" variant="solid">
            <template #prefix>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </template>
            Upload Asset
          </Button>
          <Button @click="showTemplateDialog = true">
            <template #prefix>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </template>
            New Template
          </Button>
        </div>
      </div>

      <!-- Tabs -->
      <div class="mt-4 flex gap-4 border-b">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          @click="activeTab = tab.value"
          :class="[
            'pb-3 text-sm font-medium transition-colors',
            activeTab === tab.value
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          ]"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="flex flex-1 overflow-hidden">
      <!-- Sidebar Filters -->
      <div class="w-64 border-r bg-gray-50 p-4 overflow-y-auto">
        <div class="space-y-6">
          <!-- Search -->
          <div>
            <label class="mb-2 block text-sm font-medium text-gray-700">Search</label>
            <FormControl
              v-model="filters.search"
              type="text"
              placeholder="Search..."
              @input="debouncedLoadData"
            />
          </div>

          <!-- Asset Type Filter (for assets tab) -->
          <div v-if="activeTab === 'assets'">
            <label class="mb-2 block text-sm font-medium text-gray-700">Asset Type</label>
            <FormControl
              v-model="filters.asset_type"
              type="select"
              :options="['', ...assetTypes]"
              @change="loadData"
            />
          </div>

          <!-- Channel Filter -->
          <div>
            <label class="mb-2 block text-sm font-medium text-gray-700">Channel</label>
            <FormControl
              v-model="filters.channel"
              type="select"
              :options="['', ...channels]"
              @change="loadData"
            />
          </div>

          <!-- Status Filter -->
          <div>
            <label class="mb-2 block text-sm font-medium text-gray-700">Status</label>
            <FormControl
              v-model="filters.status"
              type="select"
              :options="['', 'Draft', 'Review', 'Approved', 'Active', 'Archived']"
              @change="loadData"
            />
          </div>

          <!-- Category Filter (for templates) -->
          <div v-if="activeTab === 'templates'">
            <label class="mb-2 block text-sm font-medium text-gray-700">Category</label>
            <FormControl
              v-model="filters.category"
              type="select"
              :options="['', ...templateCategories]"
              @change="loadData"
            />
          </div>

          <!-- View Mode -->
          <div>
            <label class="mb-2 block text-sm font-medium text-gray-700">View</label>
            <div class="flex gap-2">
              <Button
                :variant="viewMode === 'grid' ? 'solid' : 'ghost'"
                size="sm"
                @click="viewMode = 'grid'"
              >
                Grid
              </Button>
              <Button
                :variant="viewMode === 'list' ? 'solid' : 'ghost'"
                size="sm"
                @click="viewMode = 'list'"
              >
                List
              </Button>
            </div>
          </div>

          <!-- Stats -->
          <div v-if="stats" class="mt-6 space-y-2">
            <div class="text-sm font-medium text-gray-700">Statistics</div>
            <div class="text-xs text-gray-600">
              <div>Total: {{ stats.total_assets }}</div>
              <div v-if="stats.total_size">Size: {{ formatSize(stats.total_size) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content Area -->
      <div class="flex-1 overflow-y-auto p-6">
        <!-- Assets Grid/List -->
        <div v-if="activeTab === 'assets'">
          <!-- Bulk Actions -->
          <div v-if="selectedAssets.length > 0" class="mb-4 flex items-center gap-2 rounded-lg bg-blue-50 p-3">
            <span class="text-sm text-gray-700">{{ selectedAssets.length }} selected</span>
            <Button size="sm" @click="bulkUpdateStatus('Approved')">Mark Approved</Button>
            <Button size="sm" @click="bulkUpdateStatus('Archived')">Archive</Button>
            <Button size="sm" variant="ghost" @click="bulkDelete">Delete</Button>
            <Button size="sm" variant="ghost" @click="selectedAssets = []">Clear</Button>
          </div>

          <!-- Grid View -->
          <div v-if="viewMode === 'grid' && !assetsLoading" class="grid grid-cols-2 gap-4 lg:grid-cols-3 xl:grid-cols-4">
            <div
              v-for="asset in assets"
              :key="asset.name"
              class="group relative cursor-pointer overflow-hidden rounded-lg border bg-white transition-shadow hover:shadow-lg"
              @click="openAsset(asset)"
            >
              <!-- Checkbox -->
              <div class="absolute left-2 top-2 z-10">
                <input
                  type="checkbox"
                  :value="asset.name"
                  v-model="selectedAssets"
                  @click.stop
                  class="h-4 w-4 rounded border-gray-300"
                />
              </div>

              <!-- Thumbnail -->
              <div class="aspect-square bg-gray-100">
                <img
                  v-if="asset.thumbnail"
                  :src="asset.thumbnail"
                  :alt="asset.asset_name"
                  class="h-full w-full object-cover"
                />
                <div v-else class="flex h-full items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                </div>
              </div>

              <!-- Info -->
              <div class="p-3">
                <h3 class="truncate font-medium text-gray-900">{{ asset.asset_name }}</h3>
                <div class="mt-1 flex items-center gap-2 text-xs text-gray-600">
                  <Badge :variant="getStatusVariant(asset.status)">{{ asset.status }}</Badge>
                  <span v-if="asset.channel">{{ asset.channel }}</span>
                </div>
                <div class="mt-2 text-xs text-gray-500">
                  <div v-if="asset.file_size">{{ asset.file_size }}</div>
                  <div>{{ formatDate(asset.modified) }}</div>
                </div>
              </div>

              <!-- Hover Actions -->
              <div class="absolute inset-x-0 bottom-0 flex gap-1 bg-white/90 p-2 opacity-0 transition-opacity group-hover:opacity-100">
                <Button size="sm" variant="ghost" @click.stop="downloadAsset(asset)">
                  Download
                </Button>
                <Button size="sm" variant="ghost" @click.stop="editAsset(asset)">
                  Edit
                </Button>
                <Button size="sm" variant="ghost" @click.stop="deleteAsset(asset)">
                  Delete
                </Button>
              </div>
            </div>
          </div>

          <!-- List View -->
          <div v-else-if="viewMode === 'list' && !assetsLoading" class="space-y-2">
            <div
              v-for="asset in assets"
              :key="asset.name"
              class="flex items-center gap-4 rounded-lg border bg-white p-4 transition-shadow hover:shadow-md cursor-pointer"
              @click="openAsset(asset)"
            >
              <input
                type="checkbox"
                :value="asset.name"
                v-model="selectedAssets"
                @click.stop
                class="h-4 w-4 rounded border-gray-300"
              />
              <div class="h-12 w-12 flex-shrink-0">
                <img
                  v-if="asset.thumbnail"
                  :src="asset.thumbnail"
                  :alt="asset.asset_name"
                  class="h-full w-full rounded object-cover"
                />
                <div v-else class="flex h-full w-full items-center justify-center rounded bg-gray-100">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                </div>
              </div>
              <div class="flex-1">
                <h3 class="font-medium text-gray-900">{{ asset.asset_name }}</h3>
                <div class="mt-1 flex items-center gap-3 text-sm text-gray-600">
                  <Badge :variant="getStatusVariant(asset.status)">{{ asset.status }}</Badge>
                  <span v-if="asset.asset_type">{{ asset.asset_type }}</span>
                  <span v-if="asset.channel">{{ asset.channel }}</span>
                  <span v-if="asset.file_size">{{ asset.file_size }}</span>
                </div>
              </div>
              <div class="text-sm text-gray-500">
                {{ formatDate(asset.modified) }}
              </div>
              <div class="flex gap-1">
                <Button size="sm" variant="ghost" @click.stop="downloadAsset(asset)">Download</Button>
                <Button size="sm" variant="ghost" @click.stop="editAsset(asset)">Edit</Button>
                <Button size="sm" variant="ghost" @click.stop="deleteAsset(asset)">Delete</Button>
              </div>
            </div>
          </div>

          <!-- Loading -->
          <div v-if="assetsLoading" class="flex items-center justify-center py-12">
            <div class="text-gray-600">Loading assets...</div>
          </div>

          <!-- Empty State -->
          <div v-if="!assetsLoading && assets.length === 0" class="flex flex-col items-center justify-center py-12">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
            </svg>
            <h3 class="mt-4 text-lg font-medium text-gray-900">No assets found</h3>
            <p class="mt-2 text-sm text-gray-600">Upload your first asset to get started</p>
            <Button class="mt-4" @click="showUploadDialog = true">
              Upload Asset
            </Button>
          </div>
        </div>

        <!-- Templates Grid/List -->
        <div v-if="activeTab === 'templates'">
          <div v-if="viewMode === 'grid' && !templatesLoading" class="grid grid-cols-1 gap-4 lg:grid-cols-2 xl:grid-cols-3">
            <div
              v-for="template in templates"
              :key="template.name"
              class="cursor-pointer rounded-lg border bg-white p-4 transition-shadow hover:shadow-lg"
              @click="openTemplate(template)"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <h3 class="font-medium text-gray-900">{{ template.template_name }}</h3>
                  <p v-if="template.subject" class="mt-1 text-sm text-gray-600">{{ template.subject }}</p>
                </div>
                <Badge :variant="getStatusVariant(template.status)">{{ template.status }}</Badge>
              </div>
              <div class="mt-3 flex items-center gap-2 text-sm text-gray-600">
                <Badge>{{ template.channel }}</Badge>
                <span v-if="template.template_type">{{ template.template_type }}</span>
              </div>
              <div class="mt-3 text-xs text-gray-500">
                {{ formatDate(template.modified) }}
              </div>
            </div>
          </div>

          <!-- Loading -->
          <div v-if="templatesLoading" class="flex items-center justify-center py-12">
            <div class="text-gray-600">Loading templates...</div>
          </div>

          <!-- Empty State -->
          <div v-if="!templatesLoading && templates.length === 0" class="flex flex-col items-center justify-center py-12">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 class="mt-4 text-lg font-medium text-gray-900">No templates found</h3>
            <p class="mt-2 text-sm text-gray-600">Create your first template to get started</p>
            <Button class="mt-4" @click="showTemplateDialog = true">
              New Template
            </Button>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="totalCount > pageSize" class="mt-6 flex items-center justify-between">
          <div class="text-sm text-gray-600">
            Showing {{ (currentPage - 1) * pageSize + 1 }} to {{ Math.min(currentPage * pageSize, totalCount) }} of {{ totalCount }}
          </div>
          <div class="flex gap-2">
            <Button
              size="sm"
              :disabled="currentPage === 1"
              @click="currentPage--; loadData()"
            >
              Previous
            </Button>
            <Button
              size="sm"
              :disabled="currentPage * pageSize >= totalCount"
              @click="currentPage++; loadData()"
            >
              Next
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Upload Dialog -->
    <Dialog v-model="showUploadDialog" :options="{ title: 'Upload Asset', size: 'lg' }">
      <template #body-content>
        <div class="space-y-4">
          <!-- Drag and Drop Zone -->
          <div
            @dragover.prevent
            @drop.prevent="handleFileDrop"
            class="flex h-48 cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-300 bg-gray-50 transition-colors hover:border-blue-500 hover:bg-blue-50"
            @click="$refs.fileInput.click()"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <p class="mt-2 text-sm text-gray-600">Drag and drop files here or click to browse</p>
            <p class="mt-1 text-xs text-gray-500">Supports images, videos, PDFs, and documents</p>
            <input
              ref="fileInput"
              type="file"
              multiple
              class="hidden"
              @change="handleFileSelect"
            />
          </div>

          <!-- Upload Queue -->
          <div v-if="uploadQueue.length > 0" class="space-y-2">
            <div
              v-for="(file, index) in uploadQueue"
              :key="index"
              class="flex items-center gap-3 rounded-lg border p-3"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              <div class="flex-1">
                <div class="text-sm font-medium">{{ file.name }}</div>
                <div class="text-xs text-gray-500">{{ formatFileSize(file.size) }}</div>
              </div>
              <Button size="sm" variant="ghost" @click="removeFromQueue(index)">Remove</Button>
            </div>
          </div>

          <!-- Asset Details -->
          <div v-if="uploadQueue.length > 0">
            <FormControl
              v-model="uploadData.asset_type"
              type="select"
              label="Asset Type"
              :options="assetTypes"
            />
            <FormControl
              v-model="uploadData.channel"
              type="select"
              label="Channel (Optional)"
              :options="['', ...channels]"
              class="mt-3"
            />
          </div>
        </div>
      </template>
      <template #actions>
        <Button variant="ghost" @click="showUploadDialog = false">Cancel</Button>
        <Button
          variant="solid"
          :disabled="uploadQueue.length === 0 || uploading"
          @click="uploadFiles"
        >
          {{ uploading ? 'Uploading...' : `Upload ${uploadQueue.length} file${uploadQueue.length > 1 ? 's' : ''}` }}
        </Button>
      </template>
    </Dialog>

    <!-- Template Dialog -->
    <Dialog v-model="showTemplateDialog" :options="{ title: 'Create Template', size: 'xl' }">
      <template #body-content>
        <div class="space-y-4">
          <FormControl
            v-model="templateData.template_name"
            type="text"
            label="Template Name"
            placeholder="Enter template name"
          />
          <div class="grid grid-cols-2 gap-4">
            <FormControl
              v-model="templateData.channel"
              type="select"
              label="Channel"
              :options="channels"
            />
            <FormControl
              v-model="templateData.template_type"
              type="select"
              label="Template Type"
              :options="['Text', 'Image', 'Video', 'Carousel', 'Collection']"
            />
          </div>
          <FormControl
            v-model="templateData.subject"
            type="text"
            label="Subject/Title"
            placeholder="Enter subject or title"
          />
          <FormControl
            v-model="templateData.body_text"
            type="textarea"
            label="Body Text"
            :rows="6"
          />
        </div>
      </template>
      <template #actions>
        <Button variant="ghost" @click="showTemplateDialog = false">Cancel</Button>
        <Button variant="solid" @click="createTemplate">Create Template</Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { createResource, Badge, Button, FormControl, Dialog } from 'frappe-ui'
import { debounce } from 'lodash'

const activeTab = ref('assets')
const viewMode = ref('grid')
const showUploadDialog = ref(false)
const showTemplateDialog = ref(false)
const selectedAssets = ref([])
const uploadQueue = ref([])
const uploading = ref(false)
const currentPage = ref(1)
const pageSize = 20

const tabs = [
  { label: 'Assets', value: 'assets' },
  { label: 'Templates', value: 'templates' },
]

const filters = reactive({
  search: '',
  asset_type: '',
  channel: '',
  status: '',
  category: '',
  template_type: ''
})

const uploadData = reactive({
  asset_type: 'Image',
  channel: ''
})

const templateData = reactive({
  template_name: '',
  channel: 'Email',
  template_type: 'Text',
  subject: '',
  body_text: '',
  status: 'Draft'
})

// Resources
const assetsResource = createResource({
  url: '/api/method/marketing_hub.www.marketing.content.get_assets',
  auto: false,
  onSuccess(data) {
    assets.value = data.assets || []
    totalCount.value = data.total_count || 0
  }
})

const templatesResource = createResource({
  url: '/api/method/marketing_hub.www.marketing.content.get_templates',
  auto: false,
  onSuccess(data) {
    templates.value = data.templates || []
    totalCount.value = data.total_count || 0
  }
})

const channelsResource = createResource({
  url: '/api/method/marketing_hub.www.marketing.content.get_channels',
  auto: true
})

const assetTypesResource = createResource({
  url: '/api/method/marketing_hub.www.marketing.content.get_asset_types',
  auto: true
})

const statsResource = createResource({
  url: '/api/method/marketing_hub.www.marketing.content.get_asset_stats',
  auto: true
})

const templateCategoriesResource = createResource({
  url: '/api/method/marketing_hub.www.marketing.content.get_template_categories',
  auto: true
})

// Data
const assets = ref([])
const templates = ref([])
const totalCount = ref(0)
const channels = computed(() => channelsResource.data || [])
const assetTypes = computed(() => (assetTypesResource.data || []).map(t => t.name))
const stats = computed(() => statsResource.data)
const templateCategories = computed(() => templateCategoriesResource.data || [])
const assetsLoading = computed(() => assetsResource.loading)
const templatesLoading = computed(() => templatesResource.loading)

// Methods
function loadData() {
  const params = {
    filters: JSON.stringify(filters),
    limit_start: (currentPage.value - 1) * pageSize,
    limit_page_length: pageSize
  }

  if (activeTab.value === 'assets') {
    assetsResource.fetch({ params })
  } else {
    templatesResource.fetch({ params })
  }
}

const debouncedLoadData = debounce(loadData, 300)

function handleFileSelect(event) {
  const files = Array.from(event.target.files)
  uploadQueue.value.push(...files)
}

function handleFileDrop(event) {
  const files = Array.from(event.dataTransfer.files)
  uploadQueue.value.push(...files)
}

function removeFromQueue(index) {
  uploadQueue.value.splice(index, 1)
}

async function uploadFiles() {
  uploading.value = true
  
  for (const file of uploadQueue.value) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('is_private', 0)
    formData.append('folder', 'Home')

    try {
      const response = await fetch('/api/method/upload_file', {
        method: 'POST',
        body: formData,
        headers: {
          'X-Frappe-CSRF-Token': window.csrf_token
        }
      })

      const result = await response.json()
      
      if (result.message) {
        // Create asset after file upload
        await createResource({
          url: '/api/method/marketing_hub.www.marketing.content.upload_file',
          makeParams: () => ({
            file: result.message.file_url,
            asset_name: file.name,
            asset_type: uploadData.asset_type,
            channel: uploadData.channel
          })
        }).fetch()
      }
    } catch (error) {
      console.error('Upload failed:', error)
    }
  }

  uploading.value = false
  uploadQueue.value = []
  showUploadDialog.value = false
  loadData()
}

function openAsset(asset) {
  // Navigate to asset detail or open preview
  console.log('Open asset:', asset)
}

function editAsset(asset) {
  // Open edit dialog
  console.log('Edit asset:', asset)
}

function deleteAsset(asset) {
  if (confirm(`Delete asset "${asset.asset_name}"?`)) {
    createResource({
      url: '/api/method/marketing_hub.www.marketing.content.delete_asset',
      makeParams: () => ({ name: asset.name })
    }).fetch().then(() => {
      loadData()
    })
  }
}

function downloadAsset(asset) {
  if (asset.file_attachment) {
    window.open(asset.file_attachment, '_blank')
  }
}

function bulkUpdateStatus(status) {
  createResource({
    url: '/api/method/marketing_hub.www.marketing.content.bulk_update_assets',
    makeParams: () => ({
      names: JSON.stringify(selectedAssets.value),
      data: JSON.stringify({ status })
    })
  }).fetch().then(() => {
    selectedAssets.value = []
    loadData()
  })
}

function bulkDelete() {
  if (confirm(`Delete ${selectedAssets.value.length} assets?`)) {
    Promise.all(
      selectedAssets.value.map(name =>
        createResource({
          url: '/api/method/marketing_hub.www.marketing.content.delete_asset',
          makeParams: () => ({ name })
        }).fetch()
      )
    ).then(() => {
      selectedAssets.value = []
      loadData()
    })
  }
}

function openTemplate(template) {
  console.log('Open template:', template)
}

function createTemplate() {
  createResource({
    url: '/api/method/marketing_hub.www.marketing.content.create_template',
    makeParams: () => ({ data: JSON.stringify(templateData) })
  }).fetch().then(() => {
    showTemplateDialog.value = false
    loadData()
    // Reset form
    Object.assign(templateData, {
      template_name: '',
      channel: 'Email',
      template_type: 'Text',
      subject: '',
      body_text: '',
      status: 'Draft'
    })
  })
}

function getStatusVariant(status) {
  const variants = {
    'Draft': 'subtle',
    'Review': 'warning',
    'Approved': 'success',
    'Active': 'success',
    'Archived': 'subtle'
  }
  return variants[status] || 'subtle'
}

function formatDate(date) {
  return new Date(date).toLocaleDateString()
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function formatSize(size) {
  if (size < 1024) return size.toFixed(1) + ' KB'
  return (size / 1024).toFixed(1) + ' MB'
}

// Watch tab changes
watch(activeTab, () => {
  currentPage.value = 1
  loadData()
})

onMounted(() => {
  loadData()
})
</script>
