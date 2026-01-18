<template>
  <div class="mx-auto max-w-2xl">
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900">New Campaign</h1>
      <p class="mt-1 text-sm text-gray-500">Create a new marketing campaign</p>
    </div>

    <div class="rounded-lg border bg-white p-6 shadow-sm">
      <p class="text-center text-gray-600">
        Campaign creation form coming soon. For now, please use the Desk interface.
      </p>
      <div class="mt-6 flex justify-center space-x-4">
        <Button variant="ghost" @click="$router.push('/marketing/campaigns')">
          Back to Campaigns
        </Button>
        <Button @click="window.location.href = '/app/campaign/new'">
          Create in Desk
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
// Campaign creation form will be implemented later
</script>
