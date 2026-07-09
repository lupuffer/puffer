<template>
  <section class="sales-section">
    <h3><i class="fas fa-tag"></i> 我的出售</h3>

    <div v-if="normalizedBooks.length === 0" class="empty-state">
      <i class="fas fa-book-open empty-icon"></i>
      <h4>您还没有上架任何书籍</h4>
      <p>点击下方按钮开始发布您的二手书</p>
      <button class="btn btn-primary" type="button" @click="goSell">发布卖书</button>
    </div>

    <div v-else class="sales-list">
      <article
        v-for="book in normalizedBooks"
        :key="book.id"
        class="sale-card"
        @click="viewBook(book)"
      >
        <div class="book-image">
          <img :src="book.displayImage" :alt="book.title" loading="lazy" />
        </div>

        <div class="book-details">
          <h4 class="book-title">{{ book.title || book.name }}</h4>
          <p class="book-author">{{ book.author || book.bookAuthor || '未知作者' }}</p>

          <div class="book-info-row">
            <span class="book-condition">
              <i class="fas fa-star"></i>
              {{ book.displayCondition }}
            </span>
            <span class="book-campus">
              <i class="fas fa-map-marker-alt"></i>
              {{ book.displayCampus }}
            </span>
          </div>

          <p class="book-price">￥{{ Number(book.price || 0).toFixed(2) }}</p>

          <div class="sale-status">
            <span class="status-badge" :class="statusClass(book.status)">
              {{ statusText(book.status) }}
            </span>
            <span class="sale-time">{{ formatTime(book.createdAt || book.createTime) }}</span>
          </div>

          <div v-if="book.status === 'on_sale'" class="sale-actions">
            <button class="remove-btn" type="button" @click.stop="$emit('remove', book)">
              <i class="far fa-circle-xmark"></i>
              <span>下架</span>
            </button>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const props = defineProps({
  books: { type: Array, default: () => [] },
})

defineEmits(['remove'])

const normalizedBooks = computed(() =>
  (props.books || []).map((book) => ({
    ...book,
    displayImage:
      book.coverImage ||
      book.image ||
      book.img ||
      (Array.isArray(book.images) ? book.images[0] : '') ||
      '/images/book1.jpg',
    displayCondition: book.conditionLabel || book.condition || '九成新',
    displayCampus: book.campusLabel || book.campus || '紫金港校区',
  })),
)

const viewBook = (book) => {
  router.push({
    path: '/book-detail',
    query: { id: book.id, source: 'catalog' },
  })
}

const goSell = () => {
  router.push('/sell')
}

const formatTime = (timestamp) => {
  if (!timestamp) return '刚刚'

  const time = typeof timestamp === 'string' ? new Date(timestamp).getTime() : Number(timestamp)
  if (Number.isNaN(time) || time <= 0) return '刚刚'

  const diff = Date.now() - time
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 30) return `${days}天前`
  return new Date(time).toLocaleDateString()
}

const statusText = (status) => {
  if (status === 'sold') return '已售出'
  if (status === 'removed') return '已下架'
  return '出售中'
}

const statusClass = (status) => {
  if (status === 'sold') return 'sold'
  if (status === 'removed') return 'removed'
  return 'active'
}
</script>

<style scoped>
.sales-section {
  background-color: white;
  border-radius: 12px;
  box-shadow: var(--shadow-md);
  padding: 24px;
}

.sales-section h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--gray-900);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.sales-section h3 i {
  color: var(--primary-blue);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--gray-500);
}

.empty-icon {
  font-size: 64px;
  color: var(--gray-300);
  margin-bottom: 20px;
  display: block;
}

.empty-state h4 {
  font-size: 18px;
  color: var(--gray-700);
  margin-bottom: 8px;
}

.empty-state p {
  margin-bottom: 24px;
}

.btn-primary {
  padding: 12px 24px;
  background: var(--primary-blue);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.sales-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sale-card {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: var(--gray-50);
  border-radius: 12px;
  border: 1px solid var(--gray-200);
  cursor: pointer;
  transition: all 0.2s ease;
}

.sale-card:hover {
  background: white;
  box-shadow: var(--shadow-md);
}

.book-image {
  width: 100px;
  height: 130px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  background-color: var(--gray-200);
}

.book-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.book-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--gray-900);
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-author {
  font-size: 13px;
  color: var(--gray-600);
  margin-bottom: 8px;
}

.book-info-row {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
  font-size: 12px;
  color: var(--gray-500);
}

.book-info-row i {
  margin-right: 4px;
}

.book-condition {
  color: var(--secondary-green);
}

.book-price {
  font-size: 20px;
  font-weight: 700;
  color: var(--primary-blue);
  margin-top: auto;
  margin-bottom: 8px;
}

.sale-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background: var(--light-green);
  color: var(--secondary-green);
}

.status-badge.sold {
  background: rgba(78, 99, 221, 0.12);
  color: var(--primary-blue);
}

.status-badge.removed {
  background: rgba(148, 163, 184, 0.18);
  color: var(--gray-600);
}

.sale-time {
  font-size: 12px;
  color: var(--gray-400);
}

.sale-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}

.remove-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 34px;
  padding: 0 12px;
  border: 1px solid rgba(239, 68, 68, 0.22);
  border-radius: 8px;
  background: rgba(254, 242, 242, 0.92);
  color: #b91c1c;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: background-color 0.2s, border-color 0.2s, transform 0.2s;
}

.remove-btn:hover {
  background: #fee2e2;
  border-color: rgba(239, 68, 68, 0.36);
  transform: translateY(-1px);
}

@media (max-width: 768px) {
  .sale-card {
    flex-direction: column;
  }

  .book-image {
    width: 100%;
    height: 200px;
  }
}
</style>
