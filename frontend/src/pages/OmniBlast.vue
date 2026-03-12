<template>
  <div class="flex h-full flex-col overflow-auto bg-surface-gray-1">
    <div class="flex-1 px-5 py-5 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-3xl">
        <!-- Header -->
        <div class="mb-5">
          <h1 class="text-xl font-semibold text-ink-gray-9">Omni-Channel Blast</h1>
          <p class="mt-1 text-sm text-ink-gray-6">
            Reach your audience across multiple channels at once
          </p>
        </div>

        <!-- Compact Stepper -->
        <div class="mb-6 flex items-center gap-1">
          <template v-for="(step, index) in steps" :key="step.id">
            <button
              @click="goToStep(index)"
              class="flex items-center gap-2 rounded-full px-3 py-1.5 text-sm font-medium transition-colors"
              :class="[
                currentStep === index
                  ? 'bg-surface-white text-ink-gray-9 shadow-sm ring-1 ring-outline-gray-2'
                  : currentStep > index
                    ? 'text-ink-gray-7 hover:text-ink-gray-9'
                    : 'text-ink-gray-5',
              ]"
              :disabled="index > furthestStep"
            >
              <div
                class="flex h-5 w-5 items-center justify-center rounded-full text-xs font-semibold"
                :class="[
                  currentStep > index
                    ? 'bg-green-100 text-green-700'
                    : currentStep === index
                      ? 'bg-surface-gray-3 text-ink-gray-9'
                      : 'bg-surface-gray-2 text-ink-gray-5',
                ]"
              >
                <IconCheck v-if="currentStep > index" class="h-3 w-3" />
                <span v-else>{{ index + 1 }}</span>
              </div>
              {{ step.title }}
            </button>
            <IconChevronRight
              v-if="index < steps.length - 1"
              class="h-4 w-4 flex-shrink-0 text-ink-gray-4"
            />
          </template>
        </div>

        <!-- Form Container -->
        <div class="rounded-lg border border-outline-gray-1 bg-surface-cards shadow-sm">

          <!-- Step 1: Setup (Campaign + Channels + Schedule) -->
          <div v-if="currentStep === 0" class="space-y-6 p-6">
            <div>
              <h2 class="mb-4 text-base font-semibold text-ink-gray-9">Campaign & Schedule</h2>
              <div class="space-y-4">
                <FormControl
                  label="Campaign"
                  v-model="formData.campaign"
                  :options="campaignOptions"
                  placeholder="Select a campaign"
                  :required="true"
                />
                <FormControl
                  label="Blast Name"
                  v-model="formData.activity_name"
                  placeholder="e.g., Summer Sale Blast"
                  :required="true"
                />
                <div class="grid grid-cols-2 gap-4">
                  <FormControl
                    label="Marketing Segment"
                    v-model="formData.segment"
                    :options="segmentOptions"
                    placeholder="Select audience"
                    :required="true"
                  />
                  <FormControl
                    label="Schedule (optional)"
                    type="datetime-local"
                    v-model="formData.scheduled_time"
                  />
                </div>
                <!-- Segment count preview inline -->
                <div v-if="segmentPreview.loading" class="flex items-center gap-2 text-sm text-ink-gray-6">
                  <LoadingIndicator class="h-4 w-4" /> Counting recipients…
                </div>
                <div
                  v-else-if="segmentPreview.data"
                  class="flex items-center gap-2 rounded-md bg-surface-gray-2 px-3 py-2 text-sm"
                >
                  <IconUsers class="h-4 w-4 text-ink-gray-6" />
                  <span class="text-ink-gray-8">
                    <strong>{{ segmentPreview.data.count }}</strong> recipients in this segment
                  </span>
                </div>
              </div>
            </div>

            <div class="border-t border-outline-gray-2 pt-5">
              <h2 class="mb-3 text-base font-semibold text-ink-gray-9">Channels</h2>
              <p class="mb-4 text-sm text-ink-gray-6">Select which channels to blast on</p>
              <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
                <button
                  v-for="channel in channels"
                  :key="channel.value"
                  @click="toggleChannel(channel.value)"
                  :disabled="!channel.enabled"
                  :class="[
                    'flex flex-col items-center gap-2 rounded-lg border-2 px-3 py-4 transition-all',
                    formData.channels.includes(channel.value)
                      ? 'border-primary-500 bg-blue-50/50'
                      : 'border-outline-gray-2 bg-surface-cards hover:border-outline-gray-3',
                    !channel.enabled && 'cursor-not-allowed opacity-40',
                  ]"
                >
                  <component :is="channel.icon" class="h-5 w-5" :class="formData.channels.includes(channel.value) ? 'text-primary-600' : 'text-ink-gray-6'" />
                  <span class="text-sm font-medium" :class="formData.channels.includes(channel.value) ? 'text-primary-700' : 'text-ink-gray-8'">{{ channel.label }}</span>
                  <span v-if="!channel.enabled" class="text-[11px] text-ink-red-3">Not configured</span>
                </button>
              </div>
              <div v-if="formData.channels.length === 0" class="mt-3 rounded-md bg-surface-amber-1 px-3 py-2 text-sm text-ink-amber-3">
                Select at least one channel
              </div>
            </div>
          </div>

          <!-- Step 2: Content & Message -->
          <div v-if="currentStep === 1" class="p-6">
            <h2 class="mb-4 text-base font-semibold text-ink-gray-9">Compose Message</h2>

            <div class="space-y-4">
              <FormControl
                label="Subject"
                v-model="formData.subject"
                placeholder="Message subject line"
                :required="true"
              />

              <div>
                <label class="mb-1.5 block text-sm font-medium text-ink-gray-8">
                  Message Content
                </label>
                <textarea
                  v-model="formData.message"
                  rows="8"
                  class="w-full rounded-lg border border-outline-gray-2 bg-surface-cards p-3 text-sm text-ink-gray-9 placeholder:text-ink-gray-5 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 focus:outline-none"
                  placeholder="Write your message here…"
                ></textarea>
                <div class="mt-1 flex items-center justify-between text-xs text-ink-gray-5">
                  <span>{{ formData.message?.length || 0 }} characters</span>
                  <span
                    v-if="formData.channels.includes('SMS') && (formData.message?.length || 0) > 160"
                    class="text-ink-amber-3"
                  >SMS messages over 160 chars will be split</span>
                </div>
              </div>

              <FormControl
                v-if="formData.channels.includes('Email')"
                label="Email Template (optional)"
                v-model="formData.template"
                :options="templateOptions"
                placeholder="Select a template"
              />
            </div>
          </div>

          <!-- Step 3: Review & Send -->
          <div v-if="currentStep === 2" class="p-6">
            <h2 class="mb-4 text-base font-semibold text-ink-gray-9">Review & Send</h2>

            <div class="space-y-3">
              <div class="rounded-lg bg-surface-gray-2 p-4">
                <div class="grid grid-cols-2 gap-y-3 text-sm">
                  <div class="text-ink-gray-6">Campaign</div>
                  <div class="font-medium text-ink-gray-9">{{ getCampaignName(formData.campaign) }}</div>
                  <div class="text-ink-gray-6">Blast Name</div>
                  <div class="font-medium text-ink-gray-9">{{ formData.activity_name }}</div>
                  <div class="text-ink-gray-6">Audience</div>
                  <div class="font-medium text-ink-gray-9">
                    {{ getSegmentName(formData.segment) }}
                    <span v-if="segmentPreview.data" class="text-ink-gray-6">({{ segmentPreview.data.count }})</span>
                  </div>
                  <div class="text-ink-gray-6">Channels</div>
                  <div class="flex flex-wrap gap-1.5">
                    <Badge
                      v-for="channel in formData.channels"
                      :key="channel"
                      :label="channel"
                      variant="subtle"
                      theme="blue"
                      size="sm"
                    />
                  </div>
                  <div v-if="formData.scheduled_time" class="text-ink-gray-6">Scheduled</div>
                  <div v-if="formData.scheduled_time" class="font-medium text-ink-gray-9">{{ formatDateTime(formData.scheduled_time) }}</div>
                </div>
              </div>

              <div class="rounded-lg border border-outline-gray-2 p-4">
                <div class="mb-2 text-sm font-medium text-ink-gray-8">Message Preview</div>
                <div class="text-sm font-medium text-ink-gray-9">{{ formData.subject }}</div>
                <div class="mt-2 whitespace-pre-wrap text-sm text-ink-gray-7">{{ formData.message?.substring(0, 300) }}{{ (formData.message?.length || 0) > 300 ? '…' : '' }}</div>
              </div>
            </div>
          </div>

          <!-- Navigation -->
          <div class="flex items-center justify-between border-t border-outline-gray-2 px-6 py-4">
            <Button
              v-if="currentStep > 0"
              variant="ghost"
              @click="previousStep"
              label="Back"
            />
            <div v-else />

            <div class="flex gap-2">
              <Button variant="ghost" @click="cancel" label="Cancel" />
              <Button
                v-if="currentStep < steps.length - 1"
                @click="nextStep"
                :disabled="!canProceed"
                variant="solid"
                label="Continue"
              />
              <Button
                v-else
                @click="createBlast"
                :loading="creating"
                variant="solid"
                :label="formData.scheduled_time ? 'Schedule Blast' : 'Send Now'"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, markRaw } from 'vue'
import { useRouter } from 'vue-router'
import { createResource, createListResource, Button, FormControl, LoadingIndicator, Badge, call } from 'frappe-ui'
import { toast } from '@/utils/toast'

import IconMail from '~icons/lucide/mail'
import IconMessageSquare from '~icons/lucide/message-square'
import IconSmartphone from '~icons/lucide/smartphone'
import IconBell from '~icons/lucide/bell'
import IconCheck from '~icons/lucide/check'
import IconChevronRight from '~icons/lucide/chevron-right'
import IconUsers from '~icons/lucide/users'

const router = useRouter()

const steps = [
  { id: 'setup', title: 'Setup' },
  { id: 'content', title: 'Content' },
  { id: 'review', title: 'Review' },
]

const currentStep = ref(0)
const furthestStep = ref(0)
const creating = ref(false)

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

const channels = ref([
  { value: 'Email', label: 'Email', icon: markRaw(IconMail), enabled: true },
  { value: 'SMS', label: 'SMS', icon: markRaw(IconMessageSquare), enabled: true },
  { value: 'WhatsApp', label: 'WhatsApp', icon: markRaw(IconSmartphone), enabled: true },
  { value: 'Push Notification', label: 'Push', icon: markRaw(IconBell), enabled: false },
])

// Fetch available networks from Social Media Network DocType
const networksResource = createListResource({
  doctype: 'Social Media Network',
  fields: ['name', 'platform_name', 'platform_type', 'enabled'],
  pageLength: 50,
  auto: true,
  onSuccess(data) {
    if (data && data.length) {
      const iconMap = {
        Email: markRaw(IconMail),
        SMS: markRaw(IconMessageSquare),
        WhatsApp: markRaw(IconSmartphone),
      }
      channels.value = data.map(n => ({
        value: n.platform_name || n.name,
        label: n.platform_name || n.name,
        icon: iconMap[n.platform_name] || markRaw(IconBell),
        enabled: Number(n.enabled) !== 0,
        disabledReason: Number(n.enabled) === 0 ? 'Disabled in settings' : '',
      }))
    }
  },
})

const campaignsResource = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'Marketing Campaign',
    fields: ['name', 'campaign_name', 'status'],
    filters: { status: ['in', ['Draft', 'Active']] },
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

const segmentPreview = ref({ loading: false, data: null })

const createBlastResource = createResource({
  url: 'marketing_hub.utils.omni_blast.execute_blast',
  onSuccess() {
    creating.value = false
    toast({ title: 'Success', text: 'Blast created successfully!', icon: 'check', iconClasses: 'text-green-600' })
    router.push('/marketing/campaigns')
  },
  onError(error) {
    creating.value = false
    toast({ title: 'Error', text: error.message || 'Failed to create blast', icon: 'x', iconClasses: 'text-red-600' })
  },
})

const campaignOptions = computed(() =>
  (campaignsResource.data || []).map(c => ({ label: c.campaign_name, value: c.name }))
)

const segmentOptions = computed(() =>
  (segmentsResource.data || []).map(s => ({ label: s.segment_name, value: s.name }))
)

const templateOptions = computed(() =>
  (templatesResource.data || []).map(t => ({ label: t.template_name, value: t.name }))
)

const canProceed = computed(() => {
  switch (currentStep.value) {
    case 0:
      return formData.value.campaign && formData.value.activity_name && formData.value.segment && formData.value.channels.length > 0
    case 1:
      return formData.value.subject && formData.value.message
    default:
      return true
  }
})

// Auto-load segment preview when segment changes
watch(() => formData.value.segment, (val) => {
  if (val) refreshSegmentPreview()
  else segmentPreview.value.data = null
})

function toggleChannel(channel) {
  const config = channels.value.find(c => c.value === channel)
  if (!config?.enabled) return
  const idx = formData.value.channels.indexOf(channel)
  if (idx > -1) formData.value.channels.splice(idx, 1)
  else formData.value.channels.push(channel)
}

function goToStep(index) {
  if (index <= furthestStep.value) currentStep.value = index
}

function nextStep() {
  if (canProceed.value && currentStep.value < steps.length - 1) {
    currentStep.value++
    if (currentStep.value > furthestStep.value) furthestStep.value = currentStep.value
  }
}

function previousStep() {
  if (currentStep.value > 0) currentStep.value--
}

async function refreshSegmentPreview() {
  if (!formData.value.segment) return
  segmentPreview.value.loading = true
  try {
    const result = await call(
      'marketing_hub.marketing_hub.doctype.marketing_segment.marketing_segment.get_segment_count',
      { segment: formData.value.segment }
    )
    segmentPreview.value.data = result
  } catch (error) {
    console.error('Error loading segment preview:', error)
  } finally {
    segmentPreview.value.loading = false
  }
}

async function createBlast() {
  creating.value = true
  try {
    const blastDoc = await call('frappe.client.insert', {
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
    })

    if (!formData.value.scheduled_time) {
      await createBlastResource.submit({ campaign_activity: blastDoc.name })
    } else {
      creating.value = false
      toast({ title: 'Success', text: 'Blast scheduled successfully!', icon: 'check', iconClasses: 'text-green-600' })
      router.push('/marketing/campaigns')
    }
  } catch (error) {
    creating.value = false
    toast({ title: 'Error', text: error.message || 'Failed to create blast', icon: 'x', iconClasses: 'text-red-600' })
  }
}

function cancel() {
  router.push('/marketing/campaigns')
}

function getCampaignName(id) {
  return campaignsResource.data?.find(c => c.name === id)?.campaign_name || id
}

function getSegmentName(id) {
  return segmentsResource.data?.find(s => s.name === id)?.segment_name || id
}

function formatDateTime(dt) {
  return dt ? new Date(dt).toLocaleString() : ''
}

// Check enabled channels from settings
onMounted(async () => {
  try {
    const data = await call('frappe.client.get_value', {
      doctype: 'Marketing Hub Settings',
      filters: {},
      fieldname: ['enable_email_blast', 'enable_sms_blast', 'enable_whatsapp_blast'],
    })

    if (data) {
      channels.value[0].enabled = Number(data.enable_email_blast) === 1
      channels.value[1].enabled = Number(data.enable_sms_blast) === 1
      channels.value[2].enabled = Number(data.enable_whatsapp_blast) === 1
    }
  } catch (error) {
    console.error('Error loading settings:', error)
  }
})
</script>
