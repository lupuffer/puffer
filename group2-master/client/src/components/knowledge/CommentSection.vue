<template>
  <section class="comment-section">
    <div class="section-head">
      <h2>{{ title }}</h2>
      <span>{{ totalComments }} 条评论</span>
    </div>

    <div v-if="topLevelComments.length" class="comment-list">
      <CommentItem
        v-for="comment in topLevelComments"
        :key="comment.id"
        :comment="comment"
        :replies="getRepliesByParentId(comment.id)"
        :current-user-id="currentUserId"
        :format-date-time="formatDateTime"
        :can-delete="currentUserId === comment.authorId"
        @reply="handleReply"
        @delete="handleDeleteRequest"
      />
    </div>

    <div v-else class="empty-state">
      <i class="far fa-comments"></i>
      <p>{{ emptyText }}</p>
    </div>

    <CommentInput
      v-model="draft"
      :reply-target="replyTarget"
      :placeholder="inputPlaceholder"
      @submit="handleSubmit"
      @cancel-reply="clearReplyTarget"
      @focus="handleInputFocus"
    />

    <KnowledgeConfirmDialog
      :open="confirmState.open"
      :title="confirmState.title"
      :message="confirmState.message"
      :confirm-text="confirmState.confirmText"
      :cancel-text="confirmState.cancelText"
      @confirm="acceptConfirm"
      @cancel="cancelConfirm"
    />
    <KnowledgeToastStack :toasts="toasts" />
  </section>
</template>

<script setup>
import { computed, inject, ref } from 'vue'
import { useRouter } from 'vue-router'
import CommentInput from './CommentInput.vue'
import CommentItem from './CommentItem.vue'
import KnowledgeConfirmDialog from './KnowledgeConfirmDialog.vue'
import KnowledgeToastStack from './KnowledgeToastStack.vue'
import {
  resolveBackendDiscussionByRecord,
  resolveBackendMaterialByRecord,
} from '@/composables/useKnowledgeBackendSync'
import { useKnowledgeFeedback } from '@/composables/useKnowledgeFeedback'
import { useKnowledgeGalaxy } from '@/composables/useKnowledgeGalaxy'
import { createKnowledgeComment, deleteKnowledgeComment } from '@/services/api'

const props = defineProps({
  targetType: {
    type: String,
    required: true,
  },
  targetId: {
    type: Number,
    required: true,
  },
  title: {
    type: String,
    default: '回复区',
  },
  emptyText: {
    type: String,
    default: '还没有回复，来留下第一条评论吧。',
  },
  basePlaceholder: {
    type: String,
    default: '写下你的回复...',
  },
})

const router = useRouter()
const appData = inject('appData', { value: {} })
const {
  getCommentsByTarget,
  getTopLevelComments,
  getRepliesByParentId,
  createComment,
  bindCommentBackendId,
  deleteComment,
  formatDateTime,
  getMaterialById,
  getDiscussionById,
} = useKnowledgeGalaxy()
const { toasts, confirmState, showToast, requestConfirm, acceptConfirm, cancelConfirm } = useKnowledgeFeedback()

const draft = ref('')
const replyTarget = ref(null)

const currentUser = computed(() => appData.value?.appState?.user || {})
const currentUserId = computed(() => {
  const user = currentUser.value
  if (!user?.isLoggedIn) {
    return ''
  }
  return String(user.id || user.email || user.name || '')
})

const topLevelComments = computed(() => getTopLevelComments(props.targetType, props.targetId))
const totalComments = computed(() => getCommentsByTarget(props.targetType, props.targetId).length)
const inputPlaceholder = computed(() =>
  replyTarget.value ? `回复 @${replyTarget.value.authorName}...` : props.basePlaceholder,
)

const resolveBackendTargetId = async () => {
  if (props.targetType === 'material') {
    const target = getMaterialById(props.targetId)
    const backendTarget = await resolveBackendMaterialByRecord(target)
    return Number(backendTarget?.id || 0)
  }

  if (props.targetType === 'discussion') {
    const target = getDiscussionById(props.targetId)
    const backendTarget = await resolveBackendDiscussionByRecord(target)
    return Number(backendTarget?.id || 0)
  }

  return 0
}

const redirectToLogin = () => {
  window.setTimeout(() => router.push('/login'), 400)
}

const ensureLoggedIn = (message = '登录后才能使用该功能') => {
  if (currentUser.value?.isLoggedIn) {
    return true
  }

  showToast(message, 'warning')
  redirectToLogin()
  return false
}

const handleReply = (comment) => {
  if (comment.isDeleted) {
    showToast('该评论已删除，不能继续回复。', 'warning')
    return
  }

  if (!ensureLoggedIn('登录后才能回复')) {
    return
  }

  replyTarget.value = comment
}

const clearReplyTarget = () => {
  replyTarget.value = null
}

const handleInputFocus = () => {
  ensureLoggedIn('登录后才能回复')
}

const friendlySyncMessage = (fallback) => {
  return fallback || '评论已保存到当前页面，但后端同步失败。请确认后端服务已启动后再试。'
}

const handleSubmit = async () => {
  if (!ensureLoggedIn('登录后才能回复')) {
    return
  }

  const previousReplyTarget = replyTarget.value
  const result = createComment(
    {
      targetType: props.targetType,
      targetId: props.targetId,
      parentId: previousReplyTarget?.id ?? null,
      content: draft.value,
    },
    currentUser.value,
  )

  if (!result.ok) {
    showToast(result.message, result.code === 'login_required' ? 'warning' : 'error')
    if (result.code === 'login_required') {
      redirectToLogin()
    }
    return
  }

  draft.value = ''
  replyTarget.value = null
  showToast(result.message, 'success')

  try {
    const backendTargetId = await resolveBackendTargetId()
    if (!backendTargetId) {
      throw new Error('没有找到对应的后端内容记录')
    }

    const backendParentId = previousReplyTarget?.backendId || previousReplyTarget?.parentBackendId || null
    const response = await createKnowledgeComment({
      targetType: props.targetType,
      targetId: backendTargetId,
      parentId: backendParentId,
      content: result.comment.content,
    })

    bindCommentBackendId(result.comment.id, response?.data?.id || 0, backendParentId)
  } catch (error) {
    const isGatewayError = String(error?.message || '').includes('502')
    showToast(
      isGatewayError
        ? '评论已保存到当前页面，但后端服务暂时不可用，请稍后重试。'
        : friendlySyncMessage(error?.message),
      'warning',
    )
  }
}

const handleDeleteRequest = async (comment) => {
  if (!ensureLoggedIn('登录后才能删除回复')) {
    return
  }

  const accepted = await requestConfirm({
    title: '删除回复',
    message: '删除后内容将显示为“该评论已删除”，是否继续？',
    confirmText: '确认删除',
    cancelText: '取消',
  })

  if (!accepted) {
    return
  }

  const result = deleteComment(comment.id, currentUser.value)
  if (!result.ok) {
    showToast(result.message, result.code === 'login_required' ? 'warning' : 'error')
    if (result.code === 'login_required') {
      redirectToLogin()
    }
    return
  }

  if (replyTarget.value?.id === comment.id) {
    replyTarget.value = null
  }

  try {
    await deleteKnowledgeComment(comment.backendId || comment.id)
  } catch (error) {
    const isGatewayError = String(error?.message || '').includes('502')
    showToast(
      isGatewayError
        ? '评论已在当前页面删除，但后端服务暂时不可用，请稍后重试。'
        : error?.message || '评论已在当前页面删除，但后端同步稍后重试。',
      'warning',
    )
    return
  }

  showToast(result.message, 'success')
}
</script>

<style scoped>
.comment-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.section-head h2 {
  color: #18233b;
  font-size: 22px;
}

.section-head span {
  color: #6f809b;
  font-size: 13px;
  font-weight: 700;
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.empty-state {
  min-height: 160px;
  display: grid;
  place-items: center;
  text-align: center;
  border-radius: 20px;
  border: 1px dashed #d8e2ff;
  background: #fbfcff;
  color: #6f819b;
}

.empty-state i {
  font-size: 34px;
  color: #9aabc2;
  margin-bottom: 12px;
}
</style>
