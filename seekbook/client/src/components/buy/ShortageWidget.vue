<template>
  <aside class="shortage-card" :class="{ collapsed }" :style="{ bottom: `${bottomOffset}px` }">
    <div class="shortage-card-header" @click="collapsed = !collapsed">
      <div class="shortage-header-main">
        <div class="shortage-header-icon">
          <i class="fas fa-bell"></i>
        </div>
        <div class="shortage-header-copy">
          <span class="shortage-title">{{ shortage.cardTitle }}</span>
        </div>
      </div>
      <button class="shortage-toggle-btn" type="button" :aria-label="collapsed ? '展开缺货登记' : '收起缺货登记'">
        <i :class="collapsed ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
      </button>
    </div>

    <div class="shortage-card-body">
      <div class="shortage-list-title">
        <span>{{ shortage.listTitle }}</span>
        <span v-if="items.length" class="shortage-count-pill">{{ items.length }} 条</span>
      </div>

      <div v-if="loading" class="shortage-empty">
        <div class="shortage-empty-icon"><i class="fas fa-spinner fa-spin"></i></div>
        <div class="empty-text">正在加载登记记录...</div>
      </div>

      <div v-else-if="items.length" class="shortage-list">
        <div v-for="item in items" :key="item.id" class="shortage-item">
          <div class="shortage-item-main">
            <div class="shortage-book-name">{{ item.bookName }}</div>
            <div class="shortage-condition">{{ item.summaryLine }}</div>
            <div v-if="item.note" class="shortage-note-line">{{ item.note }}</div>
          </div>
          <button class="shortage-cancel-btn" type="button" @click.stop="$emit('cancel', item)">{{ cancelText }}</button>
        </div>
      </div>

      <div v-else class="shortage-empty">
        <div class="shortage-empty-icon empty-icon-soft"><i class="fas fa-book-open-reader"></i></div>
        <div class="empty-text">{{ shortage.emptyTitle }}</div>
        <div class="empty-hint">{{ shortage.emptyHint }}</div>
      </div>

      <div class="shortage-footer">
        <button class="btn-shortage-register" type="button" @click.stop="$emit('open')">
          <i class="fas fa-plus"></i>
          <span>{{ shortage.registerButton }}</span>
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  shortage: { type: Object, required: true },
  items: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  bottomOffset: { type: Number, default: 24 },
})

defineEmits(['open', 'cancel'])

const collapsed = ref(false)
const cancelText = computed(() => props.shortage.form?.cancel || '取消')
</script>

<style scoped>
.shortage-card {
  position: fixed;
  right: 24px;
  width: 340px;
  border-radius: 22px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(246, 249, 255, 0.96) 100%);
  border: 1px solid rgba(220, 228, 255, 0.95);
  box-shadow: 0 24px 48px rgba(91, 114, 214, 0.18);
  z-index: 90;
  overflow: hidden;
  backdrop-filter: blur(18px);
}

.shortage-card::before {
  content: '';
  position: absolute;
  inset: 0 0 auto 0;
  height: 110px;
  background:
    radial-gradient(circle at top left, rgba(255, 196, 102, 0.22), transparent 48%),
    radial-gradient(circle at top right, rgba(124, 140, 255, 0.16), transparent 54%);
  pointer-events: none;
}

.shortage-card-header {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 18px 20px 16px;
  cursor: pointer;
  user-select: none;
}

.shortage-header-main {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.shortage-header-icon {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ff9f43;
  background: linear-gradient(135deg, rgba(255, 233, 204, 0.96), rgba(255, 246, 230, 0.92));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.85);
  flex: 0 0 auto;
}

.shortage-header-copy {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.shortage-title {
  font-size: 15px;
  font-weight: 800;
  color: var(--gray-900);
}

.shortage-toggle-btn {
  width: 36px;
  height: 36px;
  border: 1px solid rgba(218, 225, 248, 0.96);
  background: rgba(255, 255, 255, 0.82);
  color: var(--gray-500);
  cursor: pointer;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex: 0 0 auto;
}

.shortage-toggle-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 18px rgba(79, 110, 247, 0.12);
}

.shortage-card.collapsed .shortage-card-body {
  display: none;
}

.shortage-card-body {
  position: relative;
  max-height: 360px;
  overflow-y: auto;
  padding-bottom: 4px;
}

.shortage-list-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 4px 20px 12px;
  font-size: 13px;
  font-weight: 700;
  color: var(--gray-600);
}

.shortage-count-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 24px;
  padding: 0 10px;
  border-radius: 999px;
  background: rgba(79, 110, 247, 0.12);
  color: var(--primary-blue);
  font-size: 12px;
  font-weight: 700;
}

.shortage-list {
  padding: 0 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.shortage-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 14px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(228, 233, 248, 0.96);
  box-shadow: 0 10px 24px rgba(114, 131, 208, 0.08);
}

.shortage-item-main {
  min-width: 0;
  flex: 1;
}

.shortage-book-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--gray-900);
  line-height: 1.45;
  margin-bottom: 3px;
}

.shortage-note-line,
.shortage-condition,
.empty-hint {
  font-size: 12px;
  color: var(--gray-500);
  line-height: 1.55;
}

.shortage-note-line {
  margin-top: 2px;
}

.shortage-cancel-btn {
  min-height: 34px;
  padding: 0 12px;
  font-size: 12px;
  color: #8a94a7;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(225, 229, 238, 0.98);
  border-radius: 10px;
  cursor: pointer;
  font-weight: 700;
  flex: 0 0 auto;
}

.shortage-empty {
  padding: 20px 20px 22px;
  text-align: center;
}

.shortage-empty-icon {
  width: 56px;
  height: 56px;
  margin: 0 auto 12px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  color: var(--primary-blue);
  background: linear-gradient(135deg, rgba(230, 239, 255, 0.96), rgba(244, 247, 255, 0.92));
}

.empty-icon-soft {
  color: #7c8cff;
}

.empty-text {
  font-size: 14px;
  color: var(--gray-700);
  font-weight: 700;
  margin-bottom: 4px;
}

.shortage-footer {
  padding: 16px;
}

.btn-shortage-register {
  width: 100%;
  min-height: 52px;
  padding: 0 18px;
  background: linear-gradient(135deg, #4f8ef7 0%, #8a77f2 100%);
  color: white;
  border: none;
  border-radius: 16px;
  font-size: 16px;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow: 0 18px 28px rgba(108, 117, 242, 0.24);
}

.btn-shortage-register i {
  font-size: 15px;
}

@media (max-width: 768px) {
  .shortage-card {
    width: calc(100% - 32px);
    left: 16px;
    right: 16px;
    border-radius: 20px;
  }

  .shortage-card-body {
    max-height: 50vh;
  }
}
</style>
