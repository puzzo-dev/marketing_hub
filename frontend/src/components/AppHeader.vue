<template>
  <PageHeaderMobile v-if="isMobile">
    <template v-if="back" #prefix><PageHeaderBackButton :fallback-route="back" /></template>
    <PageHeaderMobileTitle :title="title" />
    <template v-if="$slots.actions" #suffix><slot name="actions" /></template>
  </PageHeaderMobile>
  <PageHeader v-else>
    <slot name="title"><PageHeaderTitle :title="title" /></slot>
    <div v-if="$slots.actions" class="flex items-center gap-2"><slot name="actions" /></div>
  </PageHeader>
</template>

<script setup>
// The header of every page. A phone gets the mobile header with a back button when the page
// is a detail (`back` is the route to fall back to); a desktop gets the standard header, and
// a page may replace the title with breadcrumbs through the #title slot.
import { PageHeader, PageHeaderBackButton, PageHeaderMobile, PageHeaderMobileTitle, PageHeaderTitle } from "frappe-ui"
import { isMobile } from "@/lib/viewport"

defineProps({ title: { type: String, default: "" }, back: Object })
</script>
