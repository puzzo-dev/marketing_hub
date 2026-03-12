<template>
  <div v-if="showOnboarding" class="fixed inset-0 z-50 flex items-center justify-center bg-ink-gray-9/50 backdrop-blur-sm">
    <div class="relative w-full max-w-2xl rounded-xl border border-outline-gray-2 bg-surface-cards shadow-2xl">
      <!-- Close Button -->
      <button
        @click="skipOnboarding"
        class="absolute right-4 top-4 rounded-lg p-2 text-ink-gray-6 transition-colors hover:bg-surface-gray-2 hover:text-ink-gray-9"
      >
        <FeatherIcon name="x" class="h-5 w-5" />
      </button>

      <!-- Step Content -->
      <div class="p-8">
        <!-- Progress Indicator -->
        <div class="mb-6 flex items-center justify-between">
          <div class="flex gap-2">
            <div
              v-for="(step, index) in steps"
              :key="index"
              :class="[
                'h-2 w-12 rounded-full transition-all',
                index === currentStep
                  ? 'bg-primary-500'
                  : index < currentStep
                  ? 'bg-primary-300'
                  : 'bg-surface-gray-3',
              ]"
            />
          </div>
          <span class="text-sm text-ink-gray-6">{{ currentStep + 1 }} / {{ steps.length }}</span>
        </div>

        <!-- Step Icon and Title -->
        <div class="mb-6 text-center">
          <div
            class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl"
            :style="{ backgroundColor: steps[currentStep].color + '20' }"
          >
            <FeatherIcon :name="steps[currentStep].icon" class="h-8 w-8" :style="{ color: steps[currentStep].color }" />
          </div>
          <h2 class="text-2xl font-semibold text-ink-gray-9">{{ steps[currentStep].title }}</h2>
          <p class="mt-2 text-base text-ink-gray-6">{{ steps[currentStep].description }}</p>
        </div>

        <!-- Step-specific Content -->
        <div class="mb-8 rounded-lg border border-outline-gray-2 bg-surface-gray-1 p-6">
          <!-- Welcome Step -->
          <div v-if="currentStep === 0" class="space-y-4">
            <div class="flex items-start gap-3">
              <div class="mt-1 flex h-6 w-6 items-center justify-center rounded-full bg-primary-100 text-primary-600">
                <FeatherIcon name="check" class="h-4 w-4" />
              </div>
              <div>
                <h4 class="font-medium text-ink-gray-9">Omni-Channel Marketing</h4>
                <p class="text-sm text-ink-gray-6">Reach your audience via Email, SMS, WhatsApp, and Push Notifications</p>
              </div>
            </div>
            <div class="flex items-start gap-3">
              <div class="mt-1 flex h-6 w-6 items-center justify-center rounded-full bg-primary-100 text-primary-600">
                <FeatherIcon name="check" class="h-4 w-4" />
              </div>
              <div>
                <h4 class="font-medium text-ink-gray-9">Advanced Segmentation</h4>
                <p class="text-sm text-ink-gray-6">Create dynamic segments with powerful filtering and targeting</p>
              </div>
            </div>
            <div class="flex items-start gap-3">
              <div class="mt-1 flex h-6 w-6 items-center justify-center rounded-full bg-primary-100 text-primary-600">
                <FeatherIcon name="check" class="h-4 w-4" />
              </div>
              <div>
                <h4 class="font-medium text-ink-gray-9">Analytics & Reporting</h4>
                <p class="text-sm text-ink-gray-6">Track performance with real-time metrics and insights</p>
              </div>
            </div>
          </div>

          <!-- Settings Step -->
          <div v-if="currentStep === 1" class="space-y-4">
            <Alert variant="info">
              <template #icon>
                <FeatherIcon name="info" class="h-4 w-4" />
              </template>
              <template #title>Configure Your Channels</template>
              <template #description>
                Enable and configure the marketing channels you want to use. You can change these settings later.
              </template>
            </Alert>

            <div class="space-y-3">
              <label class="flex items-center justify-between rounded-lg border border-outline-gray-2 bg-surface-cards p-4 transition-colors hover:border-blue-300">
                <div class="flex items-center gap-3">
                  <div class="text-2xl">📧</div>
                  <div>
                    <div class="font-medium text-ink-gray-9">Email Marketing</div>
                    <div class="text-sm text-ink-gray-6">Send email campaigns to your subscribers</div>
                  </div>
                </div>
                <Switch v-model="settings.enable_email_blast" />
              </label>

              <label class="flex items-center justify-between rounded-lg border border-outline-gray-2 bg-surface-cards p-4 transition-colors hover:border-blue-300">
                <div class="flex items-center gap-3">
                  <div class="text-2xl">💬</div>
                  <div>
                    <div class="font-medium text-ink-gray-9">SMS Marketing</div>
                    <div class="text-sm text-ink-gray-6">Reach customers via text messages</div>
                  </div>
                </div>
                <Switch v-model="settings.enable_sms_blast" />
              </label>

              <label class="flex items-center justify-between rounded-lg border border-outline-gray-2 bg-surface-cards p-4 transition-colors hover:border-blue-300">
                <div class="flex items-center gap-3">
                  <div class="text-2xl">📱</div>
                  <div>
                    <div class="font-medium text-ink-gray-9">WhatsApp Business</div>
                    <div class="text-sm text-ink-gray-6">Connect with customers on WhatsApp</div>
                  </div>
                </div>
                <Switch v-model="settings.enable_whatsapp_blast" />
              </label>
            </div>
          </div>

          <!-- Campaign Step -->
          <div v-if="currentStep === 2" class="space-y-4">
            <FormControl
              v-model="demoData.campaign_name"
              label="Campaign Name"
              placeholder="e.g., Summer Sale 2026"
              :required="true"
            />
            <FormControl
              v-model="demoData.campaign_description"
              type="textarea"
              label="Description"
              placeholder="Brief description of your campaign"
              :rows="3"
            />

            <div class="rounded-lg bg-primary-50 p-4">
              <div class="flex items-start gap-3">
                <FeatherIcon name="lightbulb" class="mt-0.5 h-5 w-5 text-primary-600" />
                <div class="text-sm text-ink-gray-7">
                  <strong>Pro Tip:</strong> Start with a clear campaign goal (awareness, conversion, retention) and choose your channels accordingly.
                </div>
              </div>
            </div>
          </div>

          <!-- Segment Step -->
          <div v-if="currentStep === 3" class="space-y-4">
            <p class="text-sm text-ink-gray-6">Create your first audience segment to target the right people with your campaigns.</p>

            <FormControl
              v-model="demoData.segment_name"
              label="Segment Name"
              placeholder="e.g., Active Customers"
              :required="true"
            />

            <div>
              <label class="mb-2 block text-sm font-medium text-ink-gray-9">Target Audience</label>
              <div class="grid gap-3 sm:grid-cols-2">
                <label
                  v-for="audience in audienceTypes"
                  :key="audience.value"
                  :class="[
                    'flex cursor-pointer items-center gap-3 rounded-lg border-2 p-4 transition-all',
                    demoData.segment_doctype === audience.value
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-outline-gray-2 hover:border-outline-gray-3',
                  ]"
                >
                  <input
                    type="radio"
                    v-model="demoData.segment_doctype"
                    :value="audience.value"
                    class="h-4 w-4 text-primary-600"
                  />
                  <div>
                    <div class="font-medium text-ink-gray-9">{{ audience.label }}</div>
                    <div class="text-xs text-ink-gray-6">{{ audience.description }}</div>
                  </div>
                </label>
              </div>
            </div>

            <Alert variant="warning">
              <template #icon>
                <FeatherIcon name="alert-circle" class="h-4 w-4" />
              </template>
              <template #description>
                You can add filters and conditions to your segment later from the Segments page.
              </template>
            </Alert>
          </div>

          <!-- Complete Step -->
          <div v-if="currentStep === 4" class="space-y-4 text-center">
            <div class="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-success-100">
              <FeatherIcon name="check" class="h-10 w-10 text-success-600" />
            </div>

            <div>
              <h3 class="text-lg font-semibold text-ink-gray-9">You're All Set!</h3>
              <p class="mt-2 text-sm text-ink-gray-6">Your Marketing Hub is ready to use. Here's what you can do next:</p>
            </div>

            <div class="space-y-2 text-left">
              <router-link
                to="/marketing/campaigns/new"
                class="flex items-center gap-3 rounded-lg border border-outline-gray-2 bg-surface-cards p-4 transition-colors hover:border-blue-300"
              >
                <FeatherIcon name="target" class="h-5 w-5 text-primary-600" />
                <div>
                  <div class="font-medium text-ink-gray-9">Create Your First Campaign</div>
                  <div class="text-xs text-ink-gray-6">Set up a complete marketing campaign</div>
                </div>
                <FeatherIcon name="chevron-right" class="ml-auto h-5 w-5 text-ink-gray-5" />
              </router-link>

              <router-link
                to="/marketing/blast/new"
                class="flex items-center gap-3 rounded-lg border border-outline-gray-2 bg-surface-cards p-4 transition-colors hover:border-blue-300"
              >
                <FeatherIcon name="send" class="h-5 w-5 text-purple-600" />
                <div>
                  <div class="font-medium text-ink-gray-9">Send Your First Blast</div>
                  <div class="text-xs text-ink-gray-6">Reach your audience across multiple channels</div>
                </div>
                <FeatherIcon name="chevron-right" class="ml-auto h-5 w-5 text-ink-gray-5" />
              </router-link>

              <router-link
                to="/marketing/segments"
                class="flex items-center gap-3 rounded-lg border border-outline-gray-2 bg-surface-cards p-4 transition-colors hover:border-blue-300"
              >
                <FeatherIcon name="users" class="h-5 w-5 text-green-600" />
                <div>
                  <div class="font-medium text-ink-gray-9">Build Audience Segments</div>
                  <div class="text-xs text-ink-gray-6">Target specific groups with filters</div>
                </div>
                <FeatherIcon name="chevron-right" class="ml-auto h-5 w-5 text-ink-gray-5" />
              </router-link>
            </div>
          </div>
        </div>

        <!-- Navigation Buttons -->
        <div class="flex items-center justify-between">
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
          <div v-else />

          <div class="flex gap-2">
            <Button
              v-if="currentStep < steps.length - 1"
              variant="ghost"
              @click="skipOnboarding"
            >
              Skip Tour
            </Button>
            <Button
              v-if="currentStep < steps.length - 1"
              variant="solid"
              @click="nextStep"
              :loading="saving"
            >
              {{ currentStep === steps.length - 2 ? 'Complete Setup' : 'Next' }}
              <template #suffix>
                <FeatherIcon name="chevron-right" class="h-4 w-4" />
              </template>
            </Button>
            <Button
              v-else
              variant="solid"
              @click="completeOnboarding"
            >
              Get Started
              <template #suffix>
                <FeatherIcon name="arrow-right" class="h-4 w-4" />
              </template>
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Button, FormControl, Switch, Alert, call } from 'frappe-ui'
import { useRouter } from 'vue-router'

const props = defineProps({
  mode: {
    type: String,
    default: 'admin', // 'admin' or 'agent'
    validator: (value) => ['admin', 'agent'].includes(value),
  },
})

const router = useRouter()
const showOnboarding = ref(false)
const currentStep = ref(0)
const saving = ref(false)

// Settings state
const settings = ref({
  enable_email_blast: true,
  enable_sms_blast: false,
  enable_whatsapp_blast: false,
})

// Demo data for creating first campaign/segment
const demoData = ref({
  campaign_name: '',
  campaign_description: '',
  segment_name: '',
  segment_doctype: 'Lead',
})

// Steps configuration based on mode
const adminSteps = [
  {
    icon: 'home',
    title: 'Welcome to Marketing Hub',
    description: 'Your all-in-one platform for omni-channel marketing campaigns',
    color: '#3b82f6',
  },
  {
    icon: 'settings',
    title: 'Configure Your Channels',
    description: 'Choose which marketing channels you want to enable',
    color: '#8b5cf6',
  },
  {
    icon: 'target',
    title: 'Create a Campaign',
    description: 'Set up your first marketing campaign',
    color: '#10b981',
  },
  {
    icon: 'users',
    title: 'Define Your Audience',
    description: 'Create segments to target the right people',
    color: '#f59e0b',
  },
  {
    icon: 'check-circle',
    title: 'Ready to Launch',
    description: 'Everything is set up and ready to go!',
    color: '#22c55e',
  },
]

const agentSteps = [
  {
    icon: 'home',
    title: 'Welcome to Marketing Hub',
    description: 'Create and manage marketing campaigns for your organization',
    color: '#3b82f6',
  },
  {
    icon: 'target',
    title: 'Your First Campaign',
    description: 'Learn how to create effective marketing campaigns',
    color: '#10b981',
  },
  {
    icon: 'send',
    title: 'Send Campaigns',
    description: 'Reach your audience across multiple channels',
    color: '#8b5cf6',
  },
  {
    icon: 'bar-chart-2',
    title: 'Track Performance',
    description: 'Monitor your campaign metrics and optimize results',
    color: '#f59e0b',
  },
  {
    icon: 'check-circle',
    title: 'You\'re Ready!',
    description: 'Start creating impactful marketing campaigns',
    color: '#22c55e',
  },
]

const steps = computed(() => props.mode === 'admin' ? adminSteps : agentSteps)

const audienceTypes = [
  {
    value: 'Lead',
    label: 'Leads',
    description: 'Target potential customers',
  },
  {
    value: 'Contact',
    label: 'Contacts',
    description: 'Reach out to existing contacts',
  },
  {
    value: 'Customer',
    label: 'Customers',
    description: 'Engage with your customers',
  },
]

onMounted(async () => {
  // Check if user has completed onboarding
  const completed = await checkOnboardingStatus()
  if (!completed) {
    showOnboarding.value = true
  }
})

async function checkOnboardingStatus() {
  try {
    const data = await call('frappe.client.get_value', {
      doctype: 'User',
      filters: { name: window.frappe.session.user },
      fieldname: 'marketing_hub_onboarding_completed',
    })
    return data?.marketing_hub_onboarding_completed === 1
  } catch (error) {
    console.error('Error checking onboarding status:', error)
    return false
  }
}

function nextStep() {
  if (currentStep.value === 1 && props.mode === 'admin') {
    // Save settings before moving forward
    saveSettings()
  } else if (currentStep.value === 2) {
    // Optionally create demo campaign
    if (demoData.value.campaign_name) {
      createDemoCampaign()
    }
  } else if (currentStep.value === 3) {
    // Optionally create demo segment
    if (demoData.value.segment_name) {
      createDemoSegment()
    }
  }

  if (currentStep.value < steps.value.length - 1) {
    currentStep.value++
  }
}

function previousStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

async function saveSettings() {
  if (props.mode !== 'admin') return

  saving.value = true
  try {
    await call('frappe.client.set_value', {
      doctype: 'Marketing Hub Settings',
      name: 'Marketing Hub Settings',
      fieldname: settings.value,
    })
  } catch (error) {
    console.error('Error saving settings:', error)
  } finally {
    saving.value = false
  }
}

async function createDemoCampaign() {
  if (!demoData.value.campaign_name) return

  try {
    await call('frappe.client.insert', {
      doc: {
        doctype: 'Marketing Campaign',
        campaign_name: demoData.value.campaign_name,
        description: demoData.value.campaign_description,
        company: window.frappe.boot.sysdefaults?.company || '',
      },
    })
  } catch (error) {
    console.error('Error creating demo campaign:', error)
  }
}

async function createDemoSegment() {
  if (!demoData.value.segment_name) return

  try {
    await call('frappe.client.insert', {
      doc: {
        doctype: 'Marketing Segment',
        segment_name: demoData.value.segment_name,
        doctype_to_segment: demoData.value.segment_doctype,
      },
    })
  } catch (error) {
    console.error('Error creating demo segment:', error)
  }
}

async function completeOnboarding() {
  // Mark onboarding as completed
  try {
    await call('frappe.client.set_value', {
      doctype: 'User',
      name: window.frappe.session.user,
      fieldname: {
        marketing_hub_onboarding_completed: 1,
      },
    })
  } catch (error) {
    console.error('Error marking onboarding complete:', error)
  }

  showOnboarding.value = false
}

function skipOnboarding() {
  showOnboarding.value = false
  completeOnboarding()
}
</script>

<style scoped>
.stat-card {
  @apply rounded-lg border border-outline-gray-2 bg-surface-cards p-6 transition-all hover:border-blue-300 hover:shadow-md;
}
</style>
