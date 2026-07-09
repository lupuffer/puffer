<template>
  <div class="isbn-barcode-uploader">
    <!-- 拖拽上传区域 -->
    <div
      class="drop-zone"
      :class="{
        'is-dragover': isDragOver,
        'is-loading': isLoading,
        'has-preview': previewUrl
      }"
      @dragenter.prevent="isDragOver = true"
      @dragover.prevent="isDragOver = true"
      @dragleave.prevent="isDragOver = false"
      @drop.prevent="handleDrop"
      @click="!isLoading && !previewUrl && $refs.fileInput.click()"
    >
      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        style="display: none"
        @change="handleFileSelect"
      />

      <!-- 默认状态 -->
      <div v-if="!previewUrl && !isLoading" class="upload-placeholder">
        <div class="upload-icon-wrapper">
          <i class="fas fa-barcode"></i>
          <div class="scan-line"></div>
        </div>
        <h4 class="upload-title">将带有本地数据库 ISBN 数字的图片拖拽到此处</h4>
        <p class="upload-subtitle">支持 JPG, PNG 格式（测试时可将图片重命名为库中现有的 ISBN 上传）</p>
      </div>

      <!-- 图片预览 + 加载状态 -->
      <div v-if="previewUrl" class="preview-container">
        <img :src="previewUrl" alt="预览" class="preview-image" />
        
        <!-- 加载遮罩层 -->
        <div v-if="isLoading" class="loading-overlay">
          <div class="scanner-effect">
            <div class="laser-line"></div>
            <div class="scan-grid"></div>
          </div>
          <div class="loading-content">
            <div class="spinner-ring">
              <div class="ring ring-1"></div>
              <div class="ring ring-2"></div>
              <div class="ring ring-3"></div>
            </div>
            <p class="loading-text">正在智能扫描并匹配本地虚拟数据库...</p>
            <p class="loading-subtext">云端 OCR 识别中 | 提取 ISBN | 检索 10 万条种子数据</p>
          </div>
        </div>

        <!-- 关闭按钮 -->
        <button v-if="!isLoading" class="close-btn" @click.stop="clearAll">
          <i class="fas fa-times"></i>
        </button>
      </div>
    </div>

    <!-- 识别成功提示 -->
    <transition name="slide-up">
      <div v-if="showSuccess" class="success-toast">
        <i class="fas fa-check-circle"></i>
        <span>识别成功！已自动填充表单</span>
      </div>
    </transition>

    <!-- 错误提示 -->
    <transition name="slide-up">
      <div v-if="errorMsg" class="error-toast">
        <i class="fas fa-exclamation-circle"></i>
        <span>{{ errorMsg }}</span>
        <button class="close-error" @click="errorMsg = ''">
          <i class="fas fa-times"></i>
        </button>
      </div>
    </transition>

    <!-- 使用说明 -->
    <div class="usage-tips">
      <div class="tips-header" @click="showTips = !showTips">
        <i class="fas fa-lightbulb"></i>
        <span>使用提示</span>
        <i class="fas fa-chevron-down" :class="{ 'is-open': showTips }"></i>
      </div>
      <transition name="expand">
        <div v-show="showTips" class="tips-content">
          <ul>
            <li>
              <span class="tip-tag">云端识别</span>
              上传条码图片，自动调用 OCR 服务提取 ISBN
            </li>
            <li>
              <span class="tip-tag">文件名后门</span>
              将图片重命名为 <code>9787229030933.jpg</code> 格式可直接识别
            </li>
            <li>
              <span class="tip-tag">自动填表</span>
              识别成功后将自动填充书名、作者、价格等表单字段
            </li>
          </ul>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['bookRecognized'])

const isDragOver = ref(false)
const isLoading = ref(false)
const previewUrl = ref('')
const selectedFile = ref(null)
const errorMsg = ref('')
const showSuccess = ref(false)
const showTips = ref(true)

// 处理拖拽
const handleDrop = (e) => {
  isDragOver.value = false
  const file = e.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    processFile(file)
  }
}

// 处理文件选择
const handleFileSelect = (e) => {
  const file = e.target.files[0]
  if (file) {
    processFile(file)
  }
}

// 处理文件
const processFile = (file) => {
  selectedFile.value = file
  errorMsg.value = ''
  
  // 创建预览
  const reader = new FileReader()
  reader.onload = (e) => {
    previewUrl.value = e.target.result
    // 自动开始识别
    recognizeISBN()
  }
  reader.readAsDataURL(file)
}

// 识别 ISBN
const recognizeISBN = async () => {
  if (!selectedFile.value) return
  
  isLoading.value = true
  errorMsg.value = ''
  
  const formData = new FormData()
  formData.append('image', selectedFile.value)
  
    try {
        const response = await fetch('/api/books/scan', {
          method: 'POST',
          body: formData
        })
        
        const data = await response.json()
        console.log('ISBN识别API返回:', data)  // 调试日志
        
        if (response.ok && data.status === 'ok' && data.book) {
          // 识别成功，填充表单
          fillForm(data.book)
          showSuccess.value = true
          setTimeout(() => {
            showSuccess.value = false
          }, 3000)
        } else {
          // 显示详细错误信息
          if (data.error) {
            errorMsg.value = data.error
          } else if (data.isbn) {
            errorMsg.value = `识别到ISBN: ${data.isbn}，但数据库中不存在该书籍`
          } else {
            errorMsg.value = '识别失败，请重试'
          }
        }
      } catch (err) {
        console.error('ISBN识别请求失败:', err)
        errorMsg.value = '网络错误，请检查后端服务是否运行或网络连接是否正常'
      } finally {
        isLoading.value = false
      }
}

// 填充表单
const fillForm = (book) => {
  // 添加闪烁高亮效果
  setTimeout(() => {
    emit('bookRecognized', book)
  }, 100)
}

// 清除所有
const clearAll = () => {
  selectedFile.value = null
  previewUrl.value = ''
  errorMsg.value = ''
  showSuccess.value = false
  isLoading.value = false
}
</script>

<style scoped>
.isbn-barcode-uploader {
  width: 100%;
}

/* ========== 拖拽上传区域 ========== */
.drop-zone {
  position: relative;
  border: 3px dashed rgba(59, 130, 246, 0.3);
  border-radius: 16px;
  padding: 48px 32px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: linear-gradient(135deg, #fafbff 0%, #f0f4ff 100%);
  overflow: hidden;
}

.drop-zone:hover {
  border-color: rgba(59, 130, 246, 0.6);
  background: linear-gradient(135deg, #f5f8ff 0%, #e8eeff 100%);
}

.drop-zone.is-dragover {
  border-style: solid;
  border-color: #3b82f6;
  border-width: 3px;
  background: rgba(59, 130, 246, 0.05);
  box-shadow: inset 0 0 30px rgba(59, 130, 246, 0.1);
  transform: scale(0.98);
}

.drop-zone.is-loading {
  cursor: default;
  border-color: #3b82f6;
}

.drop-zone.has-preview {
  padding: 0;
  min-height: 280px;
  border-style: solid;
  border-color: #e5e7eb;
}

/* ========== 上传占位符 ========== */
.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.upload-icon-wrapper {
  position: relative;
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(59, 130, 246, 0.3);
}

.upload-icon-wrapper i {
  font-size: 36px;
  color: white;
}

.scan-line {
  position: absolute;
  top: 50%;
  left: 10%;
  right: 10%;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.8), transparent);
  animation: scan 2s ease-in-out infinite;
}

@keyframes scan {
  0%, 100% { transform: translateY(-20px); opacity: 0; }
  50% { transform: translateY(20px); opacity: 1; }
}

.upload-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.upload-subtitle {
  font-size: 13px;
  color: #64748b;
  margin: 0;
  max-width: 400px;
  line-height: 1.5;
}

/* ========== 预览容器 ========== */
.preview-container {
  position: relative;
  width: 100%;
  height: 280px;
  overflow: hidden;
  border-radius: 12px;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #f8fafc;
}

/* ========== 加载遮罩 ========== */
.loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(4px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 24px;
}

.scanner-effect {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.laser-line {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, 
    transparent, 
    #ef4444 20%, 
    #ef4444 80%, 
    transparent
  );
  box-shadow: 0 0 10px #ef4444, 0 0 20px #ef4444;
  animation: laser-scan 2s ease-in-out infinite;
}

@keyframes laser-scan {
  0%, 100% { top: 10%; opacity: 0.3; }
  50% { top: 90%; opacity: 1; }
}

.scan-grid {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(rgba(239, 68, 68, 0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(239, 68, 68, 0.1) 1px, transparent 1px);
  background-size: 30px 30px;
  animation: grid-pulse 2s ease-in-out infinite;
}

@keyframes grid-pulse {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.6; }
}

/* ========== 加载内容 ========== */
.loading-content {
  position: relative;
  z-index: 10;
  text-align: center;
}

.spinner-ring {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
}

.ring {
  position: absolute;
  border-radius: 50%;
  border: 3px solid transparent;
  animation: spin 2s linear infinite;
}

.ring-1 {
  inset: 0;
  border-top-color: #3b82f6;
  animation-duration: 1.5s;
}

.ring-2 {
  inset: 8px;
  border-right-color: #10b981;
  animation-duration: 2s;
  animation-direction: reverse;
}

.ring-3 {
  inset: 16px;
  border-bottom-color: #f59e0b;
  animation-duration: 2.5s;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 16px;
  font-weight: 600;
  color: white;
  margin: 0 0 8px;
}

.loading-subtext {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

/* ========== 关闭按钮 ========== */
.close-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  z-index: 20;
}

.close-btn:hover {
  background: rgba(0, 0, 0, 0.7);
  transform: rotate(90deg);
}

/* ========== 成功提示 ========== */
.success-toast {
  margin-top: 16px;
  padding: 14px 20px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 500;
  box-shadow: 0 4px 20px rgba(16, 185, 129, 0.3);
  animation: slide-up 0.3s ease;
}

.success-toast i {
  font-size: 20px;
}

/* ========== 错误提示 ========== */
.error-toast {
  margin-top: 16px;
  padding: 14px 20px;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 500;
  box-shadow: 0 4px 20px rgba(239, 68, 68, 0.3);
  animation: slide-up 0.3s ease;
}

.error-toast i {
  font-size: 20px;
}

.close-error {
  margin-left: auto;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-error:hover {
  background: rgba(255, 255, 255, 0.3);
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* ========== 使用提示 ========== */
.usage-tips {
  margin-top: 16px;
  background: #f8fafc;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.tips-header {
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
}

.tips-header:hover {
  background: #f1f5f9;
}

.tips-header i:first-child {
  color: #f59e0b;
}

.tips-header .fa-chevron-down {
  margin-left: auto;
  transition: transform 0.2s;
  font-size: 12px;
  color: #94a3b8;
}

.tips-header .fa-chevron-down.is-open {
  transform: rotate(180deg);
}

.tips-content {
  padding: 0 16px 16px;
}

.tips-content ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

.tips-content li {
  padding: 10px 0;
  font-size: 13px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid #e2e8f0;
}

.tips-content li:last-child {
  border-bottom: none;
}

.tip-tag {
  display: inline-block;
  padding: 4px 10px;
  background: #e0e7ff;
  color: #4338ca;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 500;
  white-space: nowrap;
}

.tips-content code {
  background: #e2e8f0;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 12px;
  color: #475569;
}

/* ========== 展开动画 ========== */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  max-height: 200px;
  opacity: 1;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
  padding: 0 16px;
}
</style>