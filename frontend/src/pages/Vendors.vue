<template>
  <ListScreen
    title="Vendors" doctype="Supplier" :filters="{ disabled: 0 }"
    :columns="[
      { label: 'Vendor', field: 'supplier_name', width: 'minmax(0, 1.6fr)', strong: true },
      { label: 'Group', field: 'supplier_group', width: '160px' },
      { label: 'Email', field: 'email_id' },
    ]"
    note="Vendors are ERPNext Suppliers. Payment terms and bank details are edited in Desk."
    empty-title="No vendors" empty-text="Vendors are ERPNext Suppliers. Add one in Desk."
  />
</template>

<script setup>
import ListScreen from "@/components/ListScreen.vue"
</script>
