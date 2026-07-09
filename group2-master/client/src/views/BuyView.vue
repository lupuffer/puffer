<template>
  <div ref="buyViewRef" class="buy-view">
    <BuyFilterPanel :buy="buy" @search="handleSearch" @filter="handleFilter" />
    <BookListPanel
      :buy="buy"
      :books="pageBooks"
      :loading="loading"
      :active-sort="activeSort"
      :current-page="currentPage"
      :total-pages="totalPages"
      :page-size="pageSize"
      :page-numbers="pageNumbers"
      :start-index="startIndex"
      :total-items="totalItems"
      :catalog-status="catalogStatus"
      @select="goDetail"
      @sort="handleSort"
      @page="goPage"
      @page-size="changePageSize"
    />
    <ShortageWidget
      :shortage="buy.shortage"
      :items="shortageItems"
      :loading="shortageLoading"
      :bottom-offset="widgetBottomOffset"
      @open="handleOpenShortageModal"
      @cancel="handleCancelShortage"
    />
    <ShortageModal
      :open="modalOpen"
      :shortage="buy.shortage"
      :campus-options="props.data.shared?.campusOptions || []"
      :submitting="shortageSubmitting"
      @close="modalOpen = false"
      @submit="handleSubmitShortage"
    />
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BookListPanel from '../components/buy/BookListPanel.vue'
import BuyFilterPanel from '../components/buy/BuyFilterPanel.vue'
import ShortageModal from '../components/buy/ShortageModal.vue'
import ShortageWidget from '../components/buy/ShortageWidget.vue'
import { useCatalogBooks } from '../composables/useCatalogBooks'
import { useGlobalState } from '../composables/useGlobalState'
import { createShortageRegistration, deleteShortageRegistration, getBooks, getShortageRegistrations } from '../services/api'

const route = useRoute()
const router = useRouter()
const { currentUser } = useGlobalState()
const buyViewRef = ref(null)
const modalOpen = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const keyword = ref('')
const loading = ref(false)
const pageBooks = ref([])
const totalPages = ref(1)
const totalItems = ref(0)
const usingLocalCatalog = ref(false)
const shortageItems = ref([])
const shortageLoading = ref(false)
const shortageSubmitting = ref(false)
const widgetBottomOffset = ref(24)
const props = defineProps({
  data: { type: Object, default: () => ({}) },
})

const { loadCatalogBooks } = useCatalogBooks()
const buy = computed(() => props.data.buy ?? { shortage: {}, booksSection: {}, pagination: {} })
const activeSort = ref('')
const activeFilters = ref({})
const priceRange = ref({ min: null, max: null })
const catalogStatus = computed(() => (usingLocalCatalog.value ? '本地目录数据' : '后端目录数据'))

const startIndex = computed(() => (currentPage.value - 1) * pageSize.value)
const pageNumbers = computed(() => {
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, start + 4)
  return Array.from({ length: end - start + 1 }, (_, index) => start + index)
})

const conditionMap = {
  全新: 'new',
  九成新: 'like-new',
  良好: 'good',
  一般: 'fair',
}

const campusMap = {
  紫金港: 'zijingang',
  玉泉: 'yuquan',
  西溪: 'xixi',
  之江: 'zhijiang',
  华家池: 'huajiachi',
}

const tradeMap = {
  当面交易: 'face',
  邮寄: 'mail',
}

const mapSortToApi = (option) => {
  const options = buy.value.booksSection?.sortOptions ?? []
  if (option === options[1]) return 'price_asc'
  if (option === options[2]) return 'price_desc'
  if (option === options[3]) return 'reputation'
  return 'newest'
}

const buildParams = () => {
  const params = {
    page: currentPage.value,
    page_size: pageSize.value,
    sort: mapSortToApi(activeSort.value),
  }

  if (keyword.value.trim()) params.keyword = keyword.value.trim()
  if (priceRange.value.min !== null) params.min_price = priceRange.value.min
  if (priceRange.value.max !== null) params.max_price = priceRange.value.max

  Object.entries(activeFilters.value).forEach(([key, value]) => {
    if (!value || value === '全部') return

    if (key === 'campus' && campusMap[value]) params.campus = campusMap[value]
    if (key === 'condition' && conditionMap[value]) params.condition = conditionMap[value]
    if (key === 'trade' && tradeMap[value]) params.trade_method = tradeMap[value]
    if (key === 'other' && value === '有笔记') params.has_notes = true
  })

  return params
}

const normalizeBook = (book) => ({
  ...book,
  image: book.coverImage || book.image || book.img,
  condition: book.conditionLabel || book.condition,
  campus: book.campusLabel || book.campus,
})

const matchesCatalogBook = (book) => {
  const searchValue = keyword.value.trim().toLowerCase()
  if (searchValue) {
    const haystack = [book.title, book.name, book.author, book.isbn, book.tags]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    if (!haystack.includes(searchValue)) {
      return false
    }
  }

  if (priceRange.value.min !== null && Number(book.price) < priceRange.value.min) return false
  if (priceRange.value.max !== null && Number(book.price) > priceRange.value.max) return false

  for (const [key, value] of Object.entries(activeFilters.value)) {
    if (!value || value === '全部') continue

    if (key === 'campus' && campusMap[value] && book.campus !== campusMap[value]) return false
    if (key === 'condition' && conditionMap[value] && book.condition !== conditionMap[value]) return false
    if (key === 'trade' && tradeMap[value] && book.tradeMethod !== tradeMap[value]) return false
    if (key === 'other' && value === '有笔记' && !book.hasNotes) return false
  }

  return true
}

const sortCatalogBooks = (books) => {
  const options = buy.value.booksSection?.sortOptions ?? []
  const sorted = [...books]

  if (activeSort.value === options[1]) {
    sorted.sort((a, b) => Number(a.price) - Number(b.price))
    return sorted
  }

  if (activeSort.value === options[2]) {
    sorted.sort((a, b) => Number(b.price) - Number(a.price))
    return sorted
  }

  if (activeSort.value === options[3]) {
    sorted.sort((a, b) => {
      const scoreA = Number(a.sellerCreditScore ?? a.seller?.creditScore ?? 0)
      const scoreB = Number(b.sellerCreditScore ?? b.seller?.creditScore ?? 0)
      return scoreB - scoreA
    })
    return sorted
  }

  sorted.sort((a, b) => Number(a.id) - Number(b.id))
  return sorted
}

const applyLocalCatalogFallback = async () => {
  const catalogBooks = await loadCatalogBooks(buy.value.catalogSource)
  const filteredBooks = sortCatalogBooks(catalogBooks.filter(matchesCatalogBook))
  const start = startIndex.value
  const end = start + pageSize.value

  usingLocalCatalog.value = true
  totalItems.value = filteredBooks.length
  totalPages.value = Math.max(1, Math.ceil(filteredBooks.length / pageSize.value))
  pageBooks.value = filteredBooks.slice(start, end).map(normalizeBook)
}

const fetchBooks = async () => {
  loading.value = true

  try {
    try {
      const response = await getBooks(buildParams())
      if (response.code === 200) {
        usingLocalCatalog.value = false
        pageBooks.value = (response.data.books || []).map(normalizeBook)
        totalPages.value = response.data.total_pages || 1
        totalItems.value = response.data.total || 0
        return
      }
    } catch (error) {
      console.error('从后端获取书籍失败:', error)
    }

    try {
      await applyLocalCatalogFallback()
    } catch (error) {
      console.error('读取本地目录失败:', error)
      usingLocalCatalog.value = true
      pageBooks.value = []
      totalPages.value = 1
      totalItems.value = 0
    }
  } finally {
    loading.value = false
  }
}

const handleSearch = (value) => {
  currentPage.value = 1
  router.replace({ path: '/buy', query: value ? { search: value } : {} })
}

const handleFilter = (filter) => {
  if (filter.type === 'category') {
    activeFilters.value = { ...activeFilters.value, [filter.key]: filter.value }
  } else if (filter.type === 'price') {
    priceRange.value = { min: filter.min, max: filter.max }
  }
  currentPage.value = 1
}

const handleSort = (option) => {
  activeSort.value = option
  currentPage.value = 1
}

const goPage = (page) => {
  currentPage.value = Math.min(totalPages.value, Math.max(1, Number(page) || 1))
}

const changePageSize = (size) => {
  pageSize.value = Number(size)
  currentPage.value = 1
}

const goDetail = (book) => router.push({ path: '/book-detail', query: { id: book.id, source: 'catalog' } })

const updateWidgetOffset = () => {
  const paginationEl = buyViewRef.value?.querySelector('.pagination-wrap')
  if (!paginationEl) {
    widgetBottomOffset.value = 24
    return
  }

  const rect = paginationEl.getBoundingClientRect()
  const viewportHeight = window.innerHeight
  const isNearViewportBottom = rect.top < viewportHeight - 72 && rect.bottom > 0

  if (!isNearViewportBottom) {
    widgetBottomOffset.value = 24
    return
  }

  widgetBottomOffset.value = Math.max(24, Math.round(viewportHeight - rect.top + 16))
}

const registerWidgetObservers = async () => {
  await nextTick()
  updateWidgetOffset()

  const scrollContainer = document.querySelector('.content-body')
  scrollContainer?.addEventListener('scroll', updateWidgetOffset, { passive: true })
  window.addEventListener('resize', updateWidgetOffset)

  return () => {
    scrollContainer?.removeEventListener('scroll', updateWidgetOffset)
    window.removeEventListener('resize', updateWidgetOffset)
  }
}

let cleanupWidgetObservers = null

const loadShortageItems = async () => {
  if (!currentUser.value?.id) {
    shortageItems.value = []
    shortageLoading.value = false
    return
  }

  shortageLoading.value = true
  try {
    const response = await getShortageRegistrations()
    shortageItems.value = response?.data || []
  } catch (error) {
    console.error('加载缺货登记失败:', error)
    shortageItems.value = []
  } finally {
    shortageLoading.value = false
  }
}

const handleOpenShortageModal = () => {
  if (!currentUser.value?.id) {
    router.push('/login')
    return
  }
  modalOpen.value = true
}

const handleSubmitShortage = async (payload) => {
  shortageSubmitting.value = true
  try {
    await createShortageRegistration(payload)
    modalOpen.value = false
    await loadShortageItems()
    window.alert(buy.value.shortage?.successMessage || '缺货登记成功')
  } catch (error) {
    window.alert(error.message || '缺货登记失败，请稍后重试')
  } finally {
    shortageSubmitting.value = false
  }
}

const handleCancelShortage = async (item) => {
  if (!item?.id) return
  const confirmed = window.confirm(`确定取消《${item.bookName}》的缺货登记吗？`)
  if (!confirmed) return

  try {
    await deleteShortageRegistration(item.id)
    shortageItems.value = shortageItems.value.filter((entry) => entry.id !== item.id)
  } catch (error) {
    window.alert(error.message || '取消缺货登记失败，请稍后重试')
  }
}

watch(
  () => route.query.search,
  (value) => {
    keyword.value = typeof value === 'string' ? value : ''
    currentPage.value = 1
  },
  { immediate: true },
)

watch(
  () => buy.value.booksSection?.sortOptions,
  (options) => {
    if (!activeSort.value && options?.[0]) activeSort.value = options[0]
  },
  { immediate: true },
)

watch(
  [keyword, currentPage, pageSize, activeSort, activeFilters, priceRange],
  () => {
    fetchBooks()
    nextTick(updateWidgetOffset)
  },
  { deep: true, immediate: true },
)

watch(
  () => currentUser.value?.id,
  () => {
    loadShortageItems()
  },
  { immediate: true },
)

onMounted(async () => {
  cleanupWidgetObservers = await registerWidgetObservers()
})

onBeforeUnmount(() => {
  cleanupWidgetObservers?.()
})
</script>

<style scoped>
.buy-view {
  display: flex;
  flex-direction: column;
  gap: 0;
}
</style>
