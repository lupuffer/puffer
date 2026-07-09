<template>
  <div class="knowledge-star-river">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2 class="page-title">
        <i class="fas fa-star"></i>
        知识星河
        <span class="subtitle">知识星河</span>
      </h2>
      <p class="page-desc">分享你的学术见解，连接十万级书籍知识网络</p>
    </div>

    <div class="main-layout">
      <!-- 左侧：发布区域 -->
      <div class="publish-section">
        <div class="publish-card">
          <h3 class="card-title">
            <i class="fas fa-pen-fancy"></i>
            知识星河动态
          </h3>
          
          <form @submit.prevent="handleSubmit">
            <!-- 标题输入 -->
            <div class="form-group">
              <label>笔记标题</label>
              <input 
                v-model="form.title"
                type="text"
                placeholder="给你的资料或经验起个标题..."
                maxlength="100"
                required
              />
              <span class="char-count">{{ form.title.length }}/100</span>
            </div>

            <!-- 关联书籍 - 模糊搜索下拉框 -->
            <div class="form-group">
              <label>关联书籍资产（可选）</label>
              <div class="book-search">
                <input
                  v-model="bookSearchKeyword"
                  type="text"
                  placeholder="搜索书名、作者、ISBN..."
                  @input="handleBookSearch"
                  @focus="showBookDropdown = searchResults.length > 0"
                />
                <i class="fas fa-search search-icon"></i>
                
                <!-- 搜索结果下拉框 -->
                <div v-if="showBookDropdown && searchResults.length > 0" class="book-dropdown">
                  <div
                    v-for="book in searchResults"
                    :key="book.id"
                    class="book-option"
                    @click="selectBook(book)"
                  >
                     <img :src="book.image" :alt="book.title" loading="lazy" />
                    <div class="book-details">
                      <div class="book-title">{{ book.title }}</div>
                      <div class="book-meta">{{ book.author }} · {{ book.isbn }}</div>
                    </div>
                  </div>
                </div>
                
                <!-- 选中书籍显示 -->
                <div v-if="selectedBook" class="selected-book">
                   <img :src="selectedBook.image" :alt="selectedBook.title" loading="lazy" />
                  <span>{{ selectedBook.title }}</span>
                  <button type="button" @click="clearSelectedBook">
                    <i class="fas fa-times"></i>
                  </button>
                </div>
              </div>
            </div>

            <!-- 内容输入 -->
            <div class="form-group">
              <label>详细内容</label>
              <textarea
                v-model="form.content"
                rows="8"
                placeholder="分享你的学术见解、读书笔记或知识总结..."
                maxlength="2000"
                required
              ></textarea>
              <span class="char-count">{{ form.content.length }}/2000</span>
            </div>

            <!-- 标签 -->
            <div class="form-group">
              <label>标签（可选）</label>
              <div class="tags-input">
                <div v-for="(tag, index) in form.tags" :key="index" class="tag-item">
                  {{ tag }}
                  <button type="button" @click="removeTag(index)">
                    <i class="fas fa-times"></i>
                  </button>
                </div>
                <input
                  v-if="form.tags.length < 5"
                  v-model="tagInput"
                  type="text"
                  placeholder="添加标签，按回车确认"
                  @keydown.enter.prevent="addTag"
                />
              </div>
            </div>

            <!-- 提交按钮 -->
            <button 
              type="submit" 
              class="submit-btn"
              :disabled="isSubmitting"
            >
              <span v-if="isSubmitting">
                <i class="fas fa-spinner fa-spin"></i>
                正在传输至知识星河...
              </span>
              <span v-else>
                <i class="fas fa-paper-plane"></i>
                发布动态
              </span>
            </button>
          </form>
        </div>
      </div>

      <!-- 右侧：星河动态流 -->
      <div class="stream-section">
        <div class="stream-header">
          <h3>
            <i class="fas fa-stream"></i>
            星河动态
          </h3>
          <span class="note-count">共 {{ notes.length }} 条笔记</span>
        </div>

        <div v-if="loading" class="loading-state">
          <i class="fas fa-spinner fa-spin"></i>
          <p>正在加载星河...</p>
        </div>

        <div v-else class="notes-stream">
          <transition-group name="note-fade">
            <article
              v-for="note in notes"
              :key="note.note_id"
              class="note-card"
              :class="{ 'is-new': note.isNew }"
            >
              <div class="note-header">
                <h4 class="note-title">{{ note.title }}</h4>
                <div class="note-meta">
                  <span class="note-time">
                    <i class="far fa-clock"></i>
                    {{ formatTime(note.create_time) }}
                  </span>
                  <span class="note-stats">
                    <i class="far fa-eye"></i> {{ note.views || 0 }}
                    <i class="far fa-thumbs-up"></i> {{ note.likes || 0 }}
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
                  <span class="author-name">{{ note.user_name }}</span>
                </div>

                <!-- 关联书籍标签 -->
                <div 
                  v-if="note.related_book_title && note.related_book_title !== '未关联书籍'"
                  class="related-book-tag"
                  @click="goToBook(note.related_book_id)"
                >
                  <i class="fas fa-book"></i>
                  <span>{{ note.related_book_title }}</span>
                </div>

                <!-- 标签 -->
                <div v-if="note.tags?.length" class="note-tags">
                  <span v-for="tag in note.tags" :key="tag" class="tag">{{ tag }}</span>
                </div>
                
                <!-- 评论按钮 -->
                <button class="comment-btn" @click="openCommentModal(note)">
                  <i class="far fa-comment-dots"></i>
                  <span>评论 ({{ note.comment_count || 0 }})</span>
                </button>
              </div>
            </article>
          </transition-group>
        </div>
      </div>
    </div>
    
    <!-- 评论弹窗/抽屉 -->
    <div v-if="showCommentModal" class="comment-modal-overlay" @click.self="closeCommentModal">
      <div class="comment-modal">
        <!-- 弹窗头部 -->
        <div class="modal-header">
          <h3>
            <i class="fas fa-comments"></i>
            笔记详情与评论
          </h3>
          <button class="close-btn" @click="closeCommentModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <!-- 弹窗内容 -->
        <div class="modal-body" v-if="currentNote">
          <!-- 笔记详情 -->
          <div class="note-detail-section">
            <h4 class="detail-title">{{ currentNote.title }}</h4>
            <div class="detail-meta">
              <span class="detail-author">
                <i class="fas fa-user-circle"></i>
                {{ currentNote.user_name }}
              </span>
              <span class="detail-time">
                <i class="far fa-clock"></i>
                {{ formatTime(currentNote.create_time) }}
              </span>
            </div>
            <div class="detail-content">
              <p>{{ currentNote.content }}</p>
            </div>
            <div v-if="currentNote.related_book_title && currentNote.related_book_title !== '未关联书籍'" class="detail-book-tag">
              <i class="fas fa-book"></i>
              <span>关联书籍：{{ currentNote.related_book_title }}</span>
            </div>
          </div>
          
          <!-- 评论列表 -->
          <div class="comments-section">
            <h4 class="comments-title">
              <i class="fas fa-comment-alt"></i>
              互动评论 ({{ comments.length }})
            </h4>
            
            <div v-if="commentsLoading" class="comments-loading">
              <i class="fas fa-spinner fa-spin"></i>
              <span>加载评论中...</span>
            </div>
            
            <div v-else-if="comments.length === 0" class="no-comments">
              <i class="far fa-comment-dots"></i>
              <p>暂无评论，快来发表第一条评论吧！</p>
            </div>
            
            <div v-else class="comments-list">
              <div
                v-for="comment in comments"
                :key="comment.comment_id"
                class="comment-item"
              >
                <div class="comment-header">
                  <span class="comment-author">
                    <i class="fas fa-user-circle"></i>
                    {{ comment.user_name }}
                  </span>
                  <span class="comment-time">{{ formatTime(comment.time) }}</span>
                </div>
                <p class="comment-text">{{ comment.comment_text }}</p>
              </div>
            </div>
          </div>
          
          <!-- 评论输入 -->
          <div class="comment-input-section">
            <div class="input-wrapper">
              <textarea
                v-model="newComment"
                placeholder="写下你的评论..."
                rows="3"
                maxlength="500"
              ></textarea>
              <span class="char-count">{{ newComment.length }}/500</span>
            </div>
            <button 
              class="send-btn"
              :disabled="!newComment.trim() || isSendingComment"
              @click="submitComment"
            >
              <span v-if="isSendingComment">
                <i class="fas fa-spinner fa-spin"></i>
                发送中...
              </span>
              <span v-else>
                <i class="fas fa-paper-plane"></i>
                发送
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 表单数据
const form = reactive({
  title: '',
  content: '',
  tags: []
})

const tagInput = ref('')
const isSubmitting = ref(false)
const notes = ref([])
const loading = ref(false)

// 书籍搜索
const bookSearchKeyword = ref('')
const searchResults = ref([])
const selectedBook = ref(null)
const showBookDropdown = ref(false)
const searchingBooks = ref(false)
let searchTimeout = null

// 评论相关
const showCommentModal = ref(false)
const currentNote = ref(null)
const comments = ref([])
const commentsLoading = ref(false)
const newComment = ref('')
const isSendingComment = ref(false)

// 加载笔记列表
const loadNotes = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/community/notes')
    const data = await response.json()
    if (data.code === 200) {
      notes.value = data.data.notes || []
    }
  } catch (error) {
    console.error('加载笔记失败:', error)
  } finally {
    loading.value = false
  }
}

// 搜索书籍
const handleBookSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  
  const keyword = bookSearchKeyword.value.trim()
  if (!keyword) {
    searchResults.value = []
    return
  }
  
  searchingBooks.value = true
  searchTimeout = setTimeout(async () => {
    try {
      const response = await fetch(`/api/books?keyword=${encodeURIComponent(keyword)}`)
      const data = await response.json()
      if (data.code === 200) {
        searchResults.value = data.data.books || []
        showBookDropdown.value = true
      }
    } catch (error) {
      console.error('搜索书籍失败:', error)
    } finally {
      searchingBooks.value = false
    }
  }, 300)
}

const selectBook = (book) => {
  selectedBook.value = book
  showBookDropdown.value = false
  bookSearchKeyword.value = ''
}

const clearSelectedBook = () => {
  selectedBook.value = null
  searchResults.value = []
}

// 标签处理
const addTag = () => {
  const tag = tagInput.value.trim()
  if (tag && !form.tags.includes(tag) && form.tags.length < 5) {
    form.tags.push(tag)
    tagInput.value = ''
  }
}

const removeTag = (index) => {
  form.tags.splice(index, 1)
}

// 提交表单
const handleSubmit = async () => {
  if (!form.title.trim() || !form.content.trim()) {
    alert('请填写标题和内容')
    return
  }
  
  isSubmitting.value = true
  
  try {
    const noteData = {
      title: form.title.trim(),
      content: form.content.trim(),
      related_book_id: selectedBookId.value || null,
      tags: form.tags
    }
    
    const response = await fetch('/api/community/notes', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(noteData)
    })
    
    const data = await response.json()
    
    if (data.code === 200) {
      // 标记为新笔记
      const newNote = { ...data.data, isNew: true }
      
      // 添加到列表顶部
      notes.value.unshift(newNote)
      
      // 清空表单
      form.title = ''
      form.content = ''
      form.tags = []
      selectedBook.value = null
      
      // 1秒后移除新笔记标记
      setTimeout(() => {
        newNote.isNew = false
      }, 1000)
    } else {
      alert(data.message || '发布失败')
    }
  } catch (error) {
    console.error('发布失败:', error)
    alert('网络错误，请重试')
  } finally {
    isSubmitting.value = false
  }
}

// 评论相关函数
const openCommentModal = async (note) => {
  currentNote.value = note
  showCommentModal.value = true
  commentsLoading.value = true
  
  try {
    const response = await fetch(`/api/notes/${note.note_id}/comments`)
    const data = await response.json()
    if (data.code === 200) {
      comments.value = data.data.comments || []
      // 更新笔记的评论数
      note.comment_count = comments.value.length
    }
  } catch (error) {
    console.error('加载评论失败:', error)
  } finally {
    commentsLoading.value = false
  }
}

const closeCommentModal = () => {
  showCommentModal.value = false
  currentNote.value = null
  comments.value = []
  newComment.value = ''
}

const submitComment = async () => {
  if (!newComment.value.trim() || !currentNote.value) return
  
  isSendingComment.value = true
  
  try {
    const response = await fetch('/api/notes/comment', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        note_id: currentNote.value.note_id,
        comment_text: newComment.value.trim()
      })
    })
    
    const data = await response.json()
    
    if (data.code === 200) {
      // 更新评论列表
      comments.value = data.data.comments || []
      // 更新笔记的评论数
      currentNote.value.comment_count = comments.value.length
      // 清空输入
      newComment.value = ''
    } else {
      alert(data.message || '评论失败')
    }
  } catch (error) {
    console.error('发送评论失败:', error)
    alert('网络错误，请重试')
  } finally {
    isSendingComment.value = false
  }
}

// 跳转到书籍详情
const goToBook = (bookId) => {
  if (bookId) {
    router.push({ path: '/book-detail', query: { id: bookId } })
  }
}

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return '未知时间'
  
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now - date
  
  if (diff < 3600000) {
    const minutes = Math.floor(diff / 60000)
    return minutes < 1 ? '刚刚' : `${minutes}分钟前`
  }
  if (diff < 86400000) {
    const hours = Math.floor(diff / 3600000)
    return `${hours}小时前`
  }
  if (diff < 604800000) {
    const days = Math.floor(diff / 86400000)
    return `${days}天前`
  }
  
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

onMounted(() => {
  loadNotes()
})
</script>

<style scoped>
.knowledge-star-river {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  text-align: center;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 8px;
}

.page-title i {
  color: #f59e0b;
}

.subtitle {
  font-size: 16px;
  font-weight: 400;
  color: #6b7280;
  margin-left: 8px;
}

.page-desc {
  font-size: 15px;
  color: #9ca3af;
}

.main-layout {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 32px;
}

/* 左侧发布区域 */
.publish-section {
  position: sticky;
  top: 24px;
  height: fit-content;
}

.publish-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-title i {
  color: #3b82f6;
}

.form-group {
  margin-bottom: 20px;
  position: relative;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 6px;
}

.form-group input[type="text"],
.form-group textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
  background: #f9fafb;
}

.form-group input[type="text"]:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  background: white;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 150px;
  line-height: 1.6;
}

.char-count {
  position: absolute;
  right: 12px;
  bottom: 12px;
  font-size: 12px;
  color: #9ca3af;
}

/* 书籍搜索 */
.book-search {
  position: relative;
}

.book-search > input {
  padding-right: 40px;
}

.search-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
}

.book-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 4px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  z-index: 50;
  max-height: 250px;
  overflow-y: auto;
}

.book-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.book-option:hover {
  background: #f3f4f6;
}

.book-option img {
  width: 40px;
  height: 56px;
  object-fit: cover;
  border-radius: 4px;
}

.book-details {
  flex: 1;
  min-width: 0;
}

.book-title {
  font-weight: 500;
  color: #1f2937;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.book-meta {
  font-size: 12px;
  color: #6b7280;
  margin-top: 2px;
}

.selected-book {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
  padding: 8px 12px;
  background: #ecfdf5;
  border-radius: 8px;
  font-size: 13px;
}

.selected-book img {
  width: 32px;
  height: 44px;
  object-fit: cover;
  border-radius: 4px;
}

.selected-book button {
  margin-left: auto;
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
}

/* 标签输入 */
.tags-input {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: #f9fafb;
  min-height: 44px;
  align-items: center;
}

.tags-input:focus-within {
  border-color: #3b82f6;
  background: white;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.tag-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: #dbeafe;
  color: #1e40af;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 500;
}

.tag-item button {
  background: none;
  border: none;
  color: #1e40af;
  cursor: pointer;
  font-size: 12px;
}

.tags-input input {
  flex: 1;
  min-width: 100px;
  border: none;
  background: transparent;
  padding: 4px;
  font-size: 14px;
  outline: none;
}

/* 提交按钮 */
.submit-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px -5px rgba(59, 130, 246, 0.4);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* 右侧星河动态 */
.stream-section {
  min-height: 600px;
}

.stream-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.stream-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 8px;
}

.note-count {
  font-size: 14px;
  color: #6b7280;
}

.loading-state {
  text-align: center;
  padding: 60px;
  color: #9ca3af;
}

.loading-state i {
  font-size: 32px;
  margin-bottom: 12px;
}

.notes-stream {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 笔记卡片 */
.note-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  transition: all 0.3s;
}

.note-card:hover {
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.note-card.is-new {
  animation: highlight 1s ease;
}

@keyframes highlight {
  0% {
    background: #dbeafe;
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.3);
  }
  100% {
    background: white;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
}

/* 淡入动画 */
.note-fade-enter-active {
  transition: all 0.5s ease;
}

.note-fade-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.note-fade-enter-to {
  opacity: 1;
  transform: translateY(0);
}

.note-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  gap: 16px;
}

.note-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  line-height: 1.4;
  flex: 1;
}

.note-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
  color: #6b7280;
  text-align: right;
}

.note-stats {
  display: flex;
  gap: 12px;
}

.note-stats i {
  margin-right: 4px;
}

.note-content {
  margin-bottom: 16px;
}

.note-content p {
  font-size: 15px;
  color: #4b5563;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
}

.note-footer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

.note-author {
  display: flex;
  align-items: center;
  gap: 8px;
}

.author-avatar {
  width: 32px;
  height: 32px;
  background: #dbeafe;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #3b82f6;
}

.author-name {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.related-book-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #f3f4f6;
  border-radius: 20px;
  font-size: 13px;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.2s;
}

.related-book-tag:hover {
  background: #e5e7eb;
  color: #1f2937;
}

.related-book-tag i {
  color: #3b82f6;
}

.note-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-left: auto;
}

.note-tags .tag {
  padding: 4px 10px;
  background: #f3f4f6;
  color: #6b7280;
  border-radius: 4px;
  font-size: 12px;
}

/* 评论按钮 */
.comment-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #eff6ff;
  border: 1px solid #dbeafe;
  border-radius: 20px;
  font-size: 13px;
  color: #3b82f6;
  cursor: pointer;
  transition: all 0.2s;
  margin-left: auto;
}

.comment-btn:hover {
  background: #dbeafe;
  transform: translateY(-1px);
}

.comment-btn i {
  font-size: 14px;
}

/* 评论弹窗 */
.comment-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.comment-modal {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 8px;
}

.modal-header i {
  color: #3b82f6;
}

.close-btn {
  background: none;
  border: none;
  color: #6b7280;
  font-size: 20px;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

/* 笔记详情区域 */
.note-detail-section {
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
}

.detail-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 12px;
  line-height: 1.4;
}

.detail-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  font-size: 14px;
  color: #6b7280;
}

.detail-meta span {
  display: flex;
  align-items: center;
  gap: 6px;
}

.detail-content {
  font-size: 15px;
  color: #4b5563;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
  margin-bottom: 16px;
}

.detail-book-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: #dbeafe;
  color: #1e40af;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
}

/* 评论区域 */
.comments-section {
  margin-bottom: 20px;
}

.comments-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.comments-title i {
  color: #3b82f6;
}

.comments-loading,
.no-comments {
  text-align: center;
  padding: 40px;
  color: #9ca3af;
}

.comments-loading i,
.no-comments i {
  font-size: 32px;
  margin-bottom: 12px;
  display: block;
}

.no-comments p {
  font-size: 14px;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comment-item {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 16px;
  transition: all 0.2s;
}

.comment-item:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.comment-author {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.comment-author i {
  color: #3b82f6;
  font-size: 16px;
}

.comment-time {
  font-size: 12px;
  color: #9ca3af;
}

.comment-text {
  font-size: 14px;
  color: #4b5563;
  line-height: 1.7;
  margin: 0;
}

/* 评论输入区域 */
.comment-input-section {
  border-top: 1px solid #e5e7eb;
  padding-top: 20px;
}

.input-wrapper {
  position: relative;
  margin-bottom: 12px;
}

.input-wrapper textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 12px;
  font-size: 14px;
  resize: vertical;
  min-height: 80px;
  background: #f9fafb;
  transition: all 0.2s;
}

.input-wrapper textarea:focus {
  outline: none;
  border-color: #3b82f6;
  background: white;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.input-wrapper .char-count {
  position: absolute;
  right: 12px;
  bottom: 12px;
  font-size: 12px;
  color: #9ca3af;
}

.send-btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px -5px rgba(59, 130, 246, 0.4);
}

.send-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* 响应式 */
@media (max-width: 1024px) {
  .main-layout {
    grid-template-columns: 1fr;
  }
  
  .publish-section {
    position: static;
  }
}
</style>
