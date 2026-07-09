<template>
  <div class="note-publish-form">
    <h3 class="form-title">
      <i class="fas fa-pen-fancy"></i>
      发布笔记
    </h3>
    <form @submit.prevent="handleSubmit">
      <!-- 关联书籍搜索 -->
      <div class="form-group">
        <label for="related-book">
          <i class="fas fa-book"></i> 关联书籍（可选）
        </label>
        <div class="book-search-wrapper">
          <input
            id="related-book"
            v-model="bookSearchKeyword"
            type="text"
            placeholder="输入书名、作者或ISBN搜索..."
            @input="handleBookSearch"
            @focus="showBookDropdown = true"
          />
          <i v-if="searchingBooks" class="fas fa-spinner fa-spin search-icon"></i>
          <i v-else class="fas fa-search search-icon"></i>
          
          <!-- 书籍下拉列表 -->
          <div v-if="showBookDropdown && (searchResults.length > 0 || selectedBook)" class="book-dropdown">
            <div v-if="selectedBook" class="selected-book-info">
              <img :src="selectedBook.image" :alt="selectedBook.title" loading="lazy" />
              <div class="book-details">
                <div class="book-title">{{ selectedBook.title }}</div>
                <div class="book-meta">{{ selectedBook.author }} · ¥{{ selectedBook.price }}</div>
              </div>
              <button type="button" class="clear-book-btn" @click="clearSelectedBook">
                <i class="fas fa-times"></i>
              </button>
            </div>
            
            <div v-if="searchResults.length > 0 && !selectedBook" class="search-results">
              <div 
                v-for="book in searchResults" 
                :key="book.id"
                class="book-option"
                @click="selectBook(book)"
              >
                <img :src="book.image" :alt="book.title" loading="lazy" />
                <div class="book-details">
                  <div class="book-title">{{ book.title }}</div>
                  <div class="book-meta">{{ book.author }} · {{ book.subject }}</div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 点击外部关闭下拉 -->
          <div v-if="showBookDropdown" class="dropdown-backdrop" @click="showBookDropdown = false"></div>
        </div>
        <span class="hint">关联书籍后，笔记会显示在对应书籍的详情页</span>
      </div>
      
      <div class="form-group">
        <label for="note-title">标题</label>
        <input
          id="note-title"
          v-model="form.title"
          type="text"
          placeholder="给你的笔记起个标题吧..."
          maxlength="100"
          required
        />
        <span class="char-count">{{ form.title.length }}/100</span>
      </div>
      
      <div class="form-group">
        <label for="note-content">内容</label>
        <textarea
          id="note-content"
          v-model="form.content"
          rows="8"
          placeholder="分享你的学习心得、课程笔记或知识总结..."
          maxlength="2000"
          required
        ></textarea>
        <span class="char-count">{{ form.content.length }}/2000</span>
      </div>
      
      <div class="form-group">
        <label>标签（可选）</label>
        <div class="tags-input">
          <div v-for="(tag, index) in form.tags" :key="index" class="tag-item">
            {{ tag }}
            <button type="button" class="remove-tag" @click="removeTag(index)">
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
        <span class="hint">最多添加5个标签</span>
      </div>
      
      <div class="form-actions">
        <button type="button" class="btn btn-secondary" @click="handleCancel">
          取消
        </button>
        <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
          <i v-if="isSubmitting" class="fas fa-spinner fa-spin"></i>
          <i v-else class="fas fa-paper-plane"></i>
          {{ isSubmitting ? '发布中...' : '发布笔记' }}
        </button>
      </div>
    </form>
    
    <!-- 成功提示 -->
    <div v-if="showSuccess" class="success-message">
      <i class="fas fa-check-circle"></i>
      笔记发布成功！
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { createNote, searchBooksForNotes } from '@/services/api.js'

const emit = defineEmits(['publish', 'cancel'])

const form = reactive({
  title: '',
  content: '',
  tags: [],
  relatedBookId: null
})

const tagInput = ref('')
const isSubmitting = ref(false)
const showSuccess = ref(false)

// 书籍搜索相关
const bookSearchKeyword = ref('')
const searchResults = ref([])
const selectedBook = ref(null)
const showBookDropdown = ref(false)
const searchingBooks = ref(false)
let searchTimeout = null

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
      const response = await searchBooksForNotes(keyword)
      if (response.code === 200) {
        searchResults.value = response.data.books || []
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
  form.relatedBookId = book.id
  bookSearchKeyword.value = book.title
  showBookDropdown.value = false
}

const clearSelectedBook = () => {
  selectedBook.value = null
  form.relatedBookId = null
  bookSearchKeyword.value = ''
  searchResults.value = []
}

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

const handleSubmit = async () => {
  if (!form.title.trim() || !form.content.trim()) {
    return
  }
  
  isSubmitting.value = true
  
  try {
    const noteData = {
      title: form.title.trim(),
      content: form.content.trim(),
      tags: form.tags,
      bookId: form.relatedBookId  // 后端期望的字段名
    }
    
    const response = await createNote(noteData)
    
    if (response.code === 200) {
      showSuccess.value = true
      
      // 触发父组件事件
      emit('publish', { ...response.data, relatedBook: selectedBook.value })
      
      // 重置表单
      form.title = ''
      form.content = ''
      form.tags = []
      form.relatedBookId = null
      bookSearchKeyword.value = ''
      selectedBook.value = null
      
      // 2秒后隐藏成功提示
      setTimeout(() => {
        showSuccess.value = false
      }, 2000)
    } else {
      alert(response.message || '发布失败，请重试')
    }
  } catch (error) {
    console.error('发布笔记失败:', error)
    alert('网络错误，请检查后端服务是否运行')
  } finally {
    isSubmitting.value = false
  }
}

const handleCancel = () => {
  form.title = ''
  form.content = ''
  form.tags = []
  form.relatedBookId = null
  bookSearchKeyword.value = ''
  selectedBook.value = null
  emit('cancel')
}
</script>

<style scoped>
.note-publish-form {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--gray-100);
}

.form-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--gray-900);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-title i {
  color: var(--primary-blue);
}

.form-group {
  margin-bottom: 20px;
  position: relative;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--gray-700);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.form-group label i {
  color: var(--primary-blue);
  font-size: 13px;
}

.form-group input[type="text"],
.form-group textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--gray-200);
  border-radius: 8px;
  font-size: 15px;
  transition: all 0.2s ease;
  background: var(--gray-50);
}

.form-group input[type="text"]:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary-blue);
  background: white;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 120px;
  line-height: 1.6;
}

.char-count {
  position: absolute;
  right: 12px;
  bottom: 12px;
  font-size: 12px;
  color: var(--gray-400);
  background: rgba(255, 255, 255, 0.8);
  padding: 2px 6px;
  border-radius: 4px;
}

/* 书籍搜索样式 */
.book-search-wrapper {
  position: relative;
}

.book-search-wrapper input {
  padding-right: 40px;
}

.search-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--gray-400);
  font-size: 14px;
}

.book-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 4px;
  background: white;
  border: 1px solid var(--gray-200);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 100;
  max-height: 300px;
  overflow-y: auto;
}

.dropdown-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 99;
}

.selected-book-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f0fdf4;
  border-bottom: 1px solid var(--gray-100);
}

.selected-book-info img {
  width: 48px;
  height: 64px;
  object-fit: cover;
  border-radius: 4px;
}

.selected-book-info .book-details {
  flex: 1;
}

.selected-book-info .book-title {
  font-weight: 600;
  color: var(--gray-900);
  font-size: 14px;
}

.selected-book-info .book-meta {
  font-size: 12px;
  color: var(--gray-500);
  margin-top: 4px;
}

.clear-book-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background: var(--gray-200);
  color: var(--gray-600);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.clear-book-btn:hover {
  background: #ef4444;
  color: white;
}

.search-results {
  padding: 8px 0;
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
  background: var(--gray-50);
}

.book-option img {
  width: 40px;
  height: 56px;
  object-fit: cover;
  border-radius: 4px;
}

.book-option .book-details {
  flex: 1;
}

.book-option .book-title {
  font-weight: 500;
  color: var(--gray-900);
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.book-option .book-meta {
  font-size: 12px;
  color: var(--gray-500);
  margin-top: 2px;
}

.tags-input {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px;
  border: 1px solid var(--gray-200);
  border-radius: 8px;
  background: var(--gray-50);
  min-height: 44px;
  align-items: center;
}

.tags-input:focus-within {
  border-color: var(--primary-blue);
  background: white;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.tag-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: var(--light-blue);
  color: var(--primary-blue);
  border-radius: 16px;
  font-size: 13px;
  font-weight: 500;
}

.remove-tag {
  background: none;
  border: none;
  color: var(--primary-blue);
  cursor: pointer;
  padding: 0;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.remove-tag:hover {
  background: var(--primary-blue);
  color: white;
}

.tags-input input {
  flex: 1;
  min-width: 120px;
  border: none;
  background: transparent;
  padding: 4px 8px;
  font-size: 14px;
  outline: none;
}

.hint {
  font-size: 12px;
  color: var(--gray-400);
  margin-top: 4px;
  display: block;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--gray-100);
}

.btn {
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
  border: none;
}

.btn-secondary {
  background: var(--gray-100);
  color: var(--gray-700);
}

.btn-secondary:hover {
  background: var(--gray-200);
}

.btn-primary {
  background: var(--primary-blue);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1e40af;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.success-message {
  position: fixed;
  top: 20px;
  right: 20px;
  background: #10b981;
  color: white;
  padding: 14px 24px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
  animation: slideIn 0.3s ease;
  z-index: 1000;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>