<template>
  <router-view />
</template>

<script setup lang="ts">
import { useAppMotion } from '@/composables/useAppMotion';

useAppMotion();
</script>
