import { defineStore } from 'pinia'
import { ref } from 'vue'
import { createResource } from 'frappe-ui'

export const useConfigStore = defineStore('config', () => {
    const settings = ref({
        enable_email_blast: true,
        enable_sms_blast: false,
        enable_whatsapp_blast: false,
        enable_auto_post: true,
        require_post_approval: false,
        enable_content_library: true,
        agency_mode: false,
    })

    const settingsFields = [
        'enable_email_blast', 'enable_sms_blast', 'enable_whatsapp_blast',
        'enable_auto_post', 'require_post_approval', 'enable_content_library',
        'agency_mode', 'company',
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
                    enable_email_blast: !!data.enable_email_blast,
                    enable_sms_blast: !!data.enable_sms_blast,
                    enable_whatsapp_blast: !!data.enable_whatsapp_blast,
                    enable_auto_post: !!data.enable_auto_post,
                    require_post_approval: !!data.require_post_approval,
                    enable_content_library: !!data.enable_content_library,
                    agency_mode: !!data.agency_mode,
                    company: data.company || '',
                }
            }
        }
    })

    return {
        settings,
        fetch: settingsResource.fetch
    }
})
