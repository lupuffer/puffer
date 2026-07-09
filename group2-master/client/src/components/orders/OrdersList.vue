<template>
  <section class="orders-list">
    <div v-if="loading" class="order-section empty-section">
      <p>正在加载真实订单...</p>
    </div>
    <div v-else-if="!orders.length" class="order-section empty-section">
      <p>{{ emptyText }}</p>
    </div>
    <template v-else>
      <div v-for="section in sections" :key="section.key" class="order-section">
        <h3><i :class="section.icon"></i> {{ section.title }}</h3>
        <div v-if="groupedOrders(section.key).length" class="order-cards">
          <OrderCard
            v-for="order in groupedOrders(section.key)"
            :key="order.id"
            :order="order"
            @action="$emit('action', $event)"
          />
        </div>
        <p v-else class="section-empty">{{ section.emptyText }}</p>
      </div>
    </template>
  </section>
</template>

<script setup>
import OrderCard from './OrderCard.vue'

const props = defineProps({
  sections: { type: Array, required: true },
  orders: { type: Array, required: true },
  loading: { type: Boolean, default: false },
  emptyText: { type: String, default: '暂无订单' },
})

defineEmits(['action'])

const groupedOrders = (key) => {
  if (key === 'pending') return props.orders.filter((order) => ['created', 'negotiating', 'confirmed'].includes(order.status))
  return props.orders.filter((order) => order.status === key)
}
</script>

<style scoped>
.orders-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.order-section {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: var(--shadow-md);
}

.order-section h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--gray-900);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.order-cards {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.empty-section,
.section-empty {
  color: var(--gray-500);
}
</style>
