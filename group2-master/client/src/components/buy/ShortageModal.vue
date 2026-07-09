<template>
  <div class="shortage-modal" :class="{ show: open }" @click.self="$emit('close')">
    <div class="shortage-modal-content">
      <div class="shortage-modal-header">
        <h3><i class="fas fa-bell"></i> {{ shortage.modalTitle }}</h3>
        <button class="shortage-modal-close" type="button" @click="$emit('close')">&times;</button>
      </div>
      <form class="shortage-modal-body" @submit.prevent="handleSubmit">
        <div class="shortage-form-group">
          <label>{{ shortage.form.bookName.label }} <span class="required">*</span></label>
          <input v-model.trim="form.bookName" type="text" :placeholder="shortage.form.bookName.placeholder" maxlength="200" />
          <div class="error-msg" :class="{ visible: errors.bookName }">{{ errors.bookName || shortage.form.bookName.error }}</div>
        </div>
        <div class="shortage-form-group">
          <label>{{ shortage.form.isbn.label }}</label>
          <input v-model.trim="form.isbn" type="text" :placeholder="shortage.form.isbn.placeholder" maxlength="20" />
          <div class="error-msg" :class="{ visible: errors.isbn }">{{ errors.isbn || shortage.form.isbn.error }}</div>
        </div>
        <div class="shortage-form-group">
          <label>{{ shortage.form.campus.label }}</label>
          <select v-model="form.campus">
            <option value="">{{ shortage.form.campus.defaultText }}</option>
            <option v-for="option in campusOptions" :key="option" :value="option">{{ option }}</option>
          </select>
        </div>
        <div class="shortage-form-group">
          <label>{{ shortage.form.price.label }}</label>
          <div class="price-input-wrapper">
            <input v-model="form.expectedPrice" type="number" :placeholder="shortage.form.price.placeholder" min="0" step="0.01" />
            <span class="price-unit">{{ shortage.form.price.unit }}</span>
          </div>
          <div class="error-msg" :class="{ visible: errors.expectedPrice }">{{ errors.expectedPrice }}</div>
        </div>
        <div class="shortage-form-group">
          <label>{{ shortage.form.note.label }}</label>
          <textarea v-model.trim="form.note" :placeholder="shortage.form.note.placeholder" rows="2" maxlength="500"></textarea>
        </div>
        <div class="shortage-form-actions">
          <button class="btn btn-outline" type="button" :disabled="submitting" @click="$emit('close')">{{ shortage.form.cancel }}</button>
          <button class="btn btn-primary" type="submit" :disabled="submitting">{{ submitting ? '提交中...' : shortage.form.submit }}</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, watch } from 'vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  shortage: { type: Object, required: true },
  campusOptions: { type: Array, default: () => [] },
  submitting: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'submit'])

const form = reactive({
  bookName: '',
  isbn: '',
  campus: '',
  expectedPrice: '',
  note: '',
})

const errors = reactive({
  bookName: '',
  isbn: '',
  expectedPrice: '',
})

const campusOptions = computed(() =>
  props.campusOptions
    .map((option) => option?.fullName || option?.label || '')
    .filter(Boolean),
)

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      resetErrors()
      return
    }
    resetForm()
    resetErrors()
  },
)

function resetForm() {
  form.bookName = ''
  form.isbn = ''
  form.campus = ''
  form.expectedPrice = ''
  form.note = ''
}

function resetErrors() {
  errors.bookName = ''
  errors.isbn = ''
  errors.expectedPrice = ''
}

function handleSubmit() {
  resetErrors()

  const normalizedIsbn = String(form.isbn || '').replace(/[-\s]/g, '')
  const normalizedPrice = String(form.expectedPrice || '').trim()

  if (!form.bookName) {
    errors.bookName = props.shortage.form.bookName.error || '请输入书名'
  }
  if (normalizedIsbn && (!/^\d{10}$/.test(normalizedIsbn) && !/^\d{13}$/.test(normalizedIsbn))) {
    errors.isbn = props.shortage.form.isbn.error || '请输入有效的 ISBN'
  }
  if (normalizedPrice) {
    const numericPrice = Number(normalizedPrice)
    if (!Number.isFinite(numericPrice) || numericPrice <= 0) {
      errors.expectedPrice = '请输入大于 0 的价格'
    }
  }

  if (errors.bookName || errors.isbn || errors.expectedPrice) {
    return
  }

  emit('submit', {
    bookName: form.bookName,
    isbn: normalizedIsbn,
    campus: form.campus,
    expectedPrice: normalizedPrice ? Number(normalizedPrice) : null,
    note: form.note,
  })
}
</script>

<style scoped>
.shortage-modal {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  align-items: center;
  justify-content: center;
}

.shortage-modal.show {
  display: flex;
}

.shortage-modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 480px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-xl);
}

.shortage-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--gray-200);
}

.shortage-modal-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--gray-900);
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
}

.shortage-modal-header h3 i {
  color: var(--accent-orange);
}

.shortage-modal-close {
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  color: var(--gray-500);
  font-size: 24px;
  cursor: pointer;
  border-radius: 8px;
}

.shortage-modal-body {
  padding: 24px;
}

.shortage-form-group {
  margin-bottom: 20px;
}

.shortage-form-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--gray-700);
  margin-bottom: 8px;
}

.required,
.error-msg {
  color: #ef4444;
}

.shortage-form-group input,
.shortage-form-group select,
.shortage-form-group textarea {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid var(--gray-200);
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.price-input-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.price-input-wrapper input {
  flex: 1;
}

.price-unit {
  font-size: 14px;
  color: var(--gray-600);
}

.error-msg {
  font-size: 13px;
  margin-top: 6px;
  display: none;
}

.error-msg.visible {
  display: block;
}

.shortage-form-actions {
  display: flex;
  gap: 16px;
  margin-top: 24px;
}

.shortage-form-actions .btn {
  flex: 1;
  padding: 14px;
  font-size: 15px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  border: none;
}

.btn-primary {
  background: var(--primary-blue);
  color: white;
}

.btn-outline {
  background: white;
  color: var(--gray-700);
  border: 1px solid var(--gray-300) !important;
}

.shortage-form-actions .btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>
