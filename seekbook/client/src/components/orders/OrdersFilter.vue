<template>
  <section class="orders-filter">
    <div class="filter-groups">
      <div class="filter-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="filter-tab"
          :class="{ active: tab.key === activeKey }"
          type="button"
          @click="$emit('filter', tab.key)"
        >
          {{ tab.label }}
        </button>
      </div>
      <div v-if="secondaryTabs.length" class="secondary-tabs">
        <button
          v-for="tab in secondaryTabs"
          :key="tab.key"
          class="secondary-tab"
          :class="{ active: tab.key === secondaryActiveKey }"
          type="button"
          @click="$emit('secondary-filter', tab.key)"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>
    <form class="filter-search" @submit.prevent="$emit('search', localValue)">
      <input v-model.trim="localValue" class="search-input" type="text" :placeholder="placeholder" />
      <button class="btn btn-primary" type="submit"><i class="fas fa-search"></i> 搜索</button>
    </form>
  </section>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  tabs: { type: Array, default: () => [] },
  secondaryTabs: { type: Array, default: () => [] },
  activeKey: { type: String, default: 'all' },
  secondaryActiveKey: { type: String, default: 'all' },
  searchValue: { type: String, default: '' },
  placeholder: { type: String, default: '' },
})

defineEmits(['filter', 'secondary-filter', 'search'])

const localValue = ref(props.searchValue)

watch(
  () => props.searchValue,
  (value) => {
    localValue.value = value
  },
)
</script>

<style scoped>
.orders-filter {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.filter-groups {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.filter-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.secondary-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-tab {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  background: white;
  color: var(--gray-600);
  box-shadow: var(--shadow-sm);
}

.filter-tab.active {
  background: var(--primary-blue);
  color: white;
}

.secondary-tab {
  padding: 8px 16px;
  border: 1px solid var(--gray-300);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.8);
  color: var(--gray-600);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.secondary-tab.active {
  border-color: var(--primary-blue);
  background: var(--light-blue);
  color: var(--primary-blue);
}

.filter-search {
  display: flex;
  gap: 12px;
}

.search-input {
  width: 280px;
  padding: 10px 16px;
  border: 2px solid var(--gray-200);
  border-radius: 8px;
  font-size: 15px;
  transition: all 0.2s ease;
}

.btn-primary {
  padding: 10px 20px;
  background: var(--primary-blue);
  color: white;
  border: none;
  border-radius: 8px;
}

@media (max-width: 768px) {
  .orders-filter,
  .filter-search {
    flex-direction: column;
    align-items: stretch;
  }

  .search-input {
    width: 100%;
  }
}
</style>
