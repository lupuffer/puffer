<template>
  <article class="book-card" @click="handleCardClick">
    <div class="book-image">
      <img :src="imageSrc" :alt="bookTitle" loading="lazy" @error="setFallbackImage" />
      <div v-if="conditionText" class="book-condition">{{ conditionText }}</div>
      <div v-if="showNotes" class="book-notes"><i class="fas fa-sticky-note"></i> {{ notesText }}</div>
      <div v-if="!isOwnBook" class="book-actions-overlay" @click.stop>
        <button class="btn-chat" @click="handleChat" title="联系卖家">
          <i class="fas fa-comment-dots"></i>
          <span>私聊</span>
        </button>
      </div>
    </div>
    <div class="book-info">
      <h3>{{ bookTitle }}</h3>
      <p v-if="authorText" class="book-author">{{ authorText }}</p>
      <div class="book-meta">
        <span v-if="campusText"><i class="fas fa-map-marker-alt"></i> {{ campusText }}</span>
        <span v-if="timeText"><i class="fas fa-clock"></i> {{ timeText }}</span>
      </div>
      <div class="book-price">
        <span class="price">{{ priceText }}</span>
        <span v-if="originalPriceText" class="original-price">{{ originalPriceText }}</span>
      </div>
      <div v-if="sellerText" class="book-seller" :class="{ 'is-self': isOwnBook }">
        <i class="fas fa-user-circle"></i>
        <span>{{ sellerText }}</span>
        <span v-if="isOwnBook" class="self-badge">我的</span>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed, inject } from 'vue'
import { useRouter } from 'vue-router'
import { normalizeCatalogImage } from '../composables/useCatalogBooks'
import { useGlobalState } from '../composables/useGlobalState'
import { getCreditLabel, normalizeCreditScore } from '../utils/credit'

const props = defineProps({
  book: { type: Object, required: true },
  index: { type: Number, default: 0 },
})

const emit = defineEmits(['select', 'chat'])
const router = useRouter()
const { currentUser, getOrCreateSession } = useGlobalState()

const appData = inject('appData', { value: {} })


const shared = computed(() => appData.value?.shared ?? {})
const labels = computed(() => appData.value?.bookDetail?.labels ?? {})
const fallbackImage = computed(() => appData.value?.bookDetail?.fallbackImage || '/images/book1.jpg')

// 判断是否是自己的书
const isOwnBook = computed(() => {
  const bookSellerId = props.book.sellerId || props.book.seller?.id || props.book.seller_id
  return bookSellerId && currentUser.value?.id && bookSellerId === currentUser.value.id
})

const conditionLabelMap = {
  new: '全新',
  'like-new': '九成新',
  good: '良好',
  fair: '一般',
}

const bookTitle = computed(() => props.book.title || props.book.name || props.book.bookTitle || '')
const imageSrc = computed(() => normalizeCatalogImage(props.book.image || props.book.coverImage || props.book.img || props.book.bookImage || fallbackImage.value))
const conditionText = computed(() => {
  return props.book.conditionLabel || conditionLabelMap[props.book.condition] || props.book.condition || shared.value.displayConditions?.[props.index % 4] || ''
})
const notesText = computed(() => labels.value.hasNotes || '')
const showNotes = computed(() => Boolean(props.book.hasNotes && notesText.value))
const campusText = computed(() => props.book.campusLabel || props.book.campus || shared.value.campusOptions?.[props.index % 4]?.fullName || '')
const dayText = computed(() => props.book.daysAgo || (props.index ? (props.index % 30) + 1 : ''))
const timeText = computed(() => (dayText.value ? `${dayText.value}${labels.value.daysAgoSuffix || ''}` : ''))
const authorText = computed(() => {
  if (props.book.author || props.book.bookAuthor) return props.book.author || props.book.bookAuthor
  if (!labels.value.authorPrefix) return ''
  return `${labels.value.authorPrefix}${(props.index % 10) + 1} ${shared.value.authorSuffix || ''}`.trim()
})
const priceText = computed(() => formatPrice(props.book.price))
const originalPriceText = computed(() => {
  const original = props.book.originalPrice ?? (props.book.price ? props.book.price * 1.5 : null)
  return original ? formatPrice(original) : ''
})
const sellerCreditScore = computed(() => (
  normalizeCreditScore(props.book.sellerCreditScore ?? props.book.seller?.creditScore, null)
))
const sellerCreditLabel = computed(() => (
  sellerCreditScore.value === null ? '' : getCreditLabel(sellerCreditScore.value)
))
const sellerText = computed(() => {
  const seller = props.book.seller?.name || props.book.seller || props.book.sellerName || shared.value.sellerNames?.[props.index % 6]
  if (seller && sellerCreditScore.value !== null) {
    return `${seller} · 信誉 ${sellerCreditScore.value}分 · ${sellerCreditLabel.value}`
  }
  const level = props.book.sellerReputation || props.book.sellerLevel || shared.value.sellerLevels?.[props.index % 4]
  return seller && level ? `${seller} · ${shared.value.reputationPrefix || ''} ${level}` : seller || ''
})

const formatPrice = (value) => {
  if (value === undefined || value === null || Number.isNaN(Number(value))) return ''
  return `${shared.value.priceSymbol || ''}${Number(value).toFixed(2)}`
}

const setFallbackImage = (event) => {
  if (fallbackImage.value) event.target.src = fallbackImage.value
}

const handleCardClick = () => {
  emit('select', props.book)
}

const handleChat = async () => {
  if (!currentUser.value?.id) {
    router.push('/login')
    return
  }
  
  if (isOwnBook.value) {
    return
  }

  const sellerId = props.book.sellerId || props.book.seller?.id || props.book.seller_id
  const sellerName = props.book.seller?.name || props.book.seller || props.book.sellerName || '卖家'
  const bookTitle = props.book.title || props.book.name || props.book.bookTitle || '书籍'

  try {
    const session = await getOrCreateSession(props.book.id, sellerId, sellerName, bookTitle)
    if (session?.id) {
      router.push({
        path: '/messages',
        query: { sessionId: session.id },
      })
    }
  } catch (error) {
    console.error('创建聊天会话失败:', error)
  }
}
</script>

<style scoped>
.book-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-md);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.book-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.book-image {
  position: relative;
  height: 200px;
  background-color: var(--gray-100);
  overflow: hidden;
}

.book-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-condition {
  position: absolute;
  top: 12px;
  left: 12px;
  background-color: var(--secondary-green);
  color: white;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.book-notes {
  position: absolute;
  top: 12px;
  right: 12px;
  background-color: var(--accent-orange);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.book-info {
  padding: 20px;
}

.book-info h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--gray-900);
  margin-bottom: 8px;
  line-height: 1.4;
}

.book-author {
  font-size: 14px;
  color: var(--gray-600);
  margin-bottom: 12px;
}

.book-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 13px;
  color: var(--gray-500);
}

.book-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.book-price {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 12px;
}

.price {
  font-size: 20px;
  font-weight: 700;
  color: var(--primary-blue);
}

.original-price {
  font-size: 14px;
  color: var(--gray-500);
  text-decoration: line-through;
}

.book-seller {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--gray-600);
  padding-top: 12px;
  border-top: 1px solid var(--gray-100);
}

.book-seller i {
  color: var(--primary-blue);
}

.book-seller.is-self {
  color: var(--secondary-green);
}

.book-seller.is-self i {
  color: var(--secondary-green);
}

.self-badge {
  margin-left: auto;
  padding: 2px 8px;
  background: var(--secondary-green);
  color: white;
  font-size: 11px;
  border-radius: 4px;
  font-weight: 600;
}

.book-actions-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 12px;
  background: linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
  display: flex;
  justify-content: center;
}

.book-card:hover .book-actions-overlay {
  opacity: 1;
}

.btn-chat {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--primary-blue);
  color: white;
  border: none;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(79, 110, 247, 0.4);
}

.btn-chat:hover {
  background: #3b5ce6;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(79, 110, 247, 0.5);
}

.btn-chat i {
  font-size: 14px;
}

@media (max-width: 768px) {
  .book-actions-overlay {
    opacity: 1;
    background: linear-gradient(to top, rgba(0,0,0,0.6) 0%, rgba(0,0,0,0) 100%);
  }
  
  .btn-chat {
    padding: 6px 12px;
    font-size: 12px;
  }
}
</style>
