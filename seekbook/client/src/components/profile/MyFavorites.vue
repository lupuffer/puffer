<template>
  <section class="favorites-section">
    <h3><i class="fas fa-heart"></i> 我的收藏</h3>
    
    <div v-if="favorites.length === 0" class="empty-state">
      <i class="far fa-heart empty-icon"></i>
      <h4>还没有收藏的书籍</h4>
      <p>在书籍详情页点击"加入收藏"即可收藏</p>
      <button class="btn btn-primary" type="button" @click="goBuy">
        去浏览书籍
      </button>
    </div>
    
    <div v-else class="favorites-grid">
      <article
        v-for="book in favorites"
        :key="book.id"
        class="favorite-card"
        @click="viewBook(book)"
      >
        <div class="book-image">
          <img :src="book.image || book.img || '/images/book1.jpg'" :alt="book.title" loading="lazy" />
          <button
            class="remove-btn"
            type="button"
            @click.stop="removeFavorite(book.id)"
            title="取消收藏"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="book-info">
          <h4 class="book-title">{{ book.title || book.name }}</h4>
          <p class="book-author">{{ book.author || book.bookAuthor || '未知作者' }}</p>
          <div class="book-meta">
            <span class="book-price">¥{{ (book.price || 0).toFixed(2) }}</span>
            <span v-if="book.condition" class="book-condition">{{ book.condition }}</span>
          </div>
          <p class="book-campus">
            <i class="fas fa-map-marker-alt"></i>
            {{ book.campus || '紫金港校区' }}
          </p>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const props = defineProps({
  favorites: { type: Array, default: () => [] },
  labels: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['remove', 'view'])

const removeFavorite = (bookId) => {
  emit('remove', bookId)
}

const viewBook = (book) => {
  emit('view', book)
}

const goBuy = () => {
  router.push('/buy')
}
</script>

<style scoped>
.favorites-section {
  background-color: white;
  border-radius: 12px;
  box-shadow: var(--shadow-md);
  padding: 24px;
}

.favorites-section h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--gray-900);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.favorites-section h3 i {
  color: #ef4444;
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

.favorites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.favorite-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--gray-200);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.favorite-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.book-image {
  position: relative;
  height: 180px;
  background-color: var(--gray-100);
  overflow: hidden;
}

.book-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 28px;
  height: 28px;
  background: rgba(239, 68, 68, 0.9);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  transition: background 0.2s ease;
}

.remove-btn:hover {
  background: #dc2626;
}

.book-info {
  padding: 16px;
}

.book-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--gray-900);
  margin-bottom: 6px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-author {
  font-size: 13px;
  color: var(--gray-600);
  margin-bottom: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.book-price {
  font-size: 18px;
  font-weight: 700;
  color: var(--primary-blue);
}

.book-condition {
  font-size: 12px;
  padding: 4px 8px;
  background: var(--light-green);
  color: var(--secondary-green);
  border-radius: 4px;
}

.book-campus {
  font-size: 12px;
  color: var(--gray-500);
  display: flex;
  align-items: center;
  gap: 4px;
}

@media (max-width: 768px) {
  .favorites-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
}
</style>