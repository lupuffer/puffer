<template>
  <aside class="transaction-panel">
    <section class="price-section">
      <div class="current-price">
        <span class="price-label">{{ detail.priceLabel }}</span>
        <span class="price-amount">￥{{ Number(book.price || 0).toFixed(2) }}</span>
        <span class="original-price">￥{{ Number(book.originalPrice || 0).toFixed(2) }}</span>
      </div>
      <div class="price-savings"><i class="fas fa-piggy-bank"></i>{{ detail.savingText }}</div>
    </section>

    <section class="transaction-console">
      <h3><i class="fas fa-shopping-cart"></i>{{ detail.consoleTitle }}</h3>
      <div class="console-actions">
        <button
          v-for="(action, index) in detail.actions"
          :key="action"
          class="transaction-btn"
          :class="index === 0 ? 'primary-buy' : 'secondary-action'"
          type="button"
          @click="handleAction(action, index)"
        >
          <i :class="actionIcon(index, action)"></i>
          {{ action }}
        </button>
      </div>
      <div class="delivery-info">
        <h4><i class="fas fa-info-circle"></i>{{ detail.deliveryTitle }}</h4>
        <p v-for="line in detail.deliveryLines" :key="line">{{ line }}</p>
      </div>
    </section>

    <section class="safety-tips">
      <h4><i class="fas fa-shield-alt"></i>{{ detail.safetyTitle }}</h4>
      <ul>
        <li v-for="tip in detail.safetyTips" :key="tip">{{ tip }}</li>
      </ul>
    </section>
  </aside>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useGlobalState } from '../../composables/useGlobalState'
import { createOrder } from '../../services/api'

const props = defineProps({
  book: { type: Object, required: true },
  detail: { type: Object, required: true },
  currentUser: { type: Object, default: () => ({}) },
})

const router = useRouter()
const { getOrCreateSession, toggleFavorite } = useGlobalState()

const sellerName = () => props.book.seller?.name || props.book.sellerName || props.book.seller || '未知卖家'
const sellerId = () => props.book.sellerId || props.book.seller?.id || ''

const actionIcon = (index, action) => {
  if (index === 0) return 'fas fa-bag-shopping'
  if (index === 1 || action.includes('收藏')) return 'far fa-heart'
  return 'far fa-comments'
}

const handleAction = async (action, index) => {
  if (index === 0) {
    await handleBuy()
    return
  }

  if (index === 1) {
    await handleFavorite()
    return
  }

  if (index === 2 || action.includes('私聊') || action.includes('联系')) {
    await handleContactSeller()
  }
}

const handleBuy = async () => {
  if (!props.currentUser?.isLoggedIn || !props.currentUser?.id) {
    alert('请先登录后再购买')
    router.push('/login')
    return
  }

  if (!props.book?.id) {
    alert('当前书籍信息不完整，暂时无法购买')
    return
  }

  try {
    const result = await createOrder({
      bookId: props.book.id,
      price: props.book.price,
    })

    if (result?.code === 200) {
      alert('订单创建成功，书籍已从集市下架')
      router.push('/orders')
      return
    }

    alert(result?.message || '订单创建失败，请稍后重试')
  } catch (error) {
    alert(error.message || '订单创建失败，请稍后重试')
  }
}

const handleFavorite = async () => {
  const result = await toggleFavorite(props.book.id)
  alert(result ? '已加入收藏' : '已取消收藏')
}

const handleContactSeller = async () => {
  if (!props.currentUser?.isLoggedIn || !props.currentUser?.id) {
    alert('请先登录后再联系卖家')
    router.push('/login')
    return
  }

  if (!sellerId()) {
    alert('当前书籍缺少卖家信息，暂时无法发起会话')
    return
  }

  const session = await getOrCreateSession(props.book.id, sellerId(), sellerName(), props.book.title)
  if (!session?.id) {
    return
  }

  router.push({
    path: '/messages',
    query: { sessionId: session.id },
  })
}
</script>

<style scoped>
.transaction-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
  position: sticky;
  top: 98px;
  align-self: start;
}

.price-section,
.transaction-console,
.safety-tips {
  background-color: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--shadow-md);
}

.current-price {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--gray-200);
}

.price-label {
  display: block;
  font-size: 14px;
  color: var(--gray-600);
  margin-bottom: 8px;
  font-weight: 500;
}

.price-amount {
  font-size: 40px;
  font-weight: 700;
  color: var(--primary-blue);
  margin-right: 12px;
  line-height: 1;
}

.original-price {
  font-size: 16px;
  color: var(--gray-500);
  text-decoration: line-through;
  display: block;
  margin-top: 4px;
}

.price-savings {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 12px 20px;
  background-color: var(--light-green);
  color: var(--secondary-green);
  border-radius: 10px;
  font-weight: 600;
  font-size: 15px;
}

.transaction-console h3,
.safety-tips h4 {
  font-size: 20px;
  font-weight: 600;
  color: var(--gray-900);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.delivery-info p,
.safety-tips li {
  font-size: 14px;
  color: var(--gray-600);
}

.console-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 24px;
}

.transaction-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 46px;
  padding: 13px 16px;
  font-size: 15px;
  font-weight: 700;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease, background-color 0.18s ease, border-color 0.18s ease;
}

.transaction-btn:hover {
  transform: translateY(-1px);
}

.primary-buy {
  grid-column: 1 / -1;
  color: #fff;
  border: 1px solid rgba(118, 133, 255, 0.42);
  background: linear-gradient(135deg, #2f80ed 0%, #6f84ff 62%, #a78bfa 100%);
  box-shadow: 0 16px 34px rgba(92, 75, 140, 0.22), 0 8px 20px rgba(47, 128, 237, 0.2);
}

.primary-buy:hover {
  box-shadow: 0 20px 40px rgba(92, 75, 140, 0.26), 0 10px 24px rgba(47, 128, 237, 0.24);
}

.secondary-action {
  background-color: var(--gray-100);
  color: var(--gray-700);
  border: 1px solid var(--gray-200);
}

.secondary-action:hover {
  background-color: #eef3ff;
  border-color: rgba(79, 110, 247, 0.22);
  color: var(--primary-blue);
}

.delivery-info {
  padding: 20px;
  background-color: var(--gray-50);
  border-radius: 10px;
  border: 1px solid var(--gray-200);
}

.delivery-info h4 {
  font-size: 16px;
  font-weight: 600;
  color: var(--gray-900);
  margin-bottom: 12px;
}

.safety-tips ul {
  list-style: none;
  padding: 0;
}

@media (max-width: 1024px) {
  .transaction-panel {
    position: static;
  }
}
</style>
