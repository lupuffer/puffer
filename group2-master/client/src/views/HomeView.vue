<template>
  <div class="dashboard-page">
    <section class="hero-card">
      <div class="hero-aura hero-aura-one"></div>
      <div class="hero-mist" aria-hidden="true"></div>
      <div class="hero-copy">
        <h1>星辰书链：<br />灿若星辰的你，链成知识星河</h1>
        <p>让散落在校园里的二手教材与学习经验，连成一条流动的知识星链。</p>

        <div class="hero-mini-stats" :class="{ 'guest-mode': !isLoggedIn }">
          <span v-for="item in metrics" :key="item.label">
            <strong>{{ item.value }}</strong>
            {{ item.label }}
          </span>
        </div>

        <div class="hero-actions">
          <button class="primary-btn" type="button" @click="goSmartList">
            <i class="fas fa-list-check"></i>
            查看智能清单
          </button>
          <button class="ghost-btn" type="button" @click="goBuy">
            <i class="fas fa-store"></i>
            逛逛教材市场
          </button>
        </div>
      </div>
    </section>

    <section class="module-grid">
      <article class="module-card progress-module" :class="{ 'guest-mode': !isLoggedIn }">
        <div class="module-head">
          <div>
            <h2>书单进度</h2>
          </div>
          <i class="fas fa-chart-pie"></i>
        </div>
        <div class="progress-body">
          <div class="progress-ring" :style="{ '--progress': progressPercent }">
            <strong>{{ progressPercent ? progressPercent + '%' : '-' }}</strong>
            <span>已完成</span>
          </div>
          <div class="progress-lines">
            <div v-for="item in progressItems" :key="item.label">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
            </div>
          </div>
        </div>
        <div v-if="!isLoggedIn" class="guest-overlay">
          <div class="guest-hint">
            <i class="fas fa-lock"></i>
            <span>登录后查看你的教材整理进度</span>
          </div>
        </div>
      </article>

      <article class="module-card board-module" :class="{ 'guest-mode': !isLoggedIn }">
        <div class="module-head">
          <div>
            <h2>市场看板</h2>
          </div>
          <i class="fas fa-bolt"></i>
        </div>
        <div class="deal-number">
          <strong>{{ isLoggedIn ? activeOrderCount : '-' }}</strong>
          <span>笔交易进行中</span>
        </div>
        <div class="deal-status">
          <span v-for="item in boardStatus" :key="item.label">
            {{ item.label }} <strong>{{ item.value }}</strong>
          </span>
        </div>
        <div v-if="!isLoggedIn" class="guest-overlay">
          <div class="guest-hint">
            <i class="fas fa-lock"></i>
            <span>登录后查看与你相关的交易动态</span>
          </div>
        </div>
      </article>

      <article class="module-card credit-module" :class="{ 'guest-mode': !isLoggedIn }">
        <div class="module-head">
          <div>
            <h2>信誉状态</h2>
          </div>
          <i class="fas fa-shield-heart"></i>
        </div>
        <div class="credit-body">
          <div class="radar">
            <span class="ring ring-one"></span>
            <span class="ring ring-two"></span>
            <span class="ring ring-three"></span>
            <span class="axis axis-a"></span>
            <span class="axis axis-b"></span>
            <span class="axis axis-c"></span>
            <strong>{{ isLoggedIn ? creditScoreText : '-' }}</strong>
          </div>
          <div class="credit-tags">
            <span>等级 {{ creditLabel }}</span>
            <span>{{ responseTimeText }}</span>
            <span>{{ buyerRatingText }}</span>
          </div>
        </div>
        <div v-if="!isLoggedIn" class="guest-overlay">
          <div class="guest-hint">
            <i class="fas fa-lock"></i>
            <span>登录后查看你的信誉评价</span>
          </div>
        </div>
      </article>

      <article class="module-card reminder-module" :class="{ 'guest-mode': !isLoggedIn }">
        <div class="module-head">
          <div>
            <h2>心愿提醒</h2>
          </div>
          <i class="fas fa-bell"></i>
        </div>
        <div v-if="reminders.length" class="reminder-list">
          <button v-for="item in reminders" :key="item.id" type="button" @click="goBuy">
            <span>{{ item.title }}</span>
            <small>{{ item.meta }}</small>
          </button>
        </div>
        <div v-else-if="isLoggedIn" class="empty-reminders">
          <p>暂无待处理提醒</p>
          <span>浏览教材市场看看有没有心仪的教材</span>
        </div>
        <div v-if="!isLoggedIn" class="guest-overlay">
          <div class="guest-hint">
            <i class="fas fa-lock"></i>
            <span>登录后查看个性化提醒</span>
          </div>
        </div>
      </article>
    </section>

    <section class="lower-grid">
      <div class="books-panel">
        <div class="section-heading">
          <div>
            <h2>精选教材</h2>
          </div>
          <button type="button" @click="goBuy">
            查看全部 <i class="fas fa-arrow-right"></i>
          </button>
        </div>

        <div v-if="featuredBooks.length" class="book-grid">
          <BookCard
            v-for="(book, index) in featuredBooks"
            :key="book.id"
            :book="book"
            :index="index"
            class="featured-book-card"
            @select="goDetail"
          />
        </div>
        <div v-else-if="booksLoading" class="empty-section loading">
          <p>加载中...</p>
        </div>
        <div v-else class="empty-section">
          <i class="fas fa-book-open"></i>
          <p>暂无在售教材</p>
          <span>快去上架你的第一本二手教材吧</span>
        </div>
      </div>

      <aside class="knowledge-panel">
        <div class="section-heading compact">
          <div>
            <h2>知识经验推荐</h2>
          </div>
        </div>
        <article v-for="item in knowledgeRecommendations" :key="item.title" class="knowledge-item">
          <i :class="item.icon"></i>
          <div>
            <h3>{{ item.title }}</h3>
            <p>{{ item.desc }}</p>
          </div>
        </article>
        <button class="knowledge-btn" type="button" @click="goKnowledge">
          进入知识广场 <i class="fas fa-arrow-right"></i>
        </button>
      </aside>
    </section>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import BookCard from '../components/BookCard.vue'
import { normalizeCatalogImage } from '../composables/useCatalogBooks'
import { useGlobalState } from '../composables/useGlobalState'
import { loadSmartSchedule, normalizeCourseName, SMART_SCHEDULE_UPDATED_EVENT } from '../utils/smartScheduleStorage'
import {
  getBooks,
  getKnowledgeRanks,
  getMyBooks,
  getOrders,
  getShortageRegistrations,
  getUserStats,
} from '../services/api'

const router = useRouter()
const { chatSessions, currentUser } = useGlobalState()

const isLoggedIn = computed(() => Boolean(currentUser.value?.isLoggedIn && currentUser.value?.id))

const remoteBooks = ref([])
const userBooks = ref([])
const userOrders = ref([])
const shortageRegistrations = ref([])
const scheduleCourses = ref([])
const userStats = ref(null)
const booksLoading = ref(false)
const dashboardPollTimer = ref(null)
const dashboardRefreshing = ref(false)
const DASHBOARD_POLL_INTERVAL = 8000

const CONDITION_LABELS = { new: '全新', 'like-new': '九成新', good: '良好', fair: '一般' }

const getDaysAgo = (value) => {
  if (!value) return null
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return null
  return Math.max(0, Math.floor((Date.now() - date.getTime()) / 86400000))
}

const normalizeBookKey = (book) => {
  const isbn = String(book?.isbn || '').replace(/[^0-9Xx]/g, '').toUpperCase()
  if (isbn) return `isbn:${isbn}`

  const title = normalizeCourseName(book?.title)
  const edition = normalizeCourseName(book?.edition)
  if (title) return `title:${title}|edition:${edition}`

  return book?.id ? `id:${book.id}` : ''
}

const metrics = computed(() => {
  if (!isLoggedIn.value) {
    return [
      { value: '-', label: '课程数', icon: 'fas fa-graduation-cap' },
      { value: '-', label: '教材数', icon: 'fas fa-book-open' },
      { value: '-', label: '未读消息', icon: 'fas fa-bell' },
      { value: '-', label: '累计收益', icon: 'fas fa-sack-dollar' },
    ]
  }

    const purchasedKeys = new Set()
    userOrders.value
      .filter((order) => (
        order.status === 'completed'
        && (order.currentUserRole === 'buyer' || String(order.buyerId) === String(currentUser.value.id))
      ))
      .forEach((order) => {
        const key = normalizeBookKey(order.book)
        if (key) purchasedKeys.add(key)
      })
    const courseNames = new Set()
    scheduleCourses.value.forEach((course) => {
      const normalized = normalizeCourseName(course.name)
      if (normalized) courseNames.add(normalized)
    })
    const unreadMessages = chatSessions.value.reduce(
      (sum, session) => sum + Math.max(0, Number(session?.unread) || 0),
      0,
    )
    const earnings = userStats.value?.total_earnings

    return [
      { value: String(courseNames.size), label: '课程数', icon: 'fas fa-graduation-cap' },
      { value: String(purchasedKeys.size), label: '教材数', icon: 'fas fa-book-open' },
      { value: String(unreadMessages), label: '未读消息', icon: 'fas fa-bell' },
      { value: typeof earnings === 'number' ? `¥${earnings}` : '-', label: '累计收益', icon: 'fas fa-sack-dollar' },
    ]
})

const progressItems = computed(() => {
  if (!isLoggedIn.value) {
    return [
      { label: '已收集', value: '- 本' },
      { label: '流转中', value: '- 本' },
      { label: '未开始', value: '- 本' },
    ]
  }

  const onSale = userBooks.value.filter((b) => b.status === 'on_sale').length
  const reserved = userBooks.value.filter((b) => b.status === 'reserved').length
  const sold = userBooks.value.filter((b) => b.status === 'sold').length

  return [
    { label: '已收集', value: `${onSale} 本` },
    { label: '流转中', value: `${reserved} 本` },
    { label: '已完成', value: `${sold} 本` },
  ]
})

const progressPercent = computed(() => {
  if (!isLoggedIn.value || userBooks.value.length === 0) return 0
  const sold = userBooks.value.filter((b) => b.status === 'sold').length
  return Math.round((sold / Math.max(userBooks.value.length, 1)) * 100)
})

const boardStatus = computed(() => {
  if (!isLoggedIn.value) {
    return [
      { label: '新书上架', value: '-' },
      { label: '留言回复', value: '-' },
      { label: '收藏更新', value: '-' },
    ]
  }

  const created = userOrders.value.filter((o) => o.status === 'created').length
  const negotiating = userOrders.value.filter((o) => o.status === 'negotiating').length
  const confirmed = userOrders.value.filter((o) => o.status === 'confirmed').length

  return [
    { label: '待确认订单', value: created + negotiating },
    { label: '已确认面交', value: confirmed },
    { label: '已完成订单', value: userOrders.value.filter((o) => o.status === 'completed').length },
  ]
})

const activeOrderCount = computed(() => (
  isLoggedIn.value
    ? userOrders.value.filter((order) => ['created', 'negotiating', 'confirmed'].includes(order.status)).length
    : 0
))

const creditScore = computed(() => Number(userStats.value?.credit_score ?? currentUser.value?.creditScore ?? 100))
const creditScoreText = computed(() => `${creditScore.value}分`)
const creditLabel = computed(() => userStats.value?.reputation || currentUser.value?.reputation || '良好')
const responseMetrics = computed(() => userStats.value?.credit_components?.response || {})
const ratingMetrics = computed(() => userStats.value?.credit_components?.rating || {})
const responseTimeText = computed(() => {
  const sampleCount = Number(responseMetrics.value?.sampleCount || 0)
  const medianMinutes = responseMetrics.value?.medianMinutes
  if (!sampleCount || medianMinutes == null) return '响应时效 样本不足'
  if (medianMinutes < 60) return `响应 ${medianMinutes} 分钟`
  const hours = (Number(medianMinutes) / 60).toFixed(1).replace(/\.0$/, '')
  return `响应 ${hours} 小时`
})
const buyerRatingText = computed(() => {
  const ratingCount = Number(ratingMetrics.value?.ratingCount || 0)
  const averageRating = ratingMetrics.value?.averageRating
  if (!ratingCount || averageRating == null) return '买家评分 暂无'
  return `买家评分 ${averageRating} / 5`
})

const reminders = computed(() => {
  if (!isLoggedIn.value) {
    return [
      { id: 'guest-personalized', title: '登录后开启个性化教材提醒', meta: '系统会为你监控教材动态' },
      { id: 'guest-updates', title: '关注降价和上新通知', meta: '第一时间获取匹配消息' },
      { id: 'guest-community', title: '和同学交流课程经验', meta: '加入知识分享社区' },
    ]
  }

  const waiting = shortageRegistrations.value.filter((item) => item.status === 'waiting')
  if (!waiting.length) return []

  return waiting.slice(0, 3).map((item) => ({
    id: item.id,
    title: `心愿：${item.bookName}`,
    meta: item.summaryLine || '已登记，等待同学上架',
  }))
})

const featuredBooks = computed(() => {
  if (!remoteBooks.value.length) return []

  return remoteBooks.value.slice(0, 6).map((book) => ({
    ...book,
    conditionLabel: book.conditionLabel || CONDITION_LABELS[book.condition] || book.condition || '',
    image: book.coverImage || normalizeCatalogImage(book.image || book.img) || '/images/book1.jpg',
    daysAgo: getDaysAgo(book.createdAt),
  }))
})


const knowledgeRecommendations = ref([
  { title: '正在加载...', desc: '知识推荐加载中。', icon: 'fas fa-spinner' },
])

const loadKnowledgeRecommendations = async () => {
  try {
    const res = await getKnowledgeRanks({ rank_type: 'material', period: 'month' })
    if (res?.code === 200 && Array.isArray(res.data) && res.data.length) {
      knowledgeRecommendations.value = res.data.slice(0, 3).map((item, idx) => {
        const icons = ['fas fa-layer-group', 'fas fa-compass', 'fas fa-route']
        return {
          title: item.title || item.name || '热门资料',
          desc: item.description || '',
          icon: icons[idx] || 'fas fa-book-open',
        }
      })
      return
    }
  } catch {
    // fallback to static recommendations
  }
  knowledgeRecommendations.value = [
    { title: '期末复习资料包', desc: '高数、线代、概率论重点题型汇总。', icon: 'fas fa-layer-group' },
    { title: '课程经验分享', desc: '选课、教材版本和学习路线的真实建议。', icon: 'fas fa-compass' },
    { title: '教材流转指南', desc: '笔记标注、定价和当面交易流程建议。', icon: 'fas fa-route' },
  ]
}

const goSmartList = () => router.push('/smart-list')
const goBuy = () => router.push('/buy')
const goKnowledge = () => router.push('/knowledge')
const goDetail = (book) => router.push({ path: '/book-detail', query: { id: book.id } })

const loadDashboardData = async ({ initial = false } = {}) => {
  if (!isLoggedIn.value || dashboardRefreshing.value) return
  if (typeof document !== 'undefined' && document.hidden && !initial) return

  dashboardRefreshing.value = true

  const savedSchedule = loadSmartSchedule(currentUser.value.id)
  scheduleCourses.value = Array.isArray(savedSchedule?.courses) ? savedSchedule.courses : []

  try {
    const [booksResult, myBooksResult, ordersResult, shortageResult, statsResult] = await Promise.allSettled([
      getBooks({ page_size: 6, sort: 'newest' }),
      getMyBooks(),
      getOrders('all'),
      getShortageRegistrations(),
      getUserStats(),
    ])

    const booksRes = booksResult.status === 'fulfilled' ? booksResult.value : null
    const myBooksRes = myBooksResult.status === 'fulfilled' ? myBooksResult.value : null
    const ordersRes = ordersResult.status === 'fulfilled' ? ordersResult.value : null
    const shortageRes = shortageResult.status === 'fulfilled' ? shortageResult.value : null
    const statsRes = statsResult.status === 'fulfilled' ? statsResult.value : null

    if (Array.isArray(booksRes?.data?.books)) remoteBooks.value = booksRes.data.books
    if (Array.isArray(myBooksRes?.data)) userBooks.value = myBooksRes.data
    if (Array.isArray(ordersRes?.data)) userOrders.value = ordersRes.data
    if (Array.isArray(shortageRes?.data)) shortageRegistrations.value = shortageRes.data
    if (statsRes?.code === 200 && statsRes.data) userStats.value = statsRes.data
  } catch (error) {
    console.error('加载主页数据失败:', error)
  } finally {
    dashboardRefreshing.value = false
    booksLoading.value = false
  }
}

const startDashboardPolling = () => {
  if (dashboardPollTimer.value) clearInterval(dashboardPollTimer.value)
  if (!isLoggedIn.value) return
  dashboardPollTimer.value = setInterval(() => loadDashboardData(), DASHBOARD_POLL_INTERVAL)
}

const handleDashboardVisibilityChange = () => {
  if (document.hidden) return
  loadDashboardData()
  startDashboardPolling()
}

const handleSmartScheduleUpdated = (event) => {
  if (!isLoggedIn.value || String(event.detail?.userId) !== String(currentUser.value.id)) return
  const payload = event.detail?.payload || null
  scheduleCourses.value = Array.isArray(payload?.courses) ? payload.courses : []
}

onMounted(() => {
  booksLoading.value = true
  loadDashboardData({ initial: true })
  loadKnowledgeRecommendations()
  startDashboardPolling()
  document.addEventListener('visibilitychange', handleDashboardVisibilityChange)
  window.addEventListener(SMART_SCHEDULE_UPDATED_EVENT, handleSmartScheduleUpdated)
})

onBeforeUnmount(() => {
  if (dashboardPollTimer.value) clearInterval(dashboardPollTimer.value)
  document.removeEventListener('visibilitychange', handleDashboardVisibilityChange)
  window.removeEventListener(SMART_SCHEDULE_UPDATED_EVENT, handleSmartScheduleUpdated)
})
</script>

<style scoped>
.dashboard-page {
  --dash-blue: #4f6ef7;
  --dash-violet: #7c8cff;
  --dash-lavender: #a78bfa;
  --dash-periwinkle: #8b9cff;
  --dash-gold: #f6c85f;
  --dash-orange: #ffb86b;
  --dash-ink: #182033;
  --dash-muted: #64748b;
  --dash-line: var(--dashboard-card-border);
  --dash-glass: var(--dashboard-card-bg);
  --dash-glass-strong: var(--dashboard-book-card-bg);
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 1500px;
  margin: 0 auto;
}

.module-card,
.books-panel,
.knowledge-panel {
  border: 1px solid var(--dash-line);
  background: var(--dash-glass);
  box-shadow: var(--dashboard-card-shadow);
  backdrop-filter: blur(var(--dashboard-card-blur));
  -webkit-backdrop-filter: blur(var(--dashboard-card-blur));
}

.hero-mini-stats.guest-mode span {
  opacity: 0.6;
}

.hero-mini-stats.guest-mode strong {
  color: #a0aec0;
}

.module-card {
  position: relative;
  min-height: 260px;
  border-radius: 20px;
  padding: 20px;
}

.module-card.guest-mode {
  position: relative;
}

.guest-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(4px);
  border-radius: 20px;
  z-index: 10;
}

.guest-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 20px;
  text-align: center;
  color: #4f6ef7;
  font-weight: 700;
  font-size: 14px;
}

.guest-hint i {
  font-size: 28px;
  color: #4f6ef7;
  opacity: 0.8;
}

/* Empty states */
.empty-reminders,
.empty-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  margin-top: 14px;
  padding: 24px 16px;
  color: #94a3b8;
}

.empty-section i {
  font-size: 28px;
  margin-bottom: 8px;
}

.empty-reminders p,
.empty-section p {
  color: #64748b;
  font-size: 14px;
  font-weight: 700;
}

.empty-reminders span,
.empty-section span {
  color: #94a3b8;
  font-size: 12px;
}

.empty-section.loading p {
  color: #94a3b8;
}

.progress-ring[style*="--progress: 0"] {
  background:
    radial-gradient(circle closest-side, white 68%, transparent 70%),
    conic-gradient(#e2e8f0 0%, #e2e8f0 100%);
}

.hero-card {
  position: relative;
  overflow: hidden;
  min-height: 390px;
  border: none;
  border-radius: 0;
  padding: 52px 48% 46px 44px;
  background: transparent;
  box-shadow: none;
}

.hero-card::before,
.hero-card::after {
  content: none;
}

.hero-aura {
  position: absolute;
  border-radius: 999px;
  filter: blur(3px);
}

.hero-aura-one {
  width: 260px;
  height: 260px;
  right: 24%;
  bottom: -118px;
  background: radial-gradient(circle, rgba(167, 139, 250, 0.2), rgba(79, 110, 247, 0.1), transparent 70%);
}

.hero-mist {
  display: none;
}

.hero-copy {
  position: relative;
  z-index: 1;
}

.hero-copy h1 {
  max-width: 650px;
  color: #4e63dd;
  font-size: clamp(24px, 2.8vw, 40px);
  line-height: 1.14;
  font-weight: 950;
  letter-spacing: 0;
  text-shadow: 0 8px 20px rgba(87, 103, 160, 0.16);
}

.hero-copy p {
  max-width: 560px;
  margin-top: 16px;
  color: var(--dash-muted);
  font-size: 18px;
  font-weight: 700;
}

.hero-mini-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(92px, 1fr));
  gap: 10px;
  max-width: 640px;
  margin-top: 24px;
}

.hero-mini-stats span {
  padding: 12px 14px;
  border: 1px solid var(--dashboard-mini-border);
  border-radius: 16px;
  color: #718198;
  background: var(--dashboard-mini-bg);
  box-shadow: var(--dashboard-mini-shadow);
  font-size: 12px;
  font-weight: 800;
  backdrop-filter: blur(20px);
  transition: opacity 0.3s ease;
}

.hero-mini-stats strong {
  display: block;
  margin-bottom: 5px;
  color: var(--dash-blue);
  font-size: 24px;
  line-height: 1;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 26px;
}

.primary-btn,
.ghost-btn,
.section-heading button,
.knowledge-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 9px;
  border: none;
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease, background-color 0.18s ease;
}

.primary-btn,
.ghost-btn {
  min-height: 48px;
  padding: 0 20px;
  border-radius: 15px;
  font-weight: 900;
}

.primary-btn {
  color: #ffffff;
  background: linear-gradient(135deg, #2f80ed 0%, #7c8cff 58%, #a78bfa 100%);
  box-shadow: 0 18px 42px rgba(92, 75, 140, 0.22), 0 10px 28px rgba(47, 128, 237, 0.18);
}

.ghost-btn {
  color: #4f6ef7;
  background: rgba(255, 255, 255, 0.66);
  border: 1px solid rgba(255, 255, 255, 0.62);
  box-shadow: 0 14px 34px rgba(87, 103, 160, 0.1);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
}

.primary-btn:hover,
.ghost-btn:hover,
.section-heading button:hover,
.knowledge-btn:hover {
  transform: translateY(-2px);
}

.module-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.module-head,
.section-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
}

.module-head i {
  width: 42px;
  height: 42px;
  flex: 0 0 auto;
  display: grid;
  place-items: center;
  color: var(--dash-blue);
  border-radius: 15px;
  background: linear-gradient(135deg, rgba(238, 246, 255, 0.88), rgba(245, 240, 255, 0.78));
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.52);
}

.module-head h2,
.section-heading h2 {
  color: var(--dash-ink);
  font-size: 20px;
  line-height: 1.2;
}

.progress-body {
  display: grid;
  grid-template-columns: 124px 1fr;
  gap: 16px;
  align-items: center;
  margin-top: 22px;
}

.progress-ring {
  width: 118px;
  height: 118px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background:
    radial-gradient(circle closest-side, white 68%, transparent 70%),
    conic-gradient(#4f6ef7 calc(var(--progress) * 0.72%), #a78bfa calc(var(--progress) * 1%), rgba(238, 242, 255, 0.86) 0);
}

.progress-ring strong,
.progress-ring span {
  grid-area: 1 / 1;
}

.progress-ring strong {
  color: var(--dash-blue);
  font-size: 27px;
}

.progress-ring span {
  margin-top: 42px;
  color: #7c8da1;
  font-size: 11px;
  font-weight: 900;
}

.progress-lines,
.deal-status,
.reminder-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.progress-lines div,
.deal-status span {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 13px;
  color: #667995;
  border: 1px solid var(--dashboard-subcard-border);
  background: var(--dashboard-subcard-bg);
  box-shadow: var(--dashboard-subcard-shadow);
  font-size: 13px;
  font-weight: 800;
}

.progress-lines strong,
.deal-status strong {
  color: #102033;
}

.deal-number {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin: 22px 0 18px;
}

.deal-number strong {
  color: var(--dash-blue);
  font-size: 56px;
  line-height: 1;
}

.deal-number span {
  color: #667995;
  font-weight: 900;
}

.credit-body {
  margin-top: 16px;
}

.radar {
  position: relative;
  width: 142px;
  height: 142px;
  display: grid;
  place-items: center;
  margin: 0 auto 12px;
}

.ring,
.axis {
  position: absolute;
}

.ring {
  border: 1px solid rgba(124, 140, 255, 0.28);
  border-radius: 50%;
}

.ring-one {
  inset: 6px;
}

.ring-two {
  inset: 30px;
}

.ring-three {
  inset: 54px;
  background: rgba(167, 139, 250, 0.08);
}

.axis {
  width: 1px;
  height: 126px;
  background: rgba(124, 140, 255, 0.16);
}

.axis-b {
  transform: rotate(60deg);
}

.axis-c {
  transform: rotate(-60deg);
}

.radar strong {
  position: relative;
  color: var(--dash-blue);
  font-size: 35px;
}

.credit-tags {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 7px;
}

.credit-tags span {
  padding: 6px 9px;
  border-radius: 999px;
  color: #4f6ef7;
  border: 1px solid var(--dashboard-subcard-border);
  background: var(--dashboard-pill-bg-strong);
  box-shadow: var(--dashboard-subcard-shadow);
  font-size: 12px;
  font-weight: 900;
}

.reminder-list {
  margin-top: 18px;
}

.reminder-list button {
  border: 1px solid var(--dashboard-subcard-border);
  border-radius: 15px;
  background: var(--dashboard-subcard-bg);
  box-shadow: var(--dashboard-subcard-shadow);
  padding: 12px;
  text-align: left;
  cursor: pointer;
  transition: border-color 0.18s ease, transform 0.18s ease;
}

.reminder-list button:hover {
  border-color: rgba(79, 110, 247, 0.24);
  transform: translateX(2px);
}

.reminder-list span {
  display: block;
  color: var(--dash-ink);
  font-size: 14px;
  font-weight: 900;
}

.reminder-list small {
  display: block;
  margin-top: 4px;
  color: #718198;
  font-size: 12px;
  font-weight: 800;
}

.lower-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 330px;
  gap: 16px;
}

.books-panel,
.knowledge-panel {
  border-radius: 22px;
  padding: 22px;
}

.section-heading {
  margin-bottom: 18px;
}

.section-heading.compact {
  margin-bottom: 14px;
}

.section-heading button,
.knowledge-btn {
  min-height: 38px;
  padding: 0 13px;
  border-radius: 999px;
  color: #4f6ef7;
  border: 1px solid var(--dashboard-subcard-border);
  background: var(--dashboard-pill-bg);
  box-shadow: var(--dashboard-subcard-shadow);
  font-weight: 900;
}

.book-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 15px;
}

.featured-book-card {
  border: 1px solid var(--dashboard-book-card-border);
  border-radius: 18px;
  background: var(--dashboard-book-card-bg);
  box-shadow: var(--dashboard-book-card-shadow);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}

.featured-book-card:hover {
  box-shadow: var(--dashboard-book-card-shadow-hover);
}


.knowledge-panel {
  align-self: start;
}

.knowledge-item {
  display: flex;
  gap: 12px;
  padding: 14px;
  border-radius: 16px;
  border: 1px solid var(--dashboard-subcard-border);
  background: var(--dashboard-subcard-bg);
  box-shadow: var(--dashboard-subcard-shadow);
}

.knowledge-item + .knowledge-item {
  margin-top: 10px;
}

.knowledge-item i {
  width: 38px;
  height: 38px;
  flex: 0 0 auto;
  display: grid;
  place-items: center;
  color: var(--dash-blue);
  border-radius: 13px;
  border: 1px solid var(--dashboard-mini-border);
  background: rgba(255, 255, 255, 0.76);
  box-shadow: var(--dashboard-mini-shadow);
}

.knowledge-item h3 {
  color: var(--dash-ink);
  font-size: 14px;
}

.knowledge-item p {
  margin-top: 4px;
  color: #667995;
  font-size: 12px;
  line-height: 1.5;
}

.knowledge-btn {
  width: 100%;
  margin-top: 16px;
}

@media (max-width: 1320px) {
  .hero-card {
    padding-right: 40%;
  }

  .module-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .lower-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 980px) {
  .book-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .dashboard-page {
    gap: 16px;
  }

  .hero-card {
    padding: 24px;
  }

  .hero-mini-stats,
  .module-grid,
  .book-grid {
    grid-template-columns: 1fr;
  }

  .progress-body {
    grid-template-columns: 1fr;
    justify-items: center;
  }

  .guest-overlay {
    position: relative;
    inset: auto;
    margin-top: 16px;
    background: rgba(79, 110, 247, 0.05);
    backdrop-filter: none;
  }
}
</style>
