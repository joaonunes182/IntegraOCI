<script setup>
import { computed } from 'vue';
import { ociClasses } from './ociTheme';

const props = defineProps({
  type: {
    type: String,
    default: 'info',
    validator: (value) => ['info', 'warn', 'error', 'success'].includes(value),
  },
});

const alertClass = computed(() => {
  const map = {
    info: ociClasses.alertInfo,
    warn: ociClasses.alertWarn,
    error: ociClasses.alertError,
    success: ociClasses.alertSuccess,
  };
  return map[props.type] || map.info;
});
</script>

<template>
  <div :class="alertClass">
    <slot />
  </div>
</template>
