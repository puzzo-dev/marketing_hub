<template>
  <ListScreen
    title="Purchase orders" doctype="Purchase Order" row-route="PurchaseOrder" :filters="{ mkt_booking: ['is', 'set'] }"
    :columns="[
      { label: 'Order', field: 'name', width: '130px', strong: true },
      { label: 'Vendor', field: 'supplier_name' },
      { label: 'Booking', field: 'mkt_booking', sub: true },
      { label: 'Amount', field: 'grand_total', width: '130px', currency: 'NGN' },
      { label: 'Status', field: 'status', width: '140px', badge: true },
    ]"
    note="A purchase order is created once, when the booking is approved. Receiving and billing happen in ERPNext."
    empty-title="No purchase orders" empty-text="One is created when an out-of-home booking is approved."
  />
</template>

<script setup>
import ListScreen from "@/components/ListScreen.vue"
</script>
