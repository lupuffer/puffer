<template>
  <form class="auth-form" @submit.prevent="submitForm">
    <div v-for="field in fields" :key="field.key" class="form-group" :class="{ 'checkbox-group': isCheckboxField(field) }">
      <template v-if="isCheckboxField(field)">
        <label class="checkbox-label">
          <input v-model="form[field.key]" class="checkbox-input" type="checkbox" />
          <span>{{ field.checkboxText || field.label }}</span>
        </label>
      </template>
      <template v-else>
        <label class="form-label">{{ field.label }}</label>
        <input
          v-model="form[field.key]"
          class="form-input"
          :type="fieldType(field)"
          :placeholder="field.placeholder"
          :autocomplete="fieldAutocomplete(field)"
        />
      </template>
    </div>
    <div v-if="message" class="form-message" :class="{ success }">{{ message }}</div>
    <button class="btn btn-primary btn-full" type="submit">
      <i :class="icon"></i> {{ buttonText }}
    </button>
    <div class="text-center">
      {{ prompt }}<button class="link" type="button" @click="$emit('switch')">{{ linkText }}</button>
    </div>
  </form>
</template>

<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
  fields: { type: Array, required: true },
  buttonText: { type: String, required: true },
  prompt: { type: String, default: '' },
  linkText: { type: String, default: '' },
  message: { type: String, default: '' },
  success: { type: Boolean, default: false },
  icon: { type: String, default: 'fas fa-sign-in-alt' },
})

const emit = defineEmits(['submit', 'switch'])
const form = reactive({})

const isCheckboxField = (field) => field?.type === 'checkbox'

const fieldType = (field) => {
  if (field?.type) return field.type
  const normalizedKey = (field?.key || '').toLowerCase()
  if (normalizedKey.includes('password')) return 'password'
  if (normalizedKey.includes('email')) return 'email'
  return 'text'
}

const fieldAutocomplete = (field) => {
  const normalizedKey = (field?.key || '').toLowerCase()
  if (normalizedKey === 'email') return 'email'
  if (normalizedKey === 'username') return 'username'
  if (normalizedKey === 'password') return 'current-password'
  if (normalizedKey === 'passwordconfirm') return 'new-password'
  return 'on'
}

const submitForm = () => emit('submit', { ...form })

watch(
  () => props.fields,
  (fields) =>
    fields.forEach((field) => {
      if (Object.prototype.hasOwnProperty.call(form, field.key)) return
      form[field.key] = isCheckboxField(field) ? false : ''
    }),
  { immediate: true },
)
</script>

<style scoped>
.form-group {
  margin-bottom: 20px;
}

.checkbox-group {
  margin-top: -4px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--gray-700);
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid var(--gray-200);
  border-radius: 8px;
  font-size: 14px;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-blue);
}

.checkbox-label {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: var(--gray-700);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.checkbox-input {
  width: 16px;
  height: 16px;
  accent-color: var(--primary-blue);
}

.form-message {
  color: #ef4444;
  font-size: 12px;
  margin-bottom: 12px;
}

.form-message.success {
  color: var(--secondary-green);
}

.btn-full {
  width: 100%;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.btn-primary {
  background-color: var(--primary-blue);
  color: white;
}

.btn-primary:hover {
  background-color: var(--primary-blue-dark);
}

.text-center {
  text-align: center;
  margin-top: 16px;
  font-size: 14px;
  color: var(--gray-600);
}

.link {
  border: none;
  background: transparent;
  color: var(--primary-blue);
  cursor: pointer;
  margin-left: 4px;
}
</style>
