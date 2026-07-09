<template>
  <div class="order-state-card">
    <div class="order-state-meta">
      <span class="order-state-title">{{ title }}</span>
      <span class="order-state-value">{{ stateText }}</span>
    </div>
    <div class="order-state-actions">
      <button 
        v-for="action in actions" 
        :key="action" 
        class="state-action" 
        type="button"
        @click="handleActionClick(action)"
      >
        {{ action }}
      </button>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  title: { type: String, required: true },
  stateText: { type: String, required: true },
  actions: { type: Array, default: () => [] },
})

const emit = defineEmits(['action-click'])

const handleActionClick = (action) => {
  emit('action-click', action)
}
</script>

<style scoped>
.order-state-card {
  position: sticky;
  top: 0;
  z-index: 6;
  margin: 12px 24px 0;
  padding: 12px 14px;
  border-radius: 10px;
  border: 1px solid var(--gray-200);
  background: white;
  box-shadow: var(--shadow-sm);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.order-state-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.order-state-title {
  font-size: 12px;
  color: var(--gray-500);
}

.order-state-value {
  font-size: 15px;
  font-weight: 600;
  color: var(--gray-900);
}

.order-state-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.state-action {
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid var(--gray-200);
  background: white;
  color: var(--gray-700);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.state-action:first-child {
  background: var(--primary-blue);
  border-color: var(--primary-blue);
  color: white;
}
</style>
