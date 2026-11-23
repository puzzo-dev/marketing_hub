<template>
  <AppHeader title="Home">
    <template #actions><Button v-if="primary" variant="solid" :label="primary.label" :icon-left="primary.icon" :route="{ name: primary.route }" /></template>
  </AppHeader>
  <ErrorState v-if="call.error.value" icon="lucide-triangle-alert" title="Something went wrong on our side" text="Nothing was lost. Try again." action-label="Try again" @action="call.reload?.()" />
  <div v-else class="flex flex-col gap-8 px-3 pb-10 pt-5 sm:px-5">
    <div v-if="data?.alert" class="flex items-center justify-between gap-3 rounded-6 bg-surface-amber-2 px-4 py-3">
      <span class="flex items-center gap-2 text-base text-ink-amber-7"><span class="lucide-circle-alert size-4" aria-hidden="true" />{{ data.alert.text }}</span>
      <Button variant="outline" label="Open" :route="{ name: data.alert.route }" />
    </div>

    <div class="grid grid-cols-2 gap-y-4 divide-outline-gray-2 sm:grid-cols-4 sm:divide-x">
      <div v-for="f in figures" :key="f.label" class="flex flex-col gap-1 px-4 first:pl-0 last:pr-0">
        <div class="text-sm text-ink-gray-6">{{ f.label }}</div>
        <Skeleton v-if="!data" class="h-8 w-16" />
        <div v-else class="text-2xl font-semibold text-ink-gray-9">{{ f.value }}</div>
      </div>
    </div>

    <section v-for="l in data?.lists || []" :key="l.title" class="flex flex-col gap-2">
      <div class="flex h-7 items-center"><h3 class="text-sm font-semibold text-ink-gray-8">{{ l.title }}</h3></div>
      <List v-if="l.rows.length" class="list-row-px-0" :columns="['minmax(0,1fr)', '8rem']" :row-height="52">
        <ListRows :items="l.rows" row-key="param" v-slot="{ item, value }">
          <ListRow :value="value" :route="{ name: item.route, params: { name: item.param } }">
            <ListCell>
              <span class="flex min-w-0 flex-col gap-1"><span class="truncate text-base text-ink-gray-8">{{ item.title }}</span><span class="truncate text-sm text-ink-gray-6">{{ item.sub }}</span></span>
            </ListCell>
            <ListCell class="justify-end"><Badge v-if="item.status" :label="item.status" :theme="badgeTheme(item.status)" /></ListCell>
          </ListRow>
        </ListRows>
      </List>
      <p v-else class="text-base text-ink-gray-6">Nothing needs you right now.</p>
    </section>
  </div>
</template>

<script setup>
// Home for the roles that do not get the analytics dashboard: Marketing Head, Content Lead,
// Media Planner, Publisher and OOH Coordinator. The server decides what each role sees.
import { computed } from "vue"
import { Badge, Button, Skeleton, useCall } from "frappe-ui"
import { List, ListCell, ListRow, ListRows } from "frappe-ui/list"
import AppHeader from "@/components/AppHeader.vue"
import ErrorState from "./ErrorState.vue"
import { primaryRole, ROLES } from "@/lib/session"
import { badgeTheme } from "@/lib/status"

const call = useCall({ url: "/api/method/marketing_hub.api.role_home.get", params: { role: primaryRole.value } })
const data = computed(() => call.data.value?.message ?? call.data.value)
const figures = computed(() => data.value?.figures || [1, 2, 3].map((n) => ({ label: "…", value: n })))
const primary = computed(() => (primaryRole.value === ROLES.ooh ? { label: "New booking", icon: "lucide-plus", route: "NewOOHBooking" } : null))
</script>
