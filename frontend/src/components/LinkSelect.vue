<template>
  <Combobox :model-value="modelValue" :options="options" :label="label" :placeholder="placeholder" :disabled="disabled" @update:model-value="$emit('update:modelValue', $event)" />
</template>

<script setup>
// A pick-one field over the records of a doctype. Frappe applies User Permissions to
// the list, so a Brand Manager only sees their own brands and exercises here.
import { computed } from "vue"
import { Combobox, useList } from "frappe-ui"

const props = defineProps({
  modelValue: String,
  doctype: { type: String, required: true },
  labelField: { type: String, default: "name" },
  filters: { type: Object, default: () => ({}) },
  label: String,
  placeholder: String,
  disabled: Boolean,
})
defineEmits(["update:modelValue"])

const { data } = useList({
  doctype: props.doctype,
  fields: props.labelField === "name" ? ["name"] : ["name", props.labelField],
  filters: () => props.filters,
  limit: 200,
})
const options = computed(() => (data.value || []).map((r) => ({ label: r[props.labelField] || r.name, value: r.name })))
</script>
