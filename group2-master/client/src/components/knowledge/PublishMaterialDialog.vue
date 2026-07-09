<template>
  <Teleport to="body">
    <div v-if="open" class="dialog-overlay" @click.self="$emit('close')">
      <div class="dialog-card material-dialog">
        <div class="dialog-header">
          <div>
            <p class="dialog-kicker">知识星河</p>
            <h3>上传资料</h3>
          </div>
          <button type="button" class="icon-btn" @click="$emit('close')">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <form class="dialog-body" @submit.prevent="submitForm">
          <label class="field">
            <span>资料标题</span>
            <input v-model.trim="form.title" type="text" maxlength="50" placeholder="请输入资料标题" />
          </label>

          <div class="field-grid">
            <label class="field">
              <span>资料分类</span>
              <select v-model="form.category">
                <option value="">请选择分类</option>
                <option v-for="category in categories" :key="category" :value="category">{{ category }}</option>
              </select>
            </label>
            <label class="field">
              <span>关联课程</span>
              <input v-model.trim="form.course" type="text" placeholder="请输入课程名称或课程代码" />
            </label>
          </div>

          <label class="field">
            <span>资料描述</span>
            <textarea
              v-model.trim="form.description"
              rows="5"
              maxlength="500"
              placeholder="请简要描述资料内容、适用对象和特点"
            ></textarea>
          </label>

          <label class="field">
            <span>上传文件</span>
            <input :key="fileInputKey" type="file" @change="handleFileChange" />
            <small>支持 PDF、Word、Excel、PPT、图片、ZIP，最大 50MB</small>
            <div v-if="fileSummary" class="file-summary">{{ fileSummary }}</div>
          </label>

          <div class="field">
            <span>下载方式</span>
            <div class="choice-row">
              <label class="choice-card" :class="{ active: form.pricePoints === 0 }">
                <input v-model.number="form.pricePoints" type="radio" :value="0" />
                <strong>免费下载</strong>
                <small>任何人都可直接下载</small>
              </label>
              <label class="choice-card" :class="{ active: form.pricePoints > 0 }">
                <input v-model.number="form.pricePoints" type="radio" :value="10" />
                <strong>积分下载</strong>
                <small>通过积分兑换后永久可下</small>
              </label>
            </div>
          </div>

          <div v-if="form.pricePoints > 0" class="field">
            <span>积分档位</span>
            <div class="pill-row">
              <button
                v-for="price in [5, 10, 15]"
                :key="price"
                type="button"
                class="pill-btn"
                :class="{ active: form.pricePoints === price }"
                @click="form.pricePoints = price"
              >
                {{ price }}积分
              </button>
            </div>
          </div>

          <label class="field">
            <span>标签</span>
            <input v-model.trim="form.tags" type="text" placeholder="用逗号分隔，最多 5 个标签" />
          </label>
        </form>

        <div class="dialog-footer">
          <button type="button" class="ghost-btn" @click="$emit('close')">取消</button>
          <button type="button" class="primary-btn" :disabled="submitting" @click="submitForm">
            {{ submitting ? '上传中...' : '确认上传' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'

const categories = ['公共课', '专业课', '考研', '课堂笔记', '其他']

const props = defineProps({
  open: { type: Boolean, default: false },
  submitting: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'submit'])

const createInitialForm = () => ({
  title: '',
  category: '',
  course: '',
  description: '',
  file: null,
  pricePoints: 0,
  tags: '',
})

const form = reactive(createInitialForm())
const fileInputKey = ref(0)

const fileSummary = computed(() => {
  if (!form.file) {
    return ''
  }

  const sizeInMb = (form.file.size / (1024 * 1024)).toFixed(1)
  return `${form.file.name} · ${sizeInMb} MB`
})

const handleFileChange = (event) => {
  form.file = event.target.files?.[0] || null
}

const submitForm = () => {
  if (props.submitting) {
    return
  }
  emit('submit', { ...form })
}

const resetForm = () => {
  Object.assign(form, createInitialForm())
  fileInputKey.value += 1
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
  width: min(100%, 660px);
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

.field-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
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
  min-height: 128px;
  resize: vertical;
}

.field small,
.file-summary {
  color: #73839c;
  font-size: 12px;
}

.choice-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.choice-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 14px;
  border: 1px solid #dbe3ff;
  border-radius: 16px;
  background: #f8faff;
  cursor: pointer;
}

.choice-card.active {
  border-color: #7c8cff;
  background: #edf1ff;
}

.choice-card input {
  display: none;
}

.pill-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.pill-btn,
.icon-btn,
.ghost-btn,
.primary-btn {
  border: none;
  cursor: pointer;
}

.pill-btn {
  min-height: 38px;
  padding: 0 14px;
  border-radius: 999px;
  background: #f4f7ff;
  color: #5b6c85;
  font-weight: 700;
}

.pill-btn.active {
  background: #fff1df;
  color: #d97706;
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

  .field-grid,
  .choice-row {
    grid-template-columns: 1fr;
  }
}
</style>
