<template>
  <section class="profile-section">
    <div class="section-header">
      <div>
        <h3><i class="fas fa-bell"></i> 我的缺货登记</h3>
        <p>这里会展示你登记过的待求购书籍。</p>
      </div>
      <span class="count-pill">{{ registrations.length }} 条</span>
    </div>

    <div v-if="loading" class="empty-state">
      <h4>正在加载登记记录...</h4>
    </div>

    <div v-else-if="!registrations.length" class="empty-state">
      <h4>还没有缺货登记</h4>
      <p>去星图集市登记你想要的书，有同学上架时就更容易找到。</p>
      <button class="btn btn-primary" type="button" @click="$emit('explore')">去登记书籍</button>
    </div>

    <div v-else class="registration-list">
      <article v-for="item in registrations" :key="item.id" class="registration-card">
        <div class="registration-main">
          <div class="registration-head">
            <h4>{{ item.bookName }}</h4>
            <span class="status-pill">{{ item.statusLabel }}</span>
          </div>
          <p class="summary-line">{{ item.summaryLine }}</p>
          <p v-if="item.note" class="note-line">备注：{{ item.note }}</p>
          <p class="meta-line">登记时间：{{ formatDate(item.createdAt) }}</p>
        </div>
        <button class="btn btn-outline" type="button" @click="$emit('remove', item)">取消登记</button>
      </article>
    </div>
  </section>
</template>

<script setup>
defineProps({
  registrations: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})

defineEmits(['remove', 'explore'])

function formatDate(value) {
  if (!value) return '暂无记录'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '暂无记录'
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}
</script>

<style scoped>
.profile-section {
  background-color: white;
  border-radius: 16px;
  box-shadow: var(--shadow-md);
  padding: 24px;
}

.section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}

.section-header h3 {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 0 8px;
  color: var(--gray-900);
  font-size: 20px;
}

.section-header p,
.summary-line,
.note-line,
.meta-line,
.empty-state p {
  color: var(--gray-600);
}

.count-pill,
.status-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 32px;
  padding: 0 12px;
  border-radius: 999px;
  background: var(--light-blue);
  color: var(--primary-blue);
  font-size: 13px;
  font-weight: 700;
}

.registration-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.registration-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px;
  border-radius: 14px;
  background: rgba(246, 249, 255, 0.92);
  border: 1px solid rgba(221, 231, 255, 0.96);
}

.registration-main {
  min-width: 0;
  flex: 1;
}

.registration-head {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.registration-head h4,
.empty-state h4 {
  margin: 0;
  color: var(--gray-900);
  font-size: 17px;
}

.summary-line,
.note-line,
.meta-line {
  margin: 4px 0 0;
  font-size: 14px;
}

.empty-state {
  min-height: 240px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 12px;
}

.btn {
  border: none;
  border-radius: 10px;
  padding: 10px 16px;
  font-size: 14px;
  cursor: pointer;
}

.btn-primary {
  background: var(--primary-blue);
  color: white;
}

.btn-outline {
  background: white;
  color: var(--gray-700);
  border: 1px solid var(--gray-300);
}

@media (max-width: 768px) {
  .registration-card,
  .section-header {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
