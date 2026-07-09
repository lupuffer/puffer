<template>
  <div class="isbn-scanner">
    <h3 class="section-title">
      <i class="fas fa-barcode"></i>
      ISBN识别
    </h3>
    
    <!-- 输入模式切换 -->
    <div class="scan-tabs">
      <button :class="{ active: mode === 'camera' }" @click="mode = 'camera'">
        <i class="fas fa-camera"></i> 扫码识别
      </button>
      <button :class="{ active: mode === 'input' }" @click="mode = 'input'">
        <i class="fas fa-keyboard"></i> 手动输入
      </button>
      <button :class="{ active: mode === 'upload' }" @click="mode = 'upload'">
        <i class="fas fa-image"></i> 图片识别
      </button>
    </div>

    <!-- 摄像头扫码模式 -->
    <div v-if="mode === 'camera'" class="scan-panel">
      <div v-if="!scanning" class="camera-placeholder" @click="startCamera">
        <i class="fas fa-video"></i>
        <p>点击开启摄像头扫描ISBN条码</p>
        <span class="hint">支持书籍封面条码自动识别</span>
      </div>
      
      <div v-else class="camera-active">
        <video ref="video" autoplay playsinline class="camera-video"></video>
        <div class="scan-line"></div>
        <div class="scan-overlay">
          <p>将ISBN条码对准框内</p>
        </div>
        <button class="stop-btn" @click="stopCamera">
          <i class="fas fa-times"></i> 取消扫描
        </button>
      </div>
    </div>

    <!-- 手动输入模式 -->
    <div v-if="mode === 'input'" class="input-panel">
      <div class="isbn-input-group">
        <input 
          v-model="isbnInput" 
          type="text" 
          placeholder="请输入13位ISBN码（如：9787040580425）"
          maxlength="13"
          @keyup.enter="queryISBN"
        />
        <button :disabled="!isValidISBN" @click="queryISBN">
          <i class="fas fa-search"></i> 查询
        </button>
      </div>
      <p class="isbn-hint">ISBN通常为10位或13位数字，以978或979开头</p>
    </div>

    <!-- 图片上传模式 -->
    <div v-if="mode === 'upload'" class="upload-panel">
      <div 
        class="upload-zone"
        :class="{ 'is-dragover': isDragOver }"
        @dragenter.prevent="isDragOver = true"
        @dragover.prevent="isDragOver = true"
        @dragleave.prevent="isDragOver = false"
        @drop.prevent="handleImageDrop"
        @click="$refs.imageInput.click()"
      >
        <input 
          ref="imageInput"
          type="file" 
          accept="image/*"
          style="display: none"
          @change="handleImageSelect"
        />
        <i class="fas fa-cloud-upload-alt"></i>
        <p>点击或拖拽上传书籍条码图片</p>
        <span class="hint">支持 JPG、PNG 格式</span>
      </div>
    </div>

    <!-- 识别结果 -->
    <div v-if="scannedISBN" class="scan-result">
      <div class="isbn-display">
        <span class="label">识别结果：</span>
        <span class="code">{{ scannedISBN }}</span>
        <button class="copy-btn" @click="copyISBN">
          <i class="fas fa-copy"></i>
        </button>
      </div>
      <button v-if="!bookInfo" class="query-btn" @click="queryISBN">
        <i class="fas fa-book"></i> 查询书籍信息
      </button>
    </div>

    <!-- 书籍信息 -->
    <div v-if="bookInfo" class="book-info">
      <h4><i class="fas fa-check-circle"></i> 查询成功</h4>
      <div class="book-detail">
        <img v-if="bookInfo.cover" :src="bookInfo.cover" alt="封面" class="book-cover" />
        <div class="book-meta">
          <p class="title">{{ bookInfo.title }}</p>
          <p class="author">作者：{{ bookInfo.author }}</p>
          <p class="publisher">出版社：{{ bookInfo.publisher }}</p>
          <p class="isbn">ISBN：{{ bookInfo.isbn }}</p>
          <p v-if="bookInfo.price" class="price">定价：{{ bookInfo.price }}</p>
        </div>
      </div>
      <div class="action-btns">
        <button class="use-btn" @click="useBookInfo">
          <i class="fas fa-check"></i> 使用该信息
        </button>
        <button class="reset-btn" @click="reset">重新识别</button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <i class="fas fa-spinner fa-spin"></i>
      <span>{{ loadingText }}</span>
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMsg" class="error-alert">
      <i class="fas fa-exclamation-triangle"></i>
      {{ errorMsg }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onBeforeUnmount } from 'vue'

const emit = defineEmits(['scanned', 'bookInfo'])

const mode = ref('camera')
const isbnInput = ref('')
const scannedISBN = ref('')
const bookInfo = ref(null)
const loading = ref(false)
const loadingText = ref('')
const errorMsg = ref('')
const scanning = ref(false)
const isDragOver = ref(false)

const video = ref(null)
let stream = null

const isValidISBN = computed(() => {
  const isbn = isbnInput.value.trim()
  return /^(978|979)\d{10}$/.test(isbn) || /^\d{9}[\dX]$/.test(isbn)
})

// 摄像头扫描
const startCamera = async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ 
      video: { facingMode: 'environment' } 
    })
    scanning.value = true
    setTimeout(() => {
      if (video.value) {
        video.value.srcObject = stream
        startScanning()
      }
    }, 100)
  } catch (err) {
    errorMsg.value = '无法访问摄像头，请检查权限或使用其他模式'
  }
}

const startScanning = () => {
  // 模拟扫描成功（实际项目中使用 jsQR 或 zxing 库）
  setTimeout(() => {
    if (scanning.value) {
      scannedISBN.value = '9787040580425'
      stopCamera()
    }
  }, 3000)
}

const stopCamera = () => {
  scanning.value = false
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
    stream = null
  }
}

// 图片上传识别
const handleImageDrop = (e) => {
  isDragOver.value = false
  const file = e.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    processImage(file)
  }
}

const handleImageSelect = (e) => {
  const file = e.target.files[0]
  if (file) {
    processImage(file)
  }
}

const processImage = async (file) => {
  loading.value = true
  loadingText.value = '正在识别条码...'
  errorMsg.value = ''
  
  const formData = new FormData()
  formData.append('image', file)
  
  try {
    const response = await fetch('/api/isbn/scan', {
      method: 'POST',
      body: formData
    })
    
    const data = await response.json()
    
    if (data.code === 200 && data.data.isbn) {
      scannedISBN.value = data.data.isbn
    } else {
      errorMsg.value = '未能识别ISBN条码，请尝试手动输入'
    }
  } catch (err) {
    errorMsg.value = '识别失败，请重试或切换模式'
  } finally {
    loading.value = false
  }
}

// ISBN查询
const queryISBN = async () => {
  const isbn = scannedISBN.value || isbnInput.value.trim()
  if (!isbn) return
  
  loading.value = true
  loadingText.value = '正在查询书籍信息...'
  errorMsg.value = ''
  
  try {
    const response = await fetch(`/api/isbn/query?isbn=${encodeURIComponent(isbn)}`)
    
    const data = await response.json()
    
    if (data.code === 200 && data.data) {
      bookInfo.value = data.data
      emit('scanned', { isbn, bookInfo: bookInfo.value })
    } else {
      errorMsg.value = '未找到该ISBN对应的书籍信息'
    }
  } catch (err) {
    errorMsg.value = '查询失败，请检查网络或ISBN是否正确'
  } finally {
    loading.value = false
  }
}

const copyISBN = () => {
  navigator.clipboard.writeText(scannedISBN.value)
  alert('ISBN已复制到剪贴板')
}

const useBookInfo = () => {
  emit('bookInfo', bookInfo.value)
  reset()
}

const reset = () => {
  isbnInput.value = ''
  scannedISBN.value = ''
  bookInfo.value = null
  errorMsg.value = ''
}

onBeforeUnmount(() => {
  stopCamera()
})
</script>

<style scoped>
.isbn-scanner {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title i {
  color: #3b82f6;
}

.scan-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.scan-tabs button {
  flex: 1;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  background: #f9fafb;
  color: #6b7280;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.scan-tabs button.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

/* 摄像头模式 */
.camera-placeholder {
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  padding: 60px 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #f9fafb;
}

.camera-placeholder:hover {
  border-color: #3b82f6;
  background: #eff6ff;
}

.camera-placeholder i {
  font-size: 64px;
  color: #9ca3af;
  margin-bottom: 16px;
}

.camera-placeholder p {
  font-size: 16px;
  color: #374151;
  margin-bottom: 8px;
}

.camera-active {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  background: #000;
}

.camera-video {
  width: 100%;
  height: 300px;
  object-fit: cover;
}

.scan-line {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 2px;
  background: #10b981;
  box-shadow: 0 0 10px #10b981;
  animation: scan 2s linear infinite;
}

@keyframes scan {
  0%, 100% { opacity: 0; }
  50% { opacity: 1; }
}

.scan-overlay {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
}

.stop-btn {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 10px 24px;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

/* 输入模式 */
.isbn-input-group {
  display: flex;
  gap: 12px;
}

.isbn-input-group input {
  flex: 1;
  padding: 14px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  font-size: 16px;
}

.isbn-input-group button {
  padding: 14px 24px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
}

.isbn-input-group button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.isbn-hint {
  margin-top: 12px;
  font-size: 13px;
  color: #6b7280;
}

/* 上传模式 */
.upload-zone {
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  padding: 60px 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #f9fafb;
}

.upload-zone:hover,
.upload-zone.is-dragover {
  border-color: #3b82f6;
  background: #eff6ff;
}

.upload-zone i {
  font-size: 48px;
  color: #9ca3af;
  margin-bottom: 12px;
}

/* 识别结果 */
.scan-result {
  margin-top: 20px;
  padding: 16px;
  background: #eff6ff;
  border-radius: 10px;
  text-align: center;
}

.isbn-display {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 12px;
}

.isbn-display .label {
  color: #6b7280;
}

.isbn-display .code {
  font-size: 20px;
  font-weight: 600;
  color: #3b82f6;
  font-family: monospace;
}

.copy-btn {
  padding: 6px 10px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  cursor: pointer;
  color: #6b7280;
}

.query-btn {
  padding: 10px 24px;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

/* 书籍信息 */
.book-info {
  margin-top: 20px;
  padding: 20px;
  background: #f0fdf4;
  border-radius: 12px;
  border: 1px solid #10b981;
}

.book-info h4 {
  color: #047857;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.book-detail {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.book-cover {
  width: 100px;
  height: 140px;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.book-meta {
  flex: 1;
}

.book-meta .title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
}

.book-meta p {
  margin: 4px 0;
  font-size: 14px;
  color: #4b5563;
}

.book-meta .price {
  color: #dc2626;
  font-weight: 600;
}

.action-btns {
  display: flex;
  gap: 12px;
}

.use-btn {
  flex: 1;
  padding: 12px;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.reset-btn {
  padding: 12px 24px;
  background: white;
  color: #6b7280;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
}

/* 加载和错误 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  gap: 16px;
  z-index: 100;
}

.loading-overlay i {
  font-size: 48px;
}

.error-alert {
  margin-top: 16px;
  padding: 12px;
  background: #fef2f2;
  color: #ef4444;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>