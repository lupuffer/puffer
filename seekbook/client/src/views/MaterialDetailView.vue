<template>
  <div class="material-detail-page">
    <button type="button" class="back-link" @click="router.push('/knowledge')">
      <i class="fas fa-arrow-left"></i>
      <span>返回知识星河</span>
    </button>

    <section v-if="material" class="detail-shell">
      <header class="hero-card">
        <div class="hero-main">
          <div class="badge-row">
            <span class="file-badge">{{ material.fileType }}</span>
            <span class="category-badge">{{ material.category }}</span>
            <span class="price-badge" :class="downloadMeta.tone">{{ formatPrice(material.pricePoints) }}</span>
          </div>
          <h1>{{ material.title }}</h1>
          <p class="description">{{ material.description }}</p>
          <p v-if="material.course" class="course">关联课程：{{ material.course }}</p>

          <div v-if="material.tags?.length" class="tags">
            <span v-for="tag in material.tags" :key="tag">{{ tag }}</span>
          </div>

          <div class="meta-grid">
            <span><i class="fas fa-user"></i>{{ material.authorName }}</span>
            <span><i class="far fa-clock"></i>{{ formatDateTime(material.createdAt) }}</span>
            <span><i class="fas fa-download"></i>{{ material.downloads }}</span>
            <span><i class="far fa-eye"></i>{{ material.views }}</span>
            <span><i class="far fa-thumbs-up"></i>{{ material.likes }}</span>
            <span><i class="far fa-bookmark"></i>{{ material.favorites }}</span>
            <span><i class="far fa-file"></i>{{ formatFileSize(material.fileSize) }}</span>
          </div>
        </div>

        <div class="hero-actions">
          <button type="button" class="download-btn" :class="downloadMeta.tone" @click="handleDownload">
            {{ downloadMeta.text }}
          </button>
          <button type="button" class="secondary-btn" :class="{ active: liked }" @click="handleToggleLike">
            <i :class="liked ? 'fas fa-thumbs-up' : 'far fa-thumbs-up'"></i>
            <span>{{ liked ? '已点赞' : '点赞' }}</span>
          </button>
          <button type="button" class="secondary-btn" :class="{ active: favorited }" @click="handleToggleFavorite">
            <i :class="favorited ? 'fas fa-bookmark' : 'far fa-bookmark'"></i>
            <span>{{ favorited ? '已收藏' : '收藏' }}</span>
          </button>
        </div>
      </header>

      <section class="preview-card">
        <div class="section-head">
          <h2>资料预览</h2>
        </div>

        <div v-if="material.fileType === 'PDF'" class="preview-body">
          <iframe
            v-if="material.previewUrl"
            :src="material.previewUrl"
            title="PDF 预览"
            class="pdf-frame"
          ></iframe>
          <div v-else class="pdf-placeholder">
            <div class="pdf-summary">
              <div class="pdf-icon"><i class="fas fa-file-pdf"></i></div>
              <div class="pdf-meta">
                <strong>{{ material.fileName }}</strong>
                <span>{{ formatFileSize(material.fileSize) }}</span>
              </div>
            </div>
            <div class="pdf-thumbs">
              <div v-for="page in [1, 2, 3]" :key="page" class="pdf-thumb">
                <span class="thumb-line short"></span>
                <span class="thumb-line"></span>
                <span class="thumb-line"></span>
                <span class="thumb-page">第 {{ page }} 页</span>
              </div>
            </div>
            <p class="preview-tip">PDF 预览区域：展示前 1-3 页</p>
          </div>
        </div>

        <div v-else-if="material.fileType === '图片'" class="preview-body image-body">
          <img :src="material.previewUrl || '/images/book1.jpg'" :alt="material.title" />
        </div>

        <div v-else class="placeholder">
          <i class="fas fa-file-arrow-down"></i>
          <p>暂不支持在线预览，请下载后查看。</p>
        </div>
      </section>

      <section class="comments-card">
        <CommentSection
          target-type="material"
          :target-id="material.id"
          title="评论区"
          empty-text="还没有评论，来留下第一条评论吧。"
          base-placeholder="写下你对这份资料的看法..."
        />
      </section>
    </section>

    <section v-else class="empty-card">
      <i class="fas fa-circle-exclamation"></i>
      <h2>资料不存在或已被删除</h2>
      <p>你可以返回知识星河继续浏览其他资料。</p>
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
  </div>
</template>

<script setup>
import { computed, inject, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CommentSection from '@/components/knowledge/CommentSection.vue'
import KnowledgeConfirmDialog from '@/components/knowledge/KnowledgeConfirmDialog.vue'
import KnowledgeToastStack from '@/components/knowledge/KnowledgeToastStack.vue'
import PublishDiscussionDialog from '@/components/knowledge/PublishDiscussionDialog.vue'
import PublishMaterialDialog from '@/components/knowledge/PublishMaterialDialog.vue'
import { resolveBackendMaterialByRecord } from '@/composables/useKnowledgeBackendSync'
import { useKnowledgeFeedback } from '@/composables/useKnowledgeFeedback'
import { useKnowledgeGalaxy } from '@/composables/useKnowledgeGalaxy'
import {
  createKnowledgeDiscussion as createKnowledgeDiscussionApi,
  createKnowledgeMaterial as createKnowledgeMaterialApi,
  downloadMaterial as downloadMaterialApi,
  toggleKnowledgeFavorite,
  toggleKnowledgeMaterialLike,
} from '@/services/api'

const route = useRoute()
const router = useRouter()
const appData = inject('appData', { value: {} })

const {
  getMaterialById,
  recordMaterialView,
  executeDownload,
  toggleMaterialLike,
  toggleMaterialFavorite,
  isMaterialLiked,
  isMaterialFavorited,
  getDownloadButtonMeta,
  formatPrice,
  formatDateTime,
  formatFileSize,
  createMaterial,
  createDiscussion,
} = useKnowledgeGalaxy()

const { toasts, confirmState, showToast, requestConfirm, acceptConfirm, cancelConfirm } = useKnowledgeFeedback()

const materialDialogOpen = ref(false)
const discussionDialogOpen = ref(false)
const materialDialogRef = ref(null)
const discussionDialogRef = ref(null)

const currentUser = computed(() => appData.value?.appState?.user || {})
const materialId = computed(() => Number(route.params.id))
const material = computed(() => getMaterialById(materialId.value))
const liked = computed(() => (material.value ? isMaterialLiked(material.value.id, currentUser.value) : false))
const favorited = computed(() => (material.value ? isMaterialFavorited(material.value.id, currentUser.value) : false))
const downloadMeta = computed(() => getDownloadButtonMeta(material.value, currentUser.value))

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
  if (!material.value) {
    return
  }
  recordMaterialView(material.value.id, currentUser.value)
}

const resolveBackendMaterialId = async () => {
  if (!material.value) {
    return 0
  }

  const backendMaterial = await resolveBackendMaterialByRecord(material.value)
  return Number(backendMaterial?.id || 0)
}

const formatDownloadError = (error) => {
  const details = error?.details || {}
  if (details.code === 'INSUFFICIENT_POINTS' || Number(details.shortfall || 0) > 0) {
    return `积分不足，还差 ${Number(details.shortfall || 0)} 分`
  }
  return error?.message || '下载失败，请稍后重试。'
}

const handleDownload = async () => {
  if (!material.value) {
    return
  }

  const firstResult = executeDownload(material.value.id, currentUser.value, false)

  if (!firstResult.ok && firstResult.code === 'login_required') {
    showToast(firstResult.message, 'warning')
    redirectToLogin()
    return
  }

  if (!firstResult.ok && firstResult.code === 'confirm_required') {
    const accepted = await requestConfirm({
      title: firstResult.title,
      message: firstResult.message,
      confirmText: '确认下载',
      cancelText: '取消',
    })

    if (!accepted) {
      return
    }

    const backendMaterialId = await resolveBackendMaterialId()
    if (backendMaterialId) {
      try {
        await downloadMaterialApi(backendMaterialId)
        const confirmedResult = executeDownload(material.value.id, currentUser.value, true, {
          skipPointValidation: true,
          skipPointDeduction: true,
        })
        showToast(confirmedResult.message, confirmedResult.ok ? 'success' : 'warning')
      } catch (error) {
        showToast(formatDownloadError(error), 'warning')
      }
      return
    }

    const confirmedResult = executeDownload(material.value.id, currentUser.value, true)
    if (confirmedResult.ok) {
      try {
        const backendMaterialId = await resolveBackendMaterialId()
        if (backendMaterialId) {
          await downloadMaterialApi(backendMaterialId)
        }
      } catch {
        showToast('本地下载成功，但后端兑换记录同步稍后重试。', 'warning')
      }
    }
    showToast(confirmedResult.message, confirmedResult.ok ? 'success' : 'warning')
    return
  }

  if (firstResult.ok) {
    try {
      const backendMaterialId = await resolveBackendMaterialId()
      if (backendMaterialId) {
        await downloadMaterialApi(backendMaterialId)
      }
    } catch {
      showToast('本地下载成功，但后端兑换记录同步稍后重试。', 'warning')
    }
  }

  showToast(firstResult.message, firstResult.ok ? 'success' : 'warning')
}

const handleToggleLike = async () => {
  const result = toggleMaterialLike(materialId.value, currentUser.value)
  if (!result.ok) {
    showToast(result.message, 'warning')
    redirectToLogin()
    return
  }

  try {
    const backendMaterialId = await resolveBackendMaterialId()
    if (!backendMaterialId) {
      throw new Error('没有找到对应的后端资料记录')
    }
    await toggleKnowledgeMaterialLike(backendMaterialId)
  } catch (error) {
    showToast(error.message || '点赞状态已在当前页面更新，但后端同步稍后重试。', 'warning')
  }
}

const handleToggleFavorite = async () => {
  const result = toggleMaterialFavorite(materialId.value, currentUser.value)
  if (!result.ok) {
    showToast(result.message, 'warning')
    redirectToLogin()
    return
  }

  try {
    const backendMaterialId = await resolveBackendMaterialId()
    if (!backendMaterialId) {
      throw new Error('没有找到对应的后端资料记录')
    }
    await toggleKnowledgeFavorite(backendMaterialId)
  } catch (error) {
    showToast(error.message || '收藏状态已在当前页面更新，但后端同步稍后重试。', 'warning')
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
  const validation = await createMaterial(payload, currentUser.value, {
    validateOnly: true,
    skipPointAward: true,
  })
  if (!validation.ok) {
    showToast(validation.message, validation.code === 'login_required' ? 'warning' : 'error')
    if (validation.code === 'login_required') {
      redirectToLogin()
    }
    return
  }

  let backendResult = null
  try {
    backendResult = await createKnowledgeMaterialApi({
      title: payload.title,
      description: payload.description,
      category: payload.category,
      course: payload.course,
      pricePoints: payload.pricePoints,
      tags: payload.tags,
      fileType: payload.file?.type || payload.file?.name?.split('.').pop() || 'other',
      fileSize: payload.file?.size || '',
    })
  } catch (error) {
    showToast(error.message || '资料上传失败，请稍后重试。', 'error')
    return
  }

  const pointsData = backendResult?.data?.points || {}
  const localResult = await createMaterial(payload, currentUser.value, {
    backendId: backendResult?.data?.material?.id,
    skipPointAward: true,
    points: pointsData.balance || 0,
    message: `上传成功，积分+10，当前积分 ${pointsData.balance || 0}/${pointsData.max || 100}`,
  })

  if (!localResult.ok) {
    showToast(localResult.message, localResult.code === 'login_required' ? 'warning' : 'error')
    if (localResult.code === 'login_required') {
      redirectToLogin()
    }
    return
  }

  materialDialogOpen.value = false
  materialDialogRef.value?.resetForm()
  showToast(localResult.message, 'success')
  return

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

watch(materialId, () => syncView())

onBeforeUnmount(() => {
  window.removeEventListener('open-knowledge-upload', handleOpenUploadEvent)
  window.removeEventListener('open-knowledge-discussion', handleOpenDiscussionEvent)
})
</script>

<style scoped>
.material-detail-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
  max-width: 1040px;
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
.preview-card,
.comments-card,
.empty-card {
  padding: 24px;
  border-radius: 26px;
  border: 1px solid rgba(224, 232, 255, 0.96);
  background: #fff;
  box-shadow: 0 20px 42px rgba(90, 107, 162, 0.12);
}

.hero-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 200px;
  gap: 20px;
}

.hero-main {
  min-width: 0;
}

.badge-row,
.tags,
.meta-grid {
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
  min-height: 30px;
  padding: 0 11px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.file-badge,
.category-badge {
  background: #eef2ff;
  color: #4560d5;
}

.price-badge {
  background: #eef8f1;
  color: #1c8b5c;
}

.price-badge.is-points {
  background: #fff2e8;
  color: #d56a1f;
}

.hero-card h1 {
  margin-top: 14px;
  color: #18233b;
  font-size: clamp(30px, 3vw, 40px);
  line-height: 1.18;
}

.description {
  margin-top: 16px;
  color: #5c6e88;
  line-height: 1.9;
}

.course {
  margin-top: 14px;
  color: #4c5d7a;
  font-weight: 700;
}

.tags {
  margin-top: 16px;
}

.tags span {
  background: #f5f7ff;
  color: #667892;
}

.meta-grid {
  margin-top: 20px;
  gap: 12px 16px;
}

.meta-grid span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #71819a;
  font-size: 13px;
}

.hero-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.download-btn,
.secondary-btn {
  min-height: 46px;
  border: none;
  border-radius: 16px;
  font-weight: 700;
  cursor: pointer;
}

.download-btn {
  background: linear-gradient(135deg, #5770f0, #7d6ef6);
  color: #fff;
}

.download-btn.is-points {
  background: linear-gradient(135deg, #f59e0b, #f97316);
}

.secondary-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: #f5f7ff;
  color: #4b5f90;
}

.secondary-btn.active {
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

.preview-body {
  border-radius: 20px;
  overflow: hidden;
  background: #f6f8ff;
}

.pdf-frame {
  width: 100%;
  min-height: 560px;
  border: none;
  background: #fff;
}

.pdf-placeholder {
  padding: 22px;
}

.pdf-summary {
  display: flex;
  align-items: center;
  gap: 14px;
}

.pdf-icon {
  width: 54px;
  height: 54px;
  display: grid;
  place-items: center;
  border-radius: 18px;
  background: #fff;
  color: #d14343;
  font-size: 24px;
}

.pdf-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.pdf-meta strong {
  color: #20304e;
}

.pdf-meta span,
.preview-tip {
  color: #72839b;
  font-size: 13px;
}

.pdf-thumbs {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: 18px;
}

.pdf-thumb {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 18px;
  border-radius: 18px;
  background: #fff;
}

.thumb-line {
  height: 8px;
  border-radius: 999px;
  background: #dfe7ff;
}

.thumb-line.short {
  width: 58%;
}

.thumb-page {
  margin-top: 6px;
  color: #5c6d87;
  font-size: 12px;
  font-weight: 700;
}

.preview-tip {
  margin-top: 16px;
}

.image-body {
  display: grid;
  place-items: center;
  background: #f8faff;
}

.image-body img {
  width: 100%;
  max-height: 560px;
  object-fit: contain;
}

.placeholder,
.empty-card {
  min-height: 220px;
  display: grid;
  place-items: center;
  text-align: center;
  color: #70819a;
}

.placeholder i,
.empty-card i {
  font-size: 40px;
  color: #94a6bf;
  margin-bottom: 12px;
}

@media (max-width: 860px) {
  .hero-card {
    grid-template-columns: 1fr;
  }

  .hero-actions {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .hero-actions > * {
    flex: 1 1 180px;
  }

  .pdf-thumbs {
    grid-template-columns: 1fr;
  }
}
</style>
