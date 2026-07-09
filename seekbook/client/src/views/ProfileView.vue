<template>
  <div class="profile-container">
    <ProfileSidebar :summary="profile.summary" :menu="profile.menu" :active="activeTab" @select="handleSelect" />

    <ProfileInfoPanel
      v-if="activeTab === menuLabels.info"
      :profile="profile"
      :is-logged-in="isLoggedIn"
      :saving="isSavingProfile"
      :feedback-message="profileFeedback.message"
      :feedback-type="profileFeedback.type"
      @orders="goOrders"
      @save-profile="handleSaveProfile"
    />

    <MySales v-else-if="activeTab === menuLabels.sales" :books="userBooksList" @remove="handleRemoveSale" />

    <MyFavorites
      v-else-if="activeTab === menuLabels.favorites"
      :favorites="favoriteBooks"
      :labels="bookLabels"
      @remove="handleRemoveFavorite"
      @view="viewBookDetail"
    />

    <MyShortageRegistrations
      v-else-if="activeTab === menuLabels.shortages"
      :registrations="shortageRegistrations"
      :loading="shortageLoading"
      @remove="handleRemoveShortage"
      @explore="goBuy"
    />

    <section v-else-if="activeTab === menuLabels.settings" class="profile-section settings-panel">
      <h3>账户设置</h3>

      <div class="settings-block">
        <h4>修改密码</h4>
        <form class="settings-form" @submit.prevent="handleChangePassword">
          <label class="form-group">
            <span class="form-label">当前密码</span>
            <input v-model="passwordForm.currentPassword" class="form-input" type="password" required />
          </label>
          <label class="form-group">
            <span class="form-label">新密码</span>
            <input v-model="passwordForm.newPassword" class="form-input" type="password" required minlength="8" placeholder="至少8位，含大小写字母和数字" />
          </label>
          <label class="form-group">
            <span class="form-label">确认新密码</span>
            <input v-model="passwordForm.confirmNew" class="form-input" type="password" required />
          </label>
          <div v-if="passwordFeedback.message" class="feedback" :class="passwordFeedback.type">{{ passwordFeedback.message }}</div>
          <button class="btn btn-primary" type="submit" :disabled="passwordSaving">
            {{ passwordSaving ? '保存中...' : '修改密码' }}
          </button>
        </form>
      </div>

      <div class="settings-block">
        <h4>头像设置</h4>
        <form class="settings-form" @submit.prevent="handleUpdateAvatar">
          <label class="form-group">
            <span class="form-label">头像图片链接</span>
            <input v-model="avatarUrl" class="form-input" type="url" placeholder="https://..." />
          </label>
          <div v-if="avatarPreview" class="avatar-preview">
            <img :src="avatarPreview" alt="头像预览" />
          </div>
          <div v-if="avatarFeedback.message" class="feedback" :class="avatarFeedback.type">{{ avatarFeedback.message }}</div>
          <button class="btn btn-primary" type="submit" :disabled="avatarSaving">
            {{ avatarSaving ? '保存中...' : '更新头像' }}
          </button>
        </form>
      </div>
    </section>

    <section v-else class="profile-section">
      <h3>{{ activeTab }}</h3>
      <p>{{ placeholderText }}</p>
      <button v-if="activeTab === menuLabels.orders" class="btn btn-primary" type="button" @click="goOrders">
        {{ viewAllOrdersText }}
      </button>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MyFavorites from '../components/profile/MyFavorites.vue'
import ProfileInfoPanel from '../components/profile/ProfileInfoPanel.vue'
import ProfileSidebar from '../components/profile/ProfileSidebar.vue'
import MySales from '../components/profile/MySales.vue'
import MyShortageRegistrations from '../components/profile/MyShortageRegistrations.vue'
import { useGlobalState } from '../composables/useGlobalState'
import {
  changePassword,
  deleteBook,
  deleteShortageRegistration,
  getBookDetail,
  getOrders,
  getShortageRegistrations,
  updateAvatar,
} from '../services/api'

const router = useRouter()
const route = useRoute()
const props = defineProps({
  data: { type: Object, default: () => ({}) },
})

const TAB_KEYS = {
  info: 'info',
  orders: 'orders',
  sales: 'sales',
  favorites: 'favorites',
  shortages: 'shortages',
}

const DEFAULT_MENU_TEXT = {
  info: '\u4e2a\u4eba\u4fe1\u606f',
  orders: '\u6211\u7684\u8ba2\u5355',
  sales: '\u6211\u7684\u51fa\u552e',
  favorites: '\u6211\u7684\u6536\u85cf',
  shortages: '\u6211\u7684\u7f3a\u8d27\u767b\u8bb0',
  settings: '\u8d26\u6237\u8bbe\u7f6e',
}

const { currentUser, favorites, refreshRemoteUserState, toggleFavorite, updateCurrentUserProfile, userBooks } = useGlobalState()
const activeTab = ref('')
const orders = ref([])
const isSavingProfile = ref(false)
const profileFeedback = ref({ type: '', message: '' })
const passwordForm = ref({ currentPassword: '', newPassword: '', confirmNew: '' })
const passwordSaving = ref(false)
const passwordFeedback = ref({ type: '', message: '' })
const avatarUrl = ref('')
const avatarSaving = ref(false)
const avatarFeedback = ref({ type: '', message: '' })
const favoriteBookDetails = ref({})
const shortageRegistrations = ref([])
const shortageLoading = ref(false)

const profileConfig = computed(() => props.data.profile ?? { summary: {}, menu: [], placeholders: {} })
const bookLabels = computed(() => props.data.bookDetail?.labels || {})
const currentProfileUser = computed(() => currentUser.value || {})
const isLoggedIn = computed(() => Boolean(currentProfileUser.value?.isLoggedIn && currentProfileUser.value?.id))

const profileMenu = computed(() => {
  const baseMenu = Array.isArray(profileConfig.value.menu) ? [...profileConfig.value.menu] : []
  if (!baseMenu.includes(DEFAULT_MENU_TEXT.shortages)) {
    const favoritesIndex = baseMenu.findIndex((item) => item.includes('\u6536\u85cf'))
    if (favoritesIndex >= 0) {
      baseMenu.splice(favoritesIndex + 1, 0, DEFAULT_MENU_TEXT.shortages)
    } else {
      baseMenu.push(DEFAULT_MENU_TEXT.shortages)
    }
  }
  return baseMenu
})

const menuLabels = computed(() => ({
  info: resolveMenuLabel(profileMenu.value, ['\u4e2a\u4eba', '\u4fe1\u606f'], DEFAULT_MENU_TEXT.info),
  orders: resolveMenuLabel(profileMenu.value, ['\u8ba2\u5355'], DEFAULT_MENU_TEXT.orders),
  sales: resolveMenuLabel(profileMenu.value, ['\u51fa\u552e'], DEFAULT_MENU_TEXT.sales),
  favorites: resolveMenuLabel(profileMenu.value, ['\u6536\u85cf'], DEFAULT_MENU_TEXT.favorites),
  shortages: resolveMenuLabel(profileMenu.value, ['\u7f3a\u8d27', '\u767b\u8bb0'], DEFAULT_MENU_TEXT.shortages),
  settings: resolveMenuLabel(profileMenu.value, ['\u8bbe\u7f6e'], DEFAULT_MENU_TEXT.settings),
}))

const profile = computed(() => {
  const user = currentProfileUser.value
  const displayName = isLoggedIn.value ? user.name || user.username || '\u672a\u547d\u540d\u7528\u6237' : '\u8bf7\u5148\u767b\u5f55'
  const usernameValue = isLoggedIn.value ? user.username || '\u672a\u8bbe\u7f6e' : '\u672a\u767b\u5f55'
  const secondaryLine = isLoggedIn.value
    ? [user.college, user.grade].filter(Boolean).join(' · ') || '\u767b\u5f55\u540e\u53ef\u4f5c\u4e3a\u4e70\u5bb6\u548c\u5356\u5bb6\u4f7f\u7528\u5e73\u53f0'
    : '\u767b\u5f55\u540e\u67e5\u770b\u5b8c\u6574\u8d44\u6599'

  const buyerOrders = orders.value.filter((order) => order.buyerId === user.id)
  const sellerOrders = orders.value.filter((order) => order.sellerId === user.id)
  const ratingValues = orders.value
    .filter((order) => order.status === 'completed')
    .flatMap((order) => [order.buyerRating, order.sellerRating])
    .filter((value) => typeof value === 'number' && value > 0)
  const averageRating = ratingValues.length
    ? (ratingValues.reduce((sum, value) => sum + value, 0) / ratingValues.length).toFixed(1)
    : '--'

  return {
    infoLabel: menuLabels.value.info,
    summary: {
      name: displayName,
      username: usernameValue,
      major: secondaryLine,
      reputation: `\u4fe1\u8a89\u7b49\u7ea7\uff1a${isLoggedIn.value ? user.reputation || 'A' : '--'}`,
    },
    creditScore: isLoggedIn.value ? (user.creditScore ?? 100) : 100,
    menu: profileMenu.value,
    readonlyDetails: [
      { label: '\u7528\u6237 ID', value: user.id || '\u672a\u767b\u5f55' },
      { label: '\u7528\u6237\u540d', value: usernameValue },
    ],
    editableProfile: {
      name: isLoggedIn.value ? user.name || '' : '',
      email: isLoggedIn.value ? user.email || '' : '',
      college: isLoggedIn.value ? user.college || '' : '',
      grade: isLoggedIn.value ? user.grade || '' : '',
      campus: isLoggedIn.value ? user.campus || '' : '',
      phone: isLoggedIn.value ? user.phone || '' : '',
    },
    stats: [
      { value: String(buyerOrders.length), label: '\u8d2d\u4e70\u8ba2\u5355', icon: 'fas fa-shopping-cart' },
      { value: String(sellerOrders.length), label: '\u51fa\u552e\u8ba2\u5355', icon: 'fas fa-tag' },
      { value: String(favorites.value.length), label: '\u6536\u85cf\u4e66\u7c4d', icon: 'fas fa-heart' },
      { value: averageRating, label: '\u5e73\u5747\u8bc4\u5206', icon: 'fas fa-star' },
    ],
    recentTransactions: buildRecentTransactions(user),
    placeholders: profileConfig.value.placeholders || {},
  }
})

const placeholderText = computed(() => {
  if (activeTab.value === menuLabels.value.sales) return profile.value.placeholders?.mySales || ''
  if (activeTab.value === menuLabels.value.favorites) return profile.value.placeholders?.myFavorites || ''
  return profile.value.placeholders?.accountSettings || ''
})

const viewAllOrdersText = computed(() => menuLabels.value.orders)

const favoriteBooks = computed(() => {
  const allBooks = [
    ...(props.data.books?.featured || []),
    ...(userBooks.value || []),
    ...Object.values(favoriteBookDetails.value || {}),
  ]
  const bookMap = new Map()

  allBooks.forEach((book) => {
    if (!book?.id) return
    bookMap.set(String(book.id), book)
  })

  return favorites.value
    .map((bookId) => {
      const book = bookMap.get(String(bookId))
      if (!book) {
        return { id: bookId, title: '\u672a\u77e5\u4e66\u7c4d', price: 0, image: '/images/book1.jpg' }
      }

      return {
        ...book,
        id: book.id,
        image: book.image || book.coverImage || book.img || '/images/book1.jpg',
      }
    })
    .filter(Boolean)
})

const userBooksList = computed(() => (userBooks.value || []).filter((book) => book.status !== 'draft'))

function resolveMenuLabel(menu, keywords, fallback) {
  return menu.find((item) => keywords.some((keyword) => item.includes(keyword))) || fallback
}

function formatDate(isoString) {
  if (!isoString) return '\u6682\u65e0\u8bb0\u5f55'
  const date = new Date(isoString)
  if (Number.isNaN(date.getTime())) return '\u6682\u65e0\u8bb0\u5f55'
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function buildRecentTransactions(user) {
  return orders.value.slice(0, 3).map((order) => {
    const isBuyer = order.buyerId === user.id
    const bookTitle = order.book?.title || `\u4e66\u7c4d #${order.bookId}`
    return {
      type: order.status === 'completed' ? 'success' : 'pending',
      title: `${isBuyer ? '\u8d2d\u4e70' : '\u51fa\u552e'}《${bookTitle}》`,
      date: formatDate(order.updatedAt || order.createdAt),
      amount: `¥${Number(order.finalPrice ?? order.price ?? 0).toFixed(2)}`,
      status: order.status === 'completed' ? '' : order.statusLabel,
    }
  })
}

function resolveTabByQuery(queryValue) {
  if (typeof queryValue !== 'string') return menuLabels.value.info
  return menuLabels.value[queryValue] || menuLabels.value.info
}

function syncRouteTab(tabLabel) {
  const key = Object.entries(menuLabels.value).find(([, label]) => label === tabLabel)?.[0]
  const nextQuery = { ...route.query }
  if (key && key !== TAB_KEYS.info) {
    nextQuery.tab = key
  } else {
    delete nextQuery.tab
  }

  if (nextQuery.tab === route.query.tab || (!nextQuery.tab && !route.query.tab)) {
    return
  }

  router.replace({ path: '/profile', query: nextQuery })
}

async function loadOrders() {
  if (!isLoggedIn.value) {
    orders.value = []
    return
  }

  try {
    const result = await getOrders('all')
    orders.value = result?.data || []
  } catch (error) {
    console.error('加载个人订单失败:', error)
    orders.value = []
  }
}

async function loadShortageList() {
  if (!isLoggedIn.value) {
    shortageRegistrations.value = []
    shortageLoading.value = false
    return
  }

  shortageLoading.value = true
  try {
    const result = await getShortageRegistrations()
    shortageRegistrations.value = result?.data || []
  } catch (error) {
    console.error('加载缺货登记失败:', error)
    shortageRegistrations.value = []
  } finally {
    shortageLoading.value = false
  }
}

async function loadFavoriteBookDetails() {
  if (!favorites.value.length) return

  const knownBookIds = new Set([
    ...(userBooks.value || []).map((book) => String(book.id)),
    ...Object.keys(favoriteBookDetails.value || {}),
  ])

  const missingIds = favorites.value
    .map((bookId) => String(bookId))
    .filter((bookId) => bookId && !knownBookIds.has(bookId))

  if (!missingIds.length) return

  const responses = await Promise.all(
    missingIds.map(async (bookId) => {
      try {
        const result = await getBookDetail(bookId)
        return result?.code === 200 && result.data ? [bookId, result.data] : null
      } catch (error) {
        console.error(`加载收藏书籍 ${bookId} 失败:`, error)
        return null
      }
    }),
  )

  const nextDetails = { ...favoriteBookDetails.value }
  let hasUpdates = false

  responses.forEach((entry) => {
    if (!entry) return
    const [bookId, book] = entry
    nextDetails[bookId] = book
    hasUpdates = true
  })

  if (hasUpdates) {
    favoriteBookDetails.value = nextDetails
  }
}

function setActiveTab(tabLabel) {
  activeTab.value = tabLabel
  syncRouteTab(tabLabel)
}

function handleSelect(tab) {
  if (tab === menuLabels.value.orders) {
    goOrders()
    return
  }
  setActiveTab(tab)
}

function goOrders() {
  router.push('/orders')
}

function goBuy() {
  router.push('/buy')
}

async function handleRemoveFavorite(bookId) {
  await toggleFavorite(bookId)
}

async function handleRemoveSale(book) {
  if (!book?.id || book.status !== 'on_sale') return
  const confirmed = window.confirm(`确定下架《${book.title || book.name || '这本书'}》吗？下架后将不再出现在星图集市。`)
  if (!confirmed) return

  try {
    await deleteBook(book.id)
    userBooks.value = userBooks.value.map((item) =>
      Number(item.id) === Number(book.id)
        ? { ...item, status: 'removed', updatedAt: new Date().toISOString() }
        : item,
    )
    await refreshRemoteUserState()
  } catch (error) {
    window.alert(error.message || '下架失败，请稍后重试')
  }
}

async function handleRemoveShortage(item) {
  if (!item?.id) return
  const confirmed = window.confirm(`确定取消《${item.bookName}》的缺货登记吗？`)
  if (!confirmed) return

  try {
    await deleteShortageRegistration(item.id)
    shortageRegistrations.value = shortageRegistrations.value.filter((entry) => entry.id !== item.id)
  } catch (error) {
    window.alert(error.message || '取消缺货登记失败，请稍后重试')
  }
}

function viewBookDetail(book) {
  router.push({
    path: '/book-detail',
    query: { id: book.id, source: 'catalog' },
  })
}

function mapProfileErrorMessage(error) {
  const errorMap = {
    AUTH_REQUIRED: '\u8bf7\u5148\u767b\u5f55\u540e\u518d\u4fee\u6539\u4e2a\u4eba\u4fe1\u606f\u3002',
    EMAIL_REQUIRED: '\u90ae\u7bb1\u4e0d\u80fd\u4e3a\u7a7a\u3002',
    EMAIL_INVALID: '\u90ae\u7bb1\u683c\u5f0f\u4e0d\u6b63\u786e\uff0c\u8bf7\u91cd\u65b0\u8f93\u5165\u3002',
    EMAIL_DOMAIN_INVALID: '\u5982\u679c\u4f7f\u7528\u6d59\u5927\u90ae\u7bb1\uff0c\u8bf7\u586b\u5199\u5b8c\u6574\u7684 @zju.edu.cn \u540e\u7f00\u3002',
    EMAIL_ALREADY_EXISTS: '\u8be5\u90ae\u7bb1\u5df2\u5b58\u5728\uff0c\u8bf7\u66f4\u6362\u4e00\u4e2a\u672a\u6ce8\u518c\u7684\u90ae\u7bb1\u3002',
    NAME_REQUIRED: '\u59d3\u540d\u4e0d\u80fd\u4e3a\u7a7a\u3002',
    PROFILE_UPDATE_FAILED: '\u4e2a\u4eba\u4fe1\u606f\u66f4\u65b0\u5931\u8d25\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5\u3002',
  }

  return errorMap[error?.code] || error?.message || '\u4e2a\u4eba\u4fe1\u606f\u66f4\u65b0\u5931\u8d25\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5\u3002'
}

async function handleSaveProfile(formData) {
  if (!isLoggedIn.value || isSavingProfile.value) return

  isSavingProfile.value = true
  profileFeedback.value = { type: '', message: '' }

  try {
    await updateCurrentUserProfile(formData)
    profileFeedback.value = { type: 'success', message: '\u4e2a\u4eba\u4fe1\u606f\u5df2\u4fdd\u5b58\u3002' }
  } catch (error) {
    profileFeedback.value = { type: 'error', message: mapProfileErrorMessage(error) }
  } finally {
    isSavingProfile.value = false
  }
}

function resetPasswordForm() {
  passwordForm.value = { currentPassword: '', newPassword: '', confirmNew: '' }
}

async function handleChangePassword() {
  if (passwordSaving.value) return
  passwordFeedback.value = { type: '', message: '' }

  const { currentPassword, newPassword, confirmNew } = passwordForm.value
  if (!currentPassword || !newPassword) {
    passwordFeedback.value = { type: 'error', message: '请填写当前密码和新密码。' }
    return
  }
  if (newPassword !== confirmNew) {
    passwordFeedback.value = { type: 'error', message: '两次输入的新密码不一致。' }
    return
  }
  if (newPassword.length < 8) {
    passwordFeedback.value = { type: 'error', message: '新密码至少需要8位。' }
    return
  }

  passwordSaving.value = true
  try {
    await changePassword(currentPassword, newPassword)
    passwordFeedback.value = { type: 'success', message: '密码修改成功。' }
    resetPasswordForm()
  } catch (error) {
    passwordFeedback.value = { type: 'error', message: error.message || '密码修改失败，请重试。' }
  } finally {
    passwordSaving.value = false
  }
}

async function handleUpdateAvatar() {
  if (avatarSaving.value) return
  avatarFeedback.value = { type: '', message: '' }

  if (!avatarUrl.value.trim()) {
    avatarFeedback.value = { type: 'error', message: '请输入头像图片链接。' }
    return
  }

  avatarSaving.value = true
  try {
    await updateAvatar(avatarUrl.value.trim())
    avatarFeedback.value = { type: 'success', message: '头像更新成功。' }
    avatarUrl.value = ''
  } catch (error) {
    avatarFeedback.value = { type: 'error', message: error.message || '头像更新失败，请重试。' }
  } finally {
    avatarSaving.value = false
  }
}

const avatarPreview = computed(() => {
  const url = avatarUrl.value.trim()
  if (!url) return currentProfileUser.value?.avatar || ''
  return url
})

onMounted(loadOrders)
onMounted(loadFavoriteBookDetails)
onMounted(loadShortageList)

watch(
  () => currentProfileUser.value.id,
  () => {
    profileFeedback.value = { type: '', message: '' }
    favoriteBookDetails.value = {}
    loadOrders()
    loadFavoriteBookDetails()
    loadShortageList()
  },
)

watch(
  [() => favorites.value.slice(), () => userBooks.value.length],
  () => {
    loadFavoriteBookDetails()
  },
  { deep: true },
)

watch(
  () => route.query.tab,
  (tab) => {
    activeTab.value = resolveTabByQuery(tab)
  },
  { immediate: true },
)

watch(
  () => profileMenu.value,
  () => {
    if (!activeTab.value || !profileMenu.value.includes(activeTab.value)) {
      activeTab.value = resolveTabByQuery(route.query.tab)
    }
  },
  { immediate: true },
)
</script>

<style scoped>
.profile-container {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 30px;
  margin: 10px 0 60px;
}

.profile-section {
  background-color: white;
  border-radius: 12px;
  box-shadow: var(--shadow-md);
  padding: 24px;
}

.profile-section h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--gray-900);
  margin-bottom: 20px;
}

.profile-section p {
  color: var(--gray-600);
  margin-bottom: 20px;
}

.btn-primary {
  padding: 10px 20px;
  background: var(--primary-blue);
  color: white;
  border: none;
  border-radius: 8px;
}

.settings-panel {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.settings-block h4 {
  font-size: 16px;
  font-weight: 600;
  color: var(--gray-800);
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--dashboard-subcard-border);
}

.settings-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
  max-width: 420px;
}

.settings-form .form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.settings-form .form-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--gray-700);
}

.settings-form .form-input {
  padding: 10px 12px;
  border: 1px solid var(--dashboard-subcard-border);
  border-radius: 8px;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.72);
  color: var(--gray-700);
  transition: border-color 0.2s;
}

.settings-form .form-input:focus {
  outline: none;
  border-color: var(--primary-blue);
  box-shadow: 0 0 0 3px rgba(79, 110, 247, 0.12);
}

.feedback {
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
}

.feedback.success {
  background: var(--light-green);
  color: #065f46;
}

.feedback.error {
  background: #fee2e2;
  color: #991b1b;
}

.avatar-preview {
  margin-top: 6px;
}

.avatar-preview img {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--dashboard-subcard-border);
  box-shadow: var(--shadow-sm);
}

@media (max-width: 1024px) {
  .profile-container {
    grid-template-columns: 1fr;
  }

  .settings-form {
    max-width: 100%;
  }
}
</style>
