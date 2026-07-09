<template>
  <div class="sell-publish-container">
    <div class="sell-main-layout">
      <div>
        <SellIsbnBar :bar="sell.isbnBar" />
        <SellBookForm
          ref="formRef"
          :sell="sell"
          :shared="shared"
          :draft-saving="draftSaving"
          @submit="handleSubmit"
          @save-draft="handleSaveDraft"
        />
      </div>

      <aside class="sell-side-stack">
        <section class="draft-sidebar-card">
          <div class="draft-card-head">
            <div class="draft-card-icon">
              <i class="fas fa-box-archive"></i>
            </div>
            <div>
              <h3>草稿箱</h3>
              <p>保存后可随时回到这里继续编辑。</p>
            </div>
            <span class="draft-badge">{{ drafts.length }}</span>
          </div>

          <div v-if="activeDraft" class="draft-current">
            <span class="draft-current-label">当前编辑</span>
            <strong>{{ activeDraft.title || '未命名草稿' }}</strong>
          </div>

          <div v-if="drafts.length" class="draft-sidebar-list">
            <article
              v-for="draft in drafts"
              :key="draft.id"
              class="draft-sidebar-item"
              :class="{ active: draft.id === draftId }"
            >
              <div class="draft-sidebar-copy">
                <h4>{{ draft.title || '未命名草稿' }}</h4>
                <p>{{ buildDraftMeta(draft) }}</p>
                <small>{{ formatDraftTime(draft.updatedAt || draft.createdAt) }}</small>
              </div>
              <div class="draft-sidebar-actions">
                <button type="button" class="draft-primary-btn" @click="handleEditDraft(draft)">继续编辑</button>
                <button type="button" class="draft-secondary-btn" @click="handleDeleteDraft(draft)">删除</button>
              </div>
            </article>
          </div>

          <div v-else class="draft-sidebar-empty">
            <i class="fas fa-file-lines"></i>
            <p>暂时还没有草稿</p>
            <span>点击“保存草稿”后，这里会显示你未发布的书籍草稿。</span>
          </div>
        </section>

        <RecycleSidebar :cards="sell.recycleCards" :tip="sell.tip" />
      </aside>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import RecycleSidebar from '../components/sell/RecycleSidebar.vue'
import SellBookForm from '../components/sell/SellBookForm.vue'
import SellIsbnBar from '../components/sell/SellIsbnBar.vue'
import { useGlobalState } from '../composables/useGlobalState'
import { deleteDraft, getDrafts, saveDraft } from '../services/api'

const props = defineProps({
  data: { type: Object, default: () => ({}) },
})

const router = useRouter()
const { userBooks } = useGlobalState()

const sell = computed(() => props.data.sell ?? { isbnBar: {}, form: {}, recycleCards: [], sections: [] })
const shared = computed(() => props.data.shared ?? {})

const formRef = ref(null)
const draftId = ref(null)
const drafts = ref([])
const draftSaving = ref(false)

const activeDraft = computed(() => drafts.value.find((draft) => draft.id === draftId.value) || null)

const loadDrafts = async () => {
  try {
    const res = await getDrafts()
    if (res?.code === 200 && Array.isArray(res.data)) {
      drafts.value = res.data
    }
  } catch {
    drafts.value = []
  }
}

onMounted(async () => {
  await loadDrafts()
})

const upsertDraft = (nextDraft) => {
  const draftIndex = drafts.value.findIndex((draft) => draft.id === nextDraft.id)
  if (draftIndex >= 0) {
    drafts.value.splice(draftIndex, 1, nextDraft)
    return
  }
  drafts.value.unshift(nextDraft)
}

const formatDraftTime = (value) => {
  if (!value) return '刚刚保存'

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '刚刚保存'

  return new Intl.DateTimeFormat('zh-CN', {
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

const buildDraftMeta = (draft) => {
  const meta = []
  if (draft.price) meta.push(`￥${Number(draft.price).toFixed(2)}`)
  if (draft.campusLabel) meta.push(draft.campusLabel)
  else if (draft.campus) meta.push(draft.campus)
  if (draft.isbn) meta.push(`ISBN ${draft.isbn}`)
  return meta.join(' · ') || '还没有填写摘要信息'
}

const handleEditDraft = async (draft) => {
  draftId.value = draft.id
  formRef.value?.loadDraft?.(draft)

  await nextTick()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleDeleteDraft = async (draft) => {
  const confirmed = window.confirm(`确定删除草稿“${draft.title || '未命名草稿'}”吗？`)
  if (!confirmed) return

  try {
    await deleteDraft(draft.id)
    drafts.value = drafts.value.filter((item) => item.id !== draft.id)

    if (draftId.value === draft.id) {
      draftId.value = null
      formRef.value?.resetForm?.()
    }
  } catch (error) {
    console.error('删除草稿失败:', error)
    window.alert('删除草稿失败，请稍后重试。')
  }
}

const handleSubmit = async (createdBook) => {
  if (createdBook?.id && !userBooks.value.some((book) => book.id === createdBook.id)) {
    userBooks.value.unshift(createdBook)
  }

  if (draftId.value) {
    const currentDraftId = draftId.value
    try {
      await deleteDraft(currentDraftId)
      drafts.value = drafts.value.filter((draft) => draft.id !== currentDraftId)
    } catch {
      // Keep publish flow smooth even if draft cleanup fails.
    }
    draftId.value = null
  }

  router.push('/buy')
}

const handleSaveDraft = async (draftData) => {
  draftSaving.value = true

  try {
    const payload = { ...draftData }
    if (draftId.value) payload.draftId = draftId.value

    const res = await saveDraft(payload)
    if (res?.code === 200 && res.data?.id) {
      draftId.value = res.data.id
      upsertDraft(res.data)
      window.alert('草稿已保存，右侧草稿箱可以继续编辑。')
    }
  } catch (error) {
    console.error('草稿保存失败:', error)
    window.alert('草稿保存失败，请稍后重试。')
  } finally {
    draftSaving.value = false
  }
}
</script>

<style scoped>
.sell-publish-container {
  max-width: 1200px;
  margin: 0 auto;
}

.sell-main-layout {
  display: grid;
  grid-template-columns: 1fr 260px;
  gap: 20px;
  align-items: start;
}

.sell-side-stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.draft-sidebar-card {
  display: flex;
  flex-direction: column;
  padding: 16px;
  border: 1px solid var(--gray-200);
  border-radius: 12px;
  background: white;
  box-shadow: var(--shadow-sm);
}

.draft-card-head {
  display: grid;
  grid-template-columns: 40px 1fr auto;
  gap: 10px;
  align-items: center;
}

.draft-card-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  background: var(--light-blue);
  color: var(--primary-blue);
  font-size: 18px;
}

.draft-card-head h3 {
  color: var(--gray-900);
  font-size: 14px;
  font-weight: 600;
}

.draft-card-head p {
  margin-top: 4px;
  color: var(--gray-500);
  font-size: 12px;
  line-height: 1.5;
}

.draft-badge {
  min-width: 24px;
  height: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 7px;
  border-radius: 999px;
  background: var(--light-blue);
  color: var(--primary-blue);
  font-size: 12px;
  font-weight: 700;
}

.draft-current {
  margin-top: 14px;
  padding: 10px 12px;
  border-radius: 10px;
  background: #f8fbff;
  border: 1px solid #e4ecff;
}

.draft-current-label {
  display: block;
  color: var(--primary-blue);
  font-size: 11px;
  font-weight: 700;
}

.draft-current strong {
  display: block;
  margin-top: 4px;
  color: var(--gray-800);
  font-size: 13px;
  line-height: 1.4;
}

.draft-sidebar-list {
  margin-top: 14px;
  max-height: min(52vh, 420px);
  overflow-y: auto;
  padding-right: 4px;
}

.draft-sidebar-list::-webkit-scrollbar {
  width: 6px;
}

.draft-sidebar-list::-webkit-scrollbar-thumb {
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.5);
}

.draft-sidebar-list::-webkit-scrollbar-track {
  background: transparent;
}

.draft-sidebar-item {
  padding: 12px;
  border: 1px solid #edf1f7;
  border-radius: 10px;
  background: #fbfcff;
}

.draft-sidebar-item + .draft-sidebar-item {
  margin-top: 10px;
}

.draft-sidebar-item.active {
  border-color: #cfdcff;
  background: #f5f8ff;
}

.draft-sidebar-copy h4 {
  color: var(--gray-900);
  font-size: 13px;
  font-weight: 600;
  line-height: 1.4;
}

.draft-sidebar-copy p {
  margin-top: 6px;
  color: var(--gray-600);
  font-size: 12px;
  line-height: 1.5;
}

.draft-sidebar-copy small {
  display: block;
  margin-top: 6px;
  color: var(--gray-400);
  font-size: 11px;
}

.draft-sidebar-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-top: 10px;
}

.draft-sidebar-actions button {
  width: 100%;
  padding: 8px 10px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.draft-primary-btn {
  border: none;
  background: var(--primary-blue);
  color: white;
}

.draft-primary-btn:hover {
  background: var(--primary-blue-dark);
}

.draft-secondary-btn {
  border: 1px solid var(--gray-300);
  background: white;
  color: var(--gray-700);
}

.draft-secondary-btn:hover {
  background: #f8fafc;
}

.draft-sidebar-empty {
  margin-top: 14px;
  padding: 12px;
  border-radius: 10px;
  background: #fbfcff;
  text-align: center;
}

.draft-sidebar-empty i {
  color: var(--primary-blue);
  font-size: 20px;
}

.draft-sidebar-empty p {
  margin-top: 8px;
  color: var(--gray-800);
  font-size: 13px;
  font-weight: 600;
}

.draft-sidebar-empty span {
  display: block;
  margin-top: 6px;
  color: var(--gray-500);
  font-size: 12px;
  line-height: 1.5;
}

@media (max-width: 1024px) {
  .sell-main-layout {
    grid-template-columns: 1fr;
  }

  .sell-side-stack {
    order: -1;
  }
}
</style>
