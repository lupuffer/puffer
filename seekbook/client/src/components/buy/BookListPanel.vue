<template>
  <section class="books-section">
    <div class="books-section-header">
      <div class="header-copy">
        <h2><i :class="buy.booksSection.icon"></i> {{ buy.booksSection.title }}</h2>
        <div class="catalog-summary">
          <span class="catalog-badge">{{ catalogStatus }}</span>
          <span>共 {{ formattedTotalItems }} 本</span>
          <span v-if="books.length && !loading">当前显示 {{ visibleRangeText }}</span>
        </div>
      </div>
      <div class="sort-wrapper">
        <span class="sort-label">{{ buy.booksSection.sortLabel }}</span>
        <div class="sort-options">
          <button
            v-for="option in buy.booksSection.sortOptions"
            :key="option"
            class="sort-option"
            :class="{ active: option === activeSort }"
            type="button"
            @click="$emit('sort', option)"
          >
            {{ option }}
          </button>
        </div>
      </div>
    </div>
    <div class="virtual-list-container">
      <div class="virtual-list-content" :class="{ 'is-loading': loading }">
        <!-- Loading State -->
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>{{ buy.booksSection.loadingText || '正在加载书籍...' }}</p>
        </div>
        
        <!-- Empty State -->
        <div v-else-if="!books.length" class="empty-state">
          <div class="empty-illustration">
            <i class="fas fa-book-open"></i>
          </div>
          <h3>{{ buy.booksSection.emptyTitle || '暂无二手书' }}</h3>
          <p>{{ buy.booksSection.emptyDescription || '还没有书籍上架，快来发布第一本吧！' }}</p>
          <button v-if="buy.booksSection.emptyAction" class="btn-primary" @click="$emit('empty-action')">
            {{ buy.booksSection.emptyAction }}
          </button>
        </div>
        
        <!-- Book Grid -->
        <template v-else>
          <BookCard 
            v-for="(book, index) in books" 
            :key="book.id" 
            :book="book" 
            :index="startIndex + index" 
            @select="$emit('select', $event)"
            @chat="$emit('chat', $event)"
          />
        </template>
      </div>
    </div>
    <div class="pagination-wrap">
      <div class="pagination-left">
        <button class="page-btn" :class="{ disabled: currentPage <= 1 }" type="button" @click="$emit('page', currentPage - 1)">{{ buy.pagination.prev }}</button>
        <button v-for="page in pageNumbers" :key="page" class="page-btn" :class="{ active: page === currentPage }" type="button" @click="$emit('page', page)">{{ page }}</button>
        <button class="page-btn" :class="{ disabled: currentPage >= totalPages }" type="button" @click="$emit('page', currentPage + 1)">{{ buy.pagination.next }}</button>
      </div>
      <div class="pagination-right">
        <span class="page-label">{{ buy.pagination.pageSizeLabel }}</span>
        <button v-for="size in buy.pagination.pageSizes" :key="size" class="page-btn" :class="{ active: size === pageSize }" type="button" @click="$emit('page-size', size)">{{ size }}</button>
        <span class="page-label">{{ buy.pagination.gotoPrefix }}</span>
        <input v-model.number="gotoPage" class="page-input" type="number" min="1" :placeholder="buy.pagination.gotoPlaceholder" />
        <span class="page-label">{{ buy.pagination.gotoSuffix }}</span>
        <button class="page-btn" type="button" @click="$emit('page', gotoPage)">{{ buy.pagination.gotoButton }}</button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import BookCard from '../BookCard.vue'

const props = defineProps({
  buy: { type: Object, required: true },
  books: { type: Array, required: true },
  loading: { type: Boolean, default: false },
  activeSort: { type: String, default: '' },
  currentPage: { type: Number, default: 1 },
  totalPages: { type: Number, default: 1 },
  pageSize: { type: Number, default: 20 },
  pageNumbers: { type: Array, default: () => [] },
  startIndex: { type: Number, default: 0 },
  totalItems: { type: Number, default: 0 },
  catalogStatus: { type: String, default: '' },
})

defineEmits(['select', 'sort', 'page', 'page-size'])

const gotoPage = ref(1)
const formattedTotalItems = computed(() => Number(props.totalItems || 0).toLocaleString('zh-CN'))
const visibleRangeText = computed(() => {
  const start = props.books.length ? props.startIndex + 1 : 0
  const end = Math.min(props.startIndex + props.books.length, props.totalItems)
  return `${start}-${end} 本`
})
</script>

<style scoped>
.books-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.header-copy {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.books-section-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--gray-900);
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
}

.catalog-summary,
.sort-wrapper,
.sort-options,
.pagination-left,
.pagination-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.catalog-summary {
  color: var(--gray-600);
  font-size: 13px;
}

.catalog-badge {
  padding: 5px 10px;
  border-radius: 999px;
  background: rgba(79, 110, 247, 0.12);
  color: var(--primary-blue);
  font-weight: 600;
}

.sort-wrapper {
  gap: 12px;
}

.sort-label,
.page-label {
  font-size: 14px;
  color: var(--gray-600);
  font-weight: 500;
}

.page-label {
  font-size: 13px;
  font-weight: 400;
}

.sort-option,
.page-btn {
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--gray-600);
  border: none;
  background: transparent;
  font-weight: 500;
}

.sort-option:hover,
.sort-option.active {
  color: var(--primary-blue);
  background-color: var(--light-blue);
}

.virtual-list-container {
  position: relative;
  overflow: hidden;
  min-height: 600px;
  border-radius: 12px;
  background-color: white;
  box-shadow: var(--shadow-md);
}

.virtual-list-content {
  position: relative;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  padding: 16px;
}

@media (max-width: 1400px) {
  .virtual-list-content {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (max-width: 1200px) {
  .virtual-list-content {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .virtual-list-content {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
    padding: 12px;
  }
}

@media (max-width: 600px) {
  .virtual-list-content {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
    padding: 8px;
  }
}

.pagination-wrap {
  margin-top: 14px;
  background: white;
  border-radius: 12px;
  box-shadow: var(--shadow-md);
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.page-btn {
  min-width: 34px;
  height: 34px;
  padding: 0 10px;
  border: 1px solid var(--gray-200);
  background: white;
  color: var(--gray-700);
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-btn:hover,
.page-btn.active {
  background: var(--primary-blue);
  border-color: var(--primary-blue);
  color: white;
}

.page-btn.disabled {
  opacity: 0.45;
  cursor: not-allowed;
  pointer-events: none;
}

.page-input {
  width: 72px;
  height: 34px;
  border-radius: 8px;
  border: 2px solid var(--gray-200);
  padding: 0 10px;
  font-size: 13px;
  color: var(--gray-700);
}

.page-input:focus {
  outline: none;
  border-color: var(--primary-blue);
}

.loading-container,
.empty-state {
  grid-column: 1 / -1;
  min-height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.loading-container {
  gap: 16px;
  color: var(--gray-500);
}

.empty-state {
  gap: 16px;
  padding: 40px;
  color: var(--gray-600);
}

.empty-illustration {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--light-blue) 0%, #e0e7ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
}

.empty-illustration i {
  font-size: 48px;
  color: var(--primary-blue);
  opacity: 0.8;
}

.empty-state h3 {
  font-size: 20px;
  font-weight: 600;
  color: var(--gray-900);
  margin: 0;
}

.empty-state p {
  font-size: 14px;
  color: var(--gray-500);
  margin: 0;
  max-width: 300px;
  line-height: 1.6;
}

.btn-primary {
  margin-top: 8px;
  padding: 12px 24px;
  background: var(--primary-blue);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: #3b5ce6;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(79, 110, 247, 0.3);
}

.virtual-list-content.is-loading {
  min-height: 400px;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--gray-200);
  border-top-color: var(--primary-blue);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 1200px) {
  .virtual-list-content {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .books-section-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .empty-state {
    padding: 24px;
  }
  
  .empty-illustration {
    width: 80px;
    height: 80px;
  }
  
  .empty-illustration i {
    font-size: 36px;
  }
  
  .empty-state h3 {
    font-size: 18px;
  }
}
</style>
