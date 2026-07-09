<template>
  <div class="profile-content">
    <section class="profile-section profile-editor-shell">
      <div class="editor-hero">
        <div class="hero-copy">
          <h3><i class="fas fa-user-circle"></i> {{ profile.infoLabel || profile.menu[0] }}</h3>
        </div>
      </div>

      <form class="profile-form" @submit.prevent="handleSubmit">
        <div class="card-grid">
          <section class="info-card">
            <div class="card-head">
              <div>
                <h4>基础信息</h4>
              </div>
              <span class="card-icon"><i class="fas fa-user"></i></span>
            </div>

            <div class="field-grid">
              <label class="form-field field-span-2">
                <span class="field-label">姓名</span>
                <input
                  v-model.trim="form.name"
                  class="profile-input"
                  type="text"
                  maxlength="100"
                  placeholder="请输入姓名或展示名"
                />
              </label>

              <label class="form-field field-span-2">
                <span class="field-label">邮箱</span>
                <input
                  v-model.trim="form.email"
                  class="profile-input"
                  type="email"
                  maxlength="255"
                  placeholder="请输入邮箱地址"
                />
              </label>

              <label class="form-field field-span-2">
                <span class="field-label">手机</span>
                <input
                  v-model.trim="form.phone"
                  class="profile-input"
                  type="tel"
                  maxlength="30"
                  placeholder="请输入手机号"
                />
              </label>
            </div>
          </section>

          <section class="info-card">
            <div class="card-head">
              <div>
                <h4>校园信息</h4>
              </div>
              <span class="card-icon"><i class="fas fa-school"></i></span>
            </div>

            <div class="field-grid">
              <label class="form-field">
                <span class="field-label">学院</span>
                <input
                  v-model.trim="form.college"
                  class="profile-input"
                  type="text"
                  maxlength="100"
                  placeholder="填写学院"
                />
              </label>

              <label class="form-field">
                <span class="field-label">年级</span>
                <input
                  v-model.trim="form.grade"
                  class="profile-input"
                  type="text"
                  maxlength="50"
                  placeholder="填写年级"
                />
              </label>

              <label class="form-field field-span-2">
                <span class="field-label">校区</span>
                <input
                  v-model.trim="form.campus"
                  class="profile-input"
                  type="text"
                  maxlength="100"
                  placeholder="填写校区"
                />
              </label>
            </div>
          </section>

          <section class="info-card account-card">
            <div class="card-head">
              <div>
                <h4>账号信息</h4>
              </div>
              <span class="card-icon"><i class="fas fa-fingerprint"></i></span>
            </div>

            <div class="readonly-stack">
              <div v-for="item in profile.readonlyDetails" :key="item.label" class="readonly-row">
                <span class="readonly-label">{{ item.label }}</span>
                <strong class="readonly-value">{{ item.value }}</strong>
              </div>
            </div>
          </section>
        </div>

        <div class="editor-footer">
          <div class="status-box" :class="statusClass">
            <span class="status-dot"></span>
            <div>
              <strong>{{ statusTitle }}</strong>
              <p>{{ statusText }}</p>
            </div>
          </div>

          <div class="footer-actions">
            <span v-if="isLoggedIn && hasChanges" class="dirty-pill">内容已修改</span>
            <button
              class="save-button"
              :class="{ active: canSave }"
              type="submit"
              :disabled="!canSave"
            >
              {{ saving ? '保存中...' : '保存资料' }}
            </button>
          </div>
        </div>
      </form>
    </section>

    <section class="profile-section">
      <h3><i class="fas fa-chart-line"></i> 交易统计</h3>
      <div class="stats-grid">
        <div v-for="stat in profile.stats" :key="stat.label" class="stat-card">
          <div class="stat-icon"><i :class="stat.icon"></i></div>
          <div class="stat-content">
            <span class="stat-value">{{ stat.value }}</span>
            <span class="stat-label">{{ stat.label }}</span>
          </div>
        </div>
      </div>
    </section>

    <section class="profile-section">
      <h3><i class="fas fa-history"></i> 最近交易</h3>
      <div v-if="profile.recentTransactions.length" class="transactions-list">
        <div
          v-for="item in profile.recentTransactions"
          :key="item.title"
          class="transaction-item"
          @click="emit('orders')"
        >
          <div class="transaction-icon" :class="item.type"><i class="fas fa-check-circle"></i></div>
          <div class="transaction-details">
            <h4>{{ item.title }}</h4>
            <p class="transaction-date">{{ item.date }}</p>
            <p class="transaction-amount">{{ item.amount }}</p>
            <span v-if="item.status" class="transaction-status">{{ item.status }}</span>
          </div>
        </div>
      </div>
      <p v-else class="empty-state">暂无交易记录，完成订单后会显示在这里。</p>
    </section>
  </div>
</template>

<script setup>
import { computed, reactive, watch } from 'vue'

const props = defineProps({
  profile: { type: Object, required: true },
  isLoggedIn: { type: Boolean, default: false },
  saving: { type: Boolean, default: false },
  feedbackMessage: { type: String, default: '' },
  feedbackType: { type: String, default: '' },
})

const emit = defineEmits(['orders', 'save-profile'])

const form = reactive({
  name: '',
  email: '',
  college: '',
  grade: '',
  campus: '',
  phone: '',
})

const normalizedSourceProfile = computed(() => normalizeProfile(props.profile.editableProfile))
const normalizedForm = computed(() => normalizeProfile(form))
const hasChanges = computed(() => JSON.stringify(normalizedForm.value) !== JSON.stringify(normalizedSourceProfile.value))
const validationMessage = computed(() => validateForm(normalizedForm.value))
const canSave = computed(() => props.isLoggedIn && hasChanges.value && !validationMessage.value && !props.saving)

const statusTitle = computed(() => {
  if (!props.isLoggedIn) return '请先登录'
  if (props.saving) return '正在保存'
  if (validationMessage.value) return '资料待完善'
  if (props.feedbackType === 'success') return '资料已保存'
  if (props.feedbackType === 'error') return '保存失败'
  if (hasChanges.value) return '资料有更新'
  return '资料未修改'
})

const statusText = computed(() => {
  if (!props.isLoggedIn) return '登录后可编辑并保存你的校园资料。'
  if (props.saving) return '正在同步你最新填写的内容，请稍候。'
  if (validationMessage.value) return validationMessage.value
  if (props.feedbackMessage) return props.feedbackMessage
  if (hasChanges.value) return '保存按钮已高亮，确认无误后即可提交。'
  return '当前内容与已保存资料一致。'
})

const statusClass = computed(() => {
  if (!props.isLoggedIn) return 'status-neutral'
  if (props.saving) return 'status-pending'
  if (validationMessage.value || props.feedbackType === 'error') return 'status-error'
  if (props.feedbackType === 'success') return 'status-success'
  if (hasChanges.value) return 'status-pending'
  return 'status-neutral'
})

watch(
  () => props.profile.editableProfile,
  (nextProfile) => {
    const next = normalizeProfile(nextProfile)
    form.name = next.name
    form.email = next.email
    form.college = next.college
    form.grade = next.grade
    form.campus = next.campus
    form.phone = next.phone
  },
  { immediate: true, deep: true },
)

function normalizeProfile(profile = {}) {
  return {
    name: String(profile?.name || '').trim(),
    email: String(profile?.email || '').trim(),
    college: String(profile?.college || '').trim(),
    grade: String(profile?.grade || '').trim(),
    campus: String(profile?.campus || '').trim(),
    phone: String(profile?.phone || '').trim(),
  }
}

function validateForm(profileForm) {
  if (!props.isLoggedIn) return ''
  if (!profileForm.name) return '姓名不能为空。'
  if (!profileForm.email) return '邮箱不能为空。'
  if (!/^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/i.test(profileForm.email)) {
    return '邮箱格式不正确，请重新输入。'
  }
  if (/@zju\.edu$/i.test(profileForm.email)) {
    return '如果使用浙大邮箱，请填写完整的 @zju.edu.cn 后缀。'
  }
  return ''
}

function handleSubmit() {
  if (!canSave.value) return
  emit('save-profile', { ...normalizedForm.value })
}
</script>

<style scoped>
.profile-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.profile-section {
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.94), rgba(247, 250, 255, 0.94)),
    radial-gradient(circle at top right, rgba(124, 140, 255, 0.12), transparent 30%);
  border: 1px solid rgba(214, 226, 255, 0.82);
  border-radius: 24px;
  box-shadow: 0 22px 52px rgba(87, 103, 160, 0.12);
  padding: 24px;
}

.profile-editor-shell {
  overflow: hidden;
  padding-top: 18px;
  padding-bottom: 18px;
}

.editor-hero {
  display: flex;
  gap: 12px;
  padding: 0 0 10px;
}

.hero-copy h3 {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
  color: var(--gray-900);
  font-size: 24px;
  font-weight: 800;
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.info-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 100%;
  padding: 16px;
  border-radius: 20px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(246, 249, 255, 0.92)),
    radial-gradient(circle at top right, rgba(124, 140, 255, 0.1), transparent 30%);
  border: 1px solid rgba(221, 231, 255, 0.94);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.82);
}

.account-card {
  grid-column: span 2;
}

.card-head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.card-head h4 {
  margin: 0;
  color: var(--gray-900);
  font-size: 18px;
  font-weight: 750;
}

.card-icon {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 14px;
  color: var(--primary-blue);
  background: linear-gradient(135deg, rgba(238, 246, 255, 0.96), rgba(244, 239, 255, 0.88));
  border: 1px solid rgba(214, 226, 255, 0.92);
  font-size: 16px;
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.field-span-2 {
  grid-column: span 2;
}

.form-field {
  display: grid;
  grid-template-columns: 64px minmax(0, 1fr);
  align-items: center;
  gap: 10px;
}

.field-label {
  color: var(--gray-900);
  font-size: 14px;
  font-weight: 700;
  line-height: 1.4;
}

.profile-input {
  width: 100%;
  min-height: 40px;
  padding: 0 12px;
  border: 1px solid rgba(207, 220, 245, 0.96);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.88);
  color: var(--gray-900);
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
}

.profile-input:focus {
  outline: none;
  border-color: rgba(79, 110, 247, 0.46);
  background: white;
  box-shadow: 0 0 0 4px rgba(79, 110, 247, 0.08);
}

.readonly-stack {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.readonly-row {
  display: grid;
  grid-template-columns: 76px minmax(0, 1fr);
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-radius: 14px;
  background: rgba(244, 247, 255, 0.9);
  border: 1px solid rgba(221, 231, 255, 0.96);
}

.readonly-label {
  color: var(--gray-500);
  font-size: 13px;
  font-weight: 700;
}

.readonly-value {
  color: var(--gray-900);
  font-size: 16px;
  font-weight: 700;
  word-break: break-word;
}

.editor-footer {
  position: sticky;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 0;
  padding: 12px 14px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.84);
  border: 1px solid rgba(221, 231, 255, 0.94);
  box-shadow: 0 18px 42px rgba(87, 103, 160, 0.12);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
}

.status-box {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  min-width: 0;
}

.status-dot {
  width: 10px;
  height: 10px;
  margin-top: 6px;
  border-radius: 50%;
  flex: 0 0 auto;
  background: currentColor;
}

.status-box strong {
  display: block;
  margin-bottom: 4px;
  font-size: 14px;
  font-weight: 800;
}

.status-box p {
  margin: 0;
  color: inherit;
  font-size: 13px;
  line-height: 1.6;
  opacity: 0.88;
}

.status-neutral {
  color: var(--gray-600);
}

.status-pending {
  color: var(--primary-blue);
}

.status-success {
  color: #0f766e;
}

.status-error {
  color: #b91c1c;
}

.footer-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 0 0 auto;
}

.dirty-pill {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 0 12px;
  border-radius: 999px;
  color: var(--primary-blue);
  background: rgba(238, 246, 255, 0.92);
  border: 1px solid rgba(214, 226, 255, 0.92);
  font-size: 12px;
  font-weight: 800;
}

.save-button {
  min-width: 126px;
  min-height: 46px;
  padding: 0 20px;
  border: none;
  border-radius: 14px;
  background: rgba(207, 217, 237, 0.92);
  color: white;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease, opacity 0.18s ease;
}

.save-button.active {
  background: linear-gradient(135deg, #2f80ed 0%, #7c8cff 58%, #8ec5ff 100%);
  box-shadow: 0 18px 36px rgba(79, 110, 247, 0.24);
}

.save-button.active:hover {
  transform: translateY(-1px);
}

.save-button:disabled {
  cursor: not-allowed;
  opacity: 0.88;
}

.profile-section > h3 {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 0 16px;
  color: var(--gray-900);
  font-size: 18px;
  font-weight: 700;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.stat-card,
.transaction-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: 18px;
  background: rgba(246, 249, 255, 0.9);
  border: 1px solid rgba(221, 231, 255, 0.94);
}

.stat-icon {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border-radius: 14px;
  color: var(--primary-blue);
  background: white;
  font-size: 20px;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  color: var(--gray-900);
  font-size: 24px;
  font-weight: 800;
}

.stat-label,
.transaction-date,
.empty-state {
  color: var(--gray-600);
  font-size: 14px;
}

.transactions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.transaction-item {
  cursor: pointer;
}

.transaction-icon {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  font-size: 18px;
}

.transaction-icon.success {
  background-color: var(--light-green);
  color: var(--secondary-green);
}

.transaction-icon.pending {
  background-color: var(--light-blue);
  color: var(--primary-blue);
}

.transaction-details h4 {
  margin: 0 0 4px;
  color: var(--gray-900);
  font-size: 16px;
  font-weight: 700;
}

.transaction-amount {
  color: var(--primary-blue);
  font-size: 16px;
  font-weight: 700;
}

.transaction-status {
  display: inline-block;
  margin-top: 8px;
  padding: 4px 12px;
  border-radius: 999px;
  background-color: var(--light-blue);
  color: var(--primary-blue);
  font-size: 12px;
  font-weight: 700;
}

.empty-state {
  margin: 0;
}

@media (max-width: 1120px) {
  .card-grid {
    grid-template-columns: 1fr;
  }

  .account-card {
    grid-column: auto;
  }

  .readonly-stack {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 860px) {
  .editor-hero,
  .editor-footer {
    flex-direction: column;
    align-items: stretch;
  }

  .hero-chip-group,
  .footer-actions {
    justify-content: flex-start;
  }
}

@media (max-width: 640px) {
  .profile-section {
    padding: 18px;
    border-radius: 20px;
  }

  .hero-copy h3 {
    font-size: 22px;
  }

  .field-grid {
    grid-template-columns: 1fr;
  }

  .field-span-2 {
    grid-column: auto;
  }

  .form-field,
  .readonly-row {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .save-button {
    width: 100%;
  }
}
</style>
