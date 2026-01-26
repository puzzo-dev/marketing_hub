import { defineStore } from 'pinia'
import { ref } from 'vue'
import { createResource } from 'frappe-ui'

export const useConfigStore = defineStore('config', () => {
    const settings = ref({
        enable_email_blast: true,
        enable_sms_blast: false,
        enable_whatsapp_blast: false,
    })

    const settingsResource = createResource({
        url: 'frappe.client.get_value',
        params: {
            doctype: 'Marketing Hub Settings',
            fieldname: ['enable_email_blast', 'enable_sms_blast', 'enable_whatsapp_blast']
        },
        auto: true,
        onSuccess(data) {
            if (data) {
                settings.value = {
                    enable_email_blast: !!data.enable_email_blast,
                    enable_sms_blast: !!data.enable_sms_blast,
                    enable_whatsapp_blast: !!data.enable_whatsapp_blast,
                }
            }
        }
    })

    return {
        settings,
        fetch: settingsResource.fetch
    }
})
