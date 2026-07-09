<template>
  <div class="upload-demo">
    <h2>文件上传演示</h2>
    
    <div class="demo-section">
      <h3>1. 图片上传（默认）</h3>
      <FileUploader
        accept="image/*"
        :max-size="5"
        placeholder="上传书籍封面图片"
        @success="handleImageSuccess"
        @error="handleError"
      />
    </div>
    
    <div class="demo-section">
      <h3>2. 通用文件上传</h3>
      <FileUploader
        accept="*"
        :max-size="10"
        placeholder="上传任意文件"
        upload-url="/api/upload"
        @success="handleFileSuccess"
        @error="handleError"
      />
    </div>
    
    <div class="demo-section">
      <h3>3. 仅限特定图片格式</h3>
      <FileUploader
        accept=".jpg,.jpeg,.png"
        :max-size="2"
        placeholder="上传 JPG/PNG 图片"
        upload-url="/api/upload"
        @success="handleLimitedSuccess"
        @error="handleError"
      />
    </div>
    
    <!-- 上传结果展示 -->
    <div v-if="uploadResults.length > 0" class="results-section">
      <h3>上传结果</h3>
      <div v-for="(result, index) in uploadResults" :key="index" class="result-item">
        <img v-if="result.isImage" :src="result.url" alt="上传的图片" class="result-image" />
        <div class="result-info">
          <p><strong>文件名：</strong>{{ result.originalName }}</p>
          <p><strong>访问URL：</strong><a :href="result.url" target="_blank">{{ result.url }}</a></p>
          <p><strong>大小：</strong>{{ formatSize(result.size) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import FileUploader from './FileUploader.vue'

const uploadResults = ref([])

const handleImageSuccess = (data) => {
  console.log('图片上传成功:', data)
  uploadResults.value.unshift({
    ...data,
    isImage: true
  })
}

const handleFileSuccess = (data) => {
  console.log('文件上传成功:', data)
  uploadResults.value.unshift({
    ...data,
    isImage: false
  })
}

const handleLimitedSuccess = (data) => {
  console.log('限定格式上传成功:', data)
  uploadResults.value.unshift({
    ...data,
    isImage: true
  })
}

const handleError = (error) => {
  console.error('上传失败:', error)
}

const formatSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}
</script>

<style scoped>
.upload-demo {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}

h2 {
  color: #1f2937;
  margin-bottom: 24px;
  text-align: center;
}

.demo-section {
  margin-bottom: 32px;
  padding: 24px;
  background: #f9fafb;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.demo-section h3 {
  color: #374151;
  margin-bottom: 16px;
  font-size: 16px;
}

.results-section {
  margin-top: 32px;
  padding: 24px;
  background: #f0fdf4;
  border-radius: 12px;
  border: 1px solid #10b981;
}

.results-section h3 {
  color: #047857;
  margin-bottom: 16px;
}

.result-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  margin-bottom: 12px;
}

.result-image {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 8px;
}

.result-info {
  flex: 1;
}

.result-info p {
  margin: 4px 0;
  font-size: 14px;
  color: #4b5563;
}

.result-info a {
  color: #3b82f6;
  text-decoration: underline;
}
</style>