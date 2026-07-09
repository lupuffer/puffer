<template>
  <div class="schedule-uploader">
    <h3 class="section-title">
      <i class="fas fa-calendar-alt"></i>
      导入课程表
    </h3>
    
    <!-- 上传区域 -->
    <div class="upload-tabs">
      <button 
        :class="{ active: activeTab === 'file' }" 
        @click="activeTab = 'file'"
      >
        <i class="fas fa-file-excel"></i> 上传文件
      </button>
      <button 
        :class="{ active: activeTab === 'manual' }" 
        @click="activeTab = 'manual'"
      >
        <i class="fas fa-edit"></i> 手动填写
      </button>
    </div>

    <!-- 文件上传模式 -->
    <div v-if="activeTab === 'file'" class="upload-panel">
      <div class="template-info">
        <p><i class="fas fa-info-circle"></i> 支持 .xlsx 或 .json 格式</p>
        <a href="#" @click.prevent="downloadTemplate" class="download-link">
          <i class="fas fa-download"></i> 下载 JSON 模板
        </a>
      </div>
      
      <div 
        class="drop-zone"
        :class="{ 'is-dragover': isDragOver }"
        @dragenter.prevent="isDragOver = true"
        @dragover.prevent="isDragOver = true"
        @dragleave.prevent="isDragOver = false"
        @drop.prevent="handleDrop"
        @click="$refs.fileInput.click()"
      >
        <input 
          ref="fileInput"
          type="file" 
          accept=".xlsx,.xls,.json"
          style="display: none"
          @change="handleFileSelect"
        />
        <i class="fas fa-cloud-upload-alt"></i>
        <p>点击或拖拽文件到此处</p>
        <span class="hint">支持 Excel (.xlsx) 或 JSON 格式</span>
      </div>

      <!-- 已选文件 -->
      <div v-if="selectedFile" class="file-info">
        <i class="fas fa-file"></i>
        <span>{{ selectedFile.name }}</span>
        <button @click="clearFile" class="clear-btn"><i class="fas fa-times"></i></button>
      </div>

      <!-- 解析按钮 -->
      <button 
        v-if="selectedFile"
        class="parse-btn"
        :disabled="parsing"
        @click="parseSchedule"
      >
        <i :class="parsing ? 'fas fa-spinner fa-spin' : 'fas fa-magic'"></i>
        {{ parsing ? '解析中...' : '生成智慧清单' }}
      </button>
    </div>

    <!-- 手动填写模式 -->
    <div v-else class="manual-panel">
      <div class="course-form">
        <div v-for="(course, index) in manualCourses" :key="index" class="course-row">
          <input 
            v-model="course.name" 
            placeholder="课程名称"
            class="course-name"
          />
          <select v-model="course.day" class="course-day">
            <option value="">星期</option>
            <option v-for="d in 7" :key="d" :value="d">周{{ ['一','二','三','四','五','六','日'][d-1] }}</option>
          </select>
          <input 
            v-model="course.time" 
            placeholder="节次(如: 1-2)"
            class="course-time"
          />
          <button @click="removeCourse(index)" class="remove-btn">
            <i class="fas fa-minus"></i>
          </button>
        </div>
        <button @click="addCourse" class="add-btn">
          <i class="fas fa-plus"></i> 添加课程
        </button>
      </div>

      <button 
        class="parse-btn"
        :disabled="parsing || manualCourses.length === 0"
        @click="submitManualCourses"
      >
        <i :class="parsing ? 'fas fa-spinner fa-spin' : 'fas fa-magic'"></i>
        {{ parsing ? '生成中...' : '生成智慧清单' }}
      </button>
    </div>

    <!-- 解析结果预览 -->
    <div v-if="parsedData" class="result-preview">
      <h4><i class="fas fa-check-circle"></i> 已成功识别 {{ parsedData.courses.length }} 门课程</h4>
      <div class="course-tags">
        <span v-for="course in parsedData.courses" :key="course" class="tag">
          {{ course }}
        </span>
      </div>
      <div class="action-btns">
        <button @click="applyToSmartList" class="apply-btn">
          <i class="fas fa-check"></i> 应用到智慧清单
        </button>
        <button @click="reset" class="reset-btn">重新上传</button>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMsg" class="error-alert">
      <i class="fas fa-exclamation-triangle"></i>
      {{ errorMsg }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['parsed'])

const activeTab = ref('file')
const isDragOver = ref(false)
const selectedFile = ref(null)
const parsing = ref(false)
const parsedData = ref(null)
const errorMsg = ref('')

const manualCourses = ref([
  { name: '', day: '', time: '' }
])

const handleDrop = (e) => {
  isDragOver.value = false
  const files = e.dataTransfer.files
  if (files.length > 0) {
    validateAndSetFile(files[0])
  }
}

const handleFileSelect = (e) => {
  const file = e.target.files[0]
  if (file) {
    validateAndSetFile(file)
  }
}

const validateAndSetFile = (file) => {
  const validExtensions = ['.xlsx', '.xls', '.json']
  const ext = '.' + file.name.split('.').pop().toLowerCase()
  
  if (!validExtensions.includes(ext)) {
    errorMsg.value = '请上传 .xlsx, .xls 或 .json 格式的文件'
    return
  }
  
  selectedFile.value = file
  errorMsg.value = ''
}

const clearFile = () => {
  selectedFile.value = null
  parsedData.value = null
  errorMsg.value = ''
}

const parseSchedule = async () => {
  if (!selectedFile.value) return
  
  parsing.value = true
  errorMsg.value = ''
  
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  
  try {
    const response = await fetch('/api/schedule/parse', {
      method: 'POST',
      body: formData
    })
    
    const data = await response.json()
    
    if (data.code === 200) {
      parsedData.value = data.data
    } else {
      errorMsg.value = data.message || '解析失败'
    }
  } catch (error) {
    errorMsg.value = '网络错误，请重试'
  } finally {
    parsing.value = false
  }
}

const addCourse = () => {
  manualCourses.value.push({ name: '', day: '', time: '' })
}

const removeCourse = (index) => {
  manualCourses.value.splice(index, 1)
}

const submitManualCourses = async () => {
  const validCourses = manualCourses.value.filter(c => c.name.trim())
  if (validCourses.length === 0) {
    errorMsg.value = '请至少填写一门课程'
    return
  }
  
  parsing.value = true
  errorMsg.value = ''
  
  try {
    const response = await fetch('/api/schedule/manual', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ courses: validCourses })
    })
    
    const data = await response.json()
    
    if (data.code === 200) {
      parsedData.value = data.data
    } else {
      errorMsg.value = data.message || '生成失败'
    }
  } catch (error) {
    errorMsg.value = '网络错误，请重试'
  } finally {
    parsing.value = false
  }
}

const applyToSmartList = () => {
  emit('parsed', parsedData.value)
}

const reset = () => {
  selectedFile.value = null
  parsedData.value = null
  errorMsg.value = ''
  manualCourses.value = [{ name: '', day: '', time: '' }]
}

const downloadTemplate = () => {
  const templateData = [
    { 课程名: '高等数学', 星期: 1, 节次: '1-2', 学分: 4, 教师: '张教授' },
    { 课程名: '大学英语', 星期: 2, 节次: '3-4', 学分: 3, 教师: '李老师' },
    { 课程名: '计算机网络', 星期: 3, 节次: '5-6', 学分: 3, 教师: '王教授' },
    { 课程名: '线性代数', 星期: 4, 节次: '1-2', 学分: 3, 教师: '刘老师' }
  ]
  
  const dataStr = JSON.stringify(templateData, null, 2)
  const blob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = '课程表模板.json'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.schedule-uploader {
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

.upload-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.upload-tabs button {
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

.upload-tabs button.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.template-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-size: 13px;
  color: #6b7280;
}

.download-link {
  color: #3b82f6;
  text-decoration: none;
}

.download-link:hover {
  text-decoration: underline;
}

.drop-zone {
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #f9fafb;
}

.drop-zone:hover,
.drop-zone.is-dragover {
  border-color: #3b82f6;
  background: #eff6ff;
}

.drop-zone i {
  font-size: 48px;
  color: #9ca3af;
  margin-bottom: 12px;
}

.drop-zone p {
  font-size: 16px;
  color: #374151;
  margin-bottom: 4px;
}

.drop-zone .hint {
  font-size: 12px;
  color: #9ca3af;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  padding: 12px;
  background: #f0fdf4;
  border-radius: 8px;
  color: #047857;
}

.clear-btn {
  margin-left: auto;
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
}

.parse-btn {
  width: 100%;
  margin-top: 16px;
  padding: 14px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.parse-btn:hover:not(:disabled) {
  background: #2563eb;
}

.parse-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 手动填写样式 */
.manual-panel {
  padding: 16px 0;
}

.course-row {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  align-items: center;
}

.course-row input,
.course-row select {
  padding: 10px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
}

.course-name {
  flex: 2;
}

.course-day,
.course-time {
  flex: 1;
}

.remove-btn {
  padding: 10px;
  background: #fef2f2;
  color: #ef4444;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.add-btn {
  width: 100%;
  padding: 12px;
  background: #f3f4f6;
  color: #6b7280;
  border: 1px dashed #d1d5db;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 8px;
}

/* 结果预览 */
.result-preview {
  margin-top: 24px;
  padding: 20px;
  background: #f0fdf4;
  border-radius: 12px;
  border: 1px solid #10b981;
}

.result-preview h4 {
  color: #047857;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.course-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.tag {
  padding: 6px 12px;
  background: #10b981;
  color: white;
  border-radius: 20px;
  font-size: 13px;
}

.action-btns {
  display: flex;
  gap: 12px;
}

.apply-btn {
  flex: 1;
  padding: 12px;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.reset-btn {
  padding: 12px 24px;
  background: white;
  color: #6b7280;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
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
  font-size: 14px;
}
</style>