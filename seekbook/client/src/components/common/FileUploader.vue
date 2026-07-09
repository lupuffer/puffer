<template>
  <div class="file-uploader">
    <!-- 拖拽上传区域 -->
    <div
      class="upload-zone"
      :class="{ 
        'is-dragover': isDragOver, 
        'has-file': previewUrl,
        'is-disabled': disabled 
      }"
      @click="handleClick"
      @dragenter.prevent="handleDragEnter"
      @dragover.prevent="handleDragOver"
      @dragleave.prevent="handleDragLeave"
      @drop.prevent="handleDrop"
    >
      <input
        ref="fileInput"
        type="file"
        :accept="accept"
        :multiple="multiple"
        class="file-input"
        @change="handleFileChange"
      />
      
      <!-- 有预览图时显示预览 -->
      <div v-if="previewUrl" class="preview-container">
        <img v-if="isImage" :src="previewUrl" alt="预览" class="preview-image" />
        <div v-else class="file-preview">
          <i class="fas fa-file"></i>
          <span class="file-name">{{ selectedFile?.name }}</span>
        </div>
        <button 
          v-if="!uploading" 
          type="button" 
          class="remove-btn" 
          @click.stop="handleRemove"
        >
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <!-- 上传中状态 -->
      <div v-else-if="uploading" class="upload-status">
        <i class="fas fa-spinner fa-spin"></i>
        <span>上传中... {{ uploadProgress }}%</span>
      </div>
      
      <!-- 默认提示 -->
      <div v-else class="upload-placeholder">
        <i class="fas fa-cloud-upload-alt"></i>
        <p class="main-text">{{ placeholder }}</p>
        <p class="sub-text">点击或拖拽文件到此处</p>
        <p class="hint-text">支持 {{ acceptText }} 格式，最大 {{ maxSizeMB }}MB</p>
      </div>
    </div>
    
    <!-- 上传按钮（非自动上传模式下显示） -->
    <div v-if="selectedFile && !uploadedUrl && !uploading && !autoUpload" class="upload-actions">
      <button type="button" class="btn-upload" @click="handleUpload">
        <i class="fas fa-upload"></i>
        确认上传
      </button>
      <button type="button" class="btn-cancel" @click="handleRemove">
        取消
      </button>
    </div>
    
    <!-- 上传结果 -->
    <div v-if="uploadedUrl" class="upload-result">
      <i class="fas fa-check-circle"></i>
      <span>上传成功</span>
      <a :href="uploadedUrl" target="_blank" class="view-link">查看文件</a>
    </div>
    
    <!-- 错误提示 -->
    <div v-if="errorMessage" class="error-message">
      <i class="fas fa-exclamation-circle"></i>
      {{ errorMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  // 接受的文件类型
  accept: {
    type: String,
    default: 'image/*' // 默认只接受图片
  },
  // 允许多选
  multiple: {
    type: Boolean,
    default: false
  },
  // 最大文件大小（MB）
  maxSize: {
    type: Number,
    default: 5
  },
  // 占位提示文字
  placeholder: {
    type: String,
    default: '上传图片'
  },
  // 上传地址
  uploadUrl: {
    type: String,
    default: '/api/upload'
  },
  // 选择文件后是否自动上传
  autoUpload: {
    type: Boolean,
    default: false
  },
  // 后端上传失败时是否退回到本地可用地址
  useLocalFallback: {
    type: Boolean,
    default: false
  },
  // 是否禁用
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['success', 'error', 'remove'])

const fileInput = ref(null)
const isDragOver = ref(false)
const selectedFile = ref(null)
const previewUrl = ref('')
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadedUrl = ref('')
const errorMessage = ref('')

// 计算属性
const isImage = computed(() => {
  if (!selectedFile.value) return false
  return selectedFile.value.type.startsWith('image/')
})

const acceptText = computed(() => {
  if (props.accept === 'image/*') return '图片'
  if (props.accept === '*') return '所有'
  return props.accept
})

const maxSizeMB = computed(() => props.maxSize)

const extensionMatches = (fileName, rule) => {
  if (!rule.startsWith('.')) return false
  return fileName.toLowerCase().endsWith(rule.toLowerCase())
}

const mimeMatches = (fileType, rule) => {
  if (rule === '*') return true
  if (rule.endsWith('/*')) {
    const prefix = rule.slice(0, -1)
    return fileType.startsWith(prefix)
  }
  if (rule.includes('/')) {
    return fileType === rule
  }
  return false
}

const isAcceptedFile = (file) => {
  if (props.accept === '*' || !props.accept) {
    return true
  }

  const rules = props.accept
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)

  return rules.some((rule) => extensionMatches(file.name, rule) || mimeMatches(file.type, rule))
}

const readFileAsDataUrl = (file) =>
  new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result || ''))
    reader.onerror = () => reject(new Error('本地图片读取失败'))
    reader.readAsDataURL(file)
  })

// 方法
const handleClick = () => {
  if (props.disabled || uploading.value) return
  fileInput.value?.click()
}

const handleDragEnter = () => {
  if (props.disabled) return
  isDragOver.value = true
}

const handleDragOver = () => {
  if (props.disabled) return
  isDragOver.value = true
}

const handleDragLeave = () => {
  isDragOver.value = false
}

const handleDrop = (e) => {
  if (props.disabled) return
  isDragOver.value = false
  
  const files = e.dataTransfer.files
  if (files.length > 0) {
    processFile(files[0])
  }
}

const handleFileChange = (e) => {
  const files = e.target.files
  if (files.length > 0) {
    processFile(files[0])
  }
}

const processFile = (file) => {
  // 重置状态
  errorMessage.value = ''
  uploadedUrl.value = ''
  
  // 验证文件类型
  if (!isAcceptedFile(file)) {
    errorMessage.value = `不支持的文件格式，请上传 ${acceptText.value} 文件`
    return
  }
  
  // 验证文件大小
  if (file.size > props.maxSize * 1024 * 1024) {
    errorMessage.value = `文件过大，最大支持 ${props.maxSize}MB`
    return
  }
  
  selectedFile.value = file
  
  // 创建预览URL
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }
  previewUrl.value = URL.createObjectURL(file)

  if (props.autoUpload) {
    handleUpload()
  }
}

const handleUpload = async () => {
  if (!selectedFile.value) return
  
  uploading.value = true
  uploadProgress.value = 0
  errorMessage.value = ''
  
  // 创建 FormData
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  
  try {
    // 模拟进度
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += 10
      }
    }, 200)
    
    const response = await fetch(props.uploadUrl, {
      method: 'POST',
      body: formData
    })

    clearInterval(progressInterval)
    uploadProgress.value = 100

    if (!response.ok) {
      throw new Error(`上传失败（${response.status}）`)
    }
    
    const data = await response.json()
    
    if (data.code === 200 && data?.data?.url) {
      uploadedUrl.value = data.data.url
      emit('success', {
        url: data.data.url,
        filename: data.data.filename,
        originalName: selectedFile.value.name,
        size: selectedFile.value.size
      })
    } else {
      throw new Error(data.message || '上传失败')
    }
  } catch (error) {
    console.error('上传失败:', error)

    if (props.useLocalFallback && selectedFile.value) {
      try {
        const localUrl = await readFileAsDataUrl(selectedFile.value)
        uploadedUrl.value = localUrl
        uploadProgress.value = 100
        errorMessage.value = ''
        emit('success', {
          url: localUrl,
          filename: selectedFile.value.name,
          originalName: selectedFile.value.name,
          size: selectedFile.value.size,
          local: true
        })
        return
      } catch (fallbackError) {
        errorMessage.value = fallbackError.message || '本地图片处理失败'
        emit('error', fallbackError)
      }
    } else {
      errorMessage.value = error.message || '上传失败，请重试'
      emit('error', error)
    }
  } finally {
    uploading.value = false
  }
}

const handleRemove = () => {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }
  selectedFile.value = null
  previewUrl.value = ''
  uploadedUrl.value = ''
  errorMessage.value = ''
  uploadProgress.value = 0
  if (fileInput.value) {
    fileInput.value.value = ''
  }
  emit('remove')
}

// 暴露方法给父组件
defineExpose({
  clear: handleRemove,
  upload: handleUpload,
  getFile: () => selectedFile.value
})
</script>

<style scoped>
.file-uploader {
  width: 100%;
}

.upload-zone {
  position: relative;
  width: 100%;
  min-height: 200px;
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  background: #f9fafb;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.upload-zone:hover {
  border-color: #3b82f6;
  background: #eff6ff;
}

.upload-zone.is-dragover {
  border-color: #3b82f6;
  background: #dbeafe;
  transform: scale(1.02);
}

.upload-zone.has-file {
  border-style: solid;
  border-color: #10b981;
  background: #f0fdf4;
}

.upload-zone.is-disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.file-input {
  display: none;
}

/* 预览区域 */
.preview-container {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.preview-image {
  max-width: 100%;
  max-height: 300px;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.file-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 32px;
}

.file-preview i {
  font-size: 64px;
  color: #6b7280;
}

.file-name {
  font-size: 14px;
  color: #374151;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remove-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(239, 68, 68, 0.9);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  z-index: 10;
}

.remove-btn:hover {
  background: #dc2626;
  transform: scale(1.1);
}

/* 上传状态 */
.upload-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #3b82f6;
}

.upload-status i {
  font-size: 48px;
}

/* 默认提示 */
.upload-placeholder {
  text-align: center;
  padding: 32px;
  color: #6b7280;
}

.upload-placeholder i {
  font-size: 64px;
  margin-bottom: 16px;
  color: #d1d5db;
}

.main-text {
  font-size: 18px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
}

.sub-text {
  font-size: 14px;
  margin-bottom: 4px;
}

.hint-text {
  font-size: 12px;
  color: #9ca3af;
}

/* 操作按钮 */
.upload-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  justify-content: center;
}

.btn-upload,
.btn-cancel {
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  border: none;
}

.btn-upload {
  background: #3b82f6;
  color: white;
}

.btn-upload:hover {
  background: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.btn-cancel {
  background: #f3f4f6;
  color: #6b7280;
}

.btn-cancel:hover {
  background: #e5e7eb;
}

/* 上传结果 */
.upload-result {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 16px;
  padding: 12px;
  background: #f0fdf4;
  border-radius: 8px;
  color: #10b981;
}

.upload-result i {
  font-size: 20px;
}

.view-link {
  color: #059669;
  text-decoration: underline;
  margin-left: 8px;
}

.view-link:hover {
  color: #047857;
}

/* 错误提示 */
.error-message {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 12px;
  padding: 12px;
  background: #fef2f2;
  border-radius: 8px;
  color: #ef4444;
  font-size: 14px;
}

.error-message i {
  font-size: 16px;
}
</style>
