<template>
  <form class="sell-form-wrapper" @submit.prevent="handleSubmit">
    <section class="form-section isbn-section">
      <h3 class="section-title"><i class="fas fa-barcode"></i>ISBN条码识别</h3>
      <ISBNBarcodeUploader @bookRecognized="onBookRecognized" />
    </section>

    <section class="form-section">
      <h3 class="section-title"><i class="fas fa-book"></i>基本信息</h3>
      <div class="form-row">
        <label class="form-group">
          <span class="form-label">书名 <span class="required">*</span></span>
          <input v-model="formData.title" class="form-input isbn-highlight" type="text" placeholder="请输入书名" required />
        </label>
        <label class="form-group">
          <span class="form-label">作者</span>
          <input v-model="formData.author" class="form-input isbn-highlight" type="text" placeholder="请输入作者" />
        </label>
      </div>
      <div class="form-row">
        <label class="form-group">
          <span class="form-label">出版社</span>
          <input v-model="formData.publisher" class="form-input isbn-highlight" type="text" placeholder="请输入出版社" />
        </label>
        <label class="form-group">
          <span class="form-label">版次</span>
          <input v-model="formData.edition" class="form-input isbn-highlight" type="text" placeholder="如：第七版" />
        </label>
      </div>
      <div class="form-row">
        <label class="form-group">
          <span class="form-label">ISBN</span>
          <input v-model="formData.isbn" class="form-input isbn-highlight" type="text" placeholder="978..." maxlength="13" />
        </label>
      </div>
    </section>

    <section class="form-section">
      <h3 class="section-title"><i class="fas fa-star"></i>品相信息</h3>
      <div class="radio-group">
        <label v-for="option in conditionOptions" :key="option.value" class="radio-option">
          <input v-model="formData.condition" type="radio" name="condition" :value="option.value" />
          <span>{{ option.label }}</span>
        </label>
      </div>
      <div class="checkbox-group mt-12">
        <label class="checkbox-option">
          <input v-model="formData.hasNotes" type="checkbox" />
          <span>有笔记 / 重点标记</span>
        </label>
      </div>
    </section>

    <section class="form-section">
      <h3 class="section-title"><i class="fas fa-handshake"></i>交易信息</h3>
      <div class="form-row">
        <label class="form-group">
          <span class="form-label">售价 <span class="required">*</span></span>
          <input v-model.number="formData.price" class="form-input isbn-highlight" type="number" step="0.1" min="0" placeholder="0.00" required />
        </label>
        <label class="form-group">
          <span class="form-label">原价</span>
          <input v-model.number="formData.originalPrice" class="form-input isbn-highlight" type="number" step="0.1" min="0" placeholder="0.00" />
        </label>
      </div>
      <div class="form-group mt-12">
        <span class="form-label">交易方式</span>
        <div class="radio-group">
          <label v-for="method in tradeMethodOptions" :key="method.value" class="radio-option">
            <input v-model="formData.tradeMethod" type="radio" name="tradeMethod" :value="method.value" />
            <span>{{ method.label }}</span>
          </label>
        </div>
      </div>
      <div class="form-group mt-12">
        <span class="form-label">校区</span>
        <div class="radio-group campus-group">
          <label v-for="campus in campusOptions" :key="campus.value" class="radio-option campus-option">
            <input v-model="formData.campus" type="radio" name="campus" :value="campus.value" />
            <span>{{ campus.label }}</span>
          </label>
        </div>
      </div>
      <div class="form-group mt-12">
        <span class="form-label">联系方式</span>
        <input v-model="formData.contact" class="form-input" type="text" placeholder="微信 / QQ / 电话" />
      </div>
    </section>

    <section class="form-section">
      <h3 class="section-title"><i class="fas fa-images"></i>书籍图片 <span class="required">*</span></h3>
      <FileUploader
        accept="image/*"
        placeholder="上传书籍图片"
        :auto-upload="true"
        :use-local-fallback="true"
        @success="onImageUpload"
      />
      <div v-if="formData.images.length > 0" class="image-preview-list">
        <div v-for="(img, index) in formData.images" :key="`${img}-${index}`" class="preview-item">
          <img :src="img" alt="预览" />
          <button type="button" class="remove-img-btn" @click="removeImage(index)">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
    </section>

    <section class="form-section">
      <h3 class="section-title"><i class="fas fa-tags"></i>标签与描述</h3>
      <div class="form-group">
        <span class="form-label">标签（用逗号分隔）</span>
        <input v-model="formData.tags" class="form-input" type="text" placeholder="数学,教材,期末复习..." />
      </div>
      <div class="form-group mt-12">
        <span class="form-label">详细描述</span>
        <textarea v-model="formData.description" class="form-textarea" placeholder="描述书籍的具体情况..."></textarea>
      </div>
    </section>

    <div class="form-actions">
      <button class="btn btn-outline" type="button" :disabled="draftSaving" @click="emit('save-draft', snapshotFormData())">
        {{ draftSaving ? '保存中...' : '保存草稿' }}
      </button>
      <button class="btn btn-primary" type="submit" :disabled="submitting">
        {{ submitting ? '提交中...' : '立即发布' }}
      </button>
    </div>
  </form>
</template>

<script setup>
import { reactive, ref } from 'vue'
import ISBNBarcodeUploader from '../common/ISBNBarcodeUploader.vue'
import FileUploader from '../common/FileUploader.vue'
import { createBook } from '@/services/api.js'

defineProps({
  sell: { type: Object, default: () => ({}) },
  shared: { type: Object, default: () => ({}) },
  draftSaving: { type: Boolean, default: false },
})

const emit = defineEmits(['submit', 'save-draft'])

const submitting = ref(false)

const createEmptyFormData = () => ({
  title: '',
  author: '',
  publisher: '',
  edition: '',
  isbn: '',
  condition: 'like-new',
  hasNotes: false,
  price: null,
  originalPrice: null,
  tradeMethod: 'face',
  campus: 'zijingang',
  contact: '',
  images: [],
  tags: '',
  description: '',
})

const formData = reactive(createEmptyFormData())

const conditionOptions = [
  { value: 'new', label: '全新' },
  { value: 'like-new', label: '九成新' },
  { value: 'good', label: '八成新' },
  { value: 'fair', label: '七成新' },
]

const tradeMethodOptions = [
  { value: 'face', label: '当面交易' },
  { value: 'mail', label: '邮寄' },
  { value: 'both', label: '皆可' },
]

const campusOptions = [
  { value: 'zijingang', label: '紫金港' },
  { value: 'yuquan', label: '玉泉' },
  { value: 'xixi', label: '西溪' },
  { value: 'zhijiang', label: '之江' },
  { value: 'huajiachi', label: '华家池' },
]

const applyFormData = (nextData = {}) => {
  const base = createEmptyFormData()

  formData.title = nextData.title ?? base.title
  formData.author = nextData.author ?? base.author
  formData.publisher = nextData.publisher ?? base.publisher
  formData.edition = nextData.edition ?? base.edition
  formData.isbn = nextData.isbn ?? base.isbn
  formData.condition = nextData.condition ?? base.condition
  formData.hasNotes = Boolean(nextData.hasNotes ?? base.hasNotes)
  formData.price = nextData.price ?? base.price
  formData.originalPrice = nextData.originalPrice ?? base.originalPrice
  formData.tradeMethod = nextData.tradeMethod ?? base.tradeMethod
  formData.campus = nextData.campus ?? base.campus
  formData.contact = nextData.contact ?? base.contact
  formData.images = Array.isArray(nextData.images) ? [...nextData.images] : []
  formData.tags = nextData.tags ?? base.tags
  formData.description = nextData.description ?? base.description
}

const snapshotFormData = () => ({
  title: formData.title,
  author: formData.author,
  publisher: formData.publisher,
  edition: formData.edition,
  isbn: formData.isbn,
  condition: formData.condition,
  hasNotes: formData.hasNotes,
  price: formData.price,
  originalPrice: formData.originalPrice,
  tradeMethod: formData.tradeMethod,
  campus: formData.campus,
  contact: formData.contact,
  images: [...formData.images],
  tags: formData.tags,
  description: formData.description,
})

const resetForm = () => {
  applyFormData()
}

const loadDraft = (draft) => {
  applyFormData(draft)
}

defineExpose({
  loadDraft,
  resetForm,
})

const highlightInputs = () => {
  const inputs = document.querySelectorAll('.isbn-highlight')
  inputs.forEach((input) => {
    input.classList.add('flash-highlight')
    window.setTimeout(() => {
      input.classList.remove('flash-highlight')
    }, 1500)
  })
}

const onBookRecognized = (bookData) => {
  const book = bookData.book || bookData

  formData.title = book.title || ''
  formData.author = book.author || ''
  formData.publisher = book.publisher || ''
  formData.edition = book.edition || ''
  formData.isbn = book.isbn || ''
  formData.originalPrice = book.original_price || book.originalPrice || null
  formData.tags = book.tags || ''
  formData.description = book.description || ''

  highlightInputs()
}

const onImageUpload = (result) => {
  if (result.url && !formData.images.includes(result.url)) {
    formData.images.push(result.url)
  }
}

const removeImage = (index) => {
  formData.images.splice(index, 1)
}

const validateForm = () => {
  if (!formData.title.trim()) {
    window.alert('请输入书名')
    return false
  }
  if (!formData.price || formData.price <= 0) {
    window.alert('请输入有效的价格')
    return false
  }
  if (formData.images.length === 0) {
    window.alert('请至少上传一张图片')
    return false
  }
  return true
}

const handleSubmit = async () => {
  if (!validateForm()) return

  submitting.value = true

  try {
    const submitData = {
      title: formData.title.trim(),
      author: formData.author.trim(),
      publisher: formData.publisher.trim(),
      edition: formData.edition.trim(),
      isbn: formData.isbn.trim(),
      condition: formData.condition,
      hasNotes: formData.hasNotes,
      price: parseFloat(formData.price),
      originalPrice: formData.originalPrice ? parseFloat(formData.originalPrice) : null,
      tradeMethod: formData.tradeMethod,
      campus: formData.campus,
      contact: formData.contact.trim(),
      images: [...formData.images],
      tags: formData.tags,
      description: formData.description.trim(),
    }

    const response = await createBook(submitData)

    if (response.code === 200) {
      window.alert('书籍发布成功！')
      emit('submit', response.data)
      resetForm()
    } else {
      window.alert(response.message || '发布失败')
    }
  } catch (error) {
    console.error('发布失败:', error)
    window.alert(error?.message || '网络错误，请重试')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.sell-form-wrapper {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.form-section {
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.isbn-section {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  color: #1f2937;
  font-size: 16px;
  font-weight: 600;
}

.section-title i {
  color: #3b82f6;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  color: #374151;
  font-size: 14px;
  font-weight: 500;
}

.required {
  color: #ef4444;
}

.form-input,
.form-textarea {
  padding: 10px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
}

@keyframes flash-highlight {
  0%,
  100% {
    border-color: #e5e7eb;
    box-shadow: none;
  }

  25% {
    border-color: #10b981;
    box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.2);
    background: #f0fdf4;
  }

  50% {
    border-color: #10b981;
    box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.3);
    background: #ecfdf5;
  }

  75% {
    border-color: #10b981;
    box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.2);
    background: #f0fdf4;
  }
}

.flash-highlight {
  animation: flash-highlight 1.5s ease-in-out;
}

.form-textarea {
  min-height: 100px;
  resize: vertical;
}

.radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  background: #f9fafb;
  cursor: pointer;
  transition: all 0.2s;
}

.radio-option:hover {
  border-color: #3b82f6;
}

.radio-option input:checked + span {
  color: #3b82f6;
  font-weight: 500;
}

.campus-group .radio-option {
  padding: 8px 12px;
  font-size: 13px;
}

.checkbox-option {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.mt-12 {
  margin-top: 12px;
}

.image-preview-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 12px;
}

.preview-item {
  position: relative;
  width: 100px;
  height: 100px;
  overflow: hidden;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
}

.preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-img-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 50%;
  background: #ef4444;
  color: white;
  cursor: pointer;
}

.form-actions {
  display: flex;
  gap: 12px;
  padding: 20px;
  background: #f9fafb;
}

.btn {
  flex: 1;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-primary:disabled,
.btn-outline:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-outline {
  border: 1px solid #e5e7eb;
  background: white;
  color: #374151;
}

.btn-outline:hover:not(:disabled) {
  background: #f3f4f6;
}

@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
