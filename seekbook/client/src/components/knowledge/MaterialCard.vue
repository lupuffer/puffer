<template>
  <article class="material-card" @click="goDetail">
    <div class="card-head">
      <div class="badge-row">
        <span class="file-badge">{{ material.fileType }}</span>
        <span class="category-badge">{{ material.category }}</span>
        <span class="price-badge" :class="priceClass">{{ priceLabel }}</span>
      </div>
      <button type="button" class="detail-link" @click.stop="goDetail">查看详情</button>
    </div>

    <h3 class="title">{{ material.title }}</h3>

    <div class="course-row">
      <p v-if="material.course" class="course">{{ material.course }}</p>
      <div v-if="material.tags?.length" class="tags">
        <span v-for="tag in material.tags" :key="tag">{{ tag }}</span>
      </div>
    </div>

    <p class="description">{{ material.description }}</p>

    <div class="card-foot">
      <div class="meta-grid">
        <span><i class="fas fa-user"></i>{{ material.authorName }}</span>
        <span><i class="far fa-clock"></i>{{ formatRelativeTime(material.createdAt) }}</span>
        <span><i class="fas fa-download"></i>{{ material.downloads }}</span>
        <span><i class="far fa-eye"></i>{{ material.views }}</span>
        <span><i class="far fa-thumbs-up"></i>{{ material.likes }}</span>
      </div>

      <div class="actions">
        <button
          v-if="showDelete"
          type="button"
          class="action-btn danger"
          title="删除资料"
          @click.stop="$emit('delete', material.id)"
        >
          <i class="far fa-trash-can"></i>
          <span>删除</span>
        </button>
        <button type="button" class="action-btn" :class="{ active: liked }" @click.stop="$emit('like', material.id)">
          <i :class="liked ? 'fas fa-thumbs-up' : 'far fa-thumbs-up'"></i>
          <span>{{ liked ? '已点赞' : '点赞' }}</span>
        </button>
        <button
          type="button"
          class="action-btn"
          :class="{ active: favorited }"
          @click.stop="$emit('favorite', material.id)"
        >
          <i :class="favorited ? 'fas fa-bookmark' : 'far fa-bookmark'"></i>
          <span>{{ favorited ? '已收藏' : '收藏' }}</span>
        </button>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  material: {
    type: Object,
    required: true,
  },
  priceLabel: {
    type: String,
    default: '免费',
  },
  liked: {
    type: Boolean,
    default: false,
  },
  favorited: {
    type: Boolean,
    default: false,
  },
  formatRelativeTime: {
    type: Function,
    required: true,
  },
  showDelete: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['like', 'favorite', 'delete'])

const router = useRouter()

const priceClass = computed(() => {
  if (props.material.pricePoints === 0) return 'is-free'
  if (props.material.pricePoints > 0) return 'is-points'
  return ''
})

const goDetail = () => {
  router.push(`/knowledge/material/${props.material.id}`)
}
</script>

<style scoped>
.material-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px 18px;
  border-radius: 20px;
  border: 1px solid rgba(224, 232, 255, 0.96);
  background: #fff;
  box-shadow: 0 14px 34px rgba(92, 107, 164, 0.1);
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}

.material-card:hover {
  transform: translateY(-2px);
  border-color: rgba(99, 123, 255, 0.36);
  box-shadow: 0 20px 42px rgba(92, 107, 164, 0.16);
}

.card-head,
.card-foot {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.badge-row,
.tags,
.meta-grid,
.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.file-badge,
.category-badge,
.price-badge,
.tags span {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.file-badge {
  background: #e8f0ff;
  color: #2f5ae0;
}

.category-badge {
  background: #f3f6ff;
  color: #61708d;
}

.price-badge.is-free {
  background: #eaf3ff;
  color: #1d4ed8;
}

.price-badge.is-points {
  background: #fff3e8;
  color: #d97706;
}

.detail-link,
.action-btn {
  border: none;
  cursor: pointer;
}

.detail-link {
  min-height: 32px;
  padding: 0 12px;
  border-radius: 999px;
  background: #f3f6ff;
  color: #3b57c7;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

.title {
  font-size: 18px;
  color: #17233a;
  line-height: 1.35;
}

.course-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 10px;
}

.course {
  color: #4c5d78;
  font-weight: 600;
}

.description {
  color: #65748c;
  line-height: 1.7;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.tags span {
  background: #f6f8ff;
  color: #61708d;
}

.card-foot {
  padding-top: 12px;
  border-top: 1px solid #edf2ff;
}

.meta-grid {
  color: #708096;
  font-size: 13px;
  flex: 1;
}

.meta-grid span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.actions {
  align-items: center;
  justify-content: flex-end;
  flex-shrink: 0;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 32px;
  padding: 0 11px;
  border-radius: 11px;
  background: #f6f8ff;
  color: #53637c;
  font-size: 12px;
  font-weight: 700;
}

.action-btn.active {
  background: #e9efff;
  color: #2f5ae0;
}

.action-btn.danger {
  background: #fff1f2;
  color: #be123c;
}

.action-btn.danger:hover {
  background: #ffe4e6;
}

@media (max-width: 640px) {
  .card-head,
  .card-foot {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
