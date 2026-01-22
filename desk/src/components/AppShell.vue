<template>
	<div class="flex h-screen w-screen overflow-hidden">
		<Sidebar v-if="!hideSidebar" />
		<div class="flex flex-1 flex-col overflow-hidden">
			<RouterView v-slot="{ Component }">
				<Suspense>
					<component :is="Component" />
				</Suspense>
			</RouterView>
		</div>
	</div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from './Sidebar.vue'

const route = useRoute()
const hideSidebar = computed(() => route.meta?.hideSidebar || false)
</script>
