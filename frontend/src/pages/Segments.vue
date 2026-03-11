<template>
  <div class="flex h-full flex-col overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="[{ label: 'Marketing Hub' }, { label: 'Segments' }]" />
      </template>
      <template #right-header>
        <Button @click="createNewSegment" variant="solid" label="New Segment">
          <template #prefix>
            <IconPlus class="h-4 w-4" />
          </template>
        </Button>
      </template>
    </LayoutHeader>

    <!-- Content Area -->
    <div class="flex-1 overflow-auto p-5">
      <!-- Loading -->
      <div v-if="segmentsResource.loading" class="flex items-center justify-center py-12">
        <LoadingIndicator class="h-6 w-6" />
      </div>

      <!-- Empty State -->
      <div v-else-if="segments.length === 0" class="relative flex h-full w-full justify-center">
        <div class="absolute left-1/2 flex w-4/12 -translate-x-1/2 flex-col items-center gap-3" style="top: 35%">
          <IconUsers class="h-7 w-7 text-ink-gray-5" />
          <span class="text-base font-medium text-ink-gray-8">No segments yet</span>
          <span class="text-center text-sm text-ink-gray-6">Create your first segment to target specific audiences</span>
          <Button @click="createNewSegment" variant="solid" label="Create First Segment">
            <template #prefix>
              <IconPlus class="h-4 w-4" />
            </template>
          </Button>
        </div>
      </div>

      <!-- Segments Grid -->
      <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="segment in segments"
          :key="segment.name"
          class="group relative rounded-lg border border-outline-gray-1 bg-surface-white p-4 shadow-sm transition-shadow hover:shadow"
        >
          <!-- Segment Header -->
          <div class="mb-3 flex items-start justify-between">
            <div class="flex-1">
              <h4 class="text-base font-medium text-ink-gray-9">
                {{ segment.segment_name }}
              </h4>
              <p v-if="segment.description" class="mt-1 text-sm text-ink-gray-6">
                {{ segment.description }}
              </p>
            </div>
            <Dropdown :options="getSegmentActions(segment)">
              <template #default="{ open }">
                <Button
                  variant="ghost"
                  icon="more-vertical"
                  class="opacity-0 group-hover:opacity-100"
                />
              </template>
            </Dropdown>
          </div>

          <!-- Segment Stats -->
          <div class="mb-3 flex items-center space-x-4">
            <div class="flex items-center text-sm">
              <FeatherIcon name="users" class="mr-1 h-4 w-4 text-ink-gray-6" />
              <span class="font-medium text-ink-gray-9">
                {{ formatNumber(segment.count) || '—' }}
              </span>
              <span class="ml-1 text-ink-gray-6">contacts</span>
            </div>
          </div>

          <!-- Segment Filters Preview -->
          <div v-if="segment.filter_json" class="mb-3">
            <div class="rounded-md bg-surface-gray-1 p-2">
              <p class="text-xs text-ink-gray-6">
                {{ getFilterPreview(segment.filter_json) }}
              </p>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex space-x-2">
            <Button
              size="sm"
              variant="outline"
              @click="viewSegment(segment)"
            >
              <template #prefix>
                <FeatherIcon name="eye" class="h-4 w-4" />
              </template>
              View
            </Button>
            <Button
              size="sm"
              variant="outline"
              @click="testSegment(segment)"
              :loading="testingSegment === segment.name"
            >
              <template #prefix>
                <FeatherIcon name="play" class="h-4 w-4" />
              </template>
              Test
            </Button>
          </div>

          <!-- Status Badge -->
          <div class="absolute right-3 top-3">
            <Badge
              :label="segment.disabled ? 'Disabled' : 'Active'"
              :theme="segment.disabled ? 'red' : 'green'"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Segment Dialog -->
    <Dialog
      v-model="showSegmentDialog"
      :options="{
        title: editingSegment ? 'Edit Segment' : 'New Segment',
        size: 'xl',
      }"
    >
      <template #body-content>
        <div class="space-y-4">
          <FormControl
            label="Segment Name"
            v-model="segmentForm.segment_name"
            placeholder="e.g., High Value Customers"
            :required="true"
          />

          <FormControl
            label="Description"
            type="textarea"
            v-model="segmentForm.description"
            placeholder="Describe this segment..."
          />

          <div>
            <label class="mb-2 block text-sm font-medium text-ink-gray-9">
              Base Doctype
            </label>
            <FormControl
              v-model="segmentForm.doctype"
              :options="doctypeOptions"
              placeholder="Select doctype"
              :required="true"
            />
          </div>

          <!-- Filter Builder -->
          <div v-if="segmentForm.doctype" class="rounded-md border border-outline-gray-2 p-4">
            <h3 class="mb-3 text-sm font-medium text-ink-gray-9">Filters</h3>

            <div
              v-for="(filter, index) in segmentForm.filters"
              :key="index"
              class="mb-3 flex items-center space-x-2"
            >
              <FormControl
                v-model="filter.field"
                :options="getFieldOptions(segmentForm.doctype)"
                placeholder="Field"
                class="flex-1"
              />
              <FormControl
                v-model="filter.operator"
                :options="operatorOptions"
                placeholder="Operator"
                class="w-32"
              />
              <FormControl
                v-model="filter.value"
                placeholder="Value"
                class="flex-1"
              />
              <Button
                variant="ghost"
                icon="x"
                @click="removeFilter(index)"
                class="flex-shrink-0"
              />
            </div>

            <Button
              size="sm"
              variant="outline"
              @click="addFilter"
            >
              <template #prefix>
                <FeatherIcon name="plus" class="h-4 w-4" />
              </template>
              Add Filter
            </Button>
          </div>

          <!-- Preview Count -->
          <div
            v-if="segmentPreview.count !== null"
            class="rounded-md bg-surface-gray-2 p-3"
          >
            <p class="text-sm text-ink-gray-9">
              <strong>{{ formatNumber(segmentPreview.count) }}</strong> contacts match these filters
            </p>
          </div>
        </div>
      </template>

      <template #actions>
        <Button variant="ghost" @click="closeSegmentDialog">Cancel</Button>
        <Button
          variant="ghost"
          @click="previewSegment"
          :loading="segmentPreview.loading"
        >
          <template #prefix>
            <FeatherIcon name="eye" class="h-4 w-4" />
          </template>
          Preview
        </Button>
        <Button
          @click="saveSegment"
          :loading="savingSegment"
        >
          {{ editingSegment ? 'Update' : 'Create' }} Segment
        </Button>
      </template>
    </Dialog>

    <!-- Test Results Dialog -->
    <Dialog
      v-model="showTestDialog"
      :options="{
        title: 'Segment Test Results',
        size: 'lg',
      }"
    >
      <template #body-content>
        <div v-if="testResults">
          <div class="mb-4">
            <h3 class="text-lg font-semibold text-ink-gray-9">
              {{ testResults.count }} contacts found
            </h3>
            <p class="text-sm text-ink-gray-6">
              Showing first {{ testResults.records?.length || 0 }} records
            </p>
          </div>

          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-outline-gray-2">
              <thead class="bg-surface-gray-1">
                <tr>
                  <th class="px-3 py-2 text-left text-xs font-medium text-ink-gray-6">Name</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-ink-gray-6">Email</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-ink-gray-6">Mobile</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-ink-gray-6">Status</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-outline-gray-2 bg-surface-cards">
                <tr v-for="record in testResults.records" :key="record.name">
                  <td class="px-3 py-2 text-sm text-ink-gray-9">{{ record.name }}</td>
                  <td class="px-3 py-2 text-sm text-ink-gray-6">{{ record.email || '—' }}</td>
                  <td class="px-3 py-2 text-sm text-ink-gray-6">{{ record.mobile_no || '—' }}</td>
                  <td class="px-3 py-2 text-sm">
                    <Badge
                      :label="record.status || 'Active'"
                      theme="green"
                    />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>

      <template #actions>
        <Button @click="showTestDialog = false">Close</Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Breadcrumbs, createResource, Button, FormControl, LoadingIndicator, Dialog, Dropdown, Badge, toast } from 'frappe-ui'
import LayoutHeader from '@/components/LayoutHeader.vue'

import IconPlus from '~icons/lucide/plus'
import IconUsers from '~icons/lucide/users'

// Resources
const segmentsResource = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'Marketing Segment',
    fields: ['name', 'segment_name', 'description', 'filter_json', 'disabled', 'creation'],
    limit_page_length: 100,
    order_by: 'creation desc',
  },
  auto: true,
})

// State
const showSegmentDialog = ref(false)
const showTestDialog = ref(false)
const editingSegment = ref(null)
const savingSegment = ref(false)
const testingSegment = ref(null)
const testResults = ref(null)

const segmentForm = ref({
  segment_name: '',
  description: '',
  doctype: 'Lead',
  filters: [{ field: '', operator: '=', value: '' }],
})

const segmentPreview = ref({
  loading: false,
  count: null,
})

// Computed
const segments = computed(() => segmentsResource.data || [])

const doctypeOptions = [
  { label: 'Lead', value: 'Lead' },
  { label: 'Contact', value: 'Contact' },
  { label: 'Customer', value: 'Customer' },
]

const operatorOptions = [
  { label: 'Equals', value: '=' },
  { label: 'Not Equals', value: '!=' },
  { label: 'Like', value: 'like' },
  { label: 'Not Like', value: 'not like' },
  { label: 'In', value: 'in' },
  { label: 'Not In', value: 'not in' },
  { label: 'Greater Than', value: '>' },
  { label: 'Less Than', value: '<' },
  { label: 'Is Set', value: 'is' },
  { label: 'Is Not Set', value: 'is not' },
]

// Methods
function getFieldOptions(doctype) {
  // Common fields for Lead/Contact/Customer
  const commonFields = [
    { label: 'Email', value: 'email_id' },
    { label: 'Mobile No', value: 'mobile_no' },
    { label: 'Status', value: 'status' },
    { label: 'Source', value: 'source' },
    { label: 'Company', value: 'company' },
    { label: 'Territory', value: 'territory' },
  ]

  if (doctype === 'Lead') {
    return [
      ...commonFields,
      { label: 'Lead Name', value: 'lead_name' },
      { label: 'Qualification Status', value: 'qualifications_status' },
    ]
  }

  return commonFields
}

function createNewSegment() {
  editingSegment.value = null
  segmentForm.value = {
    segment_name: '',
    description: '',
    doctype: 'Lead',
    filters: [{ field: '', operator: '=', value: '' }],
  }
  segmentPreview.value = { loading: false, count: null }
  showSegmentDialog.value = true
}

function viewSegment(segment) {
  window.location.href = `/app/marketing-segment/${segment.name}`
}

async function testSegment(segment) {
  testingSegment.value = segment.name

  try {
    const result = await window.frappe.call({
      method: 'marketing_hub.marketing_hub.doctype.marketing_segment.marketing_segment.test_segment',
      args: {
        segment: segment.name,
      },
    })

    testResults.value = result.message
    showTestDialog.value = true
  } catch (error) {
    toast({
      title: 'Error',
      text: error.message || 'Failed to test segment',
      icon: 'x',
      iconClasses: 'text-red-600',
    })
  } finally {
    testingSegment.value = null
  }
}

function addFilter() {
  segmentForm.value.filters.push({ field: '', operator: '=', value: '' })
}

function removeFilter(index) {
  segmentForm.value.filters.splice(index, 1)
}

async function previewSegment() {
  segmentPreview.value.loading = true

  try {
    const filters = buildFilters()
    const result = await window.frappe.call({
      method: 'frappe.client.get_count',
      args: {
        doctype: segmentForm.value.doctype,
        filters: filters,
      },
    })

    segmentPreview.value.count = result.message
  } catch (error) {
    toast({
      title: 'Error',
      text: error.message || 'Failed to preview segment',
      icon: 'x',
      iconClasses: 'text-red-600',
    })
  } finally {
    segmentPreview.value.loading = false
  }
}

async function saveSegment() {
  if (!segmentForm.value.segment_name || !segmentForm.value.doctype) {
    toast({
      title: 'Validation Error',
      text: 'Please fill in all required fields',
      icon: 'alert-circle',
      iconClasses: 'text-amber-600',
    })
    return
  }

  savingSegment.value = true

  try {
    const filters = buildFilters()
    const doc = {
      doctype: 'Marketing Segment',
      segment_name: segmentForm.value.segment_name,
      description: segmentForm.value.description,
      filter_json: JSON.stringify({
        doctype: segmentForm.value.doctype,
        filters: filters,
      }),
    }

    if (editingSegment.value) {
      await window.frappe.call({
        method: 'frappe.client.set_value',
        args: {
          doctype: 'Marketing Segment',
          name: editingSegment.value,
          fieldname: doc,
        },
      })
    } else {
      await window.frappe.call({
        method: 'frappe.client.insert',
        args: { doc },
      })
    }

    toast({
      title: 'Success',
      text: editingSegment.value ? 'Segment updated' : 'Segment created',
      icon: 'check',
      iconClasses: 'text-green-600',
    })

    closeSegmentDialog()
    segmentsResource.reload()
  } catch (error) {
    toast({
      title: 'Error',
      text: error.message || 'Failed to save segment',
      icon: 'x',
      iconClasses: 'text-red-600',
    })
  } finally {
    savingSegment.value = false
  }
}

function buildFilters() {
  return segmentForm.value.filters
    .filter(f => f.field && f.value)
    .map(f => [f.field, f.operator, f.value])
}

function closeSegmentDialog() {
  showSegmentDialog.value = false
  editingSegment.value = null
}

function getFilterPreview(filterJson) {
  try {
    const filters = JSON.parse(filterJson)
    if (filters.filters && filters.filters.length > 0) {
      return filters.filters
        .slice(0, 2)
        .map(f => `${f[0]} ${f[1]} ${f[2]}`)
        .join(', ')
    }
  } catch (e) {
    return 'Custom filters'
  }
  return 'No filters'
}

function formatNumber(num) {
  if (num === null || num === undefined) return ''
  return num.toLocaleString()
}

function getSegmentActions(segment) {
  return [
    {
      label: 'Edit',
      icon: 'edit',
      onClick: () => window.location.href = `/app/marketing-segment/${segment.name}`,
    },
    {
      label: 'Duplicate',
      icon: 'copy',
      onClick: () => duplicateSegment(segment),
    },
    {
      label: segment.disabled ? 'Enable' : 'Disable',
      icon: segment.disabled ? 'check' : 'x',
      onClick: () => toggleSegmentStatus(segment),
    },
    {
      label: 'Delete',
      icon: 'trash-2',
      onClick: () => deleteSegment(segment),
    },
  ]
}

async function duplicateSegment(segment) {
  // Implementation for duplicate
  toast({
    title: 'Info',
    text: 'Duplicate feature coming soon',
    icon: 'info',
    iconClasses: 'text-blue-600',
  })
}

async function toggleSegmentStatus(segment) {
  try {
    await window.frappe.call({
      method: 'frappe.client.set_value',
      args: {
        doctype: 'Marketing Segment',
        name: segment.name,
        fieldname: 'disabled',
        value: segment.disabled ? 0 : 1,
      },
    })

    toast({
      title: 'Success',
      text: `Segment ${segment.disabled ? 'enabled' : 'disabled'}`,
      icon: 'check',
      iconClasses: 'text-green-600',
    })

    segmentsResource.reload()
  } catch (error) {
    toast({
      title: 'Error',
      text: error.message,
      icon: 'x',
      iconClasses: 'text-red-600',
    })
  }
}

async function deleteSegment(segment) {
  if (!confirm(`Are you sure you want to delete segment "${segment.segment_name}"?`)) {
    return
  }

  try {
    await window.frappe.call({
      method: 'frappe.client.delete',
      args: {
        doctype: 'Marketing Segment',
        name: segment.name,
      },
    })

    toast({
      title: 'Success',
      text: 'Segment deleted',
      icon: 'check',
      iconClasses: 'text-green-600',
    })

    segmentsResource.reload()
  } catch (error) {
    toast({
      title: 'Error',
      text: error.message,
      icon: 'x',
      iconClasses: 'text-red-600',
    })
  }
}
</script>
