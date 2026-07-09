<template>
  <section>
    <div class="filter-section">
      <div class="filter-header" @click="collapsed = !collapsed">
        <h4><i class="fas fa-filter"></i> {{ buy.filtersTitle }}</h4>
        <button class="filter-toggle-btn" type="button">
          <i :class="collapsed ? 'fas fa-chevron-up' : 'fas fa-chevron-down'" class="filter-toggle"></i>
        </button>
      </div>
      <div class="filter-options filter-grid" :class="{ collapsed }">
        <div v-for="filter in buy.filters" :key="filter.key" class="filter-category">
          <h5>{{ filter.title }}</h5>
          <div class="filter-tags">
            <button
              v-for="option in filter.options"
              :key="option"
              class="filter-tag"
              :class="{ active: selectedFilters[filter.key] === option }"
              type="button"
              @click="selectFilter(filter.key, option)"
            >
              {{ option }}
            </button>
          </div>
        </div>
        <div class="filter-category">
          <h5>{{ buy.priceFilter.title }}</h5>
          <div class="price-filter">
            <input v-model.number="minPrice" class="price-input" type="number" :placeholder="buy.priceFilter.minPlaceholder" />
            <span>-</span>
            <input v-model.number="maxPrice" class="price-input" type="number" :placeholder="buy.priceFilter.maxPlaceholder" />
            <button class="price-btn price-btn-confirm" type="button" @click="applyPriceFilter">{{ buy.priceFilter.confirmText }}</button>
            <button class="price-btn price-btn-reset" type="button" @click="resetPriceFilter">{{ buy.priceFilter.resetText }}</button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  buy: { type: Object, required: true },
})

const emit = defineEmits(['search', 'filter'])
const keyword = ref('')
const collapsed = ref(false)
const selectedFilters = ref({})
const minPrice = ref('')
const maxPrice = ref('')

// 初始化筛选状态
watch(() => props.buy.filters, (filters) => {
  if (filters) {
    filters.forEach(filter => {
      if (!selectedFilters.value[filter.key]) {
        selectedFilters.value[filter.key] = filter.options[0] || ''
      }
    })
  }
}, { immediate: true })

const handleSearchSubmit = () => {
  const value = keyword.value.trim()
  if (value) {
    emit('search', value)
  }
}

const selectFilter = (filterKey, option) => {
  selectedFilters.value[filterKey] = option
  emit('filter', { type: 'category', key: filterKey, value: option })
}

const applyPriceFilter = () => {
  emit('filter', {
    type: 'price',
    min: minPrice.value ? Number(minPrice.value) : null,
    max: maxPrice.value ? Number(maxPrice.value) : null
  })
}

const resetPriceFilter = () => {
  minPrice.value = ''
  maxPrice.value = ''
  emit('filter', { type: 'price', min: null, max: null })
}
</script>

<style scoped>
.filter-section {
  background-color: white;
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 20px;
  box-shadow: var(--shadow-md);
}

.filter-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  user-select: none;
}

.filter-header h4 {
  font-size: 16px;
  font-weight: 600;
  color: var(--gray-800);
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
}

.filter-toggle-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: var(--gray-500);
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.filter-toggle-btn:hover {
  background: var(--gray-100);
}

.filter-toggle {
  font-size: 14px;
  transition: transform 0.2s ease;
}

.filter-options {
  margin-top: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.filter-options.collapsed {
  display: none;
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.filter-category {
  margin-bottom: 16px;
}

.filter-category h5 {
  font-size: 13px;
  font-weight: 600;
  color: var(--gray-700);
  margin-bottom: 10px;
}

.filter-tags,
.price-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-tag {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid var(--gray-200);
  background-color: white;
  color: var(--gray-600);
}

.filter-tag:hover,
.filter-tag.active {
  border-color: var(--primary-blue);
  color: var(--primary-blue);
}

.filter-tag.active {
  background-color: var(--primary-blue);
  color: white;
}

.price-filter {
  align-items: center;
}

.price-input {
  width: 100px;
  padding: 8px 12px;
  border: 2px solid var(--gray-200);
  border-radius: 8px;
  font-size: 14px;
  text-align: center;
  transition: all 0.2s ease;
}

.price-input:focus,
.search-input:focus {
  outline: none;
  border-color: var(--primary-blue);
}

.price-btn {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  font-weight: 500;
}

.price-btn-confirm {
  background-color: var(--primary-blue);
  color: white;
}

.price-btn-reset {
  background-color: var(--gray-100);
  color: var(--gray-600);
}

.search-box {
  max-width: 100%;
  margin: 0 auto 20px;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: var(--shadow-md);
  display: flex;
  gap: 12px;
}

.search-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid var(--gray-200);
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.search-btn {
  padding: 12px 24px;
  background-color: var(--primary-blue);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-btn:hover {
  background-color: #1e40af;
}

@media (max-width: 768px) {
  .filter-grid {
    grid-template-columns: 1fr;
  }
  
  .search-box {
    padding: 16px;
  }
  
  .search-btn span {
    display: none;
  }
}
</style>
