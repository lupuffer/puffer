<template>
  <Teleport to="body">
    <div v-if="open" class="dialog-overlay" @click.self="$emit('close')">
      <div class="dialog-card discussion-dialog">
        <div class="dialog-header">
          <div>
            <p class="dialog-kicker">知识星河</p>
            <h3>发讨论</h3>
          </div>
          <button type="button" class="icon-btn" @click="$emit('close')">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <form class="dialog-body" @submit.prevent="submitForm">
          <label class="field">
            <span>类型</span>
            <select v-model="form.type">
              <option value="">请选择类型</option>
              <option v-for="type in ['讨论', '求助', '求资料']" :key="type" :value="type">{{ type }}</option>
            </select>
          </label>

          <label class="field">
            <span>标题</span>
            <input v-model.trim="form.title" type="text" maxlength="50" placeholder="请输入讨论标题" />
          </label>

          <label class="field">
            <span>正文</span>
            <textarea
              v-model.trim="form.content"
              rows="7"
              maxlength="1000"
              placeholder="写下你的问题、经验或资料需求"
            ></textarea>
          </label>

          <label class="field">
            <span>标签</span>
            <input v-model.trim="form.tags" type="text" placeholder="用逗号分隔，最多 5 个标签" />
          </label>
        </form>

        <div class="dialog-footer">
          <button type="button" class="ghost-btn" @click="$emit('close')">取消</button>
          <button type="button" class="primary-btn" :disabled="submitting" @click="submitForm">
            {{ submitting ? '发布中...' : '发布讨论' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { reactive } from 'vue'

defineProps({
  open: { type: Boolean, default: false },
  submitting: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'submit'])

const createInitialForm = () => ({
  type: '',
  title: '',
  content: '',
  tags: '',
})

const form = reactive(createInitialForm())

const submitForm = () => {
  emit('submit', { ...form })
}

const resetForm = () => {
  Object.assign(form, createInitialForm())
}

defineExpose({ resetForm })
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  inset: 0;
  display: grid;
  place-items: center;
  padding: 24px;
  background: rgba(18, 28, 53, 0.26);
  backdrop-filter: blur(5px);
  z-index: 2400;
}

.dialog-card {
  width: min(100%, 620px);
  max-height: 80vh;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  border-radius: 24px;
  border: 1px solid rgba(226, 234, 255, 0.94);
  background: #fff;
  box-shadow: 0 28px 72px rgba(67, 83, 136, 0.24);
  overflow: hidden;
}

.dialog-header,
.dialog-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 18px 22px;
  background: #fff;
}

.dialog-header {
  border-bottom: 1px solid #edf1ff;
}

.dialog-footer {
  justify-content: flex-end;
  border-top: 1px solid #edf1ff;
}

.dialog-kicker {
  margin-bottom: 4px;
  color: #7181a0;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.dialog-header h3 {
  color: #16213a;
  font-size: 24px;
}

.dialog-body {
  overflow-y: auto;
  padding: 20px 22px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field > span {
  color: #23314e;
  font-weight: 700;
}

.field input,
.field select,
.field textarea {
  width: 100%;
  min-height: 46px;
  padding: 12px 14px;
  border: 1px solid #dbe3ff;
  border-radius: 14px;
  background: #f8faff;
  color: #2c3a57;
}

.field textarea {
  min-height: 188px;
  resize: vertical;
}

.icon-btn,
.ghost-btn,
.primary-btn {
  border: none;
  cursor: pointer;
}

.icon-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #f4f7ff;
  color: #60718a;
}

.ghost-btn,
.primary-btn {
  min-height: 42px;
  padding: 0 18px;
  border-radius: 12px;
  font-weight: 700;
}

.ghost-btn {
  background: #f4f7ff;
  color: #41526b;
}

.primary-btn {
  color: #fff;
  background: linear-gradient(135deg, #2f80ed 0%, #6f84ff 64%, #a78bfa 100%);
}

.primary-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 640px) {
  .dialog-overlay {
    padding: 14px;
  }
}
</style>
