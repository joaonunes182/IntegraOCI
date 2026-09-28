<script setup>
import { ociClasses } from './ociTheme';

defineProps({
  label: {
    type: String,
    default: '',
  },
});
</script>

<template>
  <span :class="ociClasses.badgeNeutral">
    <slot>{{ label }}</slot>
  </span>
</template>
