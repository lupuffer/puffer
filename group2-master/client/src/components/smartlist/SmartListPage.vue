<template>
  <div class="smart-list-page">
    <div class="page-header">
      <h2 class="page-title">
        <i class="fas fa-calendar-days"></i>
        课表识别与智慧清单
      </h2>
      <p class="page-desc">导入课表后生成课程表，并推荐仍需补齐的教材与课程资料。</p>
    </div>

    <div class="upload-section">
      <div
        class="upload-zone"
        :class="{ 'is-dragover': isDragOver, 'has-file': selectedFileName }"
        @dragenter.prevent="isDragOver = true"
        @dragover.prevent="isDragOver = true"
        @dragleave.prevent="isDragOver = false"
        @drop.prevent="handleDrop"
        @click="triggerFileInput"
      >
        <input
          ref="fileInput"
          type="file"
          accept=".json"
          style="display: none"
          @change="handleFileSelect"
        />

        <div v-if="!selectedFileName" class="upload-placeholder">
          <i class="fas fa-cloud-upload-alt"></i>
          <h3>课表配置文件（JSON）投放区</h3>
          <p>点击选择文件或直接将课表 JSON 拖拽至此处</p>
          <span class="hint">第二次上传会覆盖上一次识别结果</span>
        </div>

        <div v-else class="file-selected">
          <i class="fas fa-file-code"></i>
          <span>{{ selectedFileName }}</span>
          <button type="button" title="清空课表" @click.stop="clearFile">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-content">
        <i class="fas fa-cog fa-spin"></i>
        <p>正在解析课表并匹配教材、资料...</p>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progress + '%' }"></div>
        </div>
      </div>
    </div>

    <div v-if="hasData && !isLoading" class="data-display fade-in">
      <div class="summary-cards">
        <div class="summary-card">
          <i class="fas fa-graduation-cap"></i>
          <div class="info">
            <span class="number">{{ summary.total_courses }}</span>
            <span class="label">门课程已识别</span>
          </div>
        </div>
        <div class="summary-card">
          <i class="fas fa-book-open"></i>
          <div class="info">
            <span class="number">{{ summary.related_books_count }}</span>
            <span class="label">本教材可补齐</span>
          </div>
        </div>
        <div class="summary-card">
          <i class="fas fa-file-lines"></i>
          <div class="info">
            <span class="number">{{ summary.material_count }}</span>
            <span class="label">份资料推荐</span>
          </div>
        </div>
        <div class="summary-card">
          <i class="fas fa-circle-check"></i>
          <div class="info">
            <span class="number">{{ purchasedBookCount }}</span>
            <span class="label">本已购买排除</span>
          </div>
        </div>
      </div>

      <section class="timetable-panel compact-panel">
        <div class="panel-heading">
          <h3><i class="fas fa-table-cells-large"></i> 已识别课表</h3>
          <span>{{ courses.length }} 门课程</span>
        </div>
        <div class="schedule-board">
          <section v-for="day in visibleWeekdays" :key="day" class="day-card">
            <div class="day-card-head">
              <strong>{{ day }}</strong>
              <span>{{ coursesByDay(day).length }} 门</span>
            </div>
            <div class="day-course-list">
              <article v-for="course in coursesByDay(day)" :key="course.id || course.name" class="schedule-course-card">
                <div class="course-time">{{ course.time || '未设置节次' }}</div>
                <div class="course-detail">
                  <strong>{{ course.name }}</strong>
                  <span>{{ [course.teacher, course.weeks].filter(Boolean).join(' · ') || '课程信息待完善' }}</span>
                </div>
              </article>
            </div>
          </section>
        </div>
      </section>

      <div class="recommendation-grid">
        <section class="recommend-panel">
          <div class="panel-heading">
            <h3><i class="fas fa-book"></i> 推荐教材</h3>
            <button type="button" @click="goBuy">去集市查看</button>
          </div>
          <div v-if="relatedBooks.length" class="book-grid">
            <article v-for="book in relatedBooks.slice(0, 6)" :key="bookKey(book)" class="book-card" @click="goToBook(book.id)">
              <div class="book-cover-frame">
                <img :src="book.cover || book.coverImage || '/images/book1.jpg'" :alt="book.title" loading="lazy" @error="e => e.target.src='/images/book1.jpg'" />
              </div>
              <div class="recommend-copy">
                <strong>{{ book.title }}</strong>
                <span>{{ book.author || book.publisher || 'SeekBook Catalog' }}</span>
                <p>¥{{ book.price || '-' }}</p>
              </div>
            </article>
          </div>
          <div v-else class="empty-box">
            <i class="fas fa-check-circle"></i>
            <p>暂无需要补齐的推荐教材</p>
          </div>
        </section>

        <section class="recommend-panel">
          <div class="panel-heading">
            <h3><i class="fas fa-file-lines"></i> 推荐资料</h3>
            <button type="button" @click="goKnowledge">去知识星河</button>
          </div>
          <div v-if="relatedMaterials.length" class="material-list">
            <article v-for="material in relatedMaterials.slice(0, 6)" :key="material.id" class="material-card" @click="goMaterial(material.id)">
              <div class="material-icon"><i class="fas fa-file-lines"></i></div>
              <div class="recommend-copy">
                <strong>{{ material.title }}</strong>
                <span>{{ material.course || material.courseName || '通识课程' }}</span>
                <p>{{ material.downloads || material.downloadCount || 0 }} 次下载 · {{ material.pricePoints || 0 }} 积分</p>
              </div>
            </article>
          </div>
          <div v-else class="empty-box">
            <i class="fas fa-folder-open"></i>
            <p>暂未匹配到课程资料</p>
          </div>
        </section>
      </div>
    </div>

    <div v-if="!hasData && !isLoading" class="inactive-state">
      <i class="fas fa-calendar-plus"></i>
      <p>当前尚未接入课程数据</p>
      <span>导入课表 JSON 后，会在这里保留识别结果并生成教材、资料入口。</span>
      <button type="button" class="btn-mock" :disabled="isLoadingMock" @click="generateMockSchedule">
        <i class="fas fa-magic"></i>
        {{ isLoadingMock ? '生成中...' : '一键生成模拟课表数据' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useKnowledgeGalaxy } from '../../composables/useKnowledgeGalaxy'
import { useGlobalState } from '../../composables/useGlobalState'
import { getOrders } from '../../services/api'
import {
  clearSmartSchedule,
  loadSmartSchedule,
  saveSmartSchedule,
} from '../../utils/smartScheduleStorage'

const router = useRouter()
const { currentUser } = useGlobalState()
const { materials: localMaterials } = useKnowledgeGalaxy()

const weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
const isDragOver = ref(false)
const selectedFileName = ref('')
const isLoading = ref(false)
const isLoadingMock = ref(false)
const progress = ref(0)
const hasData = ref(false)
const fileInput = ref(null)

const courses = ref([])
const relatedBooks = ref([])
const relatedMaterials = ref([])
const purchasedKeys = ref(new Set())
const summary = reactive({
  total_courses: 0,
  related_books_count: 0,
  material_count: 0,
})

const purchasedBookCount = computed(() => purchasedKeys.value.size)
const visibleWeekdays = computed(() =>
  weekdays.filter(day => courses.value.some(course => course.day === day))
)

const normalizeCourseKey = (value) => String(value || '')
  .trim()
  .toLocaleLowerCase('zh-CN')
  .replace(/[\s,，。.!！?？:：;；()（）[\]【】{}《》<>·•\-_/\\]+/g, '')

const normalizeBookKey = (book) => {
  const isbn = String(book?.isbn || '').replace(/[^0-9Xx]/g, '').toUpperCase()
  if (isbn) return `isbn:${isbn}`
  const title = normalizeCourseKey(book?.title)
  return title ? `title:${title}` : (book?.id ? `id:${book.id}` : '')
}

const bookKey = (book) => normalizeBookKey(book) || String(book?.title || Math.random())

const normalizeCourse = (course, index) => ({
  id: course.id || `course_${index}_${normalizeCourseKey(course.name || course.course || course.course_name || course['课程名'])}`,
  name: course.name || course.course || course.course_name || course['课程名'] || '未命名课程',
  day: course.day || course.weekday || course['星期'] || '未设置星期',
  time: course.time || course.schedule || course['节次'] || '未设置节次',
  teacher: course.teacher || course['教师'] || '',
  weeks: course.weeks || course.week || course.weeks_range || '1-16周',
  credits: course.credits || course['学分'] || '',
})

const triggerFileInput = () => {
  fileInput.value?.click()
}

const coursesByDay = (day) => courses.value
  .filter(course => course.day === day)
  .sort((a, b) => {
    const firstA = Number(String(a.time).match(/\d+/)?.[0] || 999)
    const firstB = Number(String(b.time).match(/\d+/)?.[0] || 999)
    return firstA - firstB || String(a.time || '').localeCompare(String(b.time || ''), 'zh-CN')
  })

const collectMaterialCandidates = async () => {
  return [...localMaterials.value]
}

const matchMaterialsByCourses = async (courseList) => {
  const candidates = await collectMaterialCandidates()
  const courseKeys = courseList.map(course => normalizeCourseKey(course.name)).filter(Boolean)
  const seen = new Set()
  return candidates.filter((material) => {
    const haystack = [
      material.title,
      material.course,
      material.courseName,
      material.description,
      ...(material.tags || []),
    ].map(normalizeCourseKey).join(' ')
    const matched = courseKeys.some(key => key && haystack.includes(key))
    if (!matched || seen.has(String(material.id))) return false
    seen.add(String(material.id))
    return true
  })
}

const loadPurchasedBooks = async () => {
  if (!currentUser.value?.id) {
    purchasedKeys.value = new Set()
    return
  }
  try {
    const response = await getOrders('all')
    const orders = Array.isArray(response?.data) ? response.data : []
    const keys = new Set()
    orders
      .filter(order => (
        order.status === 'completed'
        && (order.currentUserRole === 'buyer' || String(order.buyerId) === String(currentUser.value.id))
      ))
      .forEach((order) => {
        const key = normalizeBookKey(order.book)
        if (key) keys.add(key)
      })
    purchasedKeys.value = keys
  } catch {
    purchasedKeys.value = new Set()
  }
}

const updateSummary = () => {
  summary.total_courses = courses.value.length
  summary.related_books_count = relatedBooks.value.length
  summary.material_count = relatedMaterials.value.length
}

const buildPersistPayload = () => ({
  courses: courses.value,
  related_books: relatedBooks.value,
  related_materials: relatedMaterials.value,
  summary: { ...summary },
  fileName: selectedFileName.value,
  updatedAt: new Date().toISOString(),
})

const applySchedulePayload = async (payload, { persist = true } = {}) => {
  if (!payload || !Array.isArray(payload.courses)) return null

  courses.value = payload.courses.map(normalizeCourse)
  relatedBooks.value = (payload.related_books || [])
    .filter(book => !purchasedKeys.value.has(normalizeBookKey(book)))
  relatedMaterials.value = await matchMaterialsByCourses(courses.value)
  hasData.value = courses.value.length > 0
  updateSummary()

  const nextPayload = buildPersistPayload()
  if (persist) saveSmartSchedule(currentUser.value?.id, nextPayload)
  return nextPayload
}

const handleDrop = (e) => {
  isDragOver.value = false
  const file = e.dataTransfer.files[0]
  if (file && file.name.endsWith('.json')) {
    selectedFileName.value = file.name
    parseTimetable(file)
  }
}

const handleFileSelect = (e) => {
  const file = e.target.files[0]
  if (file) {
    selectedFileName.value = file.name
    parseTimetable(file)
  }
}

const clearFile = () => {
  selectedFileName.value = ''
  hasData.value = false
  courses.value = []
  relatedBooks.value = []
  relatedMaterials.value = []
  updateSummary()
  if (fileInput.value) fileInput.value.value = ''
  clearSmartSchedule(currentUser.value?.id)
}

const parseTimetable = async (file) => {
  if (!file) return
  isLoading.value = true
  progress.value = 0

  const progressInterval = setInterval(() => {
    if (progress.value < 90) progress.value += 10
  }, 120)

  try {
    await loadPurchasedBooks()
    const formData = new FormData()
    formData.append('file', file)
    const response = await fetch('/api/timetable/upload-file', { method: 'POST', body: formData })
    const data = await response.json()
    if (data.code === 200) {
      await applySchedulePayload(data.data, { persist: true })
      progress.value = 100
    } else {
      alert(data.message || '解析失败')
    }
  } catch (error) {
    console.error('解析失败:', error)
    alert('网络错误，请重试')
  } finally {
    clearInterval(progressInterval)
    setTimeout(() => {
      isLoading.value = false
    }, 300)
  }
}

const generateMockSchedule = async () => {
  isLoadingMock.value = true
  try {
    await loadPurchasedBooks()
    const response = await fetch('/api/schedule/mock', { method: 'POST' })
    const data = await response.json()
    if (data.code === 200) {
      selectedFileName.value = '模拟课表数据'
      await applySchedulePayload(data.data, { persist: true })
    } else {
      alert(data.message || '生成失败')
    }
  } catch (error) {
    console.error('生成模拟课表失败:', error)
    alert('网络错误，请重试')
  } finally {
    isLoadingMock.value = false
  }
}

const refreshSavedScheduleRecommendations = async () => {
  if (!courses.value.length) return
  try {
    const response = await fetch('/api/schedule/manual', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ courses: courses.value }),
    })
    const data = await response.json()
    if (data.code === 200) {
      await applySchedulePayload(data.data, { persist: true })
    }
  } catch {
    // 已保存课表仍可展示；后端不可用时不打断页面。
  }
}

const goToBook = (bookId) => {
  if (!bookId) return goBuy()
  router.push({ path: '/book-detail', query: { id: bookId } })
}

const goBuy = () => router.push('/buy')
const goKnowledge = () => router.push({ path: '/knowledge', query: { tab: 'materials' } })
const goMaterial = (id) => router.push(`/knowledge/material/${id}`)

onMounted(async () => {
  await loadPurchasedBooks()
  const savedSchedule = loadSmartSchedule(currentUser.value?.id)
  if (savedSchedule) {
    selectedFileName.value = savedSchedule.fileName || '已保存课表'
    await applySchedulePayload(savedSchedule, { persist: false })
    await refreshSavedScheduleRecommendations()
  }
})
</script>

<style scoped>
.smart-list-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  text-align: center;
  margin-bottom: 28px;
}

.page-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #1f2937;
  font-size: 28px;
  font-weight: 800;
  margin-bottom: 8px;
}

.page-title i {
  color: #8b5cf6;
}

.page-desc {
  color: #6b7280;
  font-size: 15px;
}

.upload-section {
  margin-bottom: 28px;
}

.upload-zone {
  padding: 42px;
  border: 3px dashed #d1d5db;
  border-radius: 18px;
  text-align: center;
  cursor: pointer;
  background: rgba(249, 250, 251, 0.92);
  transition: all 0.25s ease;
}

.upload-zone:hover,
.upload-zone.is-dragover {
  border-color: #8b5cf6;
  background: #f5f3ff;
}

.upload-zone.has-file {
  border-style: solid;
  border-color: #10b981;
  background: #ecfdf5;
}

.upload-placeholder i {
  color: #9ca3af;
  font-size: 56px;
  margin-bottom: 16px;
}

.upload-placeholder h3 {
  color: #374151;
  font-size: 20px;
  margin-bottom: 8px;
}

.upload-placeholder p,
.upload-placeholder .hint {
  color: #6b7280;
}

.upload-placeholder .hint {
  display: block;
  margin-top: 6px;
  font-size: 13px;
}

.file-selected {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #047857;
  font-size: 18px;
  font-weight: 700;
}

.file-selected i {
  font-size: 30px;
}

.file-selected button {
  border: none;
  background: transparent;
  color: #6b7280;
  cursor: pointer;
  font-size: 18px;
}

.loading-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.68);
  backdrop-filter: blur(4px);
}

.loading-content {
  width: min(420px, 86vw);
  text-align: center;
  color: white;
}

.loading-content i {
  color: #a78bfa;
  font-size: 46px;
  margin-bottom: 16px;
}

.progress-bar {
  height: 7px;
  margin-top: 22px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.2);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #8b5cf6, #60a5fa);
  transition: width 0.3s ease;
}

.fade-in {
  animation: fadeIn 0.35s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(14px); }
  to { opacity: 1; transform: translateY(0); }
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.summary-card,
.timetable-panel,
.recommend-panel,
.inactive-state {
  border: 1px solid rgba(226, 232, 240, 0.88);
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 16px 34px rgba(15, 23, 42, 0.07);
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: 14px;
}

.summary-card i {
  width: 48px;
  height: 48px;
  display: grid;
  place-items: center;
  border-radius: 14px;
  color: #8b5cf6;
  background: #f5f3ff;
  font-size: 26px;
}

.summary-card .info {
  display: flex;
  flex-direction: column;
}

.summary-card .number {
  color: #111827;
  font-size: 28px;
  font-weight: 800;
}

.summary-card .label {
  color: #6b7280;
  font-size: 14px;
}

.timetable-panel,
.recommend-panel {
  border-radius: 18px;
  padding: 22px;
}

.compact-panel {
  overflow: hidden;
}

.panel-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.panel-heading h3 {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #111827;
  font-size: 19px;
  font-weight: 800;
}

.panel-heading i {
  color: #8b5cf6;
}

.panel-heading span {
  color: #64748b;
  font-weight: 800;
}

.panel-heading button,
.btn-mock {
  border: none;
  border-radius: 12px;
  color: white;
  background: linear-gradient(135deg, #2f80ed, #8b5cf6);
  cursor: pointer;
  font-weight: 800;
}

.panel-heading button {
  min-height: 36px;
  padding: 0 14px;
}

.schedule-board {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 14px;
}

.day-card {
  min-height: 168px;
  padding: 14px;
  border-radius: 16px;
  border: 1px solid rgba(199, 210, 254, 0.72);
  background:
    radial-gradient(circle at 88% 12%, rgba(139, 92, 246, 0.12), transparent 36%),
    linear-gradient(180deg, rgba(248, 251, 255, 0.96), rgba(243, 247, 255, 0.9));
}

.day-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.day-card-head strong {
  color: #1f2937;
  font-size: 16px;
  font-weight: 900;
}

.day-card-head span {
  min-height: 24px;
  padding: 3px 9px;
  border-radius: 999px;
  color: #4f46e5;
  background: rgba(238, 242, 255, 0.94);
  font-size: 12px;
  font-weight: 900;
}

.day-course-list {
  display: grid;
  gap: 10px;
}

.schedule-course-card {
  display: grid;
  grid-template-columns: 58px minmax(0, 1fr);
  gap: 10px;
  align-items: stretch;
  padding: 10px;
  border-radius: 14px;
  border: 1px solid rgba(226, 232, 240, 0.95);
  background: rgba(255, 255, 255, 0.86);
  box-shadow: 0 10px 22px rgba(99, 102, 241, 0.08);
}

.course-time {
  display: grid;
  place-items: center;
  min-height: 54px;
  border-radius: 12px;
  color: white;
  background: linear-gradient(135deg, #4f6ef7, #8b5cf6);
  font-size: 12px;
  font-weight: 900;
  text-align: center;
}

.course-detail {
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.course-detail strong {
  color: #1f2937;
  font-size: 14px;
  font-weight: 900;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.course-detail span {
  margin-top: 5px;
  color: #64748b;
  font-size: 12px;
  font-weight: 700;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recommendation-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
  margin-top: 24px;
}

.book-grid,
.material-list {
  display: grid;
  gap: 14px;
}

.book-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.book-card,
.material-card {
  display: flex;
  gap: 14px;
  padding: 14px;
  border: 1px solid rgba(226, 232, 240, 0.95);
  border-radius: 16px;
  background: #f8fbff;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.book-card:hover,
.material-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.08);
}

.book-cover-frame {
  width: 68px;
  height: 92px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px;
  border-radius: 12px;
  background: white;
  border: 1px solid rgba(226, 232, 240, 0.95);
  flex: 0 0 auto;
}

.book-cover-frame img {
  width: 100%;
  height: 100%;
  max-width: 56px;
  max-height: 80px;
  border-radius: 6px;
  object-fit: contain;
  display: block;
}

.recommend-copy {
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.book-card strong,
.material-card strong {
  display: block;
  color: #1f2937;
  font-size: 15px;
  font-weight: 800;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-card span,
.material-card span {
  display: block;
  margin-top: 6px;
  color: #64748b;
  font-size: 12px;
  font-weight: 700;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-card p {
  margin-top: 8px;
  color: #ef4444;
  font-size: 14px;
  font-weight: 900;
}

.material-card p {
  margin-top: 8px;
  color: #64748b;
  font-size: 13px;
  font-weight: 800;
}

.material-icon {
  width: 52px;
  height: 52px;
  display: grid;
  place-items: center;
  border-radius: 14px;
  color: #8b5cf6;
  background: #f5f3ff;
  flex: 0 0 auto;
  font-size: 20px;
}

.empty-box,
.inactive-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #64748b;
  text-align: center;
}

.empty-box {
  min-height: 180px;
  border: 2px dashed #e5e7eb;
  border-radius: 16px;
}

.empty-box i {
  color: #94a3b8;
  font-size: 34px;
}

.inactive-state {
  padding: 74px 32px;
  border-radius: 18px;
  border-style: dashed;
}

.inactive-state i {
  color: #c4b5fd;
  font-size: 58px;
}

.inactive-state p {
  color: #475569;
  font-size: 18px;
  font-weight: 800;
}

.btn-mock {
  min-height: 42px;
  margin-top: 10px;
  padding: 0 18px;
}

@media (max-width: 1080px) {
  .summary-cards,
  .recommendation-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .smart-list-page {
    padding: 16px;
  }

  .summary-cards,
  .recommendation-grid,
  .book-grid {
    grid-template-columns: 1fr;
  }

  .upload-zone {
    padding: 30px 18px;
  }
}
</style>
