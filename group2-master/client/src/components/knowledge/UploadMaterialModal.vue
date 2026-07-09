<template>
  <div class="modal" :class="{ show: open }" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h3><i class="fas fa-cloud-upload-alt"></i> {{ modal.title }}</h3>
        <button class="modal-close" type="button" @click="$emit('close')">&times;</button>
      </div>
      <form class="modal-body upload-form" @submit.prevent="$emit('submit')">
        <div v-for="field in modal.fields" :key="field.label" class="form-group">
          <label>{{ field.label }}</label>
          <input v-if="field.type === 'text'" type="text" :placeholder="field.placeholder" />
          <select v-else-if="field.type === 'select'"><option>{{ field.placeholder }}</option><option v-for="option in field.options" :key="option">{{ option }}</option></select>
          <textarea v-else-if="field.type === 'textarea'" :placeholder="field.placeholder" rows="3"></textarea>
          <div v-else class="file-upload-area"><i class="fas fa-cloud-upload-alt"></i><p>{{ field.uploadTitle }}</p><small>{{ field.uploadHint }}</small></div>
        </div>
        <div class="price-options">
          <label v-for="option in modal.priceOptions" :key="option.value" class="price-option">
            <input type="radio" name="priceType" :value="option.value" />
            <div class="option-content"><i class="fas fa-gift"></i><span>{{ option.label }}</span><small>{{ option.description }}</small></div>
          </label>
        </div>
        <div class="tag-suggestions"><span v-for="tag in modal.tagSuggestions" :key="tag" class="tag-suggestion">{{ tag }}</span></div>
        <div class="form-actions"><button class="btn btn-outline" type="button" @click="$emit('close')">{{ modal.actions[0] }}</button><button class="btn btn-primary" type="submit">{{ modal.actions[1] }}</button></div>
      </form>
    </div>
  </div>
</template>

<script setup>
defineProps({
  open: { type: Boolean, default: false },
  modal: { type: Object, required: true },
})

defineEmits(['close', 'submit'])
</script>

<style scoped>
.modal {
  display: none !important;
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}

.modal.show {
  display: flex !important;
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--gray-200);
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--gray-900);
  display: flex;
  align-items: center;
  gap: 10px;
}

.modal-close {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: var(--gray-100);
  color: var(--gray-600);
  font-size: 20px;
  cursor: pointer;
}

.modal-body {
  padding: 24px;
}

.upload-form .form-group {
  margin-bottom: 20px;
}

.upload-form label {
  display: block;
  font-size: 15px;
  font-weight: 500;
  color: var(--gray-700);
  margin-bottom: 8px;
}

.upload-form input[type='text'],
.upload-form select,
.upload-form textarea {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid var(--gray-200);
  border-radius: 8px;
  font-size: 15px;
  transition: all 0.2s ease;
}

.file-upload-area {
  border: 2px dashed var(--gray-300);
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  background: var(--gray-50);
}

.file-upload-area i {
  font-size: 48px;
  color: var(--gray-400);
  margin-bottom: 12px;
}

.price-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.price-option input[type='radio'] {
  position: absolute;
  opacity: 0;
}

.option-content {
  padding: 16px;
  border: 2px solid var(--gray-200);
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.option-content i {
  font-size: 24px;
  color: var(--primary-blue);
  margin-bottom: 8px;
}

.option-content span {
  display: block;
  font-weight: 600;
  color: var(--gray-900);
  margin-bottom: 4px;
}

.tag-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.tag-suggestion {
  padding: 6px 12px;
  background: var(--gray-100);
  color: var(--gray-600);
  border-radius: 20px;
  font-size: 13px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.btn {
  padding: 10px 24px;
  border-radius: 6px;
  border: none;
}

.btn-primary {
  background: var(--primary-blue);
  color: white;
}

.btn-outline {
  background: white;
  color: var(--gray-700);
  border: 1px solid var(--gray-300);
}
</style>
