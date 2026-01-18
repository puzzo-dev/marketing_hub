<template>
  <div class="mx-auto max-w-2xl">
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900">New Social Post</h1>
      <p class="mt-1 text-sm text-gray-500">Create a new social media post</p>
    </div>

    <div class="rounded-lg border bg-white p-6 shadow-sm">
      <p class="text-center text-gray-600">
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
</template>

<script setup>
// Social post creation form will be implemented later
</script>
