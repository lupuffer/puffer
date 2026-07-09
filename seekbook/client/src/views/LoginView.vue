<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-card">
        <div class="login-logo">
          <i class="fas fa-book-open"></i>
          <h1>{{ login.title }}</h1>
          <p>{{ login.subtitle }}</p>
        </div>

        <div v-if="feedbackState" class="feedback-panel" :class="feedbackState.variant">
          <div class="feedback-panel-icon">
            <i :class="feedbackState.icon"></i>
          </div>
          <div class="feedback-panel-body">
            <h3>{{ feedbackState.title }}</h3>
            <p>{{ feedbackState.message }}</p>
          </div>
        </div>

        <LoginTabs :tabs="login.tabs" :active="activeTab" @change="switchTab" />

        <AuthForm
          v-if="activeTab === 'username'"
          :fields="login.username.fields"
          :button-text="login.username.loginButton"
          :prompt="login.username.registerPrompt"
          :link-text="login.username.registerLink"
          :message="message"
          @submit="loginUsername"
          @switch="switchTab('register')"
        />

        <AuthForm
          v-else
          :fields="login.register.fields"
          :button-text="login.register.registerButton"
          :prompt="login.register.loginPrompt"
          :link-text="login.register.loginLink"
          :message="message"
          :success="success"
          icon="fas fa-user-plus"
          @submit="register"
          @switch="switchTab('username')"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, inject, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AuthForm from '../components/login/AuthForm.vue'
import LoginTabs from '../components/login/LoginTabs.vue'

const router = useRouter()
const route = useRoute()
const props = defineProps({ data: { type: Object, default: () => ({}) } })
const auth = inject('authActions')

const activeTab = ref('username')
const message = ref('')
const success = ref(false)
const feedbackCode = ref('')
const resultStatus = ref(0)

function ensureField(fields, field, insertAt = fields.length) {
  if (fields.some((item) => item?.key === field.key)) return fields
  const nextFields = [...fields]
  nextFields.splice(insertAt, 0, field)
  return nextFields
}

const login = computed(() => {
  const source = props.data.login ?? { tabs: [], username: { fields: [] }, register: { fields: [] }, messages: {} }
  let usernameFields = Array.isArray(source.username?.fields) ? [...source.username.fields] : []
  let registerFields = Array.isArray(source.register?.fields) ? [...source.register.fields] : []

  usernameFields = ensureField(
    usernameFields,
    {
      label: '\u4e94\u5929\u514d\u767b\u5f55',
      key: 'rememberMe',
      type: 'checkbox',
      checkboxText: '\u8bb0\u4f4f\u6211\uff085\u5929\u514d\u767b\u5f55\uff09',
    },
    usernameFields.length,
  )

  registerFields = ensureField(
    registerFields,
    {
      label: '\u90ae\u7bb1',
      placeholder: '\u8bf7\u8f93\u5165\u5e38\u7528\u90ae\u7bb1',
      key: 'email',
      type: 'email',
    },
    2,
  )

  return {
    ...source,
    username: {
      ...(source.username || {}),
      fields: usernameFields,
    },
    register: {
      ...(source.register || {}),
      fields: registerFields,
    },
    messages: {
      ...(source.messages || {}),
      required: '\u8bf7\u586b\u5199\u5b8c\u6574\u4fe1\u606f',
      usernameTooShort: '\u7528\u6237\u540d\u81f3\u5c11\u9700\u8981 3 \u4e2a\u5b57\u7b26',
      passwordMin: '\u5bc6\u7801\u81f3\u5c11 8 \u4f4d',
      passwordLowercase: '\u5bc6\u7801\u9700\u8981\u5305\u542b\u5c0f\u5199\u5b57\u6bcd',
      passwordUppercase: '\u5bc6\u7801\u9700\u8981\u5305\u542b\u5927\u5199\u5b57\u6bcd',
      passwordNumber: '\u5bc6\u7801\u9700\u8981\u5305\u542b\u6570\u5b57',
      passwordMismatch: '\u4e24\u6b21\u8f93\u5165\u7684\u5bc6\u7801\u4e0d\u4e00\u81f4',
      passwordWeak: '\u5bc6\u7801\u5f3a\u5ea6\u4e0d\u8db3\uff0c\u8bf7\u6309\u8981\u6c42\u91cd\u65b0\u8bbe\u7f6e',
      emailInvalid: '\u90ae\u7bb1\u683c\u5f0f\u4e0d\u6b63\u786e\uff0c\u8bf7\u68c0\u67e5\u540e\u91cd\u65b0\u8f93\u5165',
      emailDomainInvalid: '\u5982\u679c\u4f7f\u7528\u6d59\u5927\u90ae\u7bb1\uff0c\u8bf7\u586b\u5199\u5b8c\u6574\u7684 @zju.edu.cn \u540e\u7f00',
      emailRegistered: '\u8be5\u90ae\u7bb1\u5df2\u88ab\u6ce8\u518c\uff0c\u8bf7\u76f4\u63a5\u767b\u5f55\u6216\u66f4\u6362\u90ae\u7bb1',
      usernameRegistered: '\u8be5\u7528\u6237\u540d\u5df2\u5b58\u5728\uff0c\u8bf7\u66f4\u6362\u5176\u4ed6\u7528\u6237\u540d',
      loginRequired: '\u8bf7\u5148\u767b\u5f55\u540e\u518d\u7ee7\u7eed\u64cd\u4f5c',
      emailOrPasswordWrong: '\u7528\u6237\u540d\u6216\u5bc6\u7801\u9519\u8bef',
      sessionExpired: '\u767b\u5f55\u72b6\u6001\u5df2\u8fc7\u671f\uff0c\u8bf7\u91cd\u65b0\u767b\u5f55',
      requestFailed: '\u8bf7\u6c42\u5931\u8d25\uff0c\u8bf7\u7a0d\u540e\u518d\u8bd5',
      registerSuccess: '\u6ce8\u518c\u6210\u529f\uff0c\u8bf7\u767b\u5f55',
    },
  }
})

function inferFeedbackCode(code, text, status = 0) {
  if (code) return code

  const rawMessage = String(text || '').toLowerCase()
  const rawMessageText = String(text || '')
  if (rawMessageText.includes('\u7528\u6237\u540d\u5df2\u5b58\u5728')) return 'USERNAME_ALREADY_EXISTS'
  if (rawMessageText.includes('\u90ae\u7bb1\u5df2\u88ab\u6ce8\u518c')) return 'EMAIL_ALREADY_EXISTS'
  if (status === 409 && rawMessageText.includes('\u7528\u6237\u540d')) return 'USERNAME_ALREADY_EXISTS'
  if (status === 409 && rawMessageText.includes('\u90ae\u7bb1')) return 'EMAIL_ALREADY_EXISTS'
  if (rawMessage.includes('username exists') || rawMessage.includes('username already exists')) return 'USERNAME_ALREADY_EXISTS'
  if (rawMessage.includes('email exists') || rawMessage.includes('email already exists')) return 'EMAIL_ALREADY_EXISTS'
  if (rawMessage.includes('username must be 3+ chars')) return 'USERNAME_TOO_SHORT'
  if (rawMessage.includes('invalid email') || rawMessage.includes('email format')) return 'EMAIL_INVALID'
  if (rawMessage.includes('password') && rawMessage.includes('weak')) return 'PASSWORD_TOO_WEAK'
  if (rawMessage.includes('expired')) return 'sessionExpired'
  if (rawMessageText.includes('\u8bf7\u5148\u767b\u5f55')) return 'AUTH_REQUIRED'
  return ''
}

const feedbackState = computed(() => {
  const code = inferFeedbackCode(feedbackCode.value, message.value, resultStatus.value)
  if (!code || success.value) return null

  const stateMap = {
    AUTH_REQUIRED: {
      title: '\u8bf7\u5148\u767b\u5f55',
      message: '\u8bf7\u5148\u767b\u5f55\u540e\u518d\u7ee7\u7eed\u64cd\u4f5c\u3002',
      icon: 'fas fa-right-to-bracket',
      variant: 'info',
    },
    BAD_CREDENTIALS: {
      title: '\u767b\u5f55\u4fe1\u606f\u4e0d\u5339\u914d',
      message: '\u7528\u6237\u540d\u6216\u5bc6\u7801\u9519\u8bef\u3002',
      icon: 'fas fa-key',
      variant: 'danger',
    },
    EMAIL_ALREADY_EXISTS: {
      title: '\u90ae\u7bb1\u5df2\u88ab\u6ce8\u518c',
      message: '\u8be5\u90ae\u7bb1\u5df2\u88ab\u6ce8\u518c\uff0c\u8bf7\u76f4\u63a5\u767b\u5f55\u6216\u66f4\u6362\u90ae\u7bb1\u3002',
      icon: 'fas fa-envelope-circle-check',
      variant: 'warning',
    },
    USERNAME_ALREADY_EXISTS: {
      title: '\u7528\u6237\u540d\u5df2\u5b58\u5728',
      message: '\u8be5\u7528\u6237\u540d\u5df2\u5b58\u5728\uff0c\u8bf7\u66f4\u6362\u5176\u4ed6\u7528\u6237\u540d\u3002',
      icon: 'fas fa-user-tag',
      variant: 'warning',
    },
    USERNAME_TOO_SHORT: {
      title: '\u7528\u6237\u540d\u957f\u5ea6\u4e0d\u591f',
      message: '\u7528\u6237\u540d\u81f3\u5c11\u9700\u8981 3 \u4e2a\u5b57\u7b26\u3002',
      icon: 'fas fa-user-pen',
      variant: 'info',
    },
    PASSWORD_TOO_WEAK: {
      title: '\u5bc6\u7801\u5f3a\u5ea6\u8fd8\u4e0d\u591f',
      message: '\u5bc6\u7801\u5f3a\u5ea6\u4e0d\u8db3\uff0c\u8bf7\u6309\u8981\u6c42\u91cd\u65b0\u8bbe\u7f6e\u3002',
      icon: 'fas fa-shield-halved',
      variant: 'info',
    },
    PASSWORD_MISMATCH: {
      title: '\u4e24\u6b21\u5bc6\u7801\u8f93\u5165\u4e0d\u4e00\u81f4',
      message: '\u4e24\u6b21\u8f93\u5165\u7684\u5bc6\u7801\u4e0d\u4e00\u81f4\u3002',
      icon: 'fas fa-lock-open',
      variant: 'warning',
    },
    EMAIL_INVALID: {
      title: '\u90ae\u7bb1\u683c\u5f0f\u9700\u8981\u8c03\u6574',
      message: '\u90ae\u7bb1\u683c\u5f0f\u4e0d\u6b63\u786e\uff0c\u8bf7\u68c0\u67e5\u540e\u91cd\u65b0\u8f93\u5165\u3002',
      icon: 'fas fa-at',
      variant: 'info',
    },
    EMAIL_DOMAIN_INVALID: {
      title: '\u90ae\u7bb1\u540e\u7f00\u9700\u8981\u8865\u5145\u5b8c\u6574',
      message: '\u5982\u679c\u4f7f\u7528\u6d59\u5927\u90ae\u7bb1\uff0c\u8bf7\u586b\u5199\u5b8c\u6574\u7684 @zju.edu.cn \u540e\u7f00\u3002',
      icon: 'fas fa-building-columns',
      variant: 'info',
    },
    FORBIDDEN: {
      title: '\u5f53\u524d\u64cd\u4f5c\u65e0\u6743\u9650',
      message: '\u5f53\u524d\u64cd\u4f5c\u6ca1\u6709\u8bbf\u95ee\u6743\u9650\u3002',
      icon: 'fas fa-user-lock',
      variant: 'warning',
    },
    NETWORK_UNAVAILABLE: {
      title: '\u540e\u7aef\u670d\u52a1\u6682\u65f6\u4e0d\u53ef\u7528',
      message: message.value || '\u8bf7\u786e\u8ba4\u540e\u7aef\u5df2\u542f\u52a8\uff0c\u6216\u7a0d\u540e\u518d\u8bd5\u3002',
      icon: 'fas fa-plug-circle-xmark',
      variant: 'danger',
    },
    BACKEND_UNAVAILABLE: {
      title: '\u540e\u7aef\u670d\u52a1\u6682\u65f6\u4e0d\u53ef\u7528',
      message: message.value || '\u8bf7\u786e\u8ba4\u540e\u7aef\u5df2\u542f\u52a8\uff0c\u6216\u7a0d\u540e\u518d\u8bd5\u3002',
      icon: 'fas fa-server',
      variant: 'danger',
    },
    INVALID_RESPONSE: {
      title: '\u540e\u7aef\u8fd4\u56de\u5f02\u5e38',
      message: message.value || '\u540e\u7aef\u8fd4\u56de\u7684\u6570\u636e\u65e0\u6cd5\u89e3\u6790\uff0c\u8bf7\u68c0\u67e5\u540e\u7aef\u63a5\u53e3\u3002',
      icon: 'fas fa-triangle-exclamation',
      variant: 'danger',
    },
    EMPTY_RESPONSE: {
      title: '\u540e\u7aef\u8fd4\u56de\u5f02\u5e38',
      message: message.value || '\u540e\u7aef\u8fd4\u56de\u4e86\u7a7a\u54cd\u5e94\uff0c\u8bf7\u68c0\u67e5\u540e\u7aef\u63a5\u53e3\u3002',
      icon: 'fas fa-triangle-exclamation',
      variant: 'danger',
    },
    NAME_REQUIRED: {
      title: '\u59d3\u540d\u8fd8\u6ca1\u6709\u586b\u5199',
      message: message.value || '\u8bf7\u8f93\u5165\u59d3\u540d\u540e\u518d\u63d0\u4ea4\u6ce8\u518c\u3002',
      icon: 'fas fa-id-card',
      variant: 'info',
    },
    EMAIL_REQUIRED: {
      title: '\u90ae\u7bb1\u8fd8\u6ca1\u6709\u586b\u5199',
      message: message.value || '\u8bf7\u8f93\u5165\u90ae\u7bb1\u5730\u5740\u540e\u518d\u63d0\u4ea4\u6ce8\u518c\u3002',
      icon: 'fas fa-envelope',
      variant: 'info',
    },
    PASSWORD_REQUIRED: {
      title: '\u5bc6\u7801\u8fd8\u6ca1\u6709\u586b\u5199',
      message: message.value || '\u8bf7\u8f93\u5165\u5bc6\u7801\u540e\u518d\u63d0\u4ea4\u6ce8\u518c\u3002',
      icon: 'fas fa-lock',
      variant: 'info',
    },
    REGISTER_FAILED: {
      title: '\u6ce8\u518c\u6682\u65f6\u6ca1\u6709\u6210\u529f',
      message: message.value || '\u7cfb\u7edf\u5fd9\u788c\uff0c\u8bf7\u7a0d\u540e\u518d\u8bd5\u3002',
      icon: 'fas fa-circle-exclamation',
      variant: 'danger',
    },
    TOKEN_INVALID: {
      title: '\u767b\u5f55\u51ed\u8bc1\u5df2\u5931\u6548',
      message: '\u767b\u5f55\u51ed\u8bc1\u5df2\u5931\u6548\uff0c\u8bf7\u91cd\u65b0\u767b\u5f55\u3002',
      icon: 'fas fa-shield-halved',
      variant: 'warning',
    },
    USER_NOT_FOUND: {
      title: '\u8d26\u53f7\u4fe1\u606f\u9700\u8981\u91cd\u65b0\u9a8c\u8bc1',
      message: '\u8d26\u53f7\u4fe1\u606f\u5df2\u5931\u6548\uff0c\u8bf7\u91cd\u65b0\u767b\u5f55\u3002',
      icon: 'fas fa-user-slash',
      variant: 'warning',
    },
    REFRESH_TOKEN_REQUIRED: {
      title: '\u767b\u5f55\u72b6\u6001\u5df2\u5931\u6548',
      message: '\u767b\u5f55\u72b6\u6001\u5df2\u8fc7\u671f\uff0c\u8bf7\u91cd\u65b0\u767b\u5f55\u3002',
      icon: 'fas fa-clock-rotate-left',
      variant: 'warning',
    },
    sessionExpired: {
      title: '\u767b\u5f55\u72b6\u6001\u9700\u8981\u91cd\u65b0\u9a8c\u8bc1',
      message: '\u767b\u5f55\u72b6\u6001\u5df2\u8fc7\u671f\uff0c\u8bf7\u91cd\u65b0\u767b\u5f55\u3002',
      icon: 'fas fa-clock-rotate-left',
      variant: 'warning',
    },
  }

  return stateMap[code] || {
    title: '\u63d0\u4ea4\u6ca1\u6709\u6210\u529f',
    message: message.value || login.value.messages.requestFailed,
    icon: 'fas fa-circle-exclamation',
    variant: 'danger',
  }
})

const switchTab = (tab) => {
  activeTab.value = tab
  message.value = ''
  success.value = false
  feedbackCode.value = ''
  resultStatus.value = 0
}

const goHome = () => router.push('/')
const loginUsername = async (form) =>
  handleResult(await auth?.loginUsername(form.username, form.password, Boolean(form.rememberMe)))
const register = async (form) => handleResult(await auth?.register(form), true)

const handleResult = (result, stay = false) => {
  success.value = Boolean(result?.success)
  resultStatus.value = Number(result?.status || 0)
  feedbackCode.value = inferFeedbackCode(result?.code || '', result?.message || '', resultStatus.value)
  message.value = result?.message || ''
  if (result?.success && !stay) goHome()
  if (result?.success && stay) {
    activeTab.value = 'username'
    message.value = result?.message || login.value.messages.registerSuccess
  }
}

watch(
  () => route.query.reason,
  (reason) => {
    if (reason === 'sessionExpired') {
      activeTab.value = 'username'
      success.value = false
      feedbackCode.value = 'sessionExpired'
      message.value = login.value.messages.sessionExpired
    }
  },
  { immediate: true },
)
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background:
    linear-gradient(135deg, rgba(15, 23, 42, 0.48), rgba(37, 99, 235, 0.26)),
    url('/images/login-bg.png') center center / cover no-repeat;
}

.login-container {
  width: 100%;
  max-width: 520px;
}

.login-card {
  background: rgba(255, 255, 255, 0.88);
  border-radius: 16px;
  padding: 32px;
  box-shadow: var(--shadow-xl);
  backdrop-filter: blur(16px);
}

.login-logo {
  text-align: center;
  margin-bottom: 24px;
}

.login-logo i {
  font-size: 48px;
  color: var(--primary-blue);
}

.login-logo h1 {
  font-size: 24px;
  color: var(--gray-900);
  margin-top: 16px;
}

.login-logo p {
  font-size: 14px;
  color: var(--gray-600);
  margin-top: 8px;
}

.feedback-panel {
  display: grid;
  grid-template-columns: 56px 1fr;
  gap: 14px;
  margin-bottom: 22px;
  padding: 16px 18px;
  border-radius: 16px;
  border: 1px solid transparent;
}

.feedback-panel.danger {
  background: rgba(254, 242, 242, 0.92);
  border-color: rgba(248, 113, 113, 0.24);
}

.feedback-panel.warning {
  background: rgba(255, 251, 235, 0.94);
  border-color: rgba(245, 158, 11, 0.2);
}

.feedback-panel.info {
  background: rgba(239, 246, 255, 0.94);
  border-color: rgba(59, 130, 246, 0.2);
}

.feedback-panel-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  font-size: 22px;
}

.feedback-panel.danger .feedback-panel-icon {
  color: #b91c1c;
  background: rgba(254, 226, 226, 0.95);
}

.feedback-panel.warning .feedback-panel-icon {
  color: #b45309;
  background: rgba(254, 243, 199, 0.95);
}

.feedback-panel.info .feedback-panel-icon {
  color: #1d4ed8;
  background: rgba(219, 234, 254, 0.95);
}

.feedback-panel-body h3 {
  margin: 0 0 8px;
  font-size: 18px;
  color: var(--gray-900);
}

.feedback-panel-body p {
  margin: 0;
  font-size: 14px;
  line-height: 1.7;
  color: var(--gray-600);
}
</style>
