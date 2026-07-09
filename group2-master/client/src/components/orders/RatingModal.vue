<template>
  <Teleport to="body">
    <div v-if="visible" class="rating-overlay" @click.self="close">
      <div class="rating-dialog" @click.stop>
        <div class="rating-header">
          <h3>评价订单</h3>
          <button class="close-btn" type="button" @click="close">&times;</button>
        </div>

        <div class="rating-body">
          <p class="rating-prompt">你对这次交易的满意度是？</p>

          <div class="star-row">
            <button
              v-for="s in 5"
              :key="s"
              class="star-btn"
              type="button"
              @click="rating = s"
              @mouseenter="hover = s"
              @mouseleave="hover = 0"
            >
              <i :class="(hover || rating) >= s ? 'fas fa-star star-on' : 'far fa-star star-off'"></i>
            </button>
          </div>

          <p v-if="rating" class="rating-label">{{ labelFor(rating) }}</p>

          <textarea
            v-model="comment"
            class="rating-textarea"
            maxlength="500"
            placeholder="写下你的评价（可选）..."
            rows="4"
          ></textarea>
          <span class="char-count">{{ comment.length }}/500</span>
        </div>

        <div class="rating-footer">
          <button class="btn-cancel" type="button" @click="close">取消</button>
          <button
            class="btn-submit"
            type="button"
            :disabled="!rating || submitting"
            @click="submit"
          >
            {{ submitting ? '提交中...' : '提交评价' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  orderId: { type: String, default: '' },
})

const emit = defineEmits(['close', 'submit'])

const rating = ref(0)
const hover = ref(0)
const comment = ref('')
const submitting = ref(false)

const labels = { 5: '非常满意', 4: '满意', 3: '一般', 2: '不满意', 1: '非常不满意' }
const labelFor = (v) => labels[v] || ''

const close = () => {
  if (!submitting.value) {
    rating.value = 0
    hover.value = 0
    comment.value = ''
    emit('close')
  }
}

const submit = async () => {
  if (!rating.value || submitting.value) return
  submitting.value = true
  emit('submit', { orderId: props.orderId, rating: rating.value, comment: comment.value })
}
</script>

<style scoped>
.rating-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(4px);
}

.rating-dialog {
  background: white;
  border-radius: 20px;
  width: 460px;
  max-width: 94vw;
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.18);
  overflow: hidden;
}

.rating-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 28px 16px;
}

.rating-header h3 {
  font-size: 20px;
  color: #0f172a;
}

.close-btn {
  background: none;
  border: none;
  font-size: 28px;
  color: #94a3b8;
  cursor: pointer;
}

.rating-body {
  padding: 0 28px 20px;
}

.rating-prompt {
  font-size: 15px;
  color: #64748b;
  margin-bottom: 16px;
}

.star-row {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-bottom: 10px;
}

.star-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 34px;
  transition: transform 0.15s;
}

.star-btn:hover {
  transform: scale(1.18);
}

.star-on { color: #f59e0b; }
.star-off { color: #d1d5db; }

.rating-label {
  text-align: center;
  font-size: 15px;
  font-weight: 600;
  color: #f59e0b;
  margin-bottom: 16px;
}

.rating-textarea {
  width: 100%;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 14px;
  font-size: 14px;
  color: #334155;
  resize: vertical;
  background: #f8fafc;
}

.rating-textarea:focus {
  outline: none;
  border-color: #3b82f6;
}

.char-count {
  display: block;
  text-align: right;
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
}

.rating-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 16px 28px 24px;
}

.btn-cancel,
.btn-submit {
  padding: 10px 24px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #e2e8f0;
}

.btn-submit {
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  color: white;
  border: none;
}

.btn-submit:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>