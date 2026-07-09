<template>
  <div class="tabs">
    <button
      v-for="tab in tabs"
      :key="tab.value"
      class="tab"
      :class="{ active: tab.value === active }"
      type="button"
      @click="$emit('change', tab.value)"
    >
      {{ tab.label }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  tabs: { type: Array, required: true },
  active: { type: String, required: true },
})

defineEmits(['change'])
</script>

<style scoped>
.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  background: var(--gray-50);
  padding: 4px;
  border-radius: 8px;
}

.tab {
  flex: 1;
  padding: 12px;
  border: none;
  background: transparent;
  color: var(--gray-600);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
}

.tab.active {
  background: white;
  color: var(--primary-blue);
  box-shadow: var(--shadow-sm);
}
</style>
