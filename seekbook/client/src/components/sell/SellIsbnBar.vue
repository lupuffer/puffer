<template>
  <section class="isbn-quick-section">
    <div class="isbn-quick-header">
      <i class="fas fa-barcode"></i>
      <span>{{ bar.title }}</span>
      <span class="hint">{{ bar.hint }}</span>
    </div>
    <div class="isbn-input-group">
      <input v-model="isbn" class="isbn-input" type="text" :placeholder="bar.placeholder" maxlength="13" />
      <button class="isbn-btn isbn-btn-scan" type="button" @click="$emit('scan', isbn)">
        <i class="fas fa-camera"></i>
        {{ bar.scan }}
      </button>
      <button class="isbn-btn isbn-btn-recognize" type="button" @click="$emit('recognize', isbn)">
        {{ bar.recognize }}
      </button>
    </div>
    <button class="history-upload-btn" type="button" @click="$emit('history')">
      <i class="fas fa-history"></i>
      {{ bar.history }}
    </button>
  </section>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  bar: { type: Object, required: true },
})

defineEmits(['scan', 'recognize', 'history'])

const isbn = ref('')
</script>

<style scoped>
.isbn-quick-section {
  background: white;
  border-radius: 10px;
  padding: 12px 16px;
  margin-bottom: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--gray-200);
}

.isbn-quick-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--gray-800);
}

.isbn-quick-header i {
  color: var(--primary-blue);
  font-size: 14px;
}

.isbn-quick-header .hint {
  font-size: 11px;
  font-weight: 400;
  color: var(--gray-400);
  margin-left: 6px;
}

.isbn-input-group {
  display: flex;
  width: 100%;
  gap: 8px;
  align-items: center;
}

.isbn-input {
  width: 300px;
  height: 42px;
  padding: 10px 12px;
  border: 2px solid var(--primary-blue);
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.isbn-input:focus {
  outline: none;
  border-color: var(--primary-blue);
  box-shadow: 0 0 0 2px rgba(26, 86, 219, 0.08);
}

.isbn-btn {
  height: 42px;
  padding: 0 16px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  border: none;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.isbn-btn-scan {
  margin-left: auto;
  background: white;
  color: var(--gray-700);
  border: 1.5px solid var(--gray-300);
}

.isbn-btn-recognize {
  background: var(--primary-blue);
  color: white;
}

.history-upload-btn {
  margin-top: 8px;
  padding: 6px 0;
  font-size: 12px;
  color: var(--gray-400);
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s ease;
}
</style>
