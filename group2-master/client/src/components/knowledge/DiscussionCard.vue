<template>
  <article class="discussion-card" @click="goDetail">
    <div class="head-row">
      <span class="type-badge" :class="typeClass">{{ discussion.type }}</span>
      <span class="time">{{ formatRelativeTime(discussion.createdAt) }}</span>
    </div>

    <h3>{{ discussion.title }}</h3>
    <p class="content">{{ discussion.content }}</p>

    <div v-if="discussion.tags?.length" class="tags">
      <span v-for="tag in discussion.tags" :key="tag">{{ tag }}</span>
    </div>

    <div class="foot-row">
      <div class="meta">
        <span><i class="fas fa-user"></i>{{ discussion.authorName }}</span>
        <span><i class="far fa-eye"></i>{{ discussion.views }}</span>
        <span><i class="far fa-thumbs-up"></i>{{ discussion.likes }}</span>
        <span><i class="far fa-comment-dots"></i>{{ discussion.replies }}</span>
        <span><i class="far fa-clock"></i>{{ lastReplyText }}</span>
      </div>
      <div class="actions">
        <button
          v-if="showDelete"
          type="button"
          class="like-btn danger"
          title="删除讨论"
          @click.stop="$emit('delete', discussion.id)"
        >
          <i class="far fa-trash-can"></i>
          <span>删除</span>
        </button>
        <button type="button" class="like-btn" :class="{ active: liked }" @click.stop="$emit('like', discussion.id)">
          <i :class="liked ? 'fas fa-thumbs-up' : 'far fa-thumbs-up'"></i>
          <span>{{ liked ? '已点赞' : '点赞' }}</span>
        </button>
        <button type="button" class="detail-btn" @click.stop="goDetail">进入讨论</button>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  discussion: {
    type: Object,
    required: true,
  },
  formatRelativeTime: {
    type: Function,
    required: true,
  },
  liked: {
    type: Boolean,
    default: false,
  },
  showDelete: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['like', 'delete'])

const router = useRouter()

const typeClass = computed(() => {
  if (props.discussion.type === '求助') return 'is-help'
  if (props.discussion.type === '求资料') return 'is-request'
  return 'is-talk'
})

const lastReplyText = computed(() => {
  if (!props.discussion.lastReplyAt || !props.discussion.replies) {
    return '暂无回复'
  }
  return props.formatRelativeTime(props.discussion.lastReplyAt)
})

const goDetail = () => {
  router.push(`/knowledge/discussion/${props.discussion.id}`)
}
</script>

<style scoped>
.discussion-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 18px;
  border-radius: 20px;
  border: 1px solid rgba(224, 232, 255, 0.96);
  background: #fff;
  box-shadow: 0 14px 34px rgba(92, 107, 164, 0.1);
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}

.discussion-card:hover {
  transform: translateY(-2px);
  border-color: rgba(99, 123, 255, 0.36);
  box-shadow: 0 20px 42px rgba(92, 107, 164, 0.16);
}

.head-row,
.foot-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.type-badge,
.tags span {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.type-badge {
  background: #ecefff;
  color: #465ed2;
}

.type-badge.is-help {
  background: #fff1df;
  color: #d97706;
}

.type-badge.is-request {
  background: #edf8ef;
  color: #15803d;
}

.time {
  color: #7d8da7;
  font-size: 13px;
}

.discussion-card h3 {
  font-size: 18px;
  color: #17233a;
  line-height: 1.35;
}

.content {
  color: #65748c;
  line-height: 1.7;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.tags,
.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tags span {
  background: #f6f8ff;
  color: #61708d;
}

.meta {
  color: #708096;
  font-size: 13px;
}

.meta span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.detail-btn {
  min-height: 34px;
  padding: 0 12px;
  border: none;
  border-radius: 999px;
  background: #f3f6ff;
  color: #3b57c7;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.like-btn {
  min-height: 34px;
  padding: 0 12px;
  border: none;
  border-radius: 999px;
  background: #f6f8ff;
  color: #51627d;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.like-btn.active {
  background: #e9efff;
  color: #2f5ae0;
}

.like-btn.danger {
  background: #fff1f2;
  color: #be123c;
}

.like-btn.danger:hover {
  background: #ffe4e6;
}

@media (max-width: 640px) {
  .foot-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .actions {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
