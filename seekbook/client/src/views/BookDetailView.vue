<template>
  <div v-if="book" class="book-detail-container">
    <BookDetailMain :book="book" :labels="detail.labels" />
    <BookTransactionPanel :book="book" :detail="detail" :current-user="props.data.appState?.user" />
  </div>
  <div v-else class="error-container">
    <i class="fas fa-exclamation-circle"></i>
    <h3>{{ detail.notFoundText }}</h3>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import BookDetailMain from '../components/book/BookDetailMain.vue'
import BookTransactionPanel from '../components/book/BookTransactionPanel.vue'
import { useCatalogBooks } from '../composables/useCatalogBooks'
import { getBookDetail } from '../services/api'

const route = useRoute()
const props = defineProps({
  data: { type: Object, default: () => ({}) },
})

const { catalogBooks, loadCatalogBooks } = useCatalogBooks()
const remoteBook = ref(null)
const detail = computed(() => props.data.bookDetail ?? { labels: {} })
const shared = computed(() => props.data.shared ?? {})
const book = computed(() => {
  const id = Number(route.query.id || 1)
  const featured = props.data.books?.featured?.find((item) => item.id === id)
  const catalog = catalogBooks.value.find((item) => item.id === id)
  const sourceBook = route.query.source === 'catalog'
    ? remoteBook.value || catalog || featured
    : remoteBook.value || featured || catalog
  return normalizeBook(sourceBook, id)
})

const normalizeTags = (value) => {
  if (Array.isArray(value)) {
    return value.map((item) => String(item || '').trim()).filter(Boolean)
  }

  return String(value || '')
    .split(/[,，]/)
    .map((item) => item.trim())
    .filter(Boolean)
}

const normalizeBook = (item, id) => {
  if (!item) return null
  const index = Math.max(0, id - 1)
  const sellerName = item.seller?.name || item.seller || item.sellerName || shared.value.sellerNames?.[index % 6] || ''
  const sellerId = item.sellerId || item.seller?.id || item.seller_id || ''
  const sellerCreditScore = item.sellerCreditScore ?? item.seller?.creditScore ?? 100
  const sellerReputation = item.sellerReputation || item.seller?.reputation || item.sellerLevel || shared.value.sellerLevels?.[index % 4] || ''
  return {
    ...item,
    title: item.title || item.name,
    image: item.image || item.coverImage || item.img,
    originalPrice: Number(item.originalPrice ?? Number(item.price) * 1.5),
    condition: item.conditionLabel || item.condition || shared.value.displayConditions?.[index % 4] || '',
    campus: item.campusLabel || item.campus || shared.value.campusOptions?.[index % 4]?.fullName || '',
    seller: typeof item.seller === 'object'
      ? { ...item.seller, name: sellerName, id: sellerId, creditScore: sellerCreditScore, reputation: sellerReputation }
      : { name: sellerName, id: sellerId, creditScore: sellerCreditScore, reputation: sellerReputation },
    sellerName,
    sellerId,
    sellerCreditScore,
    sellerReputation,
    hasNotes: item.hasNotes ?? index % 3 === 0,
    category: item.subject || item.category || '',
    tags: normalizeTags(item.tags),
    description: String(item.description || '').trim(),
  }
}

const loadRemoteBook = async () => {
  const id = Number(route.query.id || 0)
  if (!id) {
    remoteBook.value = null
    return
  }

  try {
    const response = await getBookDetail(id)
    remoteBook.value = response.code === 200 ? response.data : null
  } catch (error) {
    console.error('Failed to load remote book detail:', error)
    remoteBook.value = null
  }
}

onMounted(() => loadCatalogBooks(props.data.buy?.catalogSource))
watch(() => route.query.id, loadRemoteBook, { immediate: true })
</script>

<style scoped>
.book-detail-container {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 32px;
  margin-bottom: 48px;
}

.error-container {
  background: white;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  color: var(--gray-600);
  box-shadow: var(--shadow-md);
}

@media (max-width: 1024px) {
  .book-detail-container {
    grid-template-columns: 1fr;
    gap: 24px;
  }
}
</style>
