<template>
  <div class="material-list">
    <MaterialCard
      v-for="material in materials"
      :key="material.id"
      :material="material"
      :price-label="formatPrice(material.pricePoints)"
      :liked="isLiked(material.id)"
      :favorited="isFavorited(material.id)"
      :show-delete="showDelete"
      :format-relative-time="formatRelativeTime"
      @like="$emit('like', $event)"
      @favorite="$emit('favorite', $event)"
      @delete="$emit('delete', $event)"
    />

    <div v-if="!materials.length" class="empty-state">
      <i class="fas fa-inbox"></i>
      <p>{{ emptyText }}</p>
    </div>
  </div>
</template>

<script setup>
import MaterialCard from './MaterialCard.vue'

defineProps({
  materials: {
    type: Array,
    default: () => [],
  },
  emptyText: {
    type: String,
    default: '当前筛选条件下还没有资料，试试切换分类或先上传第一份资料。',
  },
  isLiked: {
    type: Function,
    required: true,
  },
  isFavorited: {
    type: Function,
    required: true,
  },
  formatPrice: {
    type: Function,
    required: true,
  },
  formatRelativeTime: {
    type: Function,
    required: true,
  },
  showDelete: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['like', 'favorite', 'delete'])
</script>

<style scoped>
.material-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.empty-state {
  padding: 48px 24px;
  border-radius: 22px;
  border: 1px dashed rgba(196, 210, 247, 0.96);
  background: rgba(255, 255, 255, 0.72);
  text-align: center;
  color: #6b7c96;
}

.empty-state i {
  margin-bottom: 12px;
  font-size: 36px;
  color: #94a3bd;
}
</style>
