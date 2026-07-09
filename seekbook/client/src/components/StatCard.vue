<template>
  <div class="stat-item">
    <div class="number">{{ value }}</div>
    <div class="label">{{ title }}</div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  value: { type: String, required: true },
})
</script>

<style scoped>
.stat-item {
  background: white;
  padding: 24px;
  border-radius: 12px;
  text-align: center;
  box-shadow: var(--shadow-md);
}

.stat-item .number {
  font-size: 32px;
  font-weight: 700;
  color: var(--primary-blue);
  margin-bottom: 8px;
}

.stat-item .label {
  font-size: 14px;
  color: var(--gray-600);
}
</style>