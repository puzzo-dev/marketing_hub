<template>
  <div class="flex h-full flex-col overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="[{ label: 'Marketing Hub' }, { label: 'Content Library' }]" />
      </template>
      <template #right-header>
        <Button @click="showUploadDialog = true" variant="solid" label="Upload Asset">
          <template #prefix>
            <IconUpload class="h-4 w-4" />
          </template>
        </Button>
        <Button @click="showTemplateDialog = true" variant="outline" label="New Template">
          <template #prefix>
            <IconFileText class="h-4 w-4" />
          </template>
        </Button>
      </template>
    </LayoutHeader>

    <!-- Tabs bar -->
    <div class="border-b px-5">
      <Tabs v-model="activeTab" :tabs="tabs" />
    </div>

    <!-- Content -->
    <div class="flex flex-1 overflow-hidden">
      <!-- Sidebar Filters -->
      <div class="w-64 overflow-y-auto border-r border-outline-gray-1 p-4">
        <div class="space-y-6">
          <!-- Search -->
          <div>
            <label class="mb-2 block text-sm font-medium text-ink-gray-9">Search</label>
            <FormControl
              v-model="filters.search"
              type="text"
              placeholder="Search..."
              @input="debouncedLoadData"
            />
          </div>

          <!-- Asset Type Filter (for assets tab) -->
          <div v-if="activeTab === 'assets'">
            <label class="mb-2 block text-sm font-medium text-ink-gray-9">Asset Type</label>
            <FormControl
              v-model="filters.asset_type"
              type="select"
              :options="['', ...assetTypes]"
              @change="loadData"
            />
          </div>

          <!-- Channel Filter -->
          <div>
            <label class="mb-2 block text-sm font-medium text-ink-gray-9">Channel</label>
            <FormControl
              v-model="filters.channel"
              type="select"
              :options="['', ...channels]"
              @change="loadData"
            />
          </div>

          <!-- Status Filter -->
          <div>
            <label class="mb-2 block text-sm font-medium text-ink-gray-9">Status</label>
            <FormControl
              v-model="filters.status"
              type="select"
              :options="['', 'Draft', 'Review', 'Approved', 'Active', 'Archived']"
              @change="loadData"
            />
          </div>

          <!-- Category Filter (for templates) -->
          <div v-if="activeTab === 'templates'">
            <label class="mb-2 block text-sm font-medium text-ink-gray-9">Category</label>
            <FormControl
              v-model="filters.category"
              type="select"
              :options="['', ...templateCategories]"
              @change="loadData"
            />
          </div>

          <!-- View Mode -->
          <div>
            <label class="mb-2 block text-sm font-medium text-ink-gray-9">View</label>
            <div class="flex gap-2">
              <Button
                :variant="viewMode === 'grid' ? 'solid' : 'ghost'"
                size="sm"
                @click="viewMode = 'grid'"
              >
                <template #prefix>
                  <FeatherIcon name="grid" class="h-4 w-4" />
                </template>
                Grid
              </Button>
              <Button
                :variant="viewMode === 'list' ? 'solid' : 'ghost'"
                size="sm"
                @click="viewMode = 'list'"
              >
                <template #prefix>
                  <FeatherIcon name="list" class="h-4 w-4" />
                </template>
                List
              </Button>
            </div>
          </div>

          <!-- Stats -->
          <div v-if="stats" class="mt-6 space-y-2">
            <div class="text-sm font-medium text-ink-gray-9">Statistics</div>
            <div class="text-xs text-ink-gray-6">
              <div>Total: {{ stats.total_assets }}</div>
              <div v-if="stats.total_size">Size: {{ formatFileSize(stats.total_size) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content Area -->
      <div class="flex-1 overflow-y-auto p-6">
        <!-- Assets Tab -->
        <div v-if="activeTab === 'assets'">
          <!-- Bulk Actions -->
          <div
            v-if="selectedAssets.length > 0"
            class="mb-4 flex items-center gap-2 rounded-lg bg-surface-gray-2 p-3"
          >
            <span class="text-sm text-ink-gray-7">{{ selectedAssets.length }} selected</span>
            <Button size="sm" @click="bulkUpdateStatus('Approved')">Mark Approved</Button>
            <Button size="sm" @click="bulkUpdateStatus('Archived')">Archive</Button>
            <Button size="sm" variant="ghost" @click="bulkDelete">Delete</Button>
            <Button size="sm" variant="ghost" @click="selectedAssets = []">Clear</Button>
          </div>

          <!-- Grid View -->
          <div
            v-if="viewMode === 'grid' && !assetsLoading"
            class="grid grid-cols-2 gap-4 lg:grid-cols-3 xl:grid-cols-4"
          >
            <div
              v-for="asset in assets"
              :key="asset.name"
              class="group relative cursor-pointer overflow-hidden rounded-lg border border-outline-gray-1 bg-surface-cards shadow-sm transition-shadow hover:shadow-md"
              @click="openAsset(asset)"
            >
              <!-- Checkbox -->
              <div class="absolute left-2 top-2 z-10">
                <input
                  type="checkbox"
                  :value="asset.name"
                  v-model="selectedAssets"
                  @click.stop
                  class="h-4 w-4 rounded border-outline-gray-3"
                />
              </div>

              <!-- Thumbnail -->
              <div class="aspect-square bg-surface-gray-1">
                <img
                  v-if="asset.thumbnail"
                  :src="asset.thumbnail"
                  :alt="asset.asset_name"
                  class="h-full w-full object-cover"
                />
                <div v-else class="flex h-full items-center justify-center">
                  <FeatherIcon name="file" class="h-12 w-12 text-ink-gray-4" />
                </div>
              </div>

              <!-- Info -->
              <div class="p-3">
                <h3 class="truncate font-medium text-ink-gray-9">{{ asset.asset_name }}</h3>
                <div class="mt-1 flex items-center gap-2 text-xs text-ink-gray-6">
                  <Badge :label="asset.status" :variant="getStatusVariant(asset.status)" />
                  <span v-if="asset.channel">{{ asset.channel }}</span>
                </div>
                <div class="mt-2 text-xs text-ink-gray-5">
                  <div v-if="asset.file_size">{{ formatFileSize(asset.file_size) }}</div>
                  <div>{{ formatDate(asset.modified) }}</div>
                </div>
              </div>

              <!-- Hover Actions -->
              <div
                class="absolute inset-x-0 bottom-0 flex gap-1 bg-surface-cards/90 p-2 opacity-0 transition-opacity group-hover:opacity-100"
              >
                <Button size="sm" variant="ghost" @click.stop="downloadAsset(asset)">
                  <template #prefix>
                    <FeatherIcon name="download" class="h-3 w-3" />
                  </template>
                  Download
                </Button>
                <Button size="sm" variant="ghost" @click.stop="editAsset(asset)">
                  <template #prefix>
                    <FeatherIcon name="edit-2" class="h-3 w-3" />
                  </template>
                  Edit
                </Button>
                <Button size="sm" variant="ghost" @click.stop="deleteAsset(asset)">
                  <template #prefix>
                    <FeatherIcon name="trash-2" class="h-3 w-3" />
                  </template>
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
              class="flex cursor-pointer items-center gap-4 rounded-lg border border-outline-gray-1 bg-surface-cards p-4 transition-shadow hover:shadow-md"
              @click="openAsset(asset)"
            >
              <input
                type="checkbox"
                :value="asset.name"
                v-model="selectedAssets"
                @click.stop
                class="h-4 w-4 rounded border-outline-gray-3"
              />
              <div class="h-12 w-12 flex-shrink-0">
                <img
                  v-if="asset.thumbnail"
                  :src="asset.thumbnail"
                  :alt="asset.asset_name"
                  class="h-full w-full rounded object-cover"
                />
                <div
                  v-else
                  class="flex h-full w-full items-center justify-center rounded bg-surface-gray-1"
                >
                  <FeatherIcon name="file" class="h-6 w-6 text-ink-gray-4" />
                </div>
              </div>
              <div class="flex-1">
                <h3 class="font-medium text-ink-gray-9">{{ asset.asset_name }}</h3>
                <div class="mt-1 flex items-center gap-3 text-sm text-ink-gray-6">
                  <Badge :label="asset.status" :variant="getStatusVariant(asset.status)" />
                  <span v-if="asset.asset_type">{{ asset.asset_type }}</span>
                  <span v-if="asset.channel">{{ asset.channel }}</span>
                  <span v-if="asset.file_size">{{ formatFileSize(asset.file_size) }}</span>
                </div>
              </div>
              <div class="text-sm text-ink-gray-5">
                {{ formatDate(asset.modified) }}
              </div>
              <div class="flex gap-1">
                <Button size="sm" variant="ghost" @click.stop="downloadAsset(asset)">
                  <FeatherIcon name="download" class="h-4 w-4" />
                </Button>
                <Button size="sm" variant="ghost" @click.stop="editAsset(asset)">
                  <FeatherIcon name="edit-2" class="h-4 w-4" />
                </Button>
                <Button size="sm" variant="ghost" @click.stop="deleteAsset(asset)">
                  <FeatherIcon name="trash-2" class="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>

          <!-- Loading -->
          <div v-if="assetsLoading" class="flex items-center justify-center py-12">
            <LoadingIndicator class="h-8 w-8" />
          </div>

          <!-- Empty State -->
          <div
            v-if="!assetsLoading && assets.length === 0"
            class="flex flex-col items-center justify-center py-12"
          >
            <FeatherIcon name="folder" class="h-16 w-16 text-ink-gray-4" />
            <h3 class="mt-4 text-lg font-medium text-ink-gray-9">No assets found</h3>
            <p class="mt-2 text-sm text-ink-gray-5">Upload your first asset to get started</p>
            <Button class="mt-4" @click="showUploadDialog = true">
              <template #prefix>
                <FeatherIcon name="upload-cloud" class="h-4 w-4" />
              </template>
              Upload Asset
            </Button>
          </div>
        </div>

        <!-- Templates Tab -->
        <div v-if="activeTab === 'templates'">
          <div
            v-if="viewMode === 'grid' && !templatesLoading"
            class="grid grid-cols-1 gap-4 lg:grid-cols-2 xl:grid-cols-3"
          >
            <div
              v-for="template in templates"
              :key="template.name"
              class="cursor-pointer rounded-lg border border-outline-gray-1 bg-surface-cards p-4 shadow-sm transition-shadow hover:shadow-md"
              @click="openTemplate(template)"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <h3 class="font-medium text-ink-gray-9">{{ template.template_name }}</h3>
                  <p v-if="template.subject" class="mt-1 text-sm text-ink-gray-6">
                    {{ template.subject }}
                  </p>
                </div>
                <Badge :label="template.status" :variant="getStatusVariant(template.status)" />
              </div>
              <div class="mt-3 flex items-center gap-2 text-sm text-ink-gray-6">
                <Badge :label="template.channel" variant="subtle" />
                <span v-if="template.template_type">{{ template.template_type }}</span>
              </div>
              <div class="mt-3 text-xs text-ink-gray-5">
                {{ formatDate(template.modified) }}
              </div>
            </div>
          </div>

          <!-- Loading -->
          <div v-if="templatesLoading" class="flex items-center justify-center py-12">
            <LoadingIndicator class="h-8 w-8" />
          </div>

          <!-- Empty State -->
          <div
            v-if="!templatesLoading && templates.length === 0"
            class="flex flex-col items-center justify-center py-12"
          >
            <FeatherIcon name="file-text" class="h-16 w-16 text-ink-gray-4" />
            <h3 class="mt-4 text-lg font-medium text-ink-gray-9">No templates found</h3>
            <p class="mt-2 text-sm text-ink-gray-5">Create your first template to get started</p>
            <Button class="mt-4" @click="showTemplateDialog = true">
              <template #prefix>
                <FeatherIcon name="plus" class="h-4 w-4" />
              </template>
              New Template
            </Button>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="totalCount > pageSize" class="mt-6 flex items-center justify-between">
          <div class="text-sm text-ink-gray-6">
            Showing {{ (currentPage - 1) * pageSize + 1 }} to
            {{ Math.min(currentPage * pageSize, totalCount) }} of {{ totalCount }}
          </div>
          <div class="flex gap-2">
            <Button size="sm" :disabled="currentPage === 1" @click="currentPage--; loadData()">
              <template #prefix>
                <FeatherIcon name="chevron-left" class="h-4 w-4" />
              </template>
              Previous
            </Button>
            <Button
              size="sm"
              :disabled="currentPage * pageSize >= totalCount"
              @click="currentPage++; loadData()"
            >
              Next
              <template #suffix>
                <FeatherIcon name="chevron-right" class="h-4 w-4" />
              </template>
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Upload Dialog -->
    <Dialog v-model="showUploadDialog" :options="{ title: 'Upload Asset', size: 'lg' }" :disableOutsideClickToClose="true">
      <template #body-content>
        <div class="space-y-4">
          <!-- Drag and Drop Zone -->
          <div
            @dragover.prevent
            @drop.prevent="handleFileDrop"
            class="flex h-48 cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-outline-gray-3 bg-surface-gray-1 transition-colors hover:border-outline-gray-5"
            @click="$refs.fileInput.click()"
          >
            <FeatherIcon name="upload-cloud" class="h-12 w-12 text-ink-gray-4" />
            <p class="mt-2 text-sm text-ink-gray-6">
              Drag and drop files here or click to browse
            </p>
            <p class="mt-1 text-xs text-ink-gray-5">
              Supports images, videos, PDFs, and documents
            </p>
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
              class="flex items-center gap-3 rounded-lg border border-outline-gray-1 p-3"
            >
              <FeatherIcon name="file" class="h-6 w-6 text-ink-gray-4" />
              <div class="flex-1">
                <div class="text-sm font-medium text-ink-gray-9">{{ file.name }}</div>
                <div class="text-xs text-ink-gray-5">{{ formatFileSize(file.size) }}</div>
              </div>
              <Button size="sm" variant="ghost" @click="removeFromQueue(index)">
                <FeatherIcon name="x" class="h-4 w-4" />
              </Button>
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
          :loading="uploading"
          @click="uploadFiles"
        >
          Upload {{ uploadQueue.length }} file{{ uploadQueue.length > 1 ? 's' : '' }}
        </Button>
      </template>
    </Dialog>

    <!-- Template Dialog -->
    <Dialog
      v-model="showTemplateDialog"
      :options="{ title: 'Create Template', size: 'xl' }"
      :disableOutsideClickToClose="true"
    >
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
import {
  Breadcrumbs,
  createResource,
  Badge,
  Button,
  FormControl,
  Dialog,
  LoadingIndicator,
  Tabs,
  FileUploadHandler,
} from 'frappe-ui'
import { toast } from '@/utils/toast'
import LayoutHeader from '@/components/LayoutHeader.vue'
import { debounce } from 'lodash'

import IconUpload from '~icons/lucide/upload-cloud'
import IconFileText from '~icons/lucide/file-text'

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
  template_type: '',
})

const uploadData = reactive({
  asset_type: 'Image',
  channel: '',
})

const templateData = reactive({
  template_name: '',
  channel: 'Email',
  template_type: 'Text',
  subject: '',
  body_text: '',
  status: 'Draft',
})

// Resources
const assetsResource = createResource({
  url: '/api/method/marketing_hub.api.content.get_assets',
  auto: false,
  onSuccess(data) {
    assets.value = data.assets || []
    totalCount.value = data.total_count || 0
  },
})

const templatesResource = createResource({
  url: '/api/method/marketing_hub.api.content.get_templates',
  auto: false,
  onSuccess(data) {
    templates.value = data.templates || []
    totalCount.value = data.total_count || 0
  },
})

const channelsResource = createResource({
  url: '/api/method/marketing_hub.api.content.get_channels',
  auto: true,
})

const assetTypesResource = createResource({
  url: '/api/method/marketing_hub.api.content.get_asset_types',
  auto: true,
})

const statsResource = createResource({
  url: '/api/method/marketing_hub.api.content.get_asset_stats',
  auto: true,
})

const templateCategoriesResource = createResource({
  url: '/api/method/marketing_hub.api.content.get_template_categories',
  auto: true,
})

// Data
const assets = ref([])
const templates = ref([])
const totalCount = ref(0)
const channels = computed(() => channelsResource.data || [])
const assetTypes = computed(() => (assetTypesResource.data || []).map((t) => t.name))
const stats = computed(() => statsResource.data)
const templateCategories = computed(() => templateCategoriesResource.data || [])
const assetsLoading = computed(() => assetsResource.loading)
const templatesLoading = computed(() => templatesResource.loading)

// Methods
function loadData() {
  const params = {
    filters: JSON.stringify(filters),
    limit_start: (currentPage.value - 1) * pageSize,
    limit_page_length: pageSize,
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
    try {
      const uploader = new FileUploadHandler()
      const uploadedFile = await uploader.upload(file, {
        private: false,
        folder: 'Home/Marketing Hub',
      })

      if (uploadedFile?.file_url) {
        await createResource({
          url: '/api/method/marketing_hub.api.content.upload_file',
          makeParams: () => ({
            file: uploadedFile.file_url,
            asset_name: file.name,
            asset_type: uploadData.asset_type,
            channel: uploadData.channel,
          }),
        }).fetch()
      }
    } catch (error) {
      toast({
        title: 'Upload Error',
        text: error.message || 'Failed to upload file',
        icon: 'x',
        iconClasses: 'text-ink-red-2',
      })
    }
  }

  uploading.value = false
  uploadQueue.value = []
  showUploadDialog.value = false
  toast({
    title: 'Success',
    text: 'Files uploaded successfully',
    icon: 'check',
    iconClasses: 'text-ink-green-2',
  })
  loadData()
}

function openAsset(asset) {
  window.location.href = `/app/content-asset/${asset.name}`
}

function editAsset(asset) {
  window.location.href = `/app/content-asset/${asset.name}`
}

function deleteAsset(asset) {
  if (confirm(`Delete asset "${asset.asset_name}"?`)) {
    createResource({
      url: '/api/method/marketing_hub.api.content.delete_asset',
      makeParams: () => ({ name: asset.name }),
    })
      .fetch()
      .then(() => {
        toast({ title: 'Success', text: 'Asset deleted', icon: 'check', iconClasses: 'text-ink-green-2' })
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
    url: '/api/method/marketing_hub.api.content.bulk_update_assets',
    makeParams: () => ({
      names: JSON.stringify(selectedAssets.value),
      data: JSON.stringify({ status }),
    }),
  })
    .fetch()
    .then(() => {
      selectedAssets.value = []
      toast({ title: 'Success', text: `${selectedAssets.value.length} assets updated`, icon: 'check', iconClasses: 'text-ink-green-2' })
      loadData()
    })
}

function bulkDelete() {
  if (confirm(`Delete ${selectedAssets.value.length} assets?`)) {
    Promise.all(
      selectedAssets.value.map((name) =>
        createResource({
          url: '/api/method/marketing_hub.api.content.delete_asset',
          makeParams: () => ({ name }),
        }).fetch(),
      ),
    ).then(() => {
      selectedAssets.value = []
      loadData()
    })
  }
}

function openTemplate(template) {
  window.location.href = `/app/marketing-template/${template.name}`
}

function createTemplate() {
  createResource({
    url: '/api/method/marketing_hub.api.content.create_template',
    makeParams: () => ({ data: JSON.stringify(templateData) }),
  })
    .fetch()
    .then(() => {
      showTemplateDialog.value = false
      toast({ title: 'Success', text: 'Template created', icon: 'check', iconClasses: 'text-ink-green-2' })
      loadData()
      Object.assign(templateData, {
        template_name: '',
        channel: 'Email',
        template_type: 'Text',
        subject: '',
        body_text: '',
        status: 'Draft',
      })
    })
}

function getStatusVariant(status) {
  const variants = {
    Draft: 'subtle',
    Review: 'warning',
    Approved: 'success',
    Active: 'success',
    Archived: 'subtle',
  }
  return variants[status] || 'subtle'
}

function formatDate(date) {
  if (!date) return ''
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
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
