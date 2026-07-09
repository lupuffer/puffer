<template>
  <div class="knowledge-page">
    <section class="hero-card">
      <div class="hero-copy">
        <h1>共享学习资料，让你的知识经验在星河中流转。</h1>
        <p class="subtitle">在这里共享课程资料、复习笔记、学习经验与校园知识资源。</p>
      </div>
    </section>

    <div class="page-grid">
      <aside class="left-column">
        <div class="left-stack">
          <UserPointsCard
            :user="currentUser"
            :points="points"
            :checked-in="checkedInToday"
            :checking-in="checkinSubmitting"
            :max-points="POINTS_MAX"
            :shortcuts="shortcutItems"
            :active-shortcut-key="activeMineView"
            @checkin="handleCheckinSafe"
            @shortcut="handleShortcut"
          />

          <section class="side-card">
            <div class="side-card-head">
              <h3>我的贡献</h3>
              <span v-if="overviewLoading" class="side-card-badge">同步中</span>
            </div>
            <div class="contribution-list">
              <div class="contribution-item">
                <span>资料</span>
                <strong>{{ contributionStats.materials }}</strong>
              </div>
              <div class="contribution-item">
                <span>讨论</span>
                <strong>{{ contributionStats.discussions }}</strong>
              </div>
              <div class="contribution-item">
                <span>评论</span>
                <strong>{{ contributionStats.comments }}</strong>
              </div>
              <div class="contribution-item">
                <span>获赞</span>
                <strong>{{ contributionStats.likes }}</strong>
              </div>
            </div>
          </section>

          <section class="side-card side-card--slim">
            <div class="side-card-head">
              <h3>积分规则</h3>
            </div>
            <div class="rules-list">
              <p>签到 +5 / 天</p>
              <p>上传资料 +10</p>
              <p>积分上限 100</p>
              <p>积分资料下载后永久可用</p>
            </div>
          </section>
        </div>
      </aside>

      <section class="main-column">
        <section v-if="activeMineView" class="tabs-shell mine-shell">
          <div class="mine-head">
            <div class="mine-copy">
              <span class="mine-kicker">我的空间</span>
              <h2>{{ currentMineConfig.title }}</h2>
              <p>{{ mineSummaryText }}</p>
            </div>
            <button type="button" class="back-btn" @click="clearMineView">返回知识星河</button>
          </div>

          <div class="mine-toolbar">
            <div class="mine-tabs">
              <button
                v-for="item in shortcutItems"
                :key="item.key"
                type="button"
                class="mine-tab-btn"
                :class="{ active: activeMineView === item.key }"
                @click="switchMineView(item.key)"
              >
                <i :class="item.icon"></i>
                <span>{{ item.label }}</span>
              </button>
            </div>
            <span v-if="mineSourceTag" class="mine-source-badge">{{ mineSourceTag }}</span>
          </div>

          <div v-if="mineLoading" class="state-panel">
            <i class="fas fa-spinner fa-spin"></i>
            <p>正在加载{{ currentMineConfig.title }}...</p>
          </div>

          <div v-else-if="mineError" class="state-panel state-panel--error">
            <i class="fas fa-circle-exclamation"></i>
            <p>{{ mineError }}</p>
            <button type="button" class="retry-btn" @click="loadMineRecords">重新加载</button>
          </div>

          <DiscussionList
            v-else-if="activeMineView === 'discussions'"
            :discussions="mineDiscussions"
            :is-liked="(id) => isDiscussionLiked(id, currentUser)"
            :format-relative-time="formatRelativeTime"
            :empty-text="currentMineConfig.emptyText"
            show-delete
            @like="handleDiscussionLike"
            @delete="handleDiscussionDelete"
            @create="openDiscussionDialog"
          />

          <MaterialList
            v-else
            :materials="mineMaterials"
            :empty-text="currentMineConfig.emptyText"
            :is-liked="(id) => isMaterialLiked(id, currentUser)"
            :is-favorited="(id) => isMaterialFavorited(id, currentUser)"
            :format-price="formatPrice"
            :format-relative-time="formatRelativeTime"
            :show-delete="activeMineView === 'uploads'"
            @like="handleMaterialLike"
            @favorite="handleMaterialFavorite"
            @delete="handleMaterialDelete"
          />

          <KnowledgePagination
            v-if="mineTotalPages > 1"
            :current-page="minePage"
            :total-pages="mineTotalPages"
            @change="(page) => (minePage = page)"
          />
        </section>

        <div v-else class="tabs-shell">
          <div class="top-tabs">
            <button
              v-for="tab in topTabs"
              :key="tab.value"
              type="button"
              class="tab-btn"
              :class="{ active: activeTab === tab.value }"
              @click="activeTab = tab.value"
            >
              {{ tab.label }}
            </button>
          </div>

          <div v-if="activeTab === 'materials'" class="panel-shell">
            <div class="filter-row">
              <div class="chips">
                <button
                  v-for="category in MATERIAL_CATEGORIES"
                  :key="category"
                  type="button"
                  class="chip-btn"
                  :class="{ active: activeMaterialCategory === category }"
                  @click="activeMaterialCategory = category"
                >
                  {{ category }}
                </button>
              </div>
              <div class="sorts">
                <button
                  v-for="sort in MATERIAL_SORTS"
                  :key="sort"
                  type="button"
                  class="sort-btn"
                  :class="{ active: activeMaterialSort === sort }"
                  @click="activeMaterialSort = sort"
                >
                  {{ sort }}
                </button>
              </div>
            </div>

            <p v-if="rawSearchKeyword" class="search-tip">搜索结果：{{ rawSearchKeyword }}</p>

            <MaterialList
              :materials="pagedMaterials"
              :empty-text="materialEmptyText"
              :is-liked="(id) => isMaterialLiked(id, currentUser)"
              :is-favorited="(id) => isMaterialFavorited(id, currentUser)"
              :format-price="formatPrice"
              :format-relative-time="formatRelativeTime"
              @like="handleMaterialLike"
              @favorite="handleMaterialFavorite"
            />

            <KnowledgePagination
              :current-page="materialPage"
              :total-pages="materialTotalPages"
              @change="(page) => (materialPage = page)"
            />
          </div>

          <div v-else class="panel-shell">
            <div class="filter-row">
              <div class="discussion-toolbar">
                <div class="chips">
                  <button
                    v-for="type in DISCUSSION_TYPES"
                    :key="type"
                    type="button"
                    class="chip-btn"
                    :class="{ active: activeDiscussionType === type }"
                    @click="activeDiscussionType = type"
                  >
                    {{ type }}
                  </button>
                </div>
                <button type="button" class="inline-create-btn" @click="openDiscussionDialog">发讨论</button>
              </div>
              <div class="sorts">
                <button
                  v-for="sort in DISCUSSION_SORTS"
                  :key="sort"
                  type="button"
                  class="sort-btn"
                  :class="{ active: activeDiscussionSort === sort }"
                  @click="activeDiscussionSort = sort"
                >
                  {{ sort }}
                </button>
              </div>
            </div>

            <p v-if="rawSearchKeyword" class="search-tip">搜索结果：{{ rawSearchKeyword }}</p>

            <DiscussionList
              :discussions="pagedDiscussions"
              :is-liked="(id) => isDiscussionLiked(id, currentUser)"
              :format-relative-time="formatRelativeTime"
              :empty-text="discussionEmptyText"
              @like="handleDiscussionLike"
              @create="openDiscussionDialog"
            />

            <KnowledgePagination
              :current-page="discussionPage"
              :total-pages="discussionTotalPages"
              @change="(page) => (discussionPage = page)"
            />
          </div>
        </div>
      </section>

      <RankingPanel
        class="right-column"
        :hot-materials="rankingMaterials"
        :hot-discussions="rankingDiscussions"
        :format-price="formatPrice"
      />
    </div>

    <PublishMaterialDialog
      ref="materialDialogRef"
      :open="materialDialogOpen"
      :submitting="materialSubmitting"
      @close="materialDialogOpen = false"
      @submit="handleMaterialSubmit"
    />
    <PublishDiscussionDialog
      ref="discussionDialogRef"
      :open="discussionDialogOpen"
      :submitting="discussionSubmitting"
      @close="discussionDialogOpen = false"
      @submit="handleDiscussionSubmit"
    />
    <KnowledgeConfirmDialog
      :open="confirmState.open"
      :title="confirmState.title"
      :message="confirmState.message"
      :confirm-text="confirmState.confirmText"
      :cancel-text="confirmState.cancelText"
      @confirm="acceptConfirm"
      @cancel="cancelConfirm"
    />
    <KnowledgeToastStack :toasts="toasts" />
  </div>
</template>

<script setup>
import { computed, inject, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DiscussionList from './DiscussionList.vue'
import KnowledgeConfirmDialog from './KnowledgeConfirmDialog.vue'
import KnowledgePagination from './KnowledgePagination.vue'
import KnowledgeToastStack from './KnowledgeToastStack.vue'
import MaterialList from './MaterialList.vue'
import PublishDiscussionDialog from './PublishDiscussionDialog.vue'
import PublishMaterialDialog from './PublishMaterialDialog.vue'
import RankingPanel from './RankingPanel.vue'
import UserPointsCard from './UserPointsCard.vue'
import {
  DISCUSSION_SORTS,
  DISCUSSION_TYPES,
  MATERIAL_CATEGORIES,
  MATERIAL_SORTS,
  useKnowledgeGalaxy,
} from '@/composables/useKnowledgeGalaxy'
import { resolveBackendDiscussionByRecord, resolveBackendMaterialByRecord } from '@/composables/useKnowledgeBackendSync'
import { useKnowledgeFeedback } from '@/composables/useKnowledgeFeedback'
import {
  checkinKnowledge,
  createKnowledgeDiscussion as createKnowledgeDiscussionApi,
  createKnowledgeMaterial as createKnowledgeMaterialApi,
  deleteKnowledgeDiscussion,
  deleteKnowledgeMaterial,
  downloadMaterial,
  getKnowledgeMaterials,
  getKnowledgeOverview,
  getMyKnowledgeDiscussions,
  getMyKnowledgeFavorites,
  getMyKnowledgeRedeems,
  getMyKnowledgeUploads,
  toggleKnowledgeDiscussionLike,
  toggleKnowledgeFavorite,
  toggleKnowledgeMaterialLike,
} from '@/services/api'

const pageSize = 6
const router = useRouter()
const route = useRoute()
const appData = inject('appData', { value: {} })

const {
  POINTS_MAX,
  materials,
  discussions,
  comments,
  rankingMaterials,
  rankingDiscussions,
  getPoints,
  isCheckedInToday,
  createMaterial,
  createDiscussion,
  deleteMaterial,
  deleteDiscussion,
  toggleMaterialLike,
  toggleDiscussionLike,
  toggleMaterialFavorite,
  isMaterialLiked,
  isDiscussionLiked,
  isMaterialFavorited,
  isMaterialEntitled,
  filterDiscussions,
  formatPrice,
  formatRelativeTime,
  checkIn,
} = useKnowledgeGalaxy()

const { toasts, confirmState, showToast, requestConfirm, acceptConfirm, cancelConfirm } = useKnowledgeFeedback()

const shortcutItems = [
  { key: 'uploads', label: '我的上传', icon: 'fas fa-cloud-upload-alt' },
  { key: 'discussions', label: '我的讨论', icon: 'far fa-comments' },
  { key: 'favorites', label: '我的收藏', icon: 'far fa-bookmark' },
  { key: 'redeems', label: '我的兑换', icon: 'fas fa-gift' },
]

const mineViewConfigMap = {
  uploads: {
    title: '我的上传',
    emptyText: '你还没有上传任何资料，先分享第一份学习资料吧。',
    loader: getMyKnowledgeUploads,
  },
  discussions: {
    title: '我的讨论',
    emptyText: '你还没有发布任何讨论，去发起一个话题吧。',
    loader: getMyKnowledgeDiscussions,
  },
  favorites: {
    title: '我的收藏',
    emptyText: '你还没有收藏任何资料。',
    loader: getMyKnowledgeFavorites,
  },
  redeems: {
    title: '我的兑换',
    emptyText: '你还没有获得任何积分资料。',
    loader: getMyKnowledgeRedeems,
  },
}

const topTabs = [
  { label: '学习资料', value: 'materials' },
  { label: '星河讨论', value: 'discussions' },
]

const materialDialogOpen = ref(false)
const discussionDialogOpen = ref(false)
const materialSubmitting = ref(false)
const discussionSubmitting = ref(false)
const materialDialogRef = ref(null)
const discussionDialogRef = ref(null)
const materialPage = ref(1)
const discussionPage = ref(1)
const minePage = ref(1)
const mineRecords = ref([])
const mineTotal = ref(0)
const mineTotalPages = ref(1)
const mineLoading = ref(false)
const mineError = ref('')
const mineSource = ref('backend')
const overviewLoading = ref(false)
const backendOverview = ref(null)
const checkinSubmitting = ref(false)
const syncState = ref({
  running: false,
  finishedFor: '',
})

const activeTab = ref(route.query.tab === 'discussion' ? 'discussions' : 'materials')
const activeMaterialCategory = ref('全部')
const activeMaterialSort = ref('最新上传')
const activeDiscussionType = ref('全部')
const activeDiscussionSort = ref('最新发布')

const currentUser = computed(() => appData.value?.appState?.user || {})
const points = computed(() => {
  if (currentUser.value?.isLoggedIn && backendOverview.value?.pointsBalance !== undefined) {
    return backendOverview.value.pointsBalance || 0
  }
  return getPoints(currentUser.value)
})
const checkedInToday = computed(() => {
  if (currentUser.value?.isLoggedIn && backendOverview.value?.checkedInToday !== undefined) {
    return Boolean(backendOverview.value.checkedInToday)
  }
  return isCheckedInToday(currentUser.value)
})
const rawSearchKeyword = computed(() => String(route.query.search || '').trim())
const searchKeyword = computed(() => rawSearchKeyword.value.toLowerCase())
const currentUserId = computed(() => {
  if (!currentUser.value?.isLoggedIn) {
    return ''
  }
  return String(currentUser.value.id || currentUser.value.email || currentUser.value.name || '')
})

const normalizeMineKey = (value) => {
  const normalized = String(value || '').trim().toLowerCase()
  if (normalized === 'redeem') {
    return 'redeems'
  }
  return Object.prototype.hasOwnProperty.call(mineViewConfigMap, normalized) ? normalized : ''
}

const activeMineView = computed(() => normalizeMineKey(route.query.mine))
const currentMineConfig = computed(() => {
  const key = activeMineView.value || 'uploads'
  return mineViewConfigMap[key]
})
const mineMaterials = computed(() => (activeMineView.value === 'discussions' ? [] : mineRecords.value))
const mineDiscussions = computed(() => (activeMineView.value === 'discussions' ? mineRecords.value : []))
const mineSourceTag = computed(() => {
  if (mineLoading.value || mineError.value || !activeMineView.value) {
    return ''
  }
  return mineSource.value === 'local' ? '本地记录' : '后端记录'
})
const mineSummaryText = computed(() => {
  if (mineLoading.value) {
    return '正在同步你的最新记录。'
  }
  return `当前共 ${mineTotal.value} 条记录`
})

const sortByCreatedAtDesc = (list) =>
  [...list].sort((a, b) => new Date(b.createdAt || b.updatedAt || 0) - new Date(a.createdAt || a.updatedAt || 0))

const makeMaterialSignature = (item) =>
  [
    String(item.title || '').trim(),
    String(item.course || item.courseName || '').trim(),
    String(item.category || '').trim(),
    String(item.description || '').trim(),
  ].join('::')

const makeDiscussionSignature = (item) =>
  [
    String(item.title || '').trim(),
    String(item.type || '').trim(),
    String(item.content || '').trim(),
  ].join('::')

const getLocalMineRecords = (viewKey) => {
  const userId = currentUserId.value
  if (!userId) {
    return []
  }

  if (viewKey === 'uploads') {
    return sortByCreatedAtDesc(materials.value.filter((item) => String(item.authorId) === userId))
  }

  if (viewKey === 'discussions') {
    return sortByCreatedAtDesc(discussions.value.filter((item) => String(item.authorId) === userId))
  }

  if (viewKey === 'favorites') {
    return sortByCreatedAtDesc(materials.value.filter((item) => isMaterialFavorited(item.id, currentUser.value)))
  }

  if (viewKey === 'redeems') {
    return sortByCreatedAtDesc(materials.value.filter((item) => isMaterialEntitled(item.id, currentUser.value)))
  }

  return []
}

const fetchAllPages = async (loader, params = {}) => {
  const allItems = []
  let page = 1
  let totalPages = 1

  while (page <= totalPages) {
    const response = await loader({
      ...params,
      page,
      page_size: 50,
    })
    const data = response?.data || {}
    allItems.push(...(data.items || []))
    totalPages = Math.max(1, Number(data.totalPages || 1))
    page += 1
  }

  return allItems
}

const matchesSearch = (target) => {
  if (!searchKeyword.value) {
    return true
  }

  const haystack = [
    target.title,
    target.description,
    target.content,
    target.course,
    target.authorName,
    ...(target.tags || []),
  ]
    .filter(Boolean)
    .join(' ')
    .toLowerCase()

  return haystack.includes(searchKeyword.value)
}

const filteredMaterials = computed(() => {
  let list = materials.value.filter((item) => matchesSearch(item))

  if (activeMaterialCategory.value !== '全部') {
    list = list.filter((item) => item.category === activeMaterialCategory.value)
  }

  if (activeMaterialSort.value === '最新上传') {
    list = [...list].sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
  } else if (activeMaterialSort.value === '最多下载') {
    list = [...list].sort((a, b) => (b.downloads || 0) - (a.downloads || 0))
  } else {
    list = [...list].sort((a, b) => (b.heat7d || 0) - (a.heat7d || 0))
  }

  return list
})

const filteredDiscussions = computed(() =>
  filterDiscussions({
    type: activeDiscussionType.value,
    keyword: rawSearchKeyword.value,
    sort: activeDiscussionSort.value,
  }),
)

const materialTotalPages = computed(() => Math.max(1, Math.ceil(filteredMaterials.value.length / pageSize)))
const discussionTotalPages = computed(() => Math.max(1, Math.ceil(filteredDiscussions.value.length / pageSize)))
const pagedMaterials = computed(() =>
  filteredMaterials.value.slice((materialPage.value - 1) * pageSize, materialPage.value * pageSize),
)
const pagedDiscussions = computed(() =>
  filteredDiscussions.value.slice((discussionPage.value - 1) * pageSize, discussionPage.value * pageSize),
)

const materialEmptyText = computed(() =>
  rawSearchKeyword.value
    ? `没有找到“${rawSearchKeyword.value}”相关资料，试试更换关键词或切换筛选条件。`
    : '当前筛选条件下还没有资料，试试切换分类或先上传第一份资料。',
)

const discussionEmptyText = computed(() =>
  rawSearchKeyword.value ? `没有找到“${rawSearchKeyword.value}”相关讨论。` : '还没有讨论，来发起第一个话题吧。',
)

const localContributionStats = computed(() => {
  const userId = currentUserId.value
  if (!userId) {
    return { materials: 0, discussions: 0, comments: 0, likes: 0 }
  }

  const ownMaterials = materials.value.filter((item) => String(item.authorId) === userId)
  const ownDiscussions = discussions.value.filter((item) => String(item.authorId) === userId)

  return {
    materials: ownMaterials.length,
    discussions: ownDiscussions.length,
    comments: comments.value.filter((item) => String(item.authorId) === userId && !item.isDeleted).length,
    likes:
      ownMaterials.reduce((sum, item) => sum + (item.likes || 0), 0) +
      ownDiscussions.reduce((sum, item) => sum + (item.likes || 0), 0),
  }
})

const contributionStats = computed(() => {
  if (backendOverview.value) {
    return {
      materials: backendOverview.value.uploads || 0,
      discussions: backendOverview.value.discussions || 0,
      comments: backendOverview.value.comments || 0,
      likes: backendOverview.value.likes || 0,
    }
  }
  return localContributionStats.value
})

const redirectToLogin = () => {
  window.setTimeout(() => {
    router.push('/login')
  }, 400)
}

const requireLogin = (message = '登录后才能使用该功能') => {
  if (currentUser.value?.isLoggedIn) {
    return true
  }
  showToast(message, 'warning')
  redirectToLogin()
  return false
}

const openMaterialDialog = () => {
  if (!requireLogin()) {
    return
  }
  materialDialogOpen.value = true
}

const openDiscussionDialog = () => {
  if (!requireLogin('登录后才能发讨论')) {
    return
  }
  discussionDialogOpen.value = true
}

const loadOverview = async () => {
  if (!currentUser.value?.isLoggedIn) {
    backendOverview.value = null
    return
  }

  overviewLoading.value = true
  try {
    const result = await getKnowledgeOverview()
    backendOverview.value = result?.data || null
  } catch {
    backendOverview.value = null
  } finally {
    overviewLoading.value = false
  }
}

const syncLocalKnowledgeRecordsToBackend = async (force = false) => {
  const userId = currentUserId.value
  if (!userId || syncState.value.running || (!force && syncState.value.finishedFor === userId)) {
    return
  }

  const localUploads = getLocalMineRecords('uploads')
  const localDiscussions = getLocalMineRecords('discussions')
  const localFavorites = getLocalMineRecords('favorites')
  const localRedeems = getLocalMineRecords('redeems')

  if (!localUploads.length && !localDiscussions.length && !localFavorites.length && !localRedeems.length) {
    syncState.value.finishedFor = userId
    return
  }

  syncState.value.running = true

  try {
    const [backendUploads, backendDiscussions, backendFavorites, backendRedeems] = await Promise.all([
      fetchAllPages(getMyKnowledgeUploads),
      fetchAllPages(getMyKnowledgeDiscussions),
      fetchAllPages(getMyKnowledgeFavorites),
      fetchAllPages(getMyKnowledgeRedeems),
    ])

    const uploadSignatures = new Set(backendUploads.map((item) => makeMaterialSignature(item)))
    const discussionSignatures = new Set(backendDiscussions.map((item) => makeDiscussionSignature(item)))
    const favoriteMaterialIds = new Set(
      backendFavorites.map((item) => Number(item?.material?.id || item?.materialId || 0)).filter(Boolean),
    )
    const redeemMaterialIds = new Set(
      backendRedeems.map((item) => Number(item?.material?.id || item?.materialId || 0)).filter(Boolean),
    )

    let syncedUploads = 0
    let syncedDiscussions = 0

    for (const item of localUploads) {
      if (item.backendId) {
        continue
      }

      const signature = makeMaterialSignature(item)
      if (uploadSignatures.has(signature)) {
        continue
      }

      await createKnowledgeMaterialApi({
        title: item.title,
        description: item.description,
        category: item.category,
        course: item.course,
        pricePoints: item.pricePoints || 0,
        tags: item.tags || [],
        fileType: item.fileType || 'other',
        fileSize: item.fileSize || '',
      })

      uploadSignatures.add(signature)
      syncedUploads += 1
    }

    for (const item of localDiscussions) {
      const signature = makeDiscussionSignature(item)
      if (discussionSignatures.has(signature)) {
        continue
      }

      await createKnowledgeDiscussionApi({
        type: item.type,
        title: item.title,
        content: item.content,
        tags: item.tags || [],
      })

      discussionSignatures.add(signature)
      syncedDiscussions += 1
    }

    const backendMaterials = await fetchAllPages(getKnowledgeMaterials)
    const backendMaterialMap = new Map()
    backendMaterials.forEach((item) => {
      backendMaterialMap.set(makeMaterialSignature(item), item)
    })

    let syncedFavorites = 0
    let syncedRedeems = 0

    for (const item of localFavorites) {
      const matched = backendMaterialMap.get(makeMaterialSignature(item))
      const materialId = Number(matched?.id || 0)
      if (!materialId || favoriteMaterialIds.has(materialId)) {
        continue
      }

      await toggleKnowledgeFavorite(materialId)
      favoriteMaterialIds.add(materialId)
      syncedFavorites += 1
    }

    for (const item of localRedeems) {
      const matched = backendMaterialMap.get(makeMaterialSignature(item))
      const materialId = Number(matched?.id || 0)
      if (!materialId || redeemMaterialIds.has(materialId)) {
        continue
      }

      await downloadMaterial(materialId)
      redeemMaterialIds.add(materialId)
      syncedRedeems += 1
    }

    syncState.value.finishedFor = userId

    if (syncedUploads || syncedDiscussions || syncedFavorites || syncedRedeems) {
      showToast(
        `已同步到后端：上传 ${syncedUploads}，讨论 ${syncedDiscussions}，收藏 ${syncedFavorites}，兑换 ${syncedRedeems}`,
        'success',
      )
    }
  } catch (error) {
    showToast(error.message || '本地记录同步到后端失败，请稍后重试。', 'warning')
  } finally {
    syncState.value.running = false
    await loadOverview()
    if (activeMineView.value) {
      await loadMineRecords()
    }
  }
}

const normalizeMineItems = (viewKey, items) => {
  if (viewKey === 'discussions') {
    return items
  }
  const normalizeMaterial = (record) => {
    const material = record?.material || record
    if (!material) {
      return null
    }

    const localMaterial = materials.value.find((item) => makeMaterialSignature(item) === makeMaterialSignature(material))
    if (localMaterial) {
      return {
        ...localMaterial,
        backendId: Number(material.id || 0) || localMaterial.backendId || null,
        localId: Number(localMaterial.id || 0) || null,
      }
    }

    return {
      ...material,
      backendId: Number(material.id || 0) || null,
      localId: null,
      course: material.course || material.courseName || '',
      downloads: material.downloads || material.downloadCount || 0,
      views: material.views || material.viewCount || 0,
      likes: material.likes || material.likeCount || 0,
      favorites: material.favorites || 0,
      authorId: material.authorId || material.uploaderId || '',
      authorName: material.authorName || '后端资料',
    }
  }

  if (viewKey === 'favorites' || viewKey === 'redeems') {
    return items.map(normalizeMaterial).filter(Boolean)
  }
  return items.map(normalizeMaterial).filter(Boolean)
}

const loadMineRecords = async () => {
  if (!activeMineView.value || !currentUser.value?.isLoggedIn) {
    mineRecords.value = []
    mineTotal.value = 0
    mineTotalPages.value = 1
    mineError.value = ''
    mineSource.value = 'backend'
    return
  }

  const config = mineViewConfigMap[activeMineView.value]
  const localRecords = getLocalMineRecords(activeMineView.value)

  mineLoading.value = true
  mineError.value = ''

  try {
    const response = await config.loader({
      page: minePage.value,
      page_size: pageSize,
    })

    const data = response?.data || {}
    const backendItems = normalizeMineItems(activeMineView.value, data.items || [])
    const backendTotal = Number(data.total || 0)

    if (backendTotal > 0 || backendItems.length > 0) {
      mineRecords.value = backendItems
      mineTotal.value = backendTotal
      mineTotalPages.value = Math.max(1, Number(data.totalPages || 1))
      mineSource.value = 'backend'
      return
    }

    mineRecords.value = localRecords.slice((minePage.value - 1) * pageSize, minePage.value * pageSize)
    mineTotal.value = localRecords.length
    mineTotalPages.value = Math.max(1, Math.ceil(localRecords.length / pageSize))
    mineSource.value = localRecords.length ? 'local' : 'backend'
  } catch (error) {
    if (localRecords.length) {
      mineRecords.value = localRecords.slice((minePage.value - 1) * pageSize, minePage.value * pageSize)
      mineTotal.value = localRecords.length
      mineTotalPages.value = Math.max(1, Math.ceil(localRecords.length / pageSize))
      mineSource.value = 'local'
      mineError.value = ''
      showToast('后端暂时不可用，已先展示当前浏览器中的本地记录。', 'warning')
      return
    }

    mineRecords.value = []
    mineTotal.value = 0
    mineTotalPages.value = 1
    mineSource.value = 'backend'
    mineError.value = error.message || '加载个人记录失败'
  } finally {
    mineLoading.value = false
  }
}

const switchMineView = (key) => {
  const mineKey = normalizeMineKey(key)
  if (!mineKey) {
    return
  }
  router.replace({
    path: route.path,
    query: {
      ...route.query,
      mine: mineKey,
    },
  })
}

const clearMineView = () => {
  const nextQuery = { ...route.query }
  delete nextQuery.mine
  router.replace({
    path: route.path,
    query: nextQuery,
  })
}

const handleShortcut = (key) => {
  if (!requireLogin()) {
    return
  }
  switchMineView(key)
}

const handleMaterialSubmit = async (payload) => {
  if (materialSubmitting.value) {
    return
  }
  materialSubmitting.value = true
  const validation = await createMaterial(payload, currentUser.value, {
    validateOnly: true,
    skipPointAward: true,
  })
  if (!validation.ok) {
    materialSubmitting.value = false
    showToast(validation.message, validation.code === 'login_required' ? 'warning' : 'error')
    if (validation.code === 'login_required') {
      redirectToLogin()
    }
    return
  }

  let backendResult = null
  try {
    backendResult = await createKnowledgeMaterialApi({
      title: payload.title,
      description: payload.description,
      category: payload.category,
      course: payload.course,
      pricePoints: payload.pricePoints,
      tags: payload.tags,
      fileType: payload.file?.type || payload.file?.name?.split('.').pop() || 'other',
      fileSize: payload.file?.size || '',
    })
  } catch (error) {
    materialSubmitting.value = false
    showToast(error.message || '资料上传失败，请稍后重试。', 'error')
    return
  }

  const pointsData = backendResult?.data?.points || {}
  const localResult = await createMaterial(payload, currentUser.value, {
    backendId: backendResult?.data?.material?.id,
    skipPointAward: true,
    points: pointsData.balance || 0,
    message: `上传成功，积分+10，当前积分 ${pointsData.balance || 0}/${pointsData.max || POINTS_MAX}`,
  })
  materialSubmitting.value = false

  if (!localResult.ok) {
    showToast(localResult.message, localResult.code === 'login_required' ? 'warning' : 'error')
    if (localResult.code === 'login_required') {
      redirectToLogin()
    }
    return
  }

  if (pointsData.balance !== undefined) {
    backendOverview.value = {
      ...backendOverview.value,
      pointsBalance: pointsData.balance || 0,
      checkedInToday: Boolean(pointsData.checkedInToday),
    }
  }

  materialDialogOpen.value = false
  materialDialogRef.value?.resetForm()
  materialPage.value = 1
  await loadOverview()
  if (activeMineView.value === 'uploads') {
    await loadMineRecords()
  }
  showToast(localResult.message, 'success')
  return

  const result = await createMaterial(payload, currentUser.value)
  materialSubmitting.value = false

  if (!result.ok) {
    showToast(result.message, result.code === 'login_required' ? 'warning' : 'error')
    if (result.code === 'login_required') {
      redirectToLogin()
    }
    return
  }

  try {
    await createKnowledgeMaterialApi({
      title: payload.title,
      description: payload.description,
      category: payload.category,
      course: payload.course,
      pricePoints: payload.pricePoints,
      tags: payload.tags,
      fileType: payload.file?.type || payload.file?.name?.split('.').pop() || 'other',
      fileSize: payload.file?.size || '',
    })
  } catch {
    showToast('资料已写入当前页面，但后端同步稍后重试。', 'warning')
  }

  materialDialogOpen.value = false
  materialDialogRef.value?.resetForm()
  materialPage.value = 1
  await loadOverview()
  if (activeMineView.value === 'uploads') {
    await loadMineRecords()
  }
  showToast(result.message, 'success')
}

const handleDiscussionSubmit = async (payload) => {
  discussionSubmitting.value = true
  const result = createDiscussion(payload, currentUser.value)
  discussionSubmitting.value = false

  if (!result.ok) {
    showToast(result.message, result.code === 'login_required' ? 'warning' : 'error')
    if (result.code === 'login_required') {
      redirectToLogin()
    }
    return
  }

  try {
    await createKnowledgeDiscussionApi(payload)
  } catch {
    showToast('讨论已写入当前页面，但后端同步稍后重试。', 'warning')
  }

  discussionDialogOpen.value = false
  discussionDialogRef.value?.resetForm()
  activeTab.value = 'discussions'
  discussionPage.value = 1
  await loadOverview()
  if (activeMineView.value === 'discussions') {
    await loadMineRecords()
  }

  if (activeDiscussionType.value !== '全部' && activeDiscussionType.value !== result.discussion.type) {
    showToast('发布成功，可在对应分类中查看。', 'success')
  } else {
    showToast(result.message, 'success')
  }
}

const syncMinePageAfterDelete = async () => {
  await loadOverview()

  if (mineRecords.value.length <= 1 && minePage.value > 1) {
    minePage.value -= 1
    return
  }

  await loadMineRecords()
}

const findLocalMaterialByRecord = (record) => {
  const backendId = Number(record?.backendId || 0)
  if (backendId) {
    const backendMatch = materials.value.find((item) => Number(item.backendId || 0) === backendId)
    if (backendMatch) {
      return backendMatch
    }
  }

  const localId = Number(record?.localId || 0)
  if (localId) {
    const localMatch = materials.value.find((item) => Number(item.id) === localId)
    if (localMatch) {
      return localMatch
    }
  }

  return materials.value.find((item) => makeMaterialSignature(item) === makeMaterialSignature(record)) || null
}

const findLocalDiscussionByRecord = (record) =>
  discussions.value.find((item) => makeDiscussionSignature(item) === makeDiscussionSignature(record)) || null

const resolveBackendMaterialIdForDelete = async (record) => {
  const mappedBackendId = Number(record?.backendId || 0)
  if (mappedBackendId) {
    return mappedBackendId
  }

  const backendRecordId = Number(record?.id || 0)
  if (mineSource.value === 'backend' && backendRecordId) {
    return backendRecordId
  }

  const backendMaterial = await resolveBackendMaterialByRecord(record, { mineOnly: true })
  return Number(backendMaterial?.id || 0) || null
}

const handleMaterialDelete = async (materialId) => {
  if (activeMineView.value !== 'uploads' || !requireLogin()) {
    return
  }

  const target = mineRecords.value.find((item) => Number(item.id) === Number(materialId))
  if (!target) {
    showToast('资料不存在或已刷新', 'warning')
    return
  }

  const confirmed = await requestConfirm({
    title: '删除资料',
    message: `确定删除《${target.title || '这份资料'}》吗？删除后不会再在知识星河中展示。`,
    confirmText: '删除',
    cancelText: '取消',
  })
  if (!confirmed) {
    return
  }

  try {
    const backendMaterialId = await resolveBackendMaterialIdForDelete(target)
    if (backendMaterialId) {
      await deleteKnowledgeMaterial(backendMaterialId)
    }

    const localMaterial = findLocalMaterialByRecord(target)
    if (localMaterial) {
      deleteMaterial(localMaterial.id, currentUser.value)
    }

    await syncMinePageAfterDelete()
    showToast('资料已删除', 'success')
  } catch (error) {
    showToast(error.message || '资料删除失败，请稍后重试。', 'error')
  }
}

const handleDiscussionDelete = async (discussionId) => {
  if (activeMineView.value !== 'discussions' || !requireLogin()) {
    return
  }

  const target = mineRecords.value.find((item) => Number(item.id) === Number(discussionId))
  if (!target) {
    showToast('讨论不存在或已刷新', 'warning')
    return
  }

  const confirmed = await requestConfirm({
    title: '删除讨论',
    message: `确定删除《${target.title || '这条讨论'}》吗？删除后相关回复将不再展示。`,
    confirmText: '删除',
    cancelText: '取消',
  })
  if (!confirmed) {
    return
  }

  try {
    if (mineSource.value === 'backend') {
      await deleteKnowledgeDiscussion(discussionId)
    } else {
      const backendDiscussion = await resolveBackendDiscussionByRecord(target)
      if (backendDiscussion?.id) {
        await deleteKnowledgeDiscussion(backendDiscussion.id)
      }
    }

    const localDiscussion = findLocalDiscussionByRecord(target)
    if (localDiscussion) {
      deleteDiscussion(localDiscussion.id, currentUser.value)
    }

    await syncMinePageAfterDelete()
    showToast('讨论已删除', 'success')
  } catch (error) {
    showToast(error.message || '讨论删除失败，请稍后重试。', 'error')
  }
}

const handleMaterialLike = async (materialId) => {
  const result = toggleMaterialLike(materialId, currentUser.value)
  if (!result.ok) {
    showToast(result.message, 'warning')
    redirectToLogin()
    return
  }

  try {
    const localMaterial = materials.value.find((item) => Number(item.id) === Number(materialId)) || null
    const backendMaterial = await resolveBackendMaterialByRecord(localMaterial)
    if (!backendMaterial?.id) {
      throw new Error('没有找到对应的后端资料记录')
    }
    await toggleKnowledgeMaterialLike(backendMaterial.id)
    await loadOverview()
  } catch (error) {
    showToast(error.message || '点赞状态已在当前页面更新，但后端同步稍后重试。', 'warning')
  }
}

const handleMaterialFavorite = async (materialId) => {
  const result = toggleMaterialFavorite(materialId, currentUser.value)
  if (!result.ok) {
    showToast(result.message, 'warning')
    redirectToLogin()
    return
  }

  try {
    const localMaterial = materials.value.find((item) => Number(item.id) === Number(materialId)) || null
    let backendMaterial = await resolveBackendMaterialByRecord(localMaterial)

    if (!backendMaterial) {
      await syncLocalKnowledgeRecordsToBackend(true)
      backendMaterial = await resolveBackendMaterialByRecord(localMaterial)
    }

    if (!backendMaterial?.id) {
      throw new Error('没有找到对应的后端资料记录')
    }

    await toggleKnowledgeFavorite(backendMaterial.id)
    await loadOverview()
    if (activeMineView.value === 'favorites') {
      await loadMineRecords()
    }
  } catch (error) {
    showToast(error.message || '收藏状态已在当前页面更新，但后端同步稍后重试。', 'warning')
  }
}

const handleDiscussionLike = async (discussionId) => {
  const result = toggleDiscussionLike(discussionId, currentUser.value)
  if (!result.ok) {
    showToast('登录后才能点赞', 'warning')
    redirectToLogin()
    return
  }

  try {
    const localDiscussion = discussions.value.find((item) => Number(item.id) === Number(discussionId)) || null
    const backendDiscussion = await resolveBackendDiscussionByRecord(localDiscussion)
    if (!backendDiscussion?.id) {
      throw new Error('没有找到对应的后端讨论记录')
    }
    await toggleKnowledgeDiscussionLike(backendDiscussion.id)
    await loadOverview()
  } catch (error) {
    showToast(error.message || '点赞状态已在当前页面更新，但后端同步稍后重试。', 'warning')
  }
}

const handleCheckin = async () => {
  if (!requireLogin()) {
    return
  }

  try {
    const result = await checkinKnowledge()
    const pointsData = result?.data?.points || {}
    backendOverview.value = {
      ...backendOverview.value,
      pointsBalance: pointsData.balance || 0,
      checkedInToday: Boolean(pointsData.checkedInToday),
    }
    showToast(`签到成功 +5，当前积分 ${pointsData.balance || 0}/${pointsData.max || POINTS_MAX}`, 'success')
  } catch (error) {
    showToast(error.message || '签到失败，请稍后重试。', 'warning')
  }
}

const handleCheckinSafe = async () => {
  if (!requireLogin()) {
    return
  }

  if (checkinSubmitting.value || checkedInToday.value) {
    return
  }

  checkinSubmitting.value = true
  try {
    const result = await checkinKnowledge()
    const pointsData = result?.data?.points || {}
    const reward = result?.data?.reward || {}
    backendOverview.value = {
      ...backendOverview.value,
      pointsBalance: pointsData.balance || 0,
      checkedInToday: Boolean(pointsData.checkedInToday),
    }

    if (Number(reward.delta || 0) > 0) {
      showToast(`签到成功 +${reward.delta}，当前积分 ${pointsData.balance || 0}/${pointsData.max || POINTS_MAX}`, 'success')
    } else {
      showToast(result?.message || '今日已签到', 'success')
    }
  } catch (error) {
    if (String(error?.message || '').includes('今日已签到')) {
      await loadOverview()
      showToast('今日已签到', 'success')
    } else {
      showToast(error.message || '签到失败，请稍后重试。', 'warning')
    }
  } finally {
    checkinSubmitting.value = false
  }
}

const handleOpenUploadEvent = () => openMaterialDialog()
const handleOpenDiscussionEvent = () => openDiscussionDialog()

onMounted(() => {
  loadOverview()
  syncLocalKnowledgeRecordsToBackend()
  window.addEventListener('open-knowledge-upload', handleOpenUploadEvent)
  window.addEventListener('open-knowledge-discussion', handleOpenDiscussionEvent)
})

watch(
  () => route.query.tab,
  (tab) => {
    activeTab.value = tab === 'discussion' ? 'discussions' : 'materials'
  },
)

watch(
  () => currentUser.value?.id,
  (nextId, previousId) => {
    if (nextId && nextId !== previousId) {
      syncState.value.finishedFor = ''
    }
    loadOverview()
    syncLocalKnowledgeRecordsToBackend()
  },
)

watch(activeTab, (tab) => {
  const nextTab = tab === 'discussions' ? 'discussion' : undefined
  if (route.query.tab === nextTab) {
    return
  }
  router.replace({
    path: route.path,
    query: {
      ...route.query,
      tab: nextTab,
    },
  })
})

watch([activeTab, activeMaterialCategory, activeMaterialSort, rawSearchKeyword], () => {
  materialPage.value = 1
})

watch([activeTab, activeDiscussionType, activeDiscussionSort, rawSearchKeyword], () => {
  discussionPage.value = 1
})

watch(materialTotalPages, (totalPages) => {
  if (materialPage.value > totalPages) {
    materialPage.value = totalPages
  }
})

watch(discussionTotalPages, (totalPages) => {
  if (discussionPage.value > totalPages) {
    discussionPage.value = totalPages
  }
})

watch(
  activeMineView,
  (next, prev) => {
    if (!next) {
      mineRecords.value = []
      mineTotal.value = 0
      mineTotalPages.value = 1
      mineError.value = ''
      mineSource.value = 'backend'
      return
    }

    if (!currentUser.value?.isLoggedIn) {
      clearMineView()
      return
    }

    if (next !== prev) {
      minePage.value = 1
    }
  },
  { immediate: true },
)

watch(
  [activeMineView, minePage, currentUserId],
  () => {
    if (!activeMineView.value) {
      return
    }
    loadMineRecords()
  },
  { immediate: true },
)

onBeforeUnmount(() => {
  window.removeEventListener('open-knowledge-upload', handleOpenUploadEvent)
  window.removeEventListener('open-knowledge-discussion', handleOpenDiscussionEvent)
})
</script>

<style scoped>
.knowledge-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
  max-width: 1500px;
  margin: 0 auto;
}

.hero-card {
  display: flex;
  align-items: center;
  padding: 16px 22px;
  border-radius: 24px;
  background:
    radial-gradient(circle at 92% 18%, rgba(167, 139, 250, 0.12), transparent 26%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(243, 247, 255, 0.9));
  border: 1px solid rgba(224, 232, 255, 0.96);
  box-shadow: 0 18px 36px rgba(90, 107, 162, 0.1);
}

.hero-copy {
  min-width: 0;
}

.hero-copy h1,
.subtitle {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hero-copy h1 {
  color: #4e63dd;
  font-size: clamp(28px, 2.5vw, 32px);
  line-height: 1.2;
  font-weight: 800;
}

.subtitle {
  margin-top: 6px;
  color: #61738e;
  font-size: 14px;
  line-height: 1.6;
}

.page-grid {
  display: grid;
  grid-template-columns: 224px minmax(0, 1.18fr) 296px;
  gap: 16px;
  align-items: start;
}

.left-column,
.right-column {
  position: sticky;
  top: 98px;
}

.left-stack {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.side-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 18px;
  border-radius: 22px;
  border: 1px solid rgba(224, 232, 255, 0.96);
  background: #fff;
  box-shadow: 0 18px 40px rgba(90, 107, 162, 0.12);
}

.side-card--slim {
  gap: 10px;
}

.side-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.side-card-head h3 {
  color: #18233b;
  font-size: 18px;
  font-weight: 600;
  line-height: 1.2;
}

.side-card-badge,
.mine-source-badge,
.mine-kicker {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.side-card-badge {
  min-height: 22px;
  padding: 0 8px;
  background: #eef5ff;
  color: #4760d9;
  font-size: 11px;
}

.contribution-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.contribution-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: #60718c;
  font-size: 13px;
  line-height: 1.4;
}

.contribution-item strong {
  color: #3156cf;
  font-size: 16px;
  font-weight: 800;
}

.rules-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  color: #697a94;
  font-size: 12px;
  line-height: 1.65;
}

.tabs-shell {
  padding: 16px;
  border-radius: 24px;
  border: 1px solid rgba(224, 232, 255, 0.96);
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 18px 40px rgba(90, 107, 162, 0.12);
}

.top-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 14px;
}

.panel-shell,
.mine-shell {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.filter-row,
.mine-head {
  padding-bottom: 12px;
  border-bottom: 1px solid #edf2ff;
}

.filter-row {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mine-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.mine-copy h2 {
  color: #18233b;
  font-size: 28px;
  font-weight: 800;
  line-height: 1.2;
}

.mine-copy p {
  margin-top: 8px;
  color: #687a96;
  font-size: 14px;
}

.mine-kicker {
  margin-bottom: 8px;
  background: #eef3ff;
  color: #4561da;
}

.mine-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.mine-source-badge {
  background: rgba(237, 243, 255, 0.88);
  color: #536dce;
  flex-shrink: 0;
}

.chips,
.sorts,
.mine-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.discussion-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.tab-btn,
.chip-btn,
.sort-btn,
.mine-tab-btn,
.back-btn,
.retry-btn {
  border: none;
  border-radius: 999px;
  font-weight: 700;
  cursor: pointer;
}

.tab-btn {
  min-height: 44px;
  padding: 0 18px;
  background: #edf2ff;
  color: #4b5f90;
  font-size: 15px;
}

.tab-btn.active,
.mine-tab-btn.active {
  color: #fff;
  background: linear-gradient(135deg, #2f80ed 0%, #6f84ff 64%, #a78bfa 100%);
  box-shadow: 0 12px 28px rgba(92, 75, 140, 0.16);
}

.chip-btn,
.sort-btn,
.mine-tab-btn {
  min-height: 38px;
  padding: 0 14px;
  background: #f5f7ff;
  color: #5d6f8a;
  font-size: 13px;
}

.chip-btn.active,
.sort-btn.active {
  background: #e9efff;
  color: #2f5ae0;
}

.mine-tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.back-btn {
  min-height: 40px;
  padding: 0 16px;
  background: #f3f6ff;
  color: #3b57c7;
}

.retry-btn {
  min-height: 40px;
  padding: 0 16px;
  color: #fff;
  background: linear-gradient(135deg, #2f80ed 0%, #6f84ff 64%, #a78bfa 100%);
}

.search-tip {
  color: #687a96;
  font-size: 14px;
}

.inline-create-btn {
  min-height: 36px;
  padding: 0 14px;
  border: none;
  border-radius: 999px;
  color: #fff;
  font-weight: 700;
  cursor: pointer;
  background: linear-gradient(135deg, #2f80ed 0%, #6f84ff 64%, #a78bfa 100%);
}

.state-panel {
  min-height: 240px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  border-radius: 22px;
  border: 1px dashed rgba(196, 210, 247, 0.96);
  background: rgba(255, 255, 255, 0.72);
  color: #6b7c96;
  text-align: center;
}

.state-panel i {
  font-size: 32px;
  color: #8fa0bf;
}

.state-panel--error i {
  color: #e26a6a;
}

@media (max-width: 1200px) {
  .page-grid {
    grid-template-columns: 1fr;
  }

  .left-column,
  .right-column {
    position: static;
  }
}

@media (max-width: 760px) {
  .hero-copy h1,
  .subtitle {
    white-space: normal;
  }

  .discussion-toolbar,
  .mine-head,
  .mine-toolbar {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
