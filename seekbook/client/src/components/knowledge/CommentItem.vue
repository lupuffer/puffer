<template>
  <article class="comment-item" :class="{ deleted: comment.isDeleted }">
    <div class="comment-head">
      <div class="author-meta">
        <strong>{{ comment.authorName }}</strong>
        <span>{{ formatDateTime(comment.createdAt) }}</span>
      </div>
      <div class="actions">
        <button
          v-if="showReply"
          type="button"
          class="link-btn"
          :disabled="comment.isDeleted"
          @click="$emit('reply', comment)"
        >
          回复
        </button>
        <button v-if="canDelete && !comment.isDeleted" type="button" class="link-btn danger" @click="$emit('delete', comment)">
          删除
        </button>
      </div>
    </div>

    <p class="comment-content" :class="{ muted: comment.isDeleted }">
      {{ comment.isDeleted ? '该评论已删除' : comment.content }}
    </p>

    <div v-if="replies.length" class="reply-list">
      <article v-for="reply in replies" :key="reply.id" class="reply-item" :class="{ deleted: reply.isDeleted }">
        <div class="comment-head">
          <div class="author-meta">
            <strong>{{ reply.authorName }}</strong>
            <span>{{ formatDateTime(reply.createdAt) }}</span>
          </div>
          <div class="actions">
            <button
              v-if="currentUserId === reply.authorId && !reply.isDeleted"
              type="button"
              class="link-btn danger"
              @click="$emit('delete', reply)"
            >
              删除
            </button>
          </div>
        </div>
        <p class="comment-content" :class="{ muted: reply.isDeleted }">
          {{ reply.isDeleted ? '该评论已删除' : reply.content }}
        </p>
      </article>
    </div>
  </article>
</template>

<script setup>
defineProps({
  comment: {
    type: Object,
    required: true,
  },
  replies: {
    type: Array,
    default: () => [],
  },
  currentUserId: {
    type: String,
    default: '',
  },
  formatDateTime: {
    type: Function,
    required: true,
  },
  showReply: {
    type: Boolean,
    default: true,
  },
  canDelete: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['reply', 'delete'])
</script>

<style scoped>
.comment-item,
.reply-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  border-radius: 18px;
  background: #fff;
  border: 1px solid #e8eeff;
}

.comment-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.author-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.author-meta strong {
  color: #23314e;
}

.author-meta span {
  color: #73839c;
  font-size: 12px;
}

.actions {
  display: flex;
  gap: 10px;
}

.link-btn {
  border: none;
  background: transparent;
  color: #3557d1;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}

.link-btn:disabled {
  color: #9aa7bc;
  cursor: not-allowed;
}

.link-btn.danger {
  color: #dc2626;
}

.comment-content {
  color: #53637c;
  line-height: 1.8;
  white-space: pre-wrap;
}

.comment-content.muted {
  color: #9aa7bc;
}

.reply-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-left: 22px;
  padding-left: 14px;
  border-left: 2px solid #edf2ff;
}

.comment-item.deleted,
.reply-item.deleted {
  background: #fafbfe;
}

@media (max-width: 640px) {
  .comment-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .reply-list {
    margin-left: 10px;
    padding-left: 10px;
  }
}
</style>
