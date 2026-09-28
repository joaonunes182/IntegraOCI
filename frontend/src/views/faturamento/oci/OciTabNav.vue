<script setup>
defineProps({
  modelValue: {
    type: String,
    required: true,
  },
  tabs: {
    type: Array,
    required: true,
  },
});

defineEmits(['update:modelValue']);
</script>

<template>
  <div class="border-b border-gray-200 dark:border-gray-700">
    <nav class="-mb-px flex flex-wrap gap-x-6 gap-y-2" aria-label="Abas de detalhe">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        type="button"
        @click="$emit('update:modelValue', tab.key)"
        :class="[
          modelValue === tab.key
            ? 'border-[#13335a] text-[#13335a] dark:border-[#42b9eb] dark:text-[#eceded]'
            : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-400 dark:hover:border-gray-600 dark:hover:text-gray-300',
          'inline-flex items-center gap-2 whitespace-nowrap border-b-2 py-3 px-1 text-sm font-medium transition-colors',
        ]"
      >
        {{ tab.label }}
        <span
          class="rounded-full px-2 py-0.5 text-xs font-semibold"
          :class="
            modelValue === tab.key
              ? 'bg-[#13335a]/10 text-[#13335a] dark:bg-[#42b9eb]/15 dark:text-[#eceded]'
              : 'bg-slate-100 text-slate-600 dark:bg-gray-700 dark:text-gray-300'
          "
        >
          {{ tab.count ?? 0 }}
        </span>
      </button>
    </nav>
  </div>
</template>
