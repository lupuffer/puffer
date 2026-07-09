<template>
  <Teleport to="body">
    <div v-if="open" class="confirm-overlay" @click.self="$emit('cancel')">
      <div class="confirm-card" role="dialog" aria-modal="true" :aria-labelledby="titleId">
        <div class="confirm-header">
          <div>
            <p class="confirm-kicker">操作确认</p>
            <h3 :id="titleId">{{ title }}</h3>
          </div>
          <button type="button" class="icon-btn" @click="$emit('cancel')">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="confirm-body">
          <p>{{ message }}</p>
        </div>

        <div class="confirm-footer">
          <button type="button" class="ghost-btn" @click="$emit('cancel')">{{ cancelText }}</button>
          <button type="button" class="primary-btn" @click="$emit('confirm')">{{ confirmText }}</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: '' },
  message: { type: String, default: '' },
  confirmText: { type: String, default: '确认' },
  cancelText: { type: String, default: '取消' },
})

defineEmits(['confirm', 'cancel'])

const titleId = computed(() => `knowledge-confirm-${props.title || 'dialog'}`)
</script>

<style scoped>
.confirm-overlay {
  position: fixed;
  inset: 0;
  display: grid;
  place-items: center;
  padding: 20px;
  background: rgba(20, 30, 56, 0.28);
  backdrop-filter: blur(5px);
  z-index: 2500;
}

.confirm-card {
  width: min(100%, 460px);
  border-radius: 22px;
  border: 1px solid rgba(226, 234, 255, 0.92);
  background: #ffffff;
  box-shadow: 0 28px 70px rgba(70, 84, 140, 0.24);
  overflow: hidden;
}

.confirm-header,
.confirm-footer {
  padding: 18px 22px;
}

.confirm-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px solid #edf1ff;
}

.confirm-kicker {
  margin-bottom: 4px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #7b89a8;
}

.confirm-header h3 {
  font-size: 22px;
  color: #16213a;
}

.confirm-body {
  padding: 20px 22px 4px;
  color: #55657d;
  line-height: 1.7;
}

.confirm-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.icon-btn,
.ghost-btn,
.primary-btn {
  border: none;
  cursor: pointer;
}

.icon-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #f4f7ff;
  color: #60718a;
}

.ghost-btn,
.primary-btn {
  min-height: 42px;
  padding: 0 18px;
  border-radius: 12px;
  font-weight: 700;
}

.ghost-btn {
  background: #f4f7ff;
  color: #41526b;
}

.primary-btn {
  color: #fff;
  background: linear-gradient(135deg, #2f80ed 0%, #6f84ff 64%, #a78bfa 100%);
}
</style>
