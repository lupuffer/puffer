<template>
  <aside class="sidebar-column">
    <div v-for="list in rankLists" :key="list.title" class="sidebar-card">
      <h3><i :class="list.icon"></i> {{ list.title }}</h3>
      <div class="hot-list">
        <div v-for="item in list.items" :key="item.rank" class="hot-item">
          <span class="hot-rank" :class="{ top: item.rank <= 3 }">{{ item.rank }}</span>
          <div class="hot-content">
            <div class="hot-title">{{ item.title }}</div>
            <div class="hot-meta">{{ item.meta }}</div>
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
defineProps({
  rankLists: { type: Array, required: true },
})
</script>

<style scoped>
.sidebar-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.sidebar-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: var(--shadow-md);
}

.sidebar-card h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--gray-900);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.sidebar-card h3 i {
  color: var(--primary-blue);
}

.hot-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.hot-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid var(--gray-100);
}

.hot-rank {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--gray-100);
  color: var(--gray-600);
  border-radius: 4px;
  font-size: 14px;
  font-weight: 600;
}

.hot-rank.top {
  background: var(--primary-blue);
  color: white;
}

.hot-content {
  flex: 1;
  min-width: 0;
}

.hot-title {
  font-size: 15px;
  font-weight: 500;
  color: var(--gray-800);
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hot-meta {
  font-size: 13px;
  color: var(--gray-500);
}

@media (max-width: 1024px) {
  .sidebar-column {
    display: none;
  }
}
</style>
