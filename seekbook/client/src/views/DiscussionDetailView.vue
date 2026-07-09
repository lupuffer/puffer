<template>
  <div class="discussion-detail-page">
    <button type="button" class="back-link" @click="router.push('/knowledge?tab=discussion')">
      <i class="fas fa-arrow-left"></i>
      <span>返回知识星河</span>
    </button>

    <section v-if="discussion" class="detail-shell">
      <header class="hero-card">
        <div class="hero-top">
          <div>
            <div class="badge-row">
              <span class="type-badge" :class="typeClass">{{ discussion.type }}</span>
              <span class="time-badge">{{ formatDateTime(discussion.createdAt) }}</span>
            </div>

            <h1>{{ discussion.title }}</h1>
            <p class="meta-line">作者：{{ discussion.authorName }}</p>

            <div v-if="discussion.tags?.length" class="tags">
              <span v-for="tag in discussion.tags" :key="tag">{{ tag }}</span>
            </div>
          </div>

          <button type="button" class="like-btn" :class="{ active: liked }" @click="handleToggleLike">
            <i :class="liked ? 'fas fa-thumbs-up' : 'far fa-thumbs-up'"></i>
            <span>{{ liked ? '已点赞' : '点赞' }}</span>
          </button>
        </div>

        <div class="stats-row">
          <span><i class="far fa-eye"></i>{{ discussion.views }}</span>
          <span><i class="far fa-thumbs-up"></i>{{ discussion.likes }}</span>
          <span><i class="far fa-comment-dots"></i>{{ discussion.replies }}</span>
          <span><i class="far fa-clock"></i>{{ lastReplyText }}</span>
        </div>
      </header>

      <section class="content-card">
        <div class="section-head">
          <h2>讨论正文</h2>
        </div>
        <p class="content">{{ discussion.content }}</p>
      </section>

      <section class="reply-card">
        <CommentSection
          target-type="discussion"
          :target-id="discussion.id"
          title="回复区"
          empty-text="还没有讨论回复，来发起第一条评论吧。"
          base-placeholder="写下你的回复..."
        />
      </section>
    </section>

    <section v-else class="empty-card">
      <i class="fas fa-circle-exclamation"></i>
      <h2>讨论不存在或已被删除</h2>
      <p>你可以返回知识星河继续查看其他讨论。</p>
    </section>

    <PublishMaterialDialog
      ref="materialDialogRef"
      :open="materialDialogOpen"
      @close="materialDialogOpen = false"
      @submit="handleMaterialSubmit"
    />
    <PublishDiscussionDialog
      ref="discussionDialogRef"
      :open="discussionDialogOpen"
      @close="discussionDialogOpen = false"
      @submit="handleDiscussionSubmit"
    />
    <KnowledgeToastStack :toasts="toasts" />
  </div>
</template>

<script setup>
import { computed, inject, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CommentSection from '@/components/knowledge/CommentSection.vue'
import KnowledgeToastStack from '@/components/knowledge/KnowledgeToastStack.vue'
import PublishDiscussionDialog from '@/components/knowledge/PublishDiscussionDialog.vue'
import PublishMaterialDialog from '@/components/knowledge/PublishMaterialDialog.vue'
import { resolveBackendDiscussionByRecord } from '@/composables/useKnowledgeBackendSync'
import { useKnowledgeFeedback } from '@/composables/useKnowledgeFeedback'
import { useKnowledgeGalaxy } from '@/composables/useKnowledgeGalaxy'
import {
  createKnowledgeDiscussion as createKnowledgeDiscussionApi,
  createKnowledgeMaterial as createKnowledgeMaterialApi,
  toggleKnowledgeDiscussionLike,
} from '@/services/api'

const route = useRoute()
const router = useRouter()
const appData = inject('appData', { value: {} })

const {
  getDiscussionById,
  recordDiscussionView,
  toggleDiscussionLike,
  isDiscussionLiked,
  formatDateTime,
  formatRelativeTime,
  createMaterial,
  createDiscussion,
} = useKnowledgeGalaxy()

const { toasts, showToast } = useKnowledgeFeedback()

const materialDialogOpen = ref(false)
const discussionDialogOpen = ref(false)
const materialDialogRef = ref(null)
const discussionDialogRef = ref(null)

const currentUser = computed(() => appData.value?.appState?.user || {})
const discussionId = computed(() => Number(route.params.id))
const discussion = computed(() => getDiscussionById(discussionId.value))
const liked = computed(() => (discussion.value ? isDiscussionLiked(discussion.value.id, currentUser.value) : false))
const typeClass = computed(() => {
  if (!discussion.value) return 'is-talk'
  if (discussion.value.type === '求助') return 'is-help'
  if (discussion.value.type === '求资料') return 'is-request'
  return 'is-talk'
})
const lastReplyText = computed(() => {
  if (!discussion.value?.lastReplyAt || !discussion.value?.replies) {
    return '暂无回复'
  }
  return formatRelativeTime(discussion.value.lastReplyAt)
})

const redirectToLogin = () => {
  window.setTimeout(() => router.push('/login'), 400)
}

const ensureLoggedIn = () => {
  if (currentUser.value?.isLoggedIn) {
    return true
  }

  showToast('登录后才能使用该功能', 'warning')
  redirectToLogin()
  return false
}

const syncView = () => {
  if (discussion.value) {
    recordDiscussionView(discussion.value.id, currentUser.value)
  }
}

const resolveBackendDiscussionId = async () => {
  if (!discussion.value) {
    return 0
  }

  const backendDiscussion = await resolveBackendDiscussionByRecord(discussion.value)
  return Number(backendDiscussion?.id || 0)
}

const handleToggleLike = async () => {
  const result = toggleDiscussionLike(discussionId.value, currentUser.value)
  if (!result.ok) {
    showToast('登录后才能点赞', 'warning')
    redirectToLogin()
    return
  }

  try {
    const backendDiscussionId = await resolveBackendDiscussionId()
    if (!backendDiscussionId) {
      throw new Error('没有找到对应的后端讨论记录')
    }
    await toggleKnowledgeDiscussionLike(backendDiscussionId)
  } catch (error) {
    showToast(error.message || '点赞状态已在当前页面更新，但后端同步稍后重试。', 'warning')
  }
}

const openMaterialDialog = () => {
  if (!ensureLoggedIn()) {
    return
  }
  materialDialogOpen.value = true
}

const openDiscussionDialog = () => {
  if (!ensureLoggedIn()) {
    return
  }
  discussionDialogOpen.value = true
}

const handleMaterialSubmit = async (payload) => {
  const result = await createMaterial(payload, currentUser.value)
  if (!result.ok) {
    showToast(result.message, result.code === 'login_required' ? 'warning' : 'error')
    if (result.code === 'login_required') {
      redirectToLogin()
    }
    return
  }

  try {
    await createKnowledgeMaterialApi({
      title: payload.title,
      description: payload.description,
      category: payload.category,
      course: payload.course,
      pricePoints: payload.pricePoints,
      tags: payload.tags,
      fileType: payload.file?.type || payload.file?.name?.split('.').pop() || 'other',
      fileSize: payload.file?.size || '',
    })
  } catch {
    showToast('资料已写入当前页面，但后端同步稍后重试。', 'warning')
  }

  materialDialogOpen.value = false
  materialDialogRef.value?.resetForm()
  showToast(result.message, 'success')
}

const handleDiscussionSubmit = async (payload) => {
  const result = createDiscussion(payload, currentUser.value)
  if (!result.ok) {
    showToast(result.message, result.code === 'login_required' ? 'warning' : 'error')
    if (result.code === 'login_required') {
      redirectToLogin()
    }
    return
  }

  try {
    await createKnowledgeDiscussionApi(payload)
  } catch {
    showToast('讨论已写入当前页面，但后端同步稍后重试。', 'warning')
  }

  discussionDialogOpen.value = false
  discussionDialogRef.value?.resetForm()
  showToast(result.message, 'success')
}

const handleOpenUploadEvent = () => openMaterialDialog()
const handleOpenDiscussionEvent = () => openDiscussionDialog()

onMounted(() => {
  syncView()
  window.addEventListener('open-knowledge-upload', handleOpenUploadEvent)
  window.addEventListener('open-knowledge-discussion', handleOpenDiscussionEvent)
})

watch(discussionId, () => syncView())

onBeforeUnmount(() => {
  window.removeEventListener('open-knowledge-upload', handleOpenUploadEvent)
  window.removeEventListener('open-knowledge-discussion', handleOpenDiscussionEvent)
})
</script>

<style scoped>
.discussion-detail-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
  max-width: 980px;
  margin: 0 auto;
}

.back-link {
  align-self: flex-start;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 40px;
  padding: 0 14px;
  border: none;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.82);
  color: #3856c5;
  font-weight: 700;
  cursor: pointer;
}

.detail-shell {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.hero-card,
.content-card,
.reply-card,
.empty-card {
  padding: 22px;
  border-radius: 24px;
  border: 1px solid rgba(224, 232, 255, 0.96);
  background: #fff;
  box-shadow: 0 18px 40px rgba(90, 107, 162, 0.12);
}

.badge-row,
.tags,
.stats-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hero-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

.type-badge,
.time-badge,
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

.time-badge,
.tags span {
  background: #f6f8ff;
  color: #61708d;
}

.hero-card h1 {
  margin-top: 14px;
  color: #17233a;
  font-size: clamp(28px, 3vw, 38px);
  line-height: 1.2;
}

.meta-line {
  margin-top: 10px;
  color: #61708d;
}

.tags {
  margin-top: 14px;
}

.stats-row {
  margin-top: 16px;
  color: #71819a;
  font-size: 13px;
}

.stats-row span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.like-btn {
  min-height: 44px;
  margin-top: 18px;
  padding: 0 16px;
  border: none;
  border-radius: 14px;
  background: #f5f7ff;
  color: #4b5f90;
  font-weight: 700;
  cursor: pointer;
}

.like-btn.active {
  background: #e9efff;
  color: #2f5ae0;
}

.section-head {
  margin-bottom: 14px;
}

.section-head h2 {
  color: #18233b;
  font-size: 22px;
}

.content {
  color: #5d6f89;
  line-height: 1.95;
  white-space: pre-wrap;
}

.empty-card {
  min-height: 220px;
  display: grid;
  place-items: center;
  text-align: center;
  color: #6f819b;
}

.empty-card i {
  font-size: 40px;
  color: #93a4be;
  margin-bottom: 12px;
}

@media (max-width: 720px) {
  .hero-top {
    flex-direction: column;
  }
}
</style>
