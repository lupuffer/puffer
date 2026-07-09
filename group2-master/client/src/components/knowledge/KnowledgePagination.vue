<template>
  <nav v-if="totalPages > 1" class="pagination-shell" aria-label="分页导航">
    <button type="button" class="page-btn" :disabled="currentPage <= 1" @click="$emit('change', currentPage - 1)">
      上一页
    </button>
    <span class="page-indicator">第 {{ currentPage }} / {{ totalPages }} 页</span>
    <button type="button" class="page-btn" :disabled="currentPage >= totalPages" @click="$emit('change', currentPage + 1)">
      下一页
    </button>
  </nav>
</template>

<script setup>
defineProps({
  currentPage: {
    type: Number,
    default: 1,
  },
  totalPages: {
    type: Number,
    default: 1,
  },
})

defineEmits(['change'])
</script>

<style scoped>
.pagination-shell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  padding-top: 6px;
}

.page-btn {
  min-height: 38px;
  padding: 0 16px;
  border: 1px solid rgba(214, 225, 255, 0.96);
  border-radius: 999px;
  background: rgba(242, 246, 255, 0.95);
  color: #4660d6;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}

.page-btn:disabled {
  color: #99a5bd;
  cursor: not-allowed;
  background: rgba(245, 247, 252, 0.92);
}

.page-indicator {
  min-width: 120px;
  text-align: center;
  color: #536683;
  font-size: 13px;
  font-weight: 800;
}
</style>
