<script setup>
import { ociClasses } from './ociTheme';

defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], default: 0 },
  badge: { type: String, default: '' },
  panelLabel: { type: String, default: '' },
  panelValue: { type: String, default: '' },
  helper: { type: String, default: '' },
  accentBarClass: { type: String, default: 'bg-slate-300 dark:bg-slate-600' },
});
</script>

<template>
  <article :class="[ociClasses.cardSurface, 'relative overflow-hidden p-0']">
    <div class="h-1 w-full" :class="accentBarClass" />
    <div class="p-4">
      <div class="flex items-start justify-between gap-3">
        <div>
          <p :class="ociClasses.labelSection">{{ label }}</p>
          <p class="mt-2 text-3xl font-bold leading-none text-[#13335a] dark:text-[#eceded]">
            {{ value }}
          </p>
        </div>
        <span v-if="badge" :class="ociClasses.badgeNeutral">{{ badge }}</span>
      </div>
      <div
        v-if="panelLabel || panelValue"
        class="mt-4 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 dark:border-gray-700 dark:bg-gray-900/40"
      >
        <p :class="ociClasses.labelSection">{{ panelLabel }}</p>
        <p class="mt-1 text-sm font-semibold text-slate-800 dark:text-gray-100">{{ panelValue }}</p>
      </div>
      <p v-if="helper" class="mt-3 text-xs leading-5 text-gray-600 dark:text-gray-300">
        {{ helper }}
      </p>
    </div>
  </article>
</template>
