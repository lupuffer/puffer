<template>
  <section class="materials-section">
    <!-- 分类标签 -->
    <div class="category-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        class="tab-item"
        :class="{ active: activeTab === tab.value }"
        type="button"
        @click="selectTab(tab)"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- 工具栏 -->
    <div class="content-toolbar">
      <span class="toolbar-title">学习资料</span>
      <div class="sort-options">
        <button
          v-for="option in sortOptions"
          :key="option"
          class="sort-option"
          :class="{ active: activeSort === option }"
          type="button"
          @click="selectSort(option)"
        >
          {{ option }}
        </button>
      </div>
    </div>

    <!-- 资料列表 -->
    <div class="materials-list">
      <div v-if="loading" class="loading-state">
        <i class="fas fa-spinner fa-spin"></i>
        <p>加载中...</p>
      </div>

      <article
        v-for="(material, index) in filteredMaterials"
        v-else
        :key="material.id"
        class="material-card"
        :class="{ expanded: expandedCard === index }"
        @click="toggleCard(index)"
      >
        <div class="material-header">
          <div class="material-type">
            <i :class="getFileIcon(material.fileType)"></i>
            <span>{{ material.fileType?.toUpperCase() || '资料' }}</span>
          </div>
          <div class="material-meta">
            <span class="meta-item">
              <i class="fas fa-download"></i> {{ material.downloadCount || 0 }}
            </span>
            <span class="meta-item">
              <i class="fas fa-star"></i> {{ material.likeCount || 0 }}
            </span>
            <button class="favorite-btn" type="button" @click.stop="handleFavorite(material)">
              <i class="far fa-heart"></i>
            </button>
          </div>
        </div>

        <div class="material-body">
          <h3>{{ material.title }}</h3>
          <p class="material-description">{{ material.description }}</p>
          <div v-if="material.tags?.length" class="material-tags">
            <span v-for="tag in material.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
          <div v-if="expandedCard === index" class="material-details">
            <div class="detail-item">
              <i class="fas fa-file-alt"></i> 文件大小: {{ material.fileSize || '未知' }}
            </div>
            <div class="detail-item">
              <i class="fas fa-calendar"></i> 上传时间: {{ formatDate(material.createdAt) }}
            </div>
            <div class="detail-item">
              <i class="fas fa-folder"></i> 分类: {{ material.category || '未分类' }}
            </div>
          </div>
        </div>

        <div class="material-footer">
          <div class="author-info" @click.stop="handleSelect(material)">
            <div class="author-avatar">
              <i class="fas fa-user-graduate"></i>
            </div>
            <div class="author-details">
              <span class="author-name">{{ material.uploaderName || '未知用户' }}</span>
              <span class="author-course">{{ material.courseName || '通识课程' }}</span>
            </div>
          </div>
          <div class="material-price">
            <span class="price">{{ material.price || '免费' }}</span>
            <button 
              class="btn btn-primary btn-download" 
              type="button" 
              @click.stop="handleDownload(material)"
            >
              <i class="fas fa-download"></i> 下载
            </button>
          </div>
        </div>
      </article>

      <div v-if="!loading && filteredMaterials.length === 0" class="empty-state">
        <i class="fas fa-inbox"></i>
        <p>暂无相关学习资料</p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getKnowledgeMaterials, downloadMaterial } from '@/services/api.js'

const emit = defineEmits(['select', 'download', 'favorite'])

const materials = ref([])
const loading = ref(false)
const activeTab = ref('all')
const activeSort = ref('最新上传')
const expandedCard = ref(null)

const tabs = [
  { label: '全部', value: 'all' },
  { label: '数学', value: 'math' },
  { label: '英语', value: 'english' },
  { label: '计算机', value: 'cs' },
  { label: '物理', value: 'physics' },
  { label: '其他', value: 'other' }
]

const sortOptions = ['最新上传', '最多下载', '最多点赞']

// 加载资料列表
const loadMaterials = async () => {
  loading.value = true
  try {
    const response = await getKnowledgeMaterials()
    if (response.code === 200) {
      materials.value = response.data || []
    }
  } catch (error) {
    console.error('加载资料失败:', error)
  } finally {
    loading.value = false
  }
}

const filteredMaterials = computed(() => {
  let list = [...materials.value]
  
  // 分类筛选
  if (activeTab.value && activeTab.value !== 'all') {
    list = list.filter(m => 
      m.category === activeTab.value || 
      m.courseName?.toLowerCase().includes(activeTab.value)
    )
  }
  
  // 排序
  if (activeSort.value === '最新上传') {
    list.sort((a, b) => new Date(b.createdAt || 0) - new Date(a.createdAt || 0))
  } else if (activeSort.value === '最多下载') {
    list.sort((a, b) => (b.downloadCount || 0) - (a.downloadCount || 0))
  } else if (activeSort.value === '最多点赞') {
    list.sort((a, b) => (b.likeCount || 0) - (a.likeCount || 0))
  }
  
  return list
})

const getFileIcon = (fileType) => {
  const iconMap = {
    'pdf': 'fas fa-file-pdf',
    'doc': 'fas fa-file-word',
    'docx': 'fas fa-file-word',
    'ppt': 'fas fa-file-powerpoint',
    'pptx': 'fas fa-file-powerpoint',
    'zip': 'fas fa-file-archive',
    'rar': 'fas fa-file-archive',
    'jpg': 'fas fa-file-image',
    'png': 'fas fa-file-image',
    'mp4': 'fas fa-file-video'
  }
  return iconMap[fileType?.toLowerCase()] || 'fas fa-file'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '未知'
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

const selectTab = (tab) => {
  activeTab.value = tab.value
}

const selectSort = (option) => {
  activeSort.value = option
}

const toggleCard = (index) => {
  expandedCard.value = expandedCard.value === index ? null : index
}

const handleDownload = async (material) => {
  try {
    await downloadMaterial(material.id)
    material.downloadCount = (material.downloadCount || 0) + 1
    emit('download', material)
  } catch (error) {
    console.error('下载失败:', error)
    alert('下载失败，请重试')
  }
}

const handleFavorite = (material) => {
  emit('favorite', material)
}

const handleSelect = (material) => {
  emit('select', material)
}

onMounted(() => {
  loadMaterials()
})
</script>

<style scoped>
.materials-section {
  padding: 20px;
}

.category-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.tab-item {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid #e5e7eb;
  background: white;
  color: #6b7280;
}

.tab-item.active,
.tab-item:hover {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.content-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.toolbar-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.sort-options {
  display: flex;
  gap: 16px;
}

.sort-option {
  font-size: 14px;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  background: transparent;
  padding: 4px 8px;
  border-radius: 4px;
}

.sort-option.active {
  color: #3b82f6;
  font-weight: 500;
  background: #eff6ff;
}

.materials-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.loading-state {
  text-align: center;
  padding: 60px 20px;
  color: #6b7280;
}

.loading-state i {
  font-size: 32px;
  margin-bottom: 12px;
}

.material-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  transition: all 0.2s ease;
  cursor: pointer;
}

.material-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-color: #3b82f6;
}

.material-card.expanded {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.material-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.material-type {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #eff6ff;
  color: #3b82f6;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.material-type i {
  font-size: 14px;
}

.material-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 14px;
  color: #6b7280;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.favorite-btn {
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  font-size: 18px;
  padding: 4px;
  transition: all 0.2s ease;
}

.favorite-btn:hover {
  color: #ef4444;
  transform: scale(1.1);
}

.material-body h3 {
  font-size: 17px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
}

.material-description {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 12px;
  line-height: 1.6;
}

.material-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.tag {
  padding: 4px 10px;
  background: #f3f4f6;
  color: #4b5563;
  border-radius: 4px;
  font-size: 12px;
}

.material-details {
  margin-top: 12px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.detail-item {
  font-size: 13px;
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 6px;
}

.detail-item i {
  color: #3b82f6;
}

.material-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.author-info:hover {
  opacity: 0.8;
}

.author-avatar {
  width: 40px;
  height: 40px;
  background: #eff6ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #3b82f6;
  font-size: 18px;
}

.author-details {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
}

.author-course {
  font-size: 12px;
  color: #6b7280;
}

.material-price {
  display: flex;
  align-items: center;
  gap: 12px;
}

.price {
  font-size: 18px;
  font-weight: 600;
  color: #3b82f6;
}

.btn-download {
  padding: 10px 20px;
  font-size: 14px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-download:hover {
  background: #2563eb;
  transform: translateY(-1px);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #9ca3af;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 16px;
}

@media (max-width: 640px) {
  .material-footer {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
}
</style>