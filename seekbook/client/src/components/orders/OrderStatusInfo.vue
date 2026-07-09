<template>
  <section class="order-status-info">
    <h3><i class="fas fa-info-circle"></i> 订单状态说明</h3>
    <div class="status-grid">
      <div v-for="item in items" :key="item.title" class="status-item">
        <div class="status-icon"><i :class="item.icon"></i></div>
        <div class="status-content">
          <h4>{{ item.title }}</h4>
          <p>{{ item.description }}</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
defineProps({
  items: { type: Array, required: true },
})
</script>

<style scoped>
.order-status-info {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: var(--shadow-md);
  margin-top: 24px;
}

.order-status-info h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--gray-900);
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.status-item {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: var(--gray-50);
  border-radius: 12px;
}

.status-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
  background: var(--light-blue);
  color: var(--primary-blue);
}

.status-content h4 {
  font-size: 15px;
  font-weight: 600;
  color: var(--gray-900);
  margin-bottom: 4px;
}

.status-content p {
  font-size: 14px;
  color: var(--gray-600);
  line-height: 1.5;
}
</style>
