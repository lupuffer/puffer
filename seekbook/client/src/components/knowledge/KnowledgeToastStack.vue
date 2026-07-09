<template>
  <Teleport to="body">
    <div class="toast-stack" aria-live="polite" aria-atomic="true">
      <transition-group name="toast-fade">
        <div v-for="toast in toasts" :key="toast.id" class="toast-item" :class="`is-${toast.type}`">
          <i :class="iconMap[toast.type] || iconMap.info"></i>
          <span>{{ toast.message }}</span>
        </div>
      </transition-group>
    </div>
  </Teleport>
</template>

<script setup>
const props = defineProps({
  toasts: {
    type: Array,
    default: () => [],
  },
})

const iconMap = {
  info: 'fas fa-circle-info',
  success: 'fas fa-circle-check',
  warning: 'fas fa-triangle-exclamation',
  error: 'fas fa-circle-xmark',
}
</script>

<style scoped>
.toast-stack {
  position: fixed;
  right: 24px;
  bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 2600;
  pointer-events: none;
}

.toast-item {
  min-width: 260px;
  max-width: 360px;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 14px 16px;
  border-radius: 16px;
  border: 1px solid rgba(219, 227, 255, 0.88);
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 22px 48px rgba(86, 102, 160, 0.18);
  color: #324154;
  backdrop-filter: blur(16px);
}

.toast-item i {
  margin-top: 2px;
}

.toast-item.is-success i {
  color: #16a34a;
}

.toast-item.is-warning i {
  color: #d97706;
}

.toast-item.is-error i {
  color: #dc2626;
}

.toast-item.is-info i {
  color: #2563eb;
}

.toast-fade-enter-active,
.toast-fade-leave-active {
  transition: all 0.24s ease;
}

.toast-fade-enter-from,
.toast-fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

@media (max-width: 768px) {
  .toast-stack {
    left: 16px;
    right: 16px;
    bottom: 16px;
  }

  .toast-item {
    max-width: none;
    min-width: 0;
  }
}
</style>
