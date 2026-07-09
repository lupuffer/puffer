<template>
  <div class="notes-section">
    <!-- 发布按钮 -->
    <div class="section-header">
      <h3 class="section-title">
        <i class="fas fa-book-open"></i>
        学习笔记
      </h3>
      <button class="btn-publish-toggle" @click="showPublishForm = !showPublishForm">
        <i :class="showPublishForm ? 'fas fa-times' : 'fas fa-plus'"></i>
        {{ showPublishForm ? '取消发布' : '写笔记' }}
      </button>
    </div>

    <!-- 发布表单 -->
    <NotePublishForm
      v-if="showPublishForm"
      @publish="handleNotePublished"
      @cancel="showPublishForm = false"
    />

    <!-- 笔记列表 -->
    <div class="notes-list">
      <div v-if="loading" class="loading-state">
        <i class="fas fa-spinner fa-spin"></i>
        <p>加载中...</p>
      </div>

      <div v-else-if="notes.length === 0" class="empty-state">
        <i class="fas fa-book"></i>
        <p>暂无笔记，来发布第一条吧！</p>
      </div>

         <article
         v-for="note in notes"
         :key="note.id"
         class="note-card"
         :class="{ 'is-new': note.author?.id === currentUserId }"
       >
         <div class="note-header">
           <h4 class="note-title">{{ note.title }}</h4>
           <div class="note-meta">
             <span class="note-time">
               <i class="far fa-clock"></i>
               {{ formatTime(note.createdAt) }}
             </span>
             <span class="note-likes">
               <i class="far fa-thumbs-up"></i>
               {{ note.likes || 0 }}
             </span>
           </div>
         </div>

         <div class="note-content">
           <p>{{ note.content }}</p>
         </div>

         <div class="note-footer">
           <div class="note-author">
             <div class="author-avatar">
               <i class="fas fa-user-circle"></i>
             </div>
             <span class="author-name">{{ note.author?.name || '未知用户' }}</span>
             <span v-if="note.author?.id === currentUserId" class="author-badge">我</span>
           </div>

           <div class="note-tags" v-if="note.tags && note.tags.length > 0">
             <span v-for="tag in note.tags" :key="tag" class="tag">{{ tag }}</span>
           </div>
         </div>
       </article>
    </div>

    <!-- 统计信息 -->
    <div v-if="notes.length > 0" class="notes-stats">
      <span>共 {{ notes.length }} 条笔记</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getNotes } from '@/services/api.js'
import NotePublishForm from './NotePublishForm.vue'

const notes = ref([])
const loading = ref(false)
const showPublishForm = ref(false)
const currentUserId = ref('')

const fetchNotes = async () => {
  loading.value = true
  try {
    const response = await getNotes()
    if (response.code === 200 && response.data) {
      notes.value = response.data.notes || []
      // 获取当前用户ID
       const userNote = notes.value.find(n => n.author?.id)
       if (userNote) {
         currentUserId.value = userNote.author.id
       }
    }
  } catch (error) {
    console.error('获取笔记失败:', error)
  } finally {
    loading.value = false
  }
}

const handleNotePublished = (newNote) => {
   // 将新笔记添加到列表顶部
   notes.value.unshift(newNote)
   currentUserId.value = newNote.author?.id
   showPublishForm.value = false
 }

const formatTime = (timeStr) => {
  if (!timeStr) return '未知时间'
  
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now - date
  
  // 小于1小时显示"X分钟前"
  if (diff < 3600000) {
    const minutes = Math.floor(diff / 60000)
    return minutes < 1 ? '刚刚' : `${minutes}分钟前`
  }
  
  // 小于24小时显示"X小时前"
  if (diff < 86400000) {
    const hours = Math.floor(diff / 3600000)
    return `${hours}小时前`
  }
  
  // 小于7天显示"X天前"
  if (diff < 604800000) {
    const days = Math.floor(diff / 86400000)
    return `${days}天前`
  }
  
  // 否则显示具体日期
  return date.toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric'
  })
}

onMounted(() => {
  fetchNotes()
})
</script>

<style scoped>
.notes-section {
  margin-top: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--gray-900);
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title i {
  color: var(--primary-blue);
}

.btn-publish-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--primary-blue);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-publish-toggle:hover {
  background: #1e40af;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.notes-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--gray-500);
}

.loading-state i,
.empty-state i {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.loading-state p,
.empty-state p {
  font-size: 15px;
}

.note-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid var(--gray-100);
  transition: all 0.2s ease;
}

.note-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.note-card.is-new {
  border-left: 4px solid var(--primary-blue);
}

.note-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  gap: 16px;
}

.note-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--gray-900);
  line-height: 1.4;
  flex: 1;
}

.note-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: var(--gray-500);
  flex-shrink: 0;
}

.note-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.note-content {
  margin-bottom: 16px;
}

.note-content p {
  font-size: 15px;
  color: var(--gray-700);
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
}

.note-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid var(--gray-100);
  flex-wrap: wrap;
  gap: 12px;
}

.note-author {
  display: flex;
  align-items: center;
  gap: 8px;
}

.author-avatar {
  width: 32px;
  height: 32px;
  background: var(--light-blue);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-blue);
  font-size: 16px;
}

.author-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--gray-700);
}

.author-badge {
  padding: 2px 8px;
  background: var(--primary-blue);
  color: white;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
}

.note-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag {
  padding: 4px 10px;
  background: var(--gray-100);
  color: var(--gray-600);
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.notes-stats {
  margin-top: 20px;
  text-align: center;
  font-size: 13px;
  color: var(--gray-500);
}

@media (max-width: 640px) {
  .note-header {
    flex-direction: column;
    gap: 8px;
  }

  .note-footer {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>