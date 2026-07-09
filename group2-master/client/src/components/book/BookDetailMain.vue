<template>
  <section class="book-main-info">
    <div class="book-top-grid">
      <div class="book-cover-panel">
        <div class="cover-stage">
          <img :src="book.image" :alt="book.title" loading="lazy" />
        </div>
        <div class="book-attributes" aria-label="书籍属性">
          <span class="attribute-pill">{{ book.condition }}</span>
          <span v-if="book.hasNotes" class="attribute-pill">{{ labels.hasNotes }}</span>
          <span class="attribute-pill">{{ book.campus }}</span>
        </div>
      </div>

      <div class="book-basic-info">
        <h1>{{ book.title }}</h1>
        <div class="book-meta-info">
          <div v-for="item in metaItems" :key="item.label" class="meta-item">
            <i :class="item.icon"></i>
            <div><span class="meta-label">{{ item.label }}</span><span class="meta-value">{{ item.value }}</span></div>
          </div>
        </div>
      </div>
    </div>

    <div class="book-bottom-grid">
      <section class="support-card description-card">
        <div class="support-card-head">
          <i class="fas fa-align-left"></i>
          <h3>补充说明</h3>
        </div>
        <p class="description-text">{{ descriptionText }}</p>
      </section>

      <section v-if="tagList.length" class="support-card tags-card">
        <div class="support-card-head">
          <i class="fas fa-tags"></i>
          <h3>标签</h3>
        </div>
        <div class="tag-list">
          <span v-for="tag in tagList" :key="tag" class="tag-chip">{{ tag }}</span>
        </div>
      </section>

      <section class="support-card seller-card">
        <div class="support-card-head">
          <i class="fas fa-user-circle"></i>
          <h3>卖家信息</h3>
        </div>
        <div class="seller-card-body">
          <div class="seller-avatar"><i class="fas fa-user"></i></div>
          <div class="seller-copy">
            <strong>{{ sellerName }}</strong>
            <p>{{ book.campus }} · 信誉 {{ sellerCreditScore }} 分 · {{ sellerCreditLabel }}</p>
          </div>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { getCreditLabel, normalizeCreditScore } from '../../utils/credit'

const props = defineProps({
  book: { type: Object, required: true },
  labels: { type: Object, required: true },
})

const metaItems = computed(() => [
  { icon: 'fas fa-user', label: '作者', value: props.book.author },
  { icon: 'fas fa-building', label: '出版社', value: props.book.publisher },
  { icon: 'fas fa-barcode', label: 'ISBN', value: props.book.isbn },
  { icon: 'fas fa-bookmark', label: '分类', value: props.book.category },
])

const tagList = computed(() => props.book.tags || [])
const descriptionText = computed(() => props.book.description || '卖家还没有补充这本书的详细描述。')
const sellerName = computed(() => props.book.seller?.name || props.book.sellerName || '未知卖家')
const sellerCreditScore = computed(() => normalizeCreditScore(props.book.sellerCreditScore ?? props.book.seller?.creditScore, 100))
const sellerCreditLabel = computed(() => getCreditLabel(sellerCreditScore.value))
</script>

<style scoped>
.book-main-info {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.book-top-grid {
  display: grid;
  grid-template-columns: minmax(240px, 340px) minmax(0, 1fr);
  gap: 30px;
  align-items: start;
}

.book-cover-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
}

.cover-stage {
  width: 100%;
  min-height: 360px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 26px 20px;
  border-radius: 18px;
  border: 1px solid rgba(224, 232, 255, 0.96);
  background:
    radial-gradient(circle at 50% 8%, rgba(167, 139, 250, 0.12), transparent 38%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.76), rgba(242, 246, 255, 0.66));
  box-shadow: 0 16px 34px rgba(92, 107, 164, 0.1);
}

.cover-stage img {
  width: min(86%, 250px);
  max-height: 320px;
  object-fit: contain;
  border-radius: 6px;
  filter: drop-shadow(0 18px 20px rgba(31, 41, 55, 0.18));
}

.book-attributes {
  display: flex;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
  width: 100%;
}

.attribute-pill {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid rgba(124, 140, 255, 0.22);
  background: rgba(238, 246, 255, 0.74);
  color: #4561da;
  font-size: 12px;
  font-weight: 700;
}

.book-basic-info h1 {
  font-size: 32px;
  font-weight: 700;
  color: var(--gray-900);
  margin-bottom: 20px;
  line-height: 1.2;
}

.book-meta-info {
  border-radius: 18px;
  padding: 24px;
  border: 1px solid rgba(224, 232, 255, 0.96);
  background: rgba(255, 255, 255, 0.76);
  box-shadow: 0 16px 34px rgba(92, 107, 164, 0.1);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--gray-200);
}

.meta-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.meta-item i {
  color: var(--primary-blue);
  font-size: 20px;
  width: 24px;
  text-align: center;
}

.meta-label {
  display: block;
  font-size: 13px;
  color: var(--gray-500);
  margin-bottom: 4px;
  font-weight: 500;
}

.meta-value {
  display: block;
  font-size: 15px;
  color: var(--gray-800);
  font-weight: 600;
}

.book-bottom-grid {
  display: grid;
  grid-template-columns: minmax(0, 0.88fr) minmax(0, 1.12fr);
  gap: 16px;
}

.support-card {
  border-radius: 18px;
  border: 1px solid rgba(224, 232, 255, 0.96);
  background:
    radial-gradient(circle at 92% 8%, rgba(124, 140, 255, 0.08), transparent 30%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.68), rgba(246, 249, 255, 0.58));
  box-shadow: 0 16px 34px rgba(92, 107, 164, 0.1);
  padding: 18px 20px;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.support-card-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}

.support-card-head i {
  color: var(--primary-blue);
  font-size: 17px;
}

.support-card-head h3 {
  color: var(--gray-900);
  font-size: 16px;
  font-weight: 700;
}

.seller-card {
  grid-column: 1 / -1;
}

.seller-card-body {
  display: flex;
  align-items: center;
  gap: 14px;
}

.seller-avatar {
  width: 54px;
  height: 54px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(238, 246, 255, 0.96), rgba(237, 231, 255, 0.88));
  color: var(--primary-blue);
  font-size: 23px;
  flex-shrink: 0;
}

.seller-copy strong {
  display: block;
  color: var(--gray-900);
  font-size: 17px;
  font-weight: 700;
}

.seller-copy p,
.description-text {
  color: var(--gray-600);
  font-size: 14px;
  line-height: 1.7;
}

.seller-copy p {
  margin-top: 6px;
}

.description-text {
  white-space: pre-wrap;
  word-break: break-word;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid rgba(124, 140, 255, 0.22);
  background: rgba(240, 245, 255, 0.9);
  color: #4966df;
  font-size: 13px;
  font-weight: 700;
}

@media (max-width: 720px) {
  .book-top-grid {
    grid-template-columns: 1fr;
  }

  .cover-stage {
    min-height: 300px;
  }

  .cover-stage img {
    width: min(78%, 240px);
    max-height: 280px;
  }

  .book-bottom-grid {
    grid-template-columns: 1fr;
  }
}
</style>
