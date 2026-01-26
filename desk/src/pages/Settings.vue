<template>
  <div class="flex h-full flex-col overflow-auto bg-surface-gray-1">
    <div class="flex-1 px-5 py-5 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-4xl">
        <div class="mb-6">
          <h1 class="text-2xl font-semibold text-ink-gray-9">Settings</h1>
          <p class="mt-1 text-sm text-ink-gray-6">Configure Marketing Hub preferences and integrations</p>
        </div>

        <div class="grid gap-6">
          <!-- Channels -->
          <div class="rounded-lg border border-outline-gray-2 bg-surface-cards p-6">
            <h2 class="mb-4 text-lg font-semibold text-ink-gray-9">Marketing Channels</h2>
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <div>
                  <div class="font-medium text-ink-gray-9">Email Blasts</div>
                  <div class="text-sm text-ink-gray-6">Enable sending mass email campaigns</div>
                </div>
                <Switch v-model="settings.enable_email_blast" />
              </div>
              <div class="flex items-center justify-between">
                <div>
                  <div class="font-medium text-ink-gray-9">SMS Blasts</div>
                  <div class="text-sm text-ink-gray-6">Enable sending SMS campaigns</div>
                </div>
                <Switch v-model="settings.enable_sms_blast" />
              </div>
              <div class="flex items-center justify-between">
                <div>
                  <div class="font-medium text-ink-gray-9">WhatsApp Blasts</div>
                  <div class="text-sm text-ink-gray-6">Enable WhatsApp Business API campaigns</div>
                </div>
                <Switch v-model="settings.enable_whatsapp_blast" />
              </div>
            </div>
          </div>

          <!-- API Keys (Google) -->
          <div class="rounded-lg border border-outline-gray-2 bg-surface-cards p-6">
            <h2 class="mb-4 text-lg font-semibold text-ink-gray-9">Google Ads Integration</h2>
            <div class="space-y-4">
              <FormControl
                v-model="settings.google_ads_developer_token"
                label="Developer Token"
                type="password"
                placeholder="Enter your Google Ads Developer Token"
              />
              <div class="rounded-md bg-blue-50 p-3 text-sm text-blue-700">
                You also need to configure OAuth credentials in the Ad Account doctype for each account.
              </div>
            </div>
          </div>

          <!-- General -->
          <div class="rounded-lg border border-outline-gray-2 bg-surface-cards p-6">
            <h2 class="mb-4 text-lg font-semibold text-ink-gray-9">General Preferences</h2>
            <div class="space-y-4">
              <FormControl
                v-model="settings.attribution_window"
                label="Attribution Window (Days)"
                type="number"
                placeholder="30"
              />
            </div>
          </div>

          <!-- Actions -->
          <div class="flex justify-end gap-3">
            <Button variant="solid" :loading="saving" @click="saveSettings">
              Save Changes
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Button, FormControl, Switch, toast } from 'frappe-ui'

const saving = ref(false)
const settings = ref({
  enable_email_blast: false,
  enable_sms_blast: false,
  enable_whatsapp_blast: false,
  google_ads_developer_token: '',
  attribution_window: 30
})

onMounted(async () => {
  try {
    const doc = await window.frappe.call({
      method: "frappe.client.get_value",
      args: {
        doctype: "Marketing Hub Settings",
        fieldname: ["enable_email_blast", "enable_sms_blast", "enable_whatsapp_blast", "google_ads_developer_token", "attribution_window"]
      }
    })
    
    if (doc.message) {
      settings.value = { ...settings.value, ...doc.message }
      // Convert 1/0 to true/false for switches
      settings.value.enable_email_blast = !!settings.value.enable_email_blast
      settings.value.enable_sms_blast = !!settings.value.enable_sms_blast
      settings.value.enable_whatsapp_blast = !!settings.value.enable_whatsapp_blast
    }
  } catch (error) {
    console.error("Error loading settings:", error)
  }
})

async function saveSettings() {
  saving.value = true
  try {
    await window.frappe.call({
      method: "frappe.client.set_value",
      args: {
        doctype: "Marketing Hub Settings",
        name: "Marketing Hub Settings",
        fieldname: {
          ...settings.value,
          enable_email_blast: settings.value.enable_email_blast ? 1 : 0,
          enable_sms_blast: settings.value.enable_sms_blast ? 1 : 0,
          enable_whatsapp_blast: settings.value.enable_whatsapp_blast ? 1 : 0
        }
      }
    })
    toast({ title: "Success", text: "Settings saved successfully", icon: "check", iconClasses: "text-green-600" })
  } catch (error) {
    toast({ title: "Error", text: "Failed to save settings", icon: "x", iconClasses: "text-red-600" })
  } finally {
    saving.value = false
  }
}
</script>
