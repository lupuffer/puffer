<template>
  <div class="category-grid">
    <button
      v-for="category in categoryItems"
      :key="category.title"
      class="category-card"
      type="button"
      @click="$emit('select', category)"
    >
      <i :class="category.icon"></i>
      <h3>{{ category.title }}</h3>
      <p>{{ category.count }}</p>
    </button>
  </div>
</template>

<script setup>
import { computed, inject } from 'vue'

const props = defineProps({
  categories: { type: Array, default: () => [] },
})

defineEmits(['select'])

const appData = inject('appData', { value: {} })

const categoryItems = computed(() => {
  return props.categories.length ? props.categories : appData.value?.home?.categories ?? []
})
</script>

<style scoped>
.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.category-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  text-align: center;
  box-shadow: var(--shadow-md);
  transition: all 0.2s ease;
  cursor: pointer;
  border: none;
}

.category-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.category-card i {
  font-size: 40px;
  color: var(--primary-blue);
  margin-bottom: 12px;
}

.category-card h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--gray-800);
  margin-bottom: 4px;
}

.category-card p {
  font-size: 13px;
  color: var(--gray-500);
}
</style>
