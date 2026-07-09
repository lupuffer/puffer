<template>
  <section class="chat-main">
    <div class="chat-stage">
      <div class="chat-header">
        <div class="chat-header-info">
          <div class="chat-header-avatar"><i class="fas fa-user"></i></div>
          <div>
            <div class="chat-header-name">{{ conversation.name }}</div>
            <div class="chat-header-status">
              <span class="status-dot"></span>
              <span>{{ conversation.onlineText || onlineText }}</span>
            </div>
          </div>
        </div>
        <div class="chat-actions">
          <button
            v-for="action in headerActions"
            :key="action.key"
            class="chat-action-btn"
            :class="{ danger: action.tone === 'danger' }"
            :title="action.label"
            type="button"
            :disabled="action.disabled"
            @click="action.onClick"
          >
            <i :class="action.icon"></i>
            <span>{{ action.label }}</span>
          </button>
        </div>
      </div>

      <div v-if="orderInfo && ['confirmed', 'completed'].includes(orderInfo.status)" class="order-confirmed-banner">
        <div class="confirmed-icon">🤝</div>
        <div class="confirmed-text">
          <div class="confirmed-title">{{ tradeBannerTitle }}</div>
          <div class="confirmed-detail">
            时间：<strong>{{ orderInfo.meetTime }}</strong>
            <span class="divider">|</span>
            地点：<strong>{{ orderInfo.meetPlace }}</strong>
          </div>
        </div>
        <div class="confirmed-badge">{{ orderInfo.status === 'completed' ? '已完成' : '已确认' }}</div>
      </div>

      <div ref="messagesContainer" class="chat-messages">
        <div
          v-for="message in displayMessages"
          :key="message.id || message.time + message.text"
          class="message"
          :class="{ sent: message.type === 'sent' }"
        >
          <div class="message-avatar"><i class="fas fa-user"></i></div>
          <div class="message-content">
            <div class="message-text">{{ message.text }}</div>
            <div class="message-time">{{ message.time }}</div>
          </div>
        </div>
      </div>

      <div class="chat-input-area">
        <div class="chat-toolbar">
          <button
            v-for="tool in toolbar"
            :key="tool.title"
            class="toolbar-btn"
            :title="tool.title"
            type="button"
          >
            <i :class="tool.icon"></i>
          </button>
        </div>
        <div class="chat-input-wrapper">
          <input
            v-model="inputText"
            class="chat-input"
            :placeholder="inputPlaceholder"
            maxlength="2000"
            :disabled="conversation.isSystemSession"
            @keyup.enter="handleSend"
          />
          <button class="send-btn" type="button" :disabled="conversation.isSystemSession" @click="handleSend">
            <i class="fas fa-paper-plane"></i>
            <span>{{ sendText }}</span>
          </button>
        </div>
      </div>
    </div>

    <aside v-if="!conversation.isSystemSession" class="trade-panel">
      <div class="trade-panel-header">
        <i class="fas fa-handshake"></i>
        <span>线下交易确认</span>
      </div>

      <div v-if="showTradeForm" class="trade-form">
        <div class="form-group">
          <label class="form-label">
            <i class="fas fa-clock"></i>
            约定见面时间
          </label>
          <input
            v-model="meetTime"
            type="datetime-local"
            class="form-input datetime-input"
            :min="minDateTime"
          />
        </div>

        <div class="form-group">
          <label class="form-label">
            <i class="fas fa-map-marker-alt"></i>
            约定见面地点
          </label>
          <input
            v-model="meetPlace"
            type="text"
            class="form-input"
            placeholder="如：紫金港校区东大门"
          />
        </div>

        <button
          class="confirm-trade-btn"
          :disabled="!canConfirm"
          :class="{ 'btn-disabled': !canConfirm }"
          @click="confirmTrade"
        >
          <i class="fas fa-check-circle"></i>
          确认线下交易方案
        </button>

        <p class="trade-hint">
          <i class="fas fa-info-circle"></i>
          确认后双方将收到系统通知，并锁定交易安排
        </p>
      </div>

      <div v-else-if="showCancelledState" class="trade-confirmed">
        <div class="cancelled-card">
          <div class="confirmed-header cancelled-header">
            <i class="fas fa-ban"></i>
            <span>交易已取消</span>
          </div>
          <div class="completion-status">
            这笔订单已经关闭。如果双方想继续交易，可以回到书籍页重新发起沟通或重新创建订单。
          </div>
        </div>
      </div>

      <div v-else class="trade-confirmed">
        <div class="confirmed-card">
          <div class="confirmed-header">
            <i class="fas fa-lock"></i>
            <span>{{ tradeCardTitle }}</span>
          </div>
          <div class="confirmed-item">
            <i class="fas fa-calendar-check"></i>
            <div>
              <div class="item-label">见面时间</div>
              <div class="item-value">{{ orderInfo.meetTime }}</div>
            </div>
          </div>
          <div class="confirmed-item">
            <i class="fas fa-map-pin"></i>
            <div>
              <div class="item-label">见面地点</div>
              <div class="item-value">{{ orderInfo.meetPlace }}</div>
            </div>
          </div>
          <div class="confirmed-time">确认于 {{ formatConfirmedTime(orderInfo.confirmedAt) }}</div>
          <div v-if="orderInfo.status === 'completed' && orderInfo.completedAt" class="confirmed-time">
            完成于 {{ formatConfirmedTime(orderInfo.completedAt) }}
          </div>
          <div class="completion-status">{{ completionStatusText }}</div>
        </div>

        <button
          v-if="orderInfo.status === 'confirmed'"
          class="complete-trade-btn"
          :disabled="!canCompleteTrade"
          :class="{ 'btn-disabled': !canCompleteTrade }"
          @click="completeTrade"
        >
          <i class="fas fa-check-double"></i>
          {{ completeTradeButtonText }}
        </button>
      </div>
    </aside>
  </section>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { cancelOrder, completeOrder, confirmMeet, createOrder, getOrdersByBookId } from '@/services/api.js'

const props = defineProps({
  conversation: { type: Object, required: true },
  messages: { type: Object, required: true },
  currentUser: { type: Object, default: () => ({ role: 'buyer' }) },
})

const emit = defineEmits(['send-message'])

const router = useRouter()
const inputText = ref('')
const messagesContainer = ref(null)
const orderInfo = ref(null)
const meetTime = ref('')
const meetPlace = ref('')
const isConfirming = ref(false)
const isCancellingOrder = ref(false)
const MAX_MESSAGE_LENGTH = 2000
const ACTIVE_ORDER_STATUSES = ['created', 'negotiating', 'confirmed']

const minDateTime = computed(() => {
  const now = new Date()
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset())
  return now.toISOString().slice(0, 16)
})

const canConfirm = computed(() => meetTime.value && meetPlace.value.trim() && !isConfirming.value)
const toolbar = computed(() => props.messages.toolbar || [])
const inputPlaceholder = computed(() => (
  props.conversation?.isSystemSession
    ? '系统通知会话暂不支持回复'
    : (props.messages.inputPlaceholder || '输入消息...')
))
const sendText = computed(() => props.messages.sendText || '发送')
const onlineText = computed(() => (props.conversation?.isSystemSession ? '系统通知' : '在线'))
const displayMessages = computed(() => props.conversation.messages || [])
const canCompleteTrade = computed(() => Boolean(orderInfo.value?.canCompleteOrder))
const showTradeForm = computed(() => !orderInfo.value || ['created', 'negotiating'].includes(orderInfo.value.status))
const showCancelledState = computed(() => orderInfo.value?.status === 'cancelled')
const tradeBannerTitle = computed(() => orderInfo.value?.status === 'completed' ? '双方已完成本次交易' : '双方已约定线下交易')
const tradeCardTitle = computed(() => orderInfo.value?.status === 'completed' ? '交易已完成' : '交易已锁定')
const completionStatusText = computed(() => {
  if (!orderInfo.value) return ''
  if (orderInfo.value.status === 'cancelled') return '订单已取消，本次交易不再继续。'
  if (!['confirmed', 'completed'].includes(orderInfo.value.status)) return ''
  if (orderInfo.value.status === 'completed') return '双方都已确认完成，商品已下架'
  if (orderInfo.value.currentUserCompletionConfirmed && orderInfo.value.partnerCompletionConfirmed) {
    return '双方都已确认完成'
  }
  if (orderInfo.value.currentUserCompletionConfirmed) {
    return '你已确认完成，等待对方确认'
  }
  if (orderInfo.value.partnerCompletionConfirmed) {
    return '对方已确认完成，等待你确认'
  }
  return '线下交付后需双方各自确认一次，订单才会真正完成'
})
const completeTradeButtonText = computed(() => {
  if (!orderInfo.value || orderInfo.value.status !== 'confirmed') return '确认已完成交易'
  if (orderInfo.value.currentUserCompletionConfirmed) return '已确认完成，等待对方'
  if (orderInfo.value.partnerCompletionConfirmed) return '确认完成并结束订单'
  return '确认已完成交易'
})
const canViewBook = computed(() => Boolean(props.conversation?.bookId))
const canCancelTrade = computed(() => (
  Boolean(orderInfo.value?.id)
  && ACTIVE_ORDER_STATUSES.includes(orderInfo.value.status)
  && !isCancellingOrder.value
))
const headerActions = computed(() => {
  const actions = []

  if (canViewBook.value) {
    actions.push({
      key: 'view-book',
      label: '查看书籍',
      icon: 'fas fa-book-open',
      disabled: false,
      tone: 'default',
      onClick: goToBookDetail,
    })
  }

  if (!props.conversation?.isSystemSession && canCancelTrade.value) {
    actions.push({
      key: 'cancel-trade',
      label: isCancellingOrder.value ? '取消中...' : '取消交易',
      icon: 'fas fa-ban',
      disabled: isCancellingOrder.value,
      tone: 'danger',
      onClick: handleCancelTrade,
    })
  }

  return actions
})

const matchConversationOrder = (order) => (
  String(order.bookId) === String(props.conversation.bookId)
  && String(order.buyerId) === String(props.conversation.buyerId)
  && String(order.sellerId) === String(props.conversation.sellerId)
)

const fillTradeFields = (order) => {
  if (!order) {
    meetTime.value = ''
    meetPlace.value = ''
    return
  }

  meetTime.value = order.meetTime || ''
  meetPlace.value = order.meetPlace || ''
}

const fetchOrderInfo = async () => {
  const bookId = props.conversation.bookId
  if (!bookId || props.conversation?.isSystemSession) {
    orderInfo.value = null
    fillTradeFields(null)
    return
  }

  try {
    const data = await getOrdersByBookId(bookId)
    if (data.code === 200 && Array.isArray(data.data) && data.data.length > 0) {
      orderInfo.value = data.data.find(matchConversationOrder) || data.data[0]
      fillTradeFields(orderInfo.value)
      return
    }
    orderInfo.value = null
    fillTradeFields(null)
  } catch (err) {
    console.error('获取订单信息失败:', err)
  }
}

const goToBookDetail = () => {
  if (!props.conversation?.bookId) return
  router.push({
    path: '/book-detail',
    query: {
      id: props.conversation.bookId,
      source: 'messages',
    },
  })
}

const confirmTrade = async () => {
  if (!canConfirm.value) return
  isConfirming.value = true

  if (!orderInfo.value) {
    try {
      const createData = await createOrder({
        bookId: props.conversation.bookId,
        buyerId: props.conversation.buyerId,
        sellerId: props.conversation.sellerId,
        price: props.conversation.price ?? 0,
      })

      if (createData.code === 200) {
        orderInfo.value = createData.data
      } else {
        window.alert(`创建订单失败: ${createData.message}`)
        isConfirming.value = false
        return
      }
    } catch (err) {
      console.error('创建订单失败:', err)
      window.alert(err?.message || '创建订单失败，请重试')
      isConfirming.value = false
      return
    }
  }

  try {
    const data = await confirmMeet(orderInfo.value.id, meetTime.value, meetPlace.value)
    if (data.code === 200) {
      orderInfo.value = data.data
      emit('send-message', `【系统】🤝 双方已约定于 ${meetTime.value} 在 ${meetPlace.value} 进行线下交付`)
      window.alert('交易方案确认成功')
    } else {
      window.alert(`确认失败: ${data.message}`)
    }
  } catch (err) {
    console.error('确认交易失败:', err)
    window.alert(err?.message || '确认交易失败，请重试')
  } finally {
    isConfirming.value = false
  }
}

const completeTrade = async () => {
  if (!orderInfo.value || !canCompleteTrade.value) return
  if (!window.confirm('确认你这边已经完成线下交易？双方都确认后订单才会真正完成。')) return

  try {
    const data = await completeOrder(orderInfo.value.id)
    if (data.code === 200) {
      orderInfo.value = data.data
      if (data.data?.status === 'completed') {
        emit('send-message', '【系统】✅ 本次交易已完成，感谢使用。')
      }
      window.alert(data.message || '操作成功')
    } else {
      window.alert(`操作失败: ${data.message}`)
    }
  } catch (err) {
    console.error('完成订单失败:', err)
    window.alert(err?.message || '完成订单失败，请重试')
  }
}

const handleCancelTrade = async () => {
  if (!canCancelTrade.value) return
  if (!window.confirm('确认取消这笔交易吗？取消后订单会关闭。')) return

  isCancellingOrder.value = true
  try {
    const result = await cancelOrder(orderInfo.value.id)
    await fetchOrderInfo()
    window.alert(result?.message || '交易已取消')
  } catch (err) {
    console.error('取消交易失败:', err)
    window.alert(err?.message || '取消交易失败，请稍后重试')
  } finally {
    isCancellingOrder.value = false
  }
}

const formatConfirmedTime = (isoTime) => {
  if (!isoTime) return ''
  const date = new Date(isoTime)
  return `${date.getMonth() + 1}月${date.getDate()}日 ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

const handleSend = () => {
  if (props.conversation?.isSystemSession) return
  const text = inputText.value.trim()
  if (!text) return
  if (text.length > MAX_MESSAGE_LENGTH) {
    window.alert(`消息过长，最多 ${MAX_MESSAGE_LENGTH} 个字符。`)
    return
  }
  inputText.value = ''
  emit('send-message', text)
  setTimeout(scrollToBottom, 100)
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

onMounted(() => {
  fetchOrderInfo()
})

watch(
  () => props.conversation.id,
  () => {
    fetchOrderInfo()
    scrollToBottom()
  },
)

watch(
  () => props.conversation.messages,
  () => {
    scrollToBottom()
  },
  { deep: true, immediate: true },
)
</script>

<style scoped>
.chat-main {
  min-width: 0;
  min-height: 0;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 312px;
  height: 100%;
  max-height: 100%;
  overflow: hidden;
}

.chat-stage {
  min-width: 0;
  min-height: 0;
  flex: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  padding: 16px 28px;
  border-bottom: 1px solid var(--gray-200);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.chat-header-info {
  display: flex;
  align-items: center;
  gap: 14px;
}

.chat-header-avatar,
.message-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-blue) 0%, #3b82f6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.chat-header-name {
  font-weight: 700;
  font-size: 16px;
  color: var(--gray-900);
}

.chat-header-status {
  margin-top: 2px;
  font-size: 13px;
  color: var(--gray-500);
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 8px;
  height: 8px;
  background: #10b981;
  border-radius: 50%;
}

.chat-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
}

.chat-action-btn {
  min-height: 40px;
  min-width: fit-content;
  padding: 0 14px;
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.86);
  color: var(--gray-700);
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  flex: 0 0 auto;
  white-space: nowrap;
  word-break: keep-all;
}

.chat-action-btn span {
  white-space: nowrap;
  word-break: keep-all;
}

.chat-action-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 10px 24px rgba(59, 130, 246, 0.12);
}

.chat-action-btn:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.chat-action-btn.danger {
  color: #b91c1c;
  border-color: rgba(239, 68, 68, 0.28);
  background: rgba(254, 242, 242, 0.95);
}

.chat-action-btn.danger:hover:not(:disabled) {
  box-shadow: 0 10px 24px rgba(239, 68, 68, 0.16);
}

.order-confirmed-banner {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 28px;
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  border-bottom: 1px solid rgba(16, 185, 129, 0.24);
}

.confirmed-icon {
  font-size: 30px;
}

.confirmed-text {
  flex: 1;
}

.confirmed-title {
  font-size: 15px;
  font-weight: 700;
  color: #047857;
}

.confirmed-detail {
  margin-top: 4px;
  font-size: 13px;
  color: #059669;
}

.divider {
  margin: 0 8px;
  opacity: 0.5;
}

.confirmed-badge {
  padding: 6px 14px;
  background: #10b981;
  color: white;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

.chat-messages {
  flex: 1;
  min-height: 0;
  padding: 28px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 18px;
  background: rgba(247, 248, 255, 0.68);
}

.message {
  display: flex;
  gap: 12px;
  max-width: min(72%, 560px);
}

.message.sent {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message.sent .message-avatar {
  background: var(--gray-400);
}

.message-content {
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.04);
}

.message-text {
  font-size: 14px;
  line-height: 1.65;
  word-break: break-word;
}

.message-time {
  font-size: 12px;
  color: var(--gray-400);
  margin-top: 6px;
}

.chat-input-area {
  flex-shrink: 0;
  padding: 18px 28px 20px;
  border-top: 1px solid var(--gray-200);
  background: rgba(255, 255, 255, 0.84);
}

.chat-toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
}

.toolbar-btn {
  width: 40px;
  height: 40px;
  border: 0;
  border-radius: 12px;
  color: var(--gray-600);
  cursor: pointer;
}

.chat-input-wrapper {
  display: flex;
  gap: 10px;
}

.chat-input {
  flex: 1;
  min-width: 0;
  padding: 14px 16px;
  border-radius: 14px;
  font-size: 14px;
}

.send-btn {
  padding: 12px 22px;
  border: 0;
  border-radius: 14px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.trade-panel {
  min-height: 0;
  display: flex;
  flex-direction: column;
  padding: 22px 20px;
  border-left: 1px solid var(--gray-200);
  background: rgba(248, 250, 252, 0.76);
  overflow: hidden;
}

.trade-panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  color: var(--gray-900);
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--gray-200);
}

.trade-panel-header i {
  color: var(--primary-blue);
}

.trade-form,
.trade-confirmed {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--gray-600);
  display: flex;
  align-items: center;
  gap: 6px;
}

.form-label i {
  width: 16px;
  color: var(--primary-blue);
}

.form-input {
  padding: 12px 14px;
  border: 1px solid var(--gray-200);
  border-radius: 12px;
  font-size: 14px;
  background: white;
}

.trade-hint {
  font-size: 12px;
  color: var(--gray-500);
  line-height: 1.6;
}

.trade-hint i {
  color: var(--primary-blue);
  margin-right: 4px;
}

.confirm-trade-btn,
.complete-trade-btn {
  padding: 14px 16px;
  border: none;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.confirm-trade-btn {
  color: white;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  box-shadow: 0 10px 24px rgba(59, 130, 246, 0.26);
}

.complete-trade-btn {
  color: white;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  box-shadow: 0 10px 24px rgba(16, 185, 129, 0.22);
}

.btn-disabled {
  background: var(--gray-300) !important;
  box-shadow: none !important;
  cursor: not-allowed;
}

.confirmed-card,
.cancelled-card {
  padding: 18px;
  border-radius: 16px;
  background: white;
}

.confirmed-card {
  border: 1px solid rgba(16, 185, 129, 0.28);
  box-shadow: 0 12px 26px rgba(16, 185, 129, 0.12);
}

.cancelled-card {
  border: 1px solid rgba(239, 68, 68, 0.22);
  box-shadow: 0 12px 26px rgba(239, 68, 68, 0.08);
}

.confirmed-header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #047857;
  font-weight: 700;
  margin-bottom: 14px;
  padding-bottom: 12px;
  border-bottom: 1px solid #d1fae5;
}

.cancelled-header {
  color: #b91c1c;
  border-bottom-color: #fee2e2;
}

.confirmed-item {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.confirmed-item i {
  color: #10b981;
  font-size: 18px;
  margin-top: 2px;
}

.item-label {
  margin-bottom: 4px;
  font-size: 12px;
  color: var(--gray-500);
}

.item-value {
  font-size: 14px;
  font-weight: 700;
  color: var(--gray-800);
}

.confirmed-time {
  padding-top: 12px;
  border-top: 1px dashed var(--gray-200);
  font-size: 12px;
  color: var(--gray-400);
  text-align: center;
}

.completion-status {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed var(--gray-200);
  font-size: 13px;
  line-height: 1.6;
  color: var(--gray-600);
}

@media (max-width: 1180px) {
  .chat-main {
    grid-template-columns: minmax(0, 1fr) 280px;
  }
}

@media (max-width: 1024px) {
  .chat-main {
    grid-template-columns: 1fr;
  }

  .trade-panel {
    display: none;
  }
}

@media (max-width: 720px) {
  .chat-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .chat-actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
