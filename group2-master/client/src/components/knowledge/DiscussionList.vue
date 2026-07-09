<template>
  <div class="discussion-list">
    <DiscussionCard
      v-for="discussion in discussions"
      :key="discussion.id"
      :discussion="discussion"
      :format-relative-time="formatRelativeTime"
      :liked="isLiked(discussion.id)"
      :show-delete="showDelete"
      @like="$emit('like', $event)"
      @delete="$emit('delete', $event)"
    />

    <div v-if="!discussions.length" class="empty-state">
      <i class="fas fa-comments"></i>
      <p>{{ emptyText }}</p>
      <button type="button" class="empty-btn" @click="$emit('create')">发起讨论</button>
    </div>
  </div>
</template>

<script setup>
import DiscussionCard from './DiscussionCard.vue'

defineProps({
  discussions: {
    type: Array,
    default: () => [],
  },
  formatRelativeTime: {
    type: Function,
    required: true,
  },
  isLiked: {
    type: Function,
    required: true,
  },
  showDelete: {
    type: Boolean,
    default: false,
  },
  emptyText: {
    type: String,
    default: '还没有讨论，来发起第一个话题吧。',
  },
})

defineEmits(['like', 'create', 'delete'])
</script>

<style scoped>
.discussion-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.empty-state {
  padding: 48px 24px;
  border-radius: 22px;
  border: 1px dashed rgba(196, 210, 247, 0.96);
  background: rgba(255, 255, 255, 0.72);
  text-align: center;
  color: #6b7c96;
}

.empty-state i {
  margin-bottom: 12px;
  font-size: 36px;
  color: #94a3bd;
}

.empty-btn {
  min-height: 40px;
  margin-top: 14px;
  padding: 0 16px;
  border: none;
  border-radius: 999px;
  color: #fff;
  font-weight: 700;
  cursor: pointer;
  background: linear-gradient(135deg, #2f80ed 0%, #6f84ff 64%, #a78bfa 100%);
}
</style>
