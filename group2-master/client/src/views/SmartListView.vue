<template>
  <div class="smart-list-view">
    <section class="smart-hero">
      <div>
        <p class="eyebrow"><i class="fas fa-list-check"></i> Smart Textbook Plan</p>
        <h1>智慧清单</h1>
        <p>根据已识别课表生成本学期教材与资料收集入口。</p>
      </div>
      <button type="button" @click="goBuy"><i class="fas fa-store"></i> 去星图集市补齐教材</button>
    </section>

    <section class="smart-layout">
      <div class="plan-panel">
        <div class="section-heading">
          <h2>课程教材计划</h2>
          <p>按课表课程整理待补齐教材，已购买教材会自动排除。</p>
        </div>
        <div v-if="courses.length" class="course-list">
          <article v-for="course in courses" :key="course.name">
            <div class="course-main">
              <span class="course-icon"><i :class="course.icon"></i></span>
              <div>
                <h3>{{ course.name }}</h3>
                <p>{{ course.book }}</p>
              </div>
            </div>
            <span class="course-status" :class="course.state">{{ course.status }}</span>
          </article>
        </div>
        <div v-else class="empty-plan">
          <i class="fas fa-clipboard-list"></i>
          <p>暂未导入课表</p>
          <span>请在下方导入课表后生成课程教材计划</span>
        </div>
      </div>

      <aside class="next-panel">
        <div class="section-heading">
          <h2>待办提醒</h2>
          <p>需要你关注的教材流转事项</p>
        </div>
        <div v-if="todos.length" class="todo-list">
          <button v-for="todo in todos" :key="todo" type="button" @click="goBuy">
            <i class="fas fa-circle-check"></i>
            {{ todo }}
          </button>
        </div>
        <div v-else class="empty-todos">
          <i class="fas fa-check-circle"></i>
          <p>暂无待办事项</p>
          <span>导入课表后会自动生成</span>
        </div>
      </aside>
    </section>

    <section class="activation-shell">
      <SmartListPage />
    </section>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import SmartListPage from '../components/smartlist/SmartListPage.vue'
import { useGlobalState } from '../composables/useGlobalState'
import { getOrders } from '../services/api'
import {
  loadSmartSchedule,
  normalizeCourseName,
  SMART_SCHEDULE_UPDATED_EVENT,
} from '../utils/smartScheduleStorage'

const router = useRouter()
const { currentUser } = useGlobalState()

const isLoggedIn = computed(() => Boolean(currentUser.value?.isLoggedIn && currentUser.value?.id))

const courses = ref([])
const todos = ref([])
const userOrders = ref([])
const scheduleCourses = ref([])
const schedulePayload = ref(null)

const refreshScheduleCourses = () => {
  if (!isLoggedIn.value) {
    scheduleCourses.value = []
    schedulePayload.value = null
    return
  }

  const savedSchedule = loadSmartSchedule(currentUser.value.id)
  schedulePayload.value = savedSchedule || null
  scheduleCourses.value = Array.isArray(savedSchedule?.courses) ? savedSchedule.courses : []
}

const findBookForCourse = (course) => {
  const courseKey = normalizeCourseName(course.name)
  return (schedulePayload.value?.related_books || []).find((book) => {
    const haystack = [book.title, book.subject, book.category, book.description].map(normalizeCourseName).join(' ')
    return courseKey && haystack.includes(courseKey)
  }) || null
}

const rebuildCoursePlan = () => {
  courses.value = scheduleCourses.value.slice(0, 6).map((course) => {
    const matchedBook = findBookForCourse(course)
    return {
      name: course.name || '未命名课程',
      book: matchedBook?.title || '待匹配教材',
      status: matchedBook ? '可补齐' : '待匹配',
      state: matchedBook ? 'active' : 'todo',
      icon: 'fas fa-book',
    }
  })
}

const goBuy = () => router.push('/buy')

const loadUserSmartListData = async () => {
  if (!isLoggedIn.value) {
    courses.value = []
    todos.value = []
    userOrders.value = []
    scheduleCourses.value = []
    schedulePayload.value = null
    return
  }

  try {
    refreshScheduleCourses()

    const [ordersResult] = await Promise.allSettled([
      getOrders('all'),
    ])

    const ordersRes = ordersResult.status === 'fulfilled' ? ordersResult.value : null

    userOrders.value = (ordersRes?.data && Array.isArray(ordersRes.data)) ? ordersRes.data : []

    const pendingOrders = userOrders.value.filter((o) => o.status === 'created' || o.status === 'negotiating')

    rebuildCoursePlan()

    todos.value = pendingOrders.length > 0
      ? pendingOrders
          .slice(0, 3)
          .map((o) => `确认「${o.book?.title || `订单 ${o.id}`}」交易详情`)
      : []
  } catch (error) {
    console.error('加载智慧清单数据失败:', error)
    courses.value = []
    todos.value = []
    userOrders.value = []
  }
}

const handleScheduleUpdated = () => {
  refreshScheduleCourses()
  rebuildCoursePlan()
}

onMounted(() => {
  loadUserSmartListData()
  window.addEventListener(SMART_SCHEDULE_UPDATED_EVENT, handleScheduleUpdated)
})

onBeforeUnmount(() => {
  window.removeEventListener(SMART_SCHEDULE_UPDATED_EVENT, handleScheduleUpdated)
})
</script>

<style scoped>
.smart-list-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 1320px;
  margin: 0 auto;
}

.smart-hero,
.plan-panel,
.next-panel,
.activation-shell {
  border: 1px solid rgba(226, 232, 240, 0.86);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 16px 38px rgba(15, 23, 42, 0.07);
}

.smart-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  overflow: hidden;
  padding: 34px;
  background:
    radial-gradient(circle at 92% 12%, rgba(47, 128, 237, 0.2), transparent 28%),
    linear-gradient(135deg, #ffffff, #eaf6ff);
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #2f80ed;
  font-size: 13px;
  font-weight: 900;
}

.smart-hero h1 {
  margin-top: 10px;
  color: #0f172a;
  font-size: 42px;
  line-height: 1.1;
}

.smart-hero p {
  margin-top: 10px;
  color: #64748b;
  font-weight: 700;
}

.smart-hero button,
.todo-list button {
  border: none;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.smart-hero button {
  min-height: 48px;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  border-radius: 14px;
  padding: 0 20px;
  color: white;
  background: linear-gradient(135deg, #2f80ed, #0ea5e9);
  box-shadow: 0 18px 34px rgba(47, 128, 237, 0.24);
  font-weight: 900;
  white-space: nowrap;
}

.smart-hero button:hover,
.todo-list button:hover {
  transform: translateY(-2px);
}

.smart-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 20px;
}

.plan-panel,
.next-panel {
  padding: 24px;
}

.section-heading h2 {
  color: #0f172a;
  font-size: 22px;
}

.section-heading p {
  margin-top: 6px;
  color: #7c8da1;
  font-size: 13px;
  font-weight: 700;
}

.course-list,
.todo-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 18px;
}

.course-list article {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px;
  border-radius: 16px;
  background: #f7fbff;
}

.course-main {
  display: flex;
  align-items: center;
  gap: 12px;
}

.course-icon {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border-radius: 14px;
  color: #2f80ed;
  background: white;
}

.course-main h3 {
  color: #0f172a;
  font-size: 16px;
}

.course-main p {
  margin-top: 4px;
  color: #64748b;
  font-size: 13px;
  font-weight: 700;
}

.course-status {
  padding: 7px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 900;
}

.course-status.done {
  color: #047857;
  background: #dff8ec;
}

.course-status.active {
  color: #0b75bd;
  background: #e7f4ff;
}

.course-status.todo {
  color: #b45309;
  background: #fff4d9;
}

.todo-list button {
  display: flex;
  align-items: center;
  gap: 10px;
  border-radius: 14px;
  background: #f7fbff;
  padding: 14px;
  color: #334155;
  text-align: left;
  font-weight: 800;
}

.todo-list i {
  color: #2f80ed;
}

/* Empty states */
.empty-plan,
.empty-todos {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  margin-top: 18px;
  padding: 32px 16px;
  border: 2px dashed #e2e8f0;
  border-radius: 16px;
  background: #fafbfc;
  color: #94a3b8;
}

.empty-plan i,
.empty-todos i {
  font-size: 32px;
  margin-bottom: 8px;
}

.empty-plan p,
.empty-todos p {
  color: #64748b;
  font-size: 15px;
  font-weight: 700;
}

.empty-plan span,
.empty-todos span {
  color: #94a3b8;
  font-size: 13px;
}

.activation-shell {
  padding: 10px;
}

.activation-shell :deep(.page-header) {
  display: none;
}

.activation-shell :deep(.smart-list-page) {
  max-width: none;
  padding: 14px;
}

@media (max-width: 1024px) {
  .smart-layout {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .next-panel {
    grid-column: 1 / -1;
  }
}

@media (max-width: 720px) {
  .smart-hero {
    align-items: flex-start;
    flex-direction: column;
  }

  .smart-layout {
    grid-template-columns: 1fr;
  }
}
</style>
