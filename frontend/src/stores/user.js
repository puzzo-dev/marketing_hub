import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { createResource } from 'frappe-ui'

export const useUserStore = defineStore('user', () => {
    const user = ref(null)

    const userResource = createResource({
        url: 'frappe.auth.get_logged_user',
        auto: true,
        onSuccess(data) {
            user.value = data
            // Fetch full details including roles
            fetchUserDetails()
        },
    })

    // Separate resource for details to get roles which might not be in get_logged_user depending on version
    const userDetailsResource = createResource({
        url: 'frappe.client.get',
        makeParams(values) {
            return {
                doctype: 'User',
                name: user.value?.n || window.frappe?.session?.user
            }
        },
    })

    function fetchUserDetails() {
        if (user.value) {
            userDetailsResource.fetch()
        }
    }

    const roles = computed(() => window.frappe?.boot?.user?.roles || [])

    const isAdmin = computed(() =>
        roles.value.includes('System Manager') || roles.value.includes('Marketing Manager')
    )

    const role = computed(() => isAdmin.value ? 'Admin' : 'Agent')

    const isLoggedIn = computed(() => !!user.value)
    const name = computed(() => window.frappe?.session?.user_fullname || 'User')
    const email = computed(() => user.value?.n)
    const image = computed(() => window.frappe?.session?.user_image)

    return {
        user,
        role,
        roles,
        isAdmin,
        isLoggedIn,
        name,
        email,
        image,
        fetch: userResource.fetch,
    }
})
