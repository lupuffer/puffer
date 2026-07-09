<template>
  <article class="order-card" :class="`status-${order.status}`">
    <div class="order-header">
      <div class="order-info">
        <strong>{{ order.orderNo }}</strong>
        <span class="order-time">{{ order.createdAt }}</span>
      </div>
      <div class="order-status">
        <span class="status-badge">{{ order.statusText }}</span>
      </div>
    </div>
    <div class="order-content">
      <div class="order-book">
        <div class="book-image"><img :src="order.bookImage" :alt="order.bookTitle" loading="lazy" /></div>
        <div class="book-details">
          <h4>{{ order.bookTitle }}</h4>
          <p>作者：{{ order.bookAuthor }}</p>
          <p>ISBN：{{ order.isbn }}</p>
        </div>
      </div>
      <div class="order-partner">
        <div class="partner-info">
          <i class="fas fa-user-circle"></i>
          <div>
            <strong>{{ order.partner }}</strong>
            <span>{{ order.partnerRole }} · 信誉 {{ partnerCreditScore }} 分 · {{ partnerCreditLabel }}</span>
          </div>
        </div>
        <div v-if="order.meetTime || order.meetPlace" class="meet-info">
          <span v-if="order.meetTime">见面时间：{{ order.meetTime }}</span>
          <span v-if="order.meetPlace">见面地点：{{ order.meetPlace }}</span>
        </div>
      </div>
      <div class="order-details">
        <div class="detail-item"><span>价格</span><strong>￥{{ Number(order.price || 0).toFixed(2) }}</strong></div>
        <div class="detail-item"><span>交易方式</span><strong>{{ order.tradeMethod }}</strong></div>
        <div class="detail-item"><span>校区</span><strong>{{ order.campus }}</strong></div>
      </div>
    </div>
    <div v-if="order.actions.length" class="order-actions">
      <button
        v-for="action in order.actions"
        :key="action"
        class="btn"
        type="button"
        @click="$emit('action', { order, action })"
      >
        {{ action }}
      </button>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import { getCreditLabel, normalizeCreditScore } from '../../utils/credit'

const props = defineProps({
  order: { type: Object, required: true },
})

defineEmits(['action', 'rate'])

const partnerCreditScore = computed(() => (
  normalizeCreditScore(props.order.partnerCreditScore ?? props.order.partner?.creditScore, 100)
))

const partnerCreditLabel = computed(() => getCreditLabel(partnerCreditScore.value))
</script>

<style scoped>
.order-card {
  border: 1px solid var(--gray-200);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s ease;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: var(--gray-50);
  border-bottom: 1px solid var(--gray-200);
}

.order-info strong {
  font-size: 15px;
  color: var(--gray-900);
}

.order-time {
  font-size: 14px;
  color: var(--gray-500);
  margin-left: 12px;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  background: var(--light-blue);
  color: var(--primary-blue);
}

.order-content {
  display: grid;
  grid-template-columns: 1fr 1fr 220px;
  gap: 24px;
  padding: 20px;
}

.order-book,
.partner-info {
  display: flex;
  gap: 16px;
}

.book-image {
  width: 80px;
  height: 100px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.book-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-details h4 {
  font-size: 15px;
  font-weight: 600;
  color: var(--gray-900);
  margin-bottom: 4px;
}

.book-details p,
.partner-info span,
.meet-info span {
  display: block;
  font-size: 14px;
  color: var(--gray-500);
}

.partner-info i {
  font-size: 40px;
  color: var(--gray-400);
}

.partner-info strong {
  display: block;
  font-size: 15px;
  color: var(--gray-900);
}

.meet-info {
  margin-top: 12px;
}

.order-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  font-size: 15px;
}

.detail-item span {
  color: var(--gray-500);
}

.detail-item strong {
  color: var(--gray-900);
  font-weight: 600;
}

.order-actions {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  background: var(--gray-50);
  border-top: 1px solid var(--gray-200);
}

.btn {
  flex: 1;
  padding: 10px 20px;
  border-radius: 8px;
  border: 1px solid var(--gray-300);
  background: white;
}

@media (max-width: 1024px) {
  .order-content {
    grid-template-columns: 1fr;
  }
}
</style>
