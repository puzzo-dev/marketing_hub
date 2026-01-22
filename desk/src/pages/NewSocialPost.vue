<template>
  <div class="flex h-full flex-col overflow-auto bg-surface-gray-1">
    <div class="flex-1 px-5 py-5 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-2xl">
    <div class="mb-5">
      <h1 class="text-2xl font-semibold text-ink-gray-9">New Social Post</h1>
      <p class="mt-1 text-sm text-ink-gray-6">Create a new social media post</p>
    </div>

    <div class="rounded-lg border border-outline-gray-1 bg-surface-cards p-5 shadow-sm">
      <p class="text-center text-ink-gray-6">
        Social post creation form coming soon. For now, please use the Desk interface.
      </p>
      <div class="mt-6 flex justify-center space-x-4">
        <Button variant="ghost" @click="$router.push('/marketing/social')">
          Back to Social Posts
        </Button>
        <Button @click="window.location.href = '/app/social-post/new'">
          Create in Desk
        </Button>
      </div>
    </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Social post creation form will be implemented later
</script>
