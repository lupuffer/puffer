<template>
  <OrdersHeader :hero="hero" />
  <OrdersFilter
    :tabs="filterTabs"
    :secondary-tabs="roleTabs"
    :active-key="activeFilter"
    :secondary-active-key="activeRoleFilter"
    :search-value="searchKeyword"
    :placeholder="searchPlaceholder"
    @filter="handleFilter"
    @secondary-filter="handleRoleFilter"
    @search="handleSearch"
  />
  <OrdersList
    :sections="visibleSections"
    :orders="filteredOrders"
    :loading="loading"
    :empty-text="emptyText"
    @action="handleOrderAction"
  />
  <RatingModal
    :visible="ratingModalVisible"
    :order-id="ratingTargetOrderId"
    :key="ratingResetKey"
    @close="ratingModalVisible = false; ratingResetKey++"
    @submit="handleRateSubmit"
  />
  <OrderStatusInfo :items="statusInfo" />
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import OrderStatusInfo from '../components/orders/OrderStatusInfo.vue'
import OrdersFilter from '../components/orders/OrdersFilter.vue'
import OrdersHeader from '../components/orders/OrdersHeader.vue'
import OrdersList from '../components/orders/OrdersList.vue'
import { useGlobalState } from '../composables/useGlobalState'
import { cancelOrder, completeOrder, getOrders, rateOrder } from '../services/api'
import RatingModal from '../components/orders/RatingModal.vue'

const props = defineProps({
  data: { type: Object, default: () => ({}) },
})

const ACTION_VIEW_BOOK = '查看书籍'
const ACTION_VIEW_CONVERSATION = '查看沟通记录'
const ACTION_VIEW_MEET_INFO = '查看见面信息'
const ACTION_CONTINUE_CHAT = '继续沟通'
const ACTION_COMPLETE_ORDER = '完成订单'
const ACTION_CANCEL_ORDER = '取消订单'
const ACTION_RATE_ORDER = '去评价'

const router = useRouter()
const { currentUser, chatSessions, getOrCreateSession } = useGlobalState()
const loading = ref(false)
const searchKeyword = ref('')
const activeFilter = ref('all')
const activeRoleFilter = ref('all')
const orders = ref([])
const ratingModalVisible = ref(false)
const ratingTargetOrderId = ref('')
const ratingResetKey = ref(0)

const orderConfig = computed(() => props.data.orders ?? {})
const searchPlaceholder = computed(
  () => orderConfig.value.searchPlaceholder || '搜索订单号、书名或交易对象',
)

const filterTabs = [
  { key: 'all', label: '全部订单' },
  { key: 'pending', label: '进行中' },
  { key: 'completed', label: '已完成' },
  { key: 'cancelled', label: '已取消' },
]

const roleTabs = [
  { key: 'all', label: '全部' },
  { key: 'seller', label: '售出' },
  { key: 'buyer', label: '买到' },
]

const sections = [
  { key: 'pending', title: '进行中的订单', icon: 'fas fa-spinner', emptyText: '暂无进行中的订单' },
  { key: 'completed', title: '已完成订单', icon: 'fas fa-check-circle', emptyText: '暂无已完成订单' },
  { key: 'cancelled', title: '已取消订单', icon: 'fas fa-times-circle', emptyText: '暂无已取消订单' },
]

const statusInfo = [
  { title: '待沟通', description: '订单刚创建，双方可以继续确认交易细节。', icon: 'fas fa-comments' },
  { title: '待见面', description: '交易时间和地点已经确认，等待线下完成交付。', icon: 'fas fa-handshake' },
  { title: '已完成', description: '交易已经结束，这里会保留完整记录。', icon: 'fas fa-circle-check' },
  { title: '已取消', description: '订单已经关闭，不会再继续推进。', icon: 'fas fa-ban' },
]

const formatDateTime = (value) => {
  if (!value) return '暂无时间'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return String(value)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

const buildActions = (order) => {
  if (order.status === 'created' || order.status === 'negotiating') {
    return [ACTION_VIEW_BOOK, ACTION_CONTINUE_CHAT, ACTION_CANCEL_ORDER]
  }

  if (order.status === 'confirmed') {
    const actions = [ACTION_VIEW_MEET_INFO, ACTION_CONTINUE_CHAT]
    if (order.canCompleteOrder) actions.push(ACTION_COMPLETE_ORDER)
    actions.push(ACTION_CANCEL_ORDER)
    return actions
  }

  if (order.status === 'completed') {
    const actions = [ACTION_VIEW_CONVERSATION]
    const rated = order.currentUserRole === 'buyer' ? order.buyerRating : order.sellerRating
    if (!rated) actions.push(ACTION_RATE_ORDER)
    return actions
  }

  return [ACTION_VIEW_CONVERSATION]
}

const normalizeOrder = (order) => {
  const book = order.book || {}
  const partner = order.partner || {}
  const partnerRoleText = order.partnerRole === 'seller' ? '卖家' : '买家'
  const resolvedPrice = Number(order.finalPrice ?? 0) > 0
    ? Number(order.finalPrice)
    : Number(order.price ?? 0) > 0
      ? Number(order.price)
      : Number(book.price ?? 0)

  return {
    id: order.id,
    orderNo: order.id,
    bookId: order.bookId,
    buyerId: order.buyerId,
    sellerId: order.sellerId,
    status: order.status,
    statusText: order.statusLabel || '未知状态',
    createdAt: formatDateTime(order.createdAt),
    updatedAt: formatDateTime(order.updatedAt),
    completedAt: formatDateTime(order.completedAt),
    bookTitle: book.title || `书籍 #${order.bookId}`,
    bookAuthor: book.author || '未知作者',
    bookImage: book.coverImage || book.image || book.img || '/images/book1.jpg',
    isbn: book.isbn || '暂无',
    price: resolvedPrice,
    tradeMethod: order.tradeMethodLabel || '未设置',
    campus: book.campusLabel || order.campus || '未设置',
    partner: partner.name || `${partnerRoleText}未设置`,
    partnerId: partner.id || '',
    partnerRole: partnerRoleText,
    partnerReputation: partner.reputation || 'A',
    partnerCreditScore: order.partnerCreditScore || partner.creditScore || 100,
    buyerRating: order.buyerRating,
    sellerRating: order.sellerRating,
    currentUserRole: order.currentUserRole || '',
    meetTime: order.meetTime || '',
    meetPlace: order.meetPlace || '',
    buyerCompletedConfirmed: Boolean(order.buyerCompletedConfirmed),
    sellerCompletedConfirmed: Boolean(order.sellerCompletedConfirmed),
    currentUserCompletionConfirmed: Boolean(order.currentUserCompletionConfirmed),
    partnerCompletionConfirmed: Boolean(order.partnerCompletionConfirmed),
    canCompleteOrder: Boolean(order.canCompleteOrder),
    actions: buildActions(order),
  }
}

const loadOrders = async () => {
  if (!currentUser.value?.isLoggedIn || !currentUser.value?.id) {
    orders.value = []
    return
  }

  loading.value = true
  try {
    const result = await getOrders('all')
    orders.value = (result?.data || []).map(normalizeOrder)
  } catch (error) {
    console.error('加载订单失败:', error)
    orders.value = []
  } finally {
    loading.value = false
  }
}

const filteredOrders = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase()

  return orders.value.filter((order) => {
    if (activeRoleFilter.value === 'seller' && order.currentUserRole !== 'seller') {
      return false
    }
    if (activeRoleFilter.value === 'buyer' && order.currentUserRole !== 'buyer') {
      return false
    }

    if (activeFilter.value === 'pending' && !['created', 'negotiating', 'confirmed'].includes(order.status)) {
      return false
    }
    if (activeFilter.value === 'completed' && order.status !== 'completed') {
      return false
    }
    if (activeFilter.value === 'cancelled' && order.status !== 'cancelled') {
      return false
    }

    if (!keyword) return true

    return [order.orderNo, order.bookTitle, order.bookAuthor, order.partner, order.isbn]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
      .includes(keyword)
  })
})

const visibleSections = computed(() => {
  if (activeFilter.value === 'pending') return sections.filter((section) => section.key === 'pending')
  if (activeFilter.value === 'completed') return sections.filter((section) => section.key === 'completed')
  if (activeFilter.value === 'cancelled') return sections.filter((section) => section.key === 'cancelled')
  return sections
})

const hero = computed(() => {
  const total = orders.value.length
  const pendingCount = orders.value.filter((order) => ['created', 'negotiating', 'confirmed'].includes(order.status)).length
  const completedCount = orders.value.filter((order) => order.status === 'completed').length
  const completionRate = total ? `${Math.round((completedCount / total) * 100)}%` : '0%'

  return {
    title: orderConfig.value.hero?.title || '我的订单',
    description: '',
    stats: [
      { value: String(pendingCount), label: '进行中', icon: 'fas fa-clock' },
      { value: String(completedCount), label: '已完成', icon: 'fas fa-check-circle' },
      { value: String(total), label: '全部订单', icon: 'fas fa-receipt' },
      { value: completionRate, label: '完成率', icon: 'fas fa-chart-line' },
    ],
  }
})

const emptyText = computed(() => {
  if (!currentUser.value?.isLoggedIn) return '登录后查看你自己的订单记录'
  if (searchKeyword.value.trim()) return '没有匹配当前搜索条件的订单'
  if (activeRoleFilter.value === 'seller' && activeFilter.value === 'all') return '你当前没有售出类订单'
  if (activeRoleFilter.value === 'buyer' && activeFilter.value === 'all') return '你当前没有买到类订单'
  if (activeFilter.value === 'pending') return '你当前没有进行中的订单'
  if (activeFilter.value === 'completed') return '你当前没有已完成订单'
  if (activeFilter.value === 'cancelled') return '你当前没有已取消订单'
  return '你当前还没有任何订单'
})

const handleFilter = (key) => {
  activeFilter.value = key
}

const handleRoleFilter = (key) => {
  activeRoleFilter.value = key
}

const handleSearch = (value) => {
  searchKeyword.value = value
}

const openOrderBookDetail = (order) => {
  router.push({
    path: '/book-detail',
    query: { id: order.bookId, source: 'orders' },
  })
}

const openOrderConversation = async (order, { silent = false } = {}) => {
  if (!currentUser.value?.id) return false

  const existingSession = chatSessions.value.find(
    (session) =>
      String(session.bookId) === String(order.bookId) &&
      String(session.buyerId) === String(order.buyerId) &&
      String(session.sellerId) === String(order.sellerId),
  )

  if (existingSession?.id) {
    router.push({ path: '/messages', query: { sessionId: existingSession.id } })
    return true
  }

  const session = await getOrCreateSession(
    order.bookId,
    order.sellerId,
    order.partner,
    order.bookTitle,
    { buyerId: order.buyerId },
  )

  if (session?.id) {
    router.push({ path: '/messages', query: { sessionId: session.id } })
    return true
  }

  if (!silent) {
    window.alert('暂时无法打开这笔订单的聊天会话，请稍后重试。')
  }

  return false
}

const handleCompleteOrder = async (order) => {
  if (!window.confirm(`确认将订单 ${order.orderNo} 标记为已完成吗？`)) return

  try {
    const result = await completeOrder(order.id)
    await loadOrders()
    window.alert(result?.message || '操作成功。')
  } catch (error) {
    window.alert(error.message || '完成订单失败，请稍后重试。')
  }
}

const handleRateSubmit = async ({ orderId, rating, comment }) => {
  try {
    const result = await rateOrder(orderId, rating, comment)
    window.alert(result?.message || '评价成功！')
    ratingResetKey.value++
    ratingModalVisible.value = false
    await loadOrders()
  } catch (error) {
    window.alert(error.message || '评价提交失败')
    ratingResetKey.value++
    setTimeout(() => { ratingModalVisible.value = true }, 100)
  }
}

const handleCancelOrder = async (order) => {
  if (!window.confirm(`确认取消订单 ${order.orderNo} 吗？`)) return

  try {
    await cancelOrder(order.id)
    await loadOrders()
    window.alert('订单已取消。')
  } catch (error) {
    window.alert(error.message || '取消订单失败，请稍后重试。')
  }
}

const handleOrderAction = async ({ order, action }) => {
  if (action === ACTION_VIEW_BOOK) {
    openOrderBookDetail(order)
    return
  }

  if (action === ACTION_VIEW_CONVERSATION) {
    const opened = await openOrderConversation(order, { silent: true })
    if (!opened) {
      openOrderBookDetail(order)
    }
    return
  }

  if (action === ACTION_VIEW_MEET_INFO || action === ACTION_CONTINUE_CHAT) {
    await openOrderConversation(order)
    return
  }

  if (action === ACTION_COMPLETE_ORDER) {
    await handleCompleteOrder(order)
    return
  }

  if (action === ACTION_CANCEL_ORDER) {
    await handleCancelOrder(order)
    return
  }

  if (action === ACTION_RATE_ORDER) {
    ratingTargetOrderId.value = order.id
    ratingModalVisible.value = true
  }
}

onMounted(loadOrders)

watch(
  () => currentUser.value.id,
  () => {
    loadOrders()
  },
)
</script>

<style scoped>
</style>
