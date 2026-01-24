<template>
  <div class="flex h-full flex-col overflow-auto bg-surface-gray-1">
    <div class="flex-1 px-5 py-5 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-4xl">
        <!-- Header -->
        <div class="mb-6">
          <h1 class="text-2xl font-semibold text-ink-gray-9">Create Omni-Channel Blast</h1>
          <p class="mt-1 text-sm text-ink-gray-6">
            Send multi-channel campaigns to your marketing segments
          </p>
        </div>

        <!-- Progress Steps -->
        <div class="mb-8">
          <div class="flex items-center justify-between">
            <div
              v-for="(step, index) in steps"
              :key="step.id"
              class="flex flex-1 items-center"
            >
              <div class="flex items-center">
                <div
                  :class="[
                    'flex h-10 w-10 items-center justify-center rounded-full border-2 transition-colors',
                    currentStep >= index
                      ? 'border-primary-500 bg-primary-500 text-white'
                      : 'border-outline-gray-3 bg-surface-cards text-ink-gray-6',
                  ]"
                >
                  <span class="text-sm font-semibold">{{ index + 1 }}</span>
                </div>
                <div class="ml-3">
                  <p
                    :class="[
                      'text-sm font-medium',
                      currentStep >= index ? 'text-ink-gray-9' : 'text-ink-gray-6',
                    ]"
                  >
                    {{ step.title }}
                  </p>
                </div>
              </div>
              <div
                v-if="index < steps.length - 1"
                :class="[
                  'mx-4 h-0.5 flex-1',
                  currentStep > index ? 'bg-primary-500' : 'bg-outline-gray-3',
                ]"
              ></div>
            </div>
          </div>
        </div>

        <!-- Form Container -->
        <div class="rounded-lg border border-outline-gray-1 bg-surface-cards shadow-sm">
          <!-- Step 1: Campaign Selection -->
          <div v-if="currentStep === 0" class="p-6">
            <h2 class="mb-4 text-lg font-semibold text-ink-gray-9">Select Campaign</h2>
            
            <FormControl
              label="Campaign"
              v-model="formData.campaign"
              :options="campaignOptions"
              placeholder="Select a campaign"
              :required="true"
            />
            
            <FormControl
              label="Activity Name"
              v-model="formData.activity_name"
              placeholder="e.g., Summer Sale Email Blast"
              :required="true"
              class="mt-4"
            />

            <FormControl
              label="Scheduled Date & Time"
              type="datetime-local"
              v-model="formData.scheduled_time"
              class="mt-4"
            />
          </div>

          <!-- Step 2: Channel Selection -->
          <div v-if="currentStep === 1" class="p-6">
            <h2 class="mb-4 text-lg font-semibold text-ink-gray-9">Select Channels</h2>
            <p class="mb-4 text-sm text-ink-gray-6">
              Choose which channels to use for this blast
            </p>

            <div class="grid grid-cols-2 gap-4 md:grid-cols-4">
              <div
                v-for="channel in channels"
                :key="channel.value"
                @click="toggleChannel(channel.value)"
                :class="[
                  'cursor-pointer rounded-lg border-2 p-4 text-center transition-all',
                  formData.channels.includes(channel.value)
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-outline-gray-2 bg-surface-cards hover:border-outline-gray-3',
                  !channel.enabled && 'cursor-not-allowed opacity-50',
                ]"
              >
                <div class="mb-2 text-2xl">{{ channel.icon }}</div>
                <div class="text-sm font-medium text-ink-gray-9">{{ channel.label }}</div>
                <div v-if="!channel.enabled" class="mt-1 text-xs text-red-600">
                  {{ channel.disabledReason }}
                </div>
              </div>
            </div>

            <div v-if="formData.channels.length === 0" class="mt-4 rounded-md bg-amber-50 p-3">
              <p class="text-sm text-amber-800">Please select at least one channel</p>
            </div>
          </div>

          <!-- Step 3: Segment Selection -->
          <div v-if="currentStep === 2" class="p-6">
            <h2 class="mb-4 text-lg font-semibold text-ink-gray-9">Select Audience Segment</h2>

            <FormControl
              label="Marketing Segment"
              v-model="formData.segment"
              :options="segmentOptions"
              placeholder="Select a segment"
              :required="true"
            />

            <div v-if="formData.segment && segmentPreview.loading" class="mt-4">
              <LoadingIndicator class="h-6 w-6" />
            </div>

            <div
              v-if="formData.segment && !segmentPreview.loading && segmentPreview.data"
              class="mt-4 rounded-md bg-blue-50 p-4"
            >
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm font-medium text-blue-900">Segment Preview</p>
                  <p class="mt-1 text-xs text-blue-700">
                    {{ segmentPreview.data.count }} recipients will receive this blast
                  </p>
                </div>
                <Button size="sm" variant="ghost" @click="refreshSegmentPreview">
                  <template #prefix>
                    <FeatherIcon name="refresh-cw" class="h-4 w-4" />
                  </template>
                  Refresh
                </Button>
              </div>
            </div>
          </div>

          <!-- Step 4: Content & Message -->
          <div v-if="currentStep === 3" class="p-6">
            <h2 class="mb-4 text-lg font-semibold text-ink-gray-9">Compose Message</h2>

            <FormControl
              label="Subject / Title"
              v-model="formData.subject"
              placeholder="Message subject"
              class="mb-4"
            />

            <div class="mb-4">
              <label class="mb-2 block text-sm font-medium text-ink-gray-9">
                Message Content
              </label>
              <textarea
                v-model="formData.message"
                rows="8"
                class="w-full rounded-md border border-outline-gray-2 p-3 text-sm focus:border-primary-500 focus:outline-none"
                placeholder="Enter your message here..."
              ></textarea>
              <p class="mt-1 text-xs text-ink-gray-6">
                Character count: {{ formData.message?.length || 0 }}
                <span v-if="formData.channels.includes('SMS')" class="text-amber-600">
                  (SMS limit: 160 characters)
                </span>
              </p>
            </div>

            <FormControl
              v-if="formData.channels.includes('Email')"
              label="Email Template (Optional)"
              v-model="formData.template"
              :options="templateOptions"
              placeholder="Select a template"
              class="mb-4"
            />

            <div class="rounded-md bg-blue-50 p-3">
              <p class="text-xs text-blue-700">
                <strong>Tip:</strong> Content will be automatically adapted for each channel.
                SMS will be truncated to 160 characters, HTML will be stripped for plain text channels.
              </p>
            </div>
          </div>

          <!-- Step 5: Review & Send -->
          <div v-if="currentStep === 4" class="p-6">
            <h2 class="mb-4 text-lg font-semibold text-ink-gray-9">Review & Send</h2>

            <div class="space-y-4">
              <!-- Campaign Info -->
              <div class="rounded-md border border-outline-gray-2 p-4">
                <h3 class="mb-2 text-sm font-medium text-ink-gray-9">Campaign Details</h3>
                <dl class="space-y-2 text-sm">
                  <div class="flex justify-between">
                    <dt class="text-ink-gray-6">Campaign:</dt>
                    <dd class="font-medium text-ink-gray-9">{{ getCampaignName(formData.campaign) }}</dd>
                  </div>
                  <div class="flex justify-between">
                    <dt class="text-ink-gray-6">Activity Name:</dt>
                    <dd class="font-medium text-ink-gray-9">{{ formData.activity_name }}</dd>
                  </div>
                  <div v-if="formData.scheduled_time" class="flex justify-between">
                    <dt class="text-ink-gray-6">Scheduled:</dt>
                    <dd class="font-medium text-ink-gray-9">{{ formatDateTime(formData.scheduled_time) }}</dd>
                  </div>
                </dl>
              </div>

              <!-- Channels -->
              <div class="rounded-md border border-outline-gray-2 p-4">
                <h3 class="mb-2 text-sm font-medium text-ink-gray-9">Channels</h3>
                <div class="flex flex-wrap gap-2">
                  <span
                    v-for="channel in formData.channels"
                    :key="channel"
                    class="inline-flex items-center rounded-full bg-primary-100 px-3 py-1 text-xs font-medium text-primary-700"
                  >
                    {{ channel }}
                  </span>
                </div>
              </div>

              <!-- Audience -->
              <div class="rounded-md border border-outline-gray-2 p-4">
                <h3 class="mb-2 text-sm font-medium text-ink-gray-9">Audience</h3>
                <dl class="space-y-2 text-sm">
                  <div class="flex justify-between">
                    <dt class="text-ink-gray-6">Segment:</dt>
                    <dd class="font-medium text-ink-gray-9">{{ getSegmentName(formData.segment) }}</dd>
                  </div>
                  <div v-if="segmentPreview.data" class="flex justify-between">
                    <dt class="text-ink-gray-6">Recipients:</dt>
                    <dd class="font-medium text-ink-gray-9">{{ segmentPreview.data.count }}</dd>
                  </div>
                </dl>
              </div>

              <!-- Message Preview -->
              <div class="rounded-md border border-outline-gray-2 p-4">
                <h3 class="mb-2 text-sm font-medium text-ink-gray-9">Message Preview</h3>
                <dl class="space-y-2 text-sm">
                  <div>
                    <dt class="text-ink-gray-6">Subject:</dt>
                    <dd class="mt-1 font-medium text-ink-gray-9">{{ formData.subject }}</dd>
                  </div>
                  <div>
                    <dt class="text-ink-gray-6">Content:</dt>
                    <dd class="mt-1 text-ink-gray-9">{{ formData.message?.substring(0, 200) }}{{ formData.message?.length > 200 ? '...' : '' }}</dd>
                  </div>
                </dl>
              </div>
            </div>
          </div>

          <!-- Navigation Buttons -->
          <div class="flex items-center justify-between border-t border-outline-gray-2 p-6">
            <Button
              v-if="currentStep > 0"
              variant="ghost"
              @click="previousStep"
            >
              <template #prefix>
                <FeatherIcon name="chevron-left" class="h-4 w-4" />
              </template>
              Back
            </Button>
            <div v-else></div>

            <div class="flex space-x-3">
              <Button
                variant="ghost"
                @click="cancel"
              >
                Cancel
              </Button>
              <Button
                v-if="currentStep < steps.length - 1"
                @click="nextStep"
                :disabled="!canProceed"
              >
                Next
                <template #suffix>
                  <FeatherIcon name="chevron-right" class="h-4 w-4" />
                </template>
              </Button>
              <Button
                v-else
                @click="createBlast"
                :loading="creating"
                variant="solid"
              >
                <template #prefix>
                  <FeatherIcon name="send" class="h-4 w-4" />
                </template>
                {{ formData.scheduled_time ? 'Schedule Blast' : 'Send Now' }}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { createResource, Button, FormControl, FeatherIcon, LoadingIndicator } from 'frappe-ui'
import { toast } from 'frappe-ui'

const router = useRouter()

const steps = [
  { id: 'campaign', title: 'Campaign' },
  { id: 'channels', title: 'Channels' },
  { id: 'segment', title: 'Audience' },
  { id: 'content', title: 'Content' },
  { id: 'review', title: 'Review' },
]

const currentStep = ref(0)
const creating = ref(false)

// Form data
const formData = ref({
  campaign: '',
  activity_name: '',
  scheduled_time: '',
  channels: [],
  segment: '',
  subject: '',
  message: '',
  template: '',
})

// Available channels
const channels = ref([
  { value: 'Email', label: 'Email', icon: '📧', enabled: true },
  { value: 'SMS', label: 'SMS', icon: '💬', enabled: true },
  { value: 'WhatsApp', label: 'WhatsApp', icon: '📱', enabled: true },
  { value: 'Push Notification', label: 'Push', icon: '🔔', enabled: false, disabledReason: 'Not configured' },
])

// API Resources
const campaignsResource = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'Campaign',
    fields: ['name', 'campaign_name', 'status'],
    filters: { status: ['in', ['Planning', 'Running']] },
    limit_page_length: 100,
  },
  auto: true,
})

const segmentsResource = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'Marketing Segment',
    fields: ['name', 'segment_name'],
    filters: { disabled: 0 },
    limit_page_length: 100,
  },
  auto: true,
})

const templatesResource = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'Marketing Template',
    fields: ['name', 'template_name'],
    filters: { disabled: 0 },
    limit_page_length: 100,
  },
  auto: true,
})

const segmentPreview = ref({
  loading: false,
  data: null,
})

const createBlastResource = createResource({
  url: 'marketing_hub.utils.omni_blast.execute_blast',
  onSuccess(data) {
    creating.value = false
    toast({
      title: 'Success',
      text: 'Blast created successfully!',
      icon: 'check',
      iconClasses: 'text-green-600',
    })
    router.push('/marketing/campaigns')
  },
  onError(error) {
    creating.value = false
    toast({
      title: 'Error',
      text: error.message || 'Failed to create blast',
      icon: 'x',
      iconClasses: 'text-red-600',
    })
  },
})

// Computed properties
const campaignOptions = computed(() => {
  if (!campaignsResource.data) return []
  return campaignsResource.data.map(c => ({
    label: c.campaign_name,
    value: c.name,
  }))
})

const segmentOptions = computed(() => {
  if (!segmentsResource.data) return []
  return segmentsResource.data.map(s => ({
    label: s.segment_name,
    value: s.name,
  }))
})

const templateOptions = computed(() => {
  if (!templatesResource.data) return []
  return templatesResource.data.map(t => ({
    label: t.template_name,
    value: t.name,
  }))
})

const canProceed = computed(() => {
  switch (currentStep.value) {
    case 0:
      return formData.value.campaign && formData.value.activity_name
    case 1:
      return formData.value.channels.length > 0
    case 2:
      return formData.value.segment
    case 3:
      return formData.value.subject && formData.value.message
    default:
      return true
  }
})

// Methods
function toggleChannel(channel) {
  const channelConfig = channels.value.find(c => c.value === channel)
  if (!channelConfig.enabled) return

  const index = formData.value.channels.indexOf(channel)
  if (index > -1) {
    formData.value.channels.splice(index, 1)
  } else {
    formData.value.channels.push(channel)
  }
}

function nextStep() {
  if (canProceed.value && currentStep.value < steps.length - 1) {
    currentStep.value++
    
    // Load segment preview when entering segment step
    if (currentStep.value === 2 && formData.value.segment) {
      refreshSegmentPreview()
    }
  }
}

function previousStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

async function refreshSegmentPreview() {
  if (!formData.value.segment) return

  segmentPreview.value.loading = true
  try {
    const result = await window.frappe.call({
      method: 'marketing_hub.marketing_hub.doctype.marketing_segment.marketing_segment.get_segment_count',
      args: {
        segment: formData.value.segment,
      },
    })
    segmentPreview.value.data = result.message
  } catch (error) {
    console.error('Error loading segment preview:', error)
  } finally {
    segmentPreview.value.loading = false
  }
}

async function createBlast() {
  creating.value = true

  // Create Omni Blast doctype
  try {
    const blastDoc = await window.frappe.call({
      method: 'frappe.client.insert',
      args: {
        doc: {
          doctype: 'Omni Blast',
          campaign: formData.value.campaign,
          blast_name: formData.value.activity_name,
          segment: formData.value.segment,
          subject: formData.value.subject,
          message: formData.value.message,
          channels: formData.value.channels.join('\n'),
          scheduled_time: formData.value.scheduled_time || null,
          status: formData.value.scheduled_time ? 'Scheduled' : 'Draft',
        },
      },
    })

    // If sending now, execute the blast
    if (!formData.value.scheduled_time) {
      await createBlastResource.submit({
        campaign_activity: blastDoc.message.name,
      })
    } else {
      creating.value = false
      toast({
        title: 'Success',
        text: 'Blast scheduled successfully!',
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      router.push('/marketing/campaigns')
    }
  } catch (error) {
    creating.value = false
    toast({
      title: 'Error',
      text: error.message || 'Failed to create blast',
      icon: 'x',
      iconClasses: 'text-red-600',
    })
  }
}

function cancel() {
  router.push('/marketing/campaigns')
}

function getCampaignName(campaignId) {
  const campaign = campaignsResource.data?.find(c => c.name === campaignId)
  return campaign?.campaign_name || campaignId
}

function getSegmentName(segmentId) {
  const segment = segmentsResource.data?.find(s => s.name === segmentId)
  return segment?.segment_name || segmentId
}

function formatDateTime(dateTime) {
  if (!dateTime) return ''
  return new Date(dateTime).toLocaleString()
}

// Load settings on mount to check enabled channels
onMounted(async () => {
  try {
    const settings = await window.frappe.call({
      method: 'frappe.client.get_value',
      args: {
        doctype: 'Marketing Hub Settings',
        filters: {},
        fieldname: ['enable_email_blast', 'enable_sms_blast', 'enable_whatsapp_blast'],
      },
    })

    if (settings.message) {
      channels.value[0].enabled = settings.message.enable_email_blast === 1
      channels.value[1].enabled = settings.message.enable_sms_blast === 1
      channels.value[2].enabled = settings.message.enable_whatsapp_blast === 1

      // Update disabled reasons
      if (!channels.value[0].enabled) channels.value[0].disabledReason = 'Disabled in settings'
      if (!channels.value[1].enabled) channels.value[1].disabledReason = 'Disabled in settings'
      if (!channels.value[2].enabled) channels.value[2].disabledReason = 'Disabled in settings'
    }
  } catch (error) {
    console.error('Error loading settings:', error)
  }
})
</script>
