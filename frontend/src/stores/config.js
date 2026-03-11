import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { createResource } from 'frappe-ui'

export const useConfigStore = defineStore('config', () => {
    const isReady = ref(false)

    const settings = ref({
        company: '',
        default_lead_source: '',
        enable_auto_attribution: false,
        enable_utm_tracking: false,
        enable_email_blast: true,
        enable_sms_blast: false,
        enable_whatsapp_blast: false,
        enable_auto_post: true,
        require_post_approval: false,
        enable_analytics_sync: false,
        sync_frequency: '',
        google_ads_developer_token: '',
        enable_content_library: true,
        enable_version_control: false,
        enable_brand_guidelines: false,
        agency_mode: false,
    })

    const settingsFields = [
        'company', 'default_lead_source',
        'enable_auto_attribution', 'enable_utm_tracking',
        'enable_email_blast', 'enable_sms_blast', 'enable_whatsapp_blast',
        'enable_auto_post', 'require_post_approval',
        'enable_analytics_sync', 'sync_frequency', 'google_ads_developer_token',
        'enable_content_library', 'enable_version_control', 'enable_brand_guidelines',
        'agency_mode',
    ]

    const settingsResource = createResource({
        url: 'frappe.client.get_value',
        params: {
            doctype: 'Marketing Hub Settings',
            fieldname: settingsFields
        },
        auto: true,
        onSuccess(data) {
            if (data) {
                settings.value = {
                    ...settings.value,
                    company: data.company || '',
                    default_lead_source: data.default_lead_source || '',
                    enable_auto_attribution: !!data.enable_auto_attribution,
                    enable_utm_tracking: !!data.enable_utm_tracking,
                    enable_email_blast: !!data.enable_email_blast,
                    enable_sms_blast: !!data.enable_sms_blast,
                    enable_whatsapp_blast: !!data.enable_whatsapp_blast,
                    enable_auto_post: !!data.enable_auto_post,
                    require_post_approval: !!data.require_post_approval,
                    enable_analytics_sync: !!data.enable_analytics_sync,
                    sync_frequency: data.sync_frequency || '',
                    google_ads_developer_token: data.google_ads_developer_token || '',
                    enable_content_library: !!data.enable_content_library,
                    enable_version_control: !!data.enable_version_control,
                    enable_brand_guidelines: !!data.enable_brand_guidelines,
                    agency_mode: !!data.agency_mode,
                }
            }
            isReady.value = true
        },
        onError() {
            isReady.value = true
        }
    })

    const isAgencyMode = computed(() => settings.value.agency_mode)

    return {
        settings,
        isReady,
        isAgencyMode,
        fetch: settingsResource.fetch
    }
})
