import { toast as frappeToast } from 'frappe-ui'

/**
 * Wrapper around frappe-ui toast.create() that maps the legacy API
 * used throughout the codebase to the actual frappe-ui toast API.
 *
 * Legacy: toast({ title, text, icon, iconClasses })
 * Actual: toast.create({ message, type })
 */
export function toast(options) {
  if (!options) return

  // Determine type from icon/iconClasses
  let type = 'info'
  if (options.icon === 'check' || options.iconClasses?.includes('green')) {
    type = 'success'
  } else if (options.icon === 'x' || options.iconClasses?.includes('red')) {
    type = 'error'
  } else if (options.icon === 'alert-circle' || options.iconClasses?.includes('amber') || options.iconClasses?.includes('orange')) {
    type = 'warning'
  }

  // Build message from title + text
  const message = [options.title, options.text].filter(Boolean).join(': ')

  return frappeToast.create({
    message: message || 'Notification',
    type,
  })
}
