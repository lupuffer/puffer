<template>
  <Teleport to="body">
    <div v-if="open" class="records-overlay" @click.self="$emit('close')">
      <div class="records-dialog">
        <div class="records-head">
          <div>
            <h3>{{ title }}</h3>
            <p v-if="summary">{{ summary }}</p>
          </div>
          <button type="button" class="close-btn" @click="$emit('close')">
            <i class="fas fa-xmark"></i>
          </button>
        </div>

        <div v-if="loading" class="records-state">
          <i class="fas fa-spinner fa-spin"></i>
          <p>正在加载...</p>
        </div>

        <div v-else-if="items.length" class="records-list">
          <article v-for="item in items" :key="item.id" class="record-item">
            <h4>{{ item.title }}</h4>
            <p v-if="item.subtitle" class="record-subtitle">{{ item.subtitle }}</p>
            <p v-if="item.meta" class="record-meta">{{ item.meta }}</p>
          </article>
        </div>

        <div v-else class="records-state">
          <i class="fas fa-inbox"></i>
          <p>{{ emptyText }}</p>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  open: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
    default: '',
  },
  summary: {
    type: String,
    default: '',
  },
  loading: {
    type: Boolean,
    default: false,
  },
  items: {
    type: Array,
    default: () => [],
  },
  emptyText: {
    type: String,
    default: '暂无数据',
  },
})

defineEmits(['close'])
</script>

<style scoped>
.records-overlay {
  position: fixed;
  inset: 0;
  z-index: 2600;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(24, 35, 58, 0.28);
  backdrop-filter: blur(8px);
}

.records-dialog {
  width: min(680px, 100%);
  max-height: min(78vh, 760px);
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 20px;
  border-radius: 24px;
  border: 1px solid rgba(224, 232, 255, 0.96);
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 24px 60px rgba(92, 75, 140, 0.18);
}

.records-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
}

.records-head h3 {
  color: #18233b;
  font-size: 20px;
  font-weight: 700;
}

.records-head p {
  margin-top: 4px;
  color: #6b7c96;
  font-size: 13px;
}

.close-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 12px;
  background: #f3f6ff;
  color: #4760d9;
  cursor: pointer;
}

.records-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
  padding-right: 4px;
}

.record-item {
  padding: 14px 16px;
  border-radius: 18px;
  border: 1px solid rgba(228, 234, 255, 0.96);
  background: rgba(246, 248, 255, 0.84);
}

.record-item h4 {
  color: #18233b;
  font-size: 16px;
  line-height: 1.4;
}

.record-subtitle {
  margin-top: 6px;
  color: #50627f;
  font-size: 13px;
  line-height: 1.6;
}

.record-meta {
  margin-top: 8px;
  color: #7a89a3;
  font-size: 12px;
}

.records-state {
  min-height: 180px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #6b7c96;
}

.records-state i {
  font-size: 30px;
  color: #95a4c0;
}
</style>
