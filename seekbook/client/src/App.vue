<template>
  <RouterView v-if="isStandalone" v-slot="{ Component }">
    <component :is="Component" :data="appData" />
  </RouterView>
  <div v-else class="app-shell">
    <AppSidebar
      :active-path="activePath"
      :brand="brandName"
      :items="layoutNavItems"
      :user="appData.appState?.user"
      :auth-badge-text="site.authBadge"
      :default-user-name="site.defaultUserName"
      :login-text="site.loginText"
      :logout-text="site.logoutText"
      @login="goLogin"
      @logout="logout"
    />
    <main class="main-content" :class="`page-${pageKey}`">
      <AppHeader
        :site="site"
        :search-placeholder="searchPlaceholder"
        :show-search="showSearch"
        :show-publish="showPublish"
        :has-notification="hasNotification"
        :notification-count="totalUnreadNotifications"
        :action-text="actionText"
        :action-icon="actionIcon"
        :secondary-action-text="secondaryActionText"
        :secondary-action-icon="secondaryActionIcon"
        :user="appData.appState?.user"
        @search="handleSearch"
        @publish="handlePrimaryAction"
        @secondary-action="handleSecondaryAction"
        @notification="goMessages"
        @profile="goProfile"
      />
      <div class="content-body" :class="{ flush: route.meta.flush }">
        <RouterView v-slot="{ Component }">
          <component :is="Component" :data="appData" />
        </RouterView>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, provide, ref, watch } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import AppSidebar from './components/AppSidebar.vue'
import AppHeader from './components/AppHeader.vue'
import { loginByUsername as apiLoginByUsername, logoutUser as apiLogoutUser, registerUser } from './services/api'
import { useGlobalState } from './composables/useGlobalState'
import { getStoredAuthUser, setStoredAuthUser } from './utils/authStorage'

const router = useRouter()
const route = useRoute()
const appData = ref({ site: { nav: [], header: {}, pageTitles: {} }, appState: {} })
const authInvalidatedEvent = 'starbook-auth-invalidated'
const appFeedbackEvent = 'starbook-app-feedback'
const brandName = '\u661f\u8fb0\u4e66\u94fe'
const { chatSessions, currentUser, fetchChatSessionsState, clearAuthenticatedUser, setAuthenticatedUser } = useGlobalState()
const unreadPollTimer = ref(null)
const UNREAD_POLL_INTERVAL = 8000

provide('appData', appData)
provide('authActions', {
  loginUsername: (username, password, rememberMe) => loginUsername(username, password, rememberMe),
  register: (form) => register(form),
  logout: () => logout(),
})

const stopUnreadPolling = () => {
  if (unreadPollTimer.value) {
    clearInterval(unreadPollTimer.value)
    unreadPollTimer.value = null
  }
}

const pollUnreadNotifications = async () => {
  if (typeof document !== 'undefined' && document.hidden) return
  if (!currentUser.value?.id) return

  await fetchChatSessionsState({ silent: true })
}

const startUnreadPolling = () => {
  stopUnreadPolling()
  if (!currentUser.value?.id) return
  unreadPollTimer.value = setInterval(() => {
    pollUnreadNotifications()
  }, UNREAD_POLL_INTERVAL)
}

const handleVisibilityChange = () => {
  if (typeof document !== 'undefined' && document.hidden) {
    stopUnreadPolling()
    return
  }

  pollUnreadNotifications()
  startUnreadPolling()
}

onMounted(async () => {
  try {
    const response = await fetch('/data.json')
    if (!response.ok) {
      throw new Error(`\u52a0\u8f7d\u914d\u7f6e\u5931\u8d25\uff0c\u72b6\u6001\u7801\uff1a${response.status}`)
    }
    const data = await response.json()
    appData.value = { ...data, appState: { ...data.appState, user: loadStoredUser(data.appState?.user) } }
  } catch (error) {
    console.error('Failed to load data.json:', error)
    appData.value = {
      site: { nav: [], header: {}, pageTitles: {} },
      appState: { user: loadStoredUser({}) },
    }
  }

  window.addEventListener(authInvalidatedEvent, handleAuthInvalidated)
  window.addEventListener(appFeedbackEvent, handleAppFeedback)
  document.addEventListener('visibilitychange', handleVisibilityChange)
})

onBeforeUnmount(() => {
  window.removeEventListener(authInvalidatedEvent, handleAuthInvalidated)
  window.removeEventListener(appFeedbackEvent, handleAppFeedback)
  document.removeEventListener('visibilitychange', handleVisibilityChange)
  stopUnreadPolling()
})

const site = computed(() => appData.value.site || {})
const pageKey = computed(() => route.meta.pageKey || 'index')
const isStandalone = computed(() => route.meta.standalone === true)
const activePath = computed(() => route.meta.activePath || route.path)
const layoutNavItems = [
  { label: '\u9996\u9875', path: '/', icon: 'fas fa-house' },
  { label: '\u667a\u6167\u6e05\u5355', path: '/smart-list', icon: 'fas fa-list-check' },
  { label: '\u661f\u56fe\u96c6\u5e02', path: '/buy', icon: 'fas fa-store' },
  { label: '\u6211\u8981\u5356\u4e66', path: '/sell', icon: 'fas fa-tag' },
  { label: '\u77e5\u8bc6\u661f\u6cb3', path: '/knowledge', icon: 'fas fa-graduation-cap' },
  { label: '\u6d88\u606f\u4e2d\u5fc3', path: '/messages', icon: 'fas fa-comments' },
  { label: '\u4e2a\u4eba\u4e2d\u5fc3', path: '/profile', icon: 'fas fa-user' },
]
const pageTitles = {
  index: '\u9996\u9875',
  smartList: '\u667a\u6167\u6e05\u5355',
  buy: '\u661f\u56fe\u96c6\u5e02',
  sell: '\u6211\u8981\u5356\u4e66',
  knowledge: '\u77e5\u8bc6\u661f\u6cb3',
  messages: '\u6d88\u606f\u4e2d\u5fc3',
  profile: '\u4e2a\u4eba\u4e2d\u5fc3',
  orders: '\u6211\u7684\u8ba2\u5355',
  bookDetail: '\u4e66\u7c4d\u8be6\u60c5',
  publishSell: '\u53d1\u5e03\u5356\u4e66',
  login: '\u767b\u5f55',
}
const showSearch = computed(() => route.meta.showSearch !== false)
const showPublish = computed(() => route.meta.showPublish !== false)
const actionIcon = computed(() => route.meta.actionIcon || 'fas fa-plus')
const secondaryActionIcon = computed(() => (pageKey.value === 'knowledge' ? 'fas fa-comment-dots' : ''))
const totalUnreadNotifications = computed(() => {
  return (chatSessions.value || []).reduce(
    (sum, session) => sum + Math.max(0, Number(session?.unread) || 0),
    0,
  )
})
const hasNotification = computed(() => totalUnreadNotifications.value > 0)
const searchPlaceholder = computed(() => {
  if (pageKey.value === 'knowledge') return '\u641c\u7d22\u8d44\u6599\u3001\u8bfe\u7a0b\u6216\u8ba8\u8bba'
  return '\u641c\u7d22\u4e66\u540d\u3001ISBN\u3001\u8bfe\u7a0b...'
})
const actionText = computed(() => {
  if (pageKey.value === 'knowledge') return '\u4e0a\u4f20\u8d44\u6599'
  return '\u53d1\u5e03\u5356\u4e66'
})
const secondaryActionText = computed(() => (pageKey.value === 'knowledge' ? '\u53d1\u5e03\u8ba8\u8bba' : ''))

const handleSearch = (keyword) => {
  if (!keyword) return
  if (pageKey.value === 'knowledge') {
    router.push({ path: '/knowledge', query: { search: keyword, tab: route.query.tab || undefined } })
    return
  }
  router.push({ path: '/buy', query: { search: keyword } })
}

const handlePrimaryAction = () => {
  if (pageKey.value === 'knowledge') {
    window.dispatchEvent(new Event('open-knowledge-upload'))
    return
  }
  router.push('/sell')
}

const handleSecondaryAction = () => {
  if (pageKey.value === 'knowledge') {
    window.dispatchEvent(new Event('open-knowledge-discussion'))
  }
}

const goMessages = () => router.push('/messages')
const goLogin = () => router.push('/login')
const goProfile = () => router.push('/profile')

const buildLoggedOutUser = (fallback = {}) => ({
  ...fallback,
  id: null,
  username: '',
  email: '',
  accessToken: '',
  refreshToken: '',
  tokenType: 'Bearer',
  expiresAt: '',
  refreshExpiresAt: '',
  rememberMe: false,
  isLoggedIn: false,
  name: site.value.defaultUserName || fallback.name || '\u8bf7\u5148\u767b\u5f55',
})

const loadStoredUser = (fallback = {}) => {
  try {
    const storedUser = getStoredAuthUser()
    if (!storedUser?.id || (!storedUser?.accessToken && !storedUser?.refreshToken)) {
      return buildLoggedOutUser(fallback)
    }
    return { ...fallback, ...storedUser, isLoggedIn: true }
  } catch {
    return buildLoggedOutUser(fallback)
  }
}

const isBasicEmailFormat = (email) => /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/i.test(email)
const hasIncompleteZjuDomain = (email) => /@zju\.edu$/i.test(email)

const getAuthMessages = (messages = {}) => ({
  ...messages,
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
  nameRequired: '\u59d3\u540d\u4e0d\u80fd\u4e3a\u7a7a',
  emailRequired: '\u8bf7\u8f93\u5165\u90ae\u7bb1\u5730\u5740',
  passwordRequired: '\u8bf7\u8f93\u5165\u5bc6\u7801',
})

const getPasswordRequirementMessage = (password, messages = {}) => {
  if (password.length < 8) return messages.passwordMin || '\u5bc6\u7801\u81f3\u5c11 8 \u4f4d'
  if (!/[a-z]/.test(password)) return messages.passwordLowercase || '\u5bc6\u7801\u9700\u8981\u5305\u542b\u5c0f\u5199\u5b57\u6bcd'
  if (!/[A-Z]/.test(password)) return messages.passwordUppercase || '\u5bc6\u7801\u9700\u8981\u5305\u542b\u5927\u5199\u5b57\u6bcd'
  if (!/\d/.test(password)) return messages.passwordNumber || '\u5bc6\u7801\u9700\u8981\u5305\u542b\u6570\u5b57'
  return ''
}

const mapAuthErrorMessage = (error, messages = {}) => {
  if (!error?.code) return error?.message || messages.requestFailed || ''

  const errorMessageMap = {
    AUTH_REQUIRED: messages.loginRequired || '\u8bf7\u5148\u767b\u5f55',
    BACKEND_UNAVAILABLE: error.message || messages.requestFailed,
    BAD_CREDENTIALS: messages.emailOrPasswordWrong || '\u7528\u6237\u540d\u6216\u5bc6\u7801\u9519\u8bef',
    EMAIL_ALREADY_EXISTS: messages.emailRegistered || '\u8be5\u90ae\u7bb1\u5df2\u88ab\u6ce8\u518c\uff0c\u8bf7\u76f4\u63a5\u767b\u5f55\u6216\u66f4\u6362\u90ae\u7bb1',
    EMAIL_DOMAIN_INVALID: messages.emailDomainInvalid || '\u5982\u679c\u4f7f\u7528\u6d59\u5927\u90ae\u7bb1\uff0c\u8bf7\u586b\u5199\u5b8c\u6574\u7684 @zju.edu.cn \u540e\u7f00',
    EMAIL_INVALID: messages.emailInvalid || '\u90ae\u7bb1\u683c\u5f0f\u4e0d\u6b63\u786e\uff0c\u8bf7\u68c0\u67e5\u540e\u91cd\u65b0\u8f93\u5165',
    EMAIL_REQUIRED: messages.emailRequired || error.message,
    EMPTY_RESPONSE: error.message || messages.requestFailed,
    FORBIDDEN: '\u5f53\u524d\u64cd\u4f5c\u6ca1\u6709\u8bbf\u95ee\u6743\u9650',
    INVALID_RESPONSE: error.message || messages.requestFailed,
    LOGIN_FIELDS_REQUIRED: messages.required || error.message,
    NAME_REQUIRED: messages.nameRequired || error.message,
    NETWORK_UNAVAILABLE: error.message || messages.requestFailed,
    PASSWORD_REQUIRED: messages.passwordRequired || error.message,
    PASSWORD_TOO_WEAK: messages.passwordWeak || '\u5bc6\u7801\u5f3a\u5ea6\u4e0d\u8db3\uff0c\u8bf7\u6309\u8981\u6c42\u91cd\u65b0\u8bbe\u7f6e',
    REGISTER_FAILED: error.message || messages.requestFailed,
    REFRESH_TOKEN_REQUIRED: messages.sessionExpired || '\u767b\u5f55\u72b6\u6001\u5df2\u8fc7\u671f\uff0c\u8bf7\u91cd\u65b0\u767b\u5f55',
    TOKEN_EXPIRED: messages.sessionExpired || '\u767b\u5f55\u72b6\u6001\u5df2\u8fc7\u671f\uff0c\u8bf7\u91cd\u65b0\u767b\u5f55',
    TOKEN_INVALID: '\u767b\u5f55\u51ed\u8bc1\u5df2\u5931\u6548\uff0c\u8bf7\u91cd\u65b0\u767b\u5f55',
    TOKEN_REVOKED: '\u767b\u5f55\u51ed\u8bc1\u5df2\u5931\u6548\uff0c\u8bf7\u91cd\u65b0\u767b\u5f55',
    USER_NOT_FOUND: '\u8d26\u53f7\u4fe1\u606f\u5df2\u5931\u6548\uff0c\u8bf7\u91cd\u65b0\u767b\u5f55',
    USERNAME_ALREADY_EXISTS: messages.usernameRegistered || '\u8be5\u7528\u6237\u540d\u5df2\u5b58\u5728\uff0c\u8bf7\u66f4\u6362\u5176\u4ed6\u7528\u6237\u540d',
    USERNAME_TOO_SHORT: messages.usernameTooShort || '\u7528\u6237\u540d\u81f3\u5c11\u9700\u8981 3 \u4e2a\u5b57\u7b26',
  }

  return errorMessageMap[error.code] || error.message || messages.requestFailed || ''
}

const inferLegacyAuthErrorCode = (error) => {
  const rawMessage = String(error?.message || '').toLowerCase()
  const rawMessageText = String(error?.message || '')

  if (error?.code) return error.code
  if (error?.status === 409 && rawMessage.includes('username')) return 'USERNAME_ALREADY_EXISTS'
  if (error?.status === 409 && rawMessage.includes('email')) return 'EMAIL_ALREADY_EXISTS'
  if (rawMessage.includes('username exists')) return 'USERNAME_ALREADY_EXISTS'
  if (rawMessage.includes('email exists')) return 'EMAIL_ALREADY_EXISTS'
  if (rawMessage.includes('username must be 3+ chars')) return 'USERNAME_TOO_SHORT'
  if (rawMessage.includes('password') && rawMessage.includes('weak')) return 'PASSWORD_TOO_WEAK'
  if (rawMessage.includes('invalid email') || rawMessage.includes('email format')) return 'EMAIL_INVALID'
  if (rawMessageText.includes('\u7528\u6237\u540d\u5df2\u5b58\u5728')) return 'USERNAME_ALREADY_EXISTS'
  if (rawMessageText.includes('\u90ae\u7bb1\u5df2\u88ab\u6ce8\u518c')) return 'EMAIL_ALREADY_EXISTS'
  if (rawMessageText.includes('\u7528\u6237\u540d\u81f3\u5c11\u9700\u8981')) return 'USERNAME_TOO_SHORT'
  if (rawMessageText.includes('\u5bc6\u7801\u5f3a\u5ea6\u4e0d\u8db3')) return 'PASSWORD_TOO_WEAK'
  if (rawMessageText.includes('\u90ae\u7bb1\u683c\u5f0f\u4e0d\u6b63\u786e')) return 'EMAIL_INVALID'
  if (rawMessageText.includes('\u8bf7\u5148\u767b\u5f55')) return 'AUTH_REQUIRED'

  return ''
}

const handleAuthInvalidated = async (event) => {
  const detail = event?.detail || {}
  appData.value.appState.user = buildLoggedOutUser(appData.value.appState?.user || {})
  await clearAuthenticatedUser()
  if (detail.code === 'TOKEN_EXPIRED' || detail.code === 'TOKEN_REVOKED') {
    router.push({
      path: '/auth-feedback',
      query: {
        type: 'sessionExpired',
        message: detail.message || '',
      },
    })
  }
}

const handleAppFeedback = (event) => {
  const detail = event?.detail || {}
  if (detail.type === 'forbidden') {
    router.push({
      path: '/auth-feedback',
      query: {
        type: 'forbidden',
        message: detail.message || '',
      },
    })
  }
}

const loginWithUser = async (user) => {
  const nextUser = { ...appData.value.appState?.user, ...user, isLoggedIn: true }
  const messages = getAuthMessages(appData.value.login?.messages || {})
  appData.value.appState.user = nextUser
  setStoredAuthUser(nextUser)
  await setAuthenticatedUser(nextUser)
  return { success: true, user: nextUser, message: `${messages.loginSuccessPrefix || ''}${nextUser.name || ''}` }
}

const loginUsername = async (username, password, rememberMe = false) => {
  const messages = getAuthMessages(appData.value.login?.messages || {})
  if (!username || !password) return { success: false, message: messages.required || '' }

  try {
    const result = await apiLoginByUsername(username, password, rememberMe)
    return await loginWithUser(result.data)
  } catch (error) {
    const normalizedCode = inferLegacyAuthErrorCode(error)
    const normalizedError = {
      ...error,
      code: normalizedCode || error?.code || '',
      message: error?.message || '',
      status: error?.status || 0,
      details: error?.details || null,
    }
    return {
      success: false,
      code: normalizedError.code,
      status: normalizedError.status,
      details: normalizedError.details,
      message: mapAuthErrorMessage(normalizedError, messages) || messages.emailOrPasswordWrong || '',
    }
  }
}

const register = async (form) => {
  const messages = getAuthMessages(appData.value.login?.messages || {})
  if (!form.name || !form.username || !form.email || !form.password || !form.passwordConfirm) {
    return { success: false, code: 'FORM_INCOMPLETE', message: messages.required || '' }
  }
  if (!isBasicEmailFormat(form.email)) {
    return { success: false, code: 'EMAIL_INVALID', message: messages.emailInvalid || '' }
  }
  if (hasIncompleteZjuDomain(form.email)) {
    return { success: false, code: 'EMAIL_DOMAIN_INVALID', message: messages.emailDomainInvalid || '' }
  }
  const passwordRequirementMessage = getPasswordRequirementMessage(form.password, messages)
  if (passwordRequirementMessage) {
    return { success: false, code: 'PASSWORD_TOO_WEAK', message: passwordRequirementMessage }
  }
  if (form.password !== form.passwordConfirm) {
    return { success: false, code: 'PASSWORD_MISMATCH', message: messages.passwordMismatch || '' }
  }

  try {
    const result = await registerUser({
      name: form.name,
      username: form.username,
      email: form.email,
      password: form.password,
    })
    return { success: true, message: messages.registerSuccess || result.message || '' }
  } catch (error) {
    const rawMessageText = String(error?.message || '')
    const normalizedCode =
      inferLegacyAuthErrorCode(error) ||
      (rawMessageText.includes('\u7528\u6237\u540d\u5df2\u5b58\u5728') ? 'USERNAME_ALREADY_EXISTS' : '') ||
      (rawMessageText.includes('\u90ae\u7bb1\u5df2\u88ab\u6ce8\u518c') ? 'EMAIL_ALREADY_EXISTS' : '') ||
      ((error?.status === 409 && rawMessageText.includes('\u7528\u6237\u540d')) ? 'USERNAME_ALREADY_EXISTS' : '') ||
      ((error?.status === 409 && rawMessageText.includes('\u90ae\u7bb1')) ? 'EMAIL_ALREADY_EXISTS' : '')
    const normalizedError = {
      ...error,
      code: normalizedCode || error?.code || '',
      message: error?.message || '',
      status: error?.status || 0,
      details: error?.details || null,
    }
    const fallbackMessage =
      normalizedError.code === 'USERNAME_ALREADY_EXISTS'
        ? '\u8be5\u7528\u6237\u540d\u5df2\u5b58\u5728\uff0c\u8bf7\u66f4\u6362\u5176\u4ed6\u7528\u6237\u540d'
        : normalizedError.code === 'EMAIL_ALREADY_EXISTS'
          ? '\u8be5\u90ae\u7bb1\u5df2\u88ab\u6ce8\u518c\uff0c\u8bf7\u76f4\u63a5\u767b\u5f55\u6216\u66f4\u6362\u90ae\u7bb1'
          : ''
    return {
      success: false,
      code: normalizedError.code,
      status: normalizedError.status,
      details: normalizedError.details,
      message: fallbackMessage || mapAuthErrorMessage(normalizedError, messages) || messages.emailRegistered || '',
    }
  }
}

const logout = async () => {
  try {
    await apiLogoutUser()
  } catch {
  }

  appData.value.appState.user = buildLoggedOutUser(appData.value.appState?.user || {})
  await clearAuthenticatedUser()
  if (route.meta.standalone !== true) router.push('/')
}

watch(
  () => currentUser.value?.id,
  async (userId) => {
    if (!userId) {
      stopUnreadPolling()
      return
    }

    await pollUnreadNotifications()
    startUnreadPolling()
  },
  { immediate: true },
)
</script>

<style>
:root {
  /* === Refined Design System — "Cosmic Scholar" === */
  /* Primary: deep indigo → warm violet spectrum */
  --primary-blue: #3B5998;
  --primary-blue-dark: #2E4777;
  --primary-blue-light: #EFF2F9;
  --primary-indigo: #5B6AB5;
  --primary-lavender: #8B7EC8;
  --primary-periwinkle: #6B7DB3;
  /* Gold — warmth for knowledge/book elements */
  --star-gold: #D4A853;
  --sunset-orange: #E07B5A;
  --secondary-green: #3B8B7A;
  --accent-orange: #E07B5A;
  --light-blue: #EFF2F9;
  --light-green: #D4EDE6;
  /* Refined grays — warmer, more sophisticated */
  --gray-50: #F8F7F4;
  --gray-100: #F0EEE9;
  --gray-200: #E2DED6;
  --gray-300: #C8C3B8;
  --gray-400: #9E988B;
  --gray-500: #706A5E;
  --gray-600: #534D43;
  --gray-700: #3A352E;
  --gray-800: #1E1B18;
  --gray-900: #1E1B18;
  /* Shadows — softer, warmer tones */
  --shadow-sm: 0 1px 3px rgba(59, 89, 152, 0.05);
  --shadow-md: 0 12px 32px rgba(59, 89, 152, 0.10);
  --shadow-lg: 0 16px 40px rgba(59, 89, 152, 0.14);
  --shadow-xl: 0 20px 52px rgba(91, 80, 130, 0.12);
  /* Glass surfaces — warm transparency */
  --glass-bg: rgba(255, 255, 255, 0.68);
  --glass-border: rgba(200, 192, 175, 0.45);
  --glass-shadow: 0 14px 38px rgba(59, 89, 152, 0.12);
  /* Layout */
  --sidebar-width: 260px;
  --header-height: 78px;
  --content-padding: 32px;
  --card-border-radius: 18px;
  --btn-border-radius: 10px;
  --input-border-radius: 14px;
  /* Page background — warmer, more sophisticated */
  --page-bg-fill: #D5CFC6;
  --page-bg-overlay:
    linear-gradient(180deg, rgba(248, 247, 244, 0.46) 0%, rgba(240, 238, 233, 0.32) 34%, rgba(239, 242, 249, 0.40) 100%);
  --main-visual-ratio: 0.742;
  --main-visual-overlap: 28px;
  /* Dashboard surfaces — refined glass */
  --dashboard-card-bg: rgba(255, 255, 255, 0.44);
  --dashboard-card-border: rgba(184, 175, 160, 0.34);
  --dashboard-card-shadow: 0 14px 38px rgba(59, 89, 152, 0.12);
  --dashboard-card-blur: 18px;
  --dashboard-book-card-bg: rgba(255, 255, 255, 0.68);
  --dashboard-book-card-border: rgba(200, 192, 175, 0.42);
  --dashboard-book-card-shadow: 0 12px 34px rgba(91, 80, 130, 0.08);
  --dashboard-book-card-shadow-hover: 0 18px 42px rgba(91, 80, 130, 0.14);
  --dashboard-mini-bg: rgba(255, 255, 255, 0.54);
  --dashboard-mini-border: rgba(255, 255, 255, 0.50);
  --dashboard-mini-shadow: 0 10px 30px rgba(91, 80, 130, 0.07);
  --dashboard-subcard-bg: rgba(248, 246, 242, 0.60);
  --dashboard-subcard-border: rgba(210, 202, 188, 0.66);
  --dashboard-subcard-shadow: 0 8px 20px rgba(80, 75, 60, 0.06);
  --dashboard-pill-bg: rgba(239, 242, 249, 0.72);
  --dashboard-pill-bg-strong: rgba(239, 242, 249, 0.80);
  /* Surface aliases */
  --surface-glass: var(--dashboard-card-bg);
  --surface-glass-strong: var(--dashboard-book-card-bg);
  --surface-soft: var(--dashboard-subcard-bg);
  --surface-softer: var(--dashboard-mini-bg);
  --surface-pill: var(--dashboard-pill-bg);
  --surface-border: var(--dashboard-card-border);
  --surface-border-strong: var(--dashboard-mini-border);
  --surface-shadow-soft: var(--dashboard-mini-shadow);
  --surface-shadow-main: var(--dashboard-card-shadow);
  --surface-shadow-nested: var(--dashboard-subcard-shadow);
  /* CTA — refined gradient using new primaries */
  --cta-gradient: linear-gradient(135deg, #3B5998 0%, #5B6AB5 48%, #8B7EC8 100%);
  --cta-gradient-hover: linear-gradient(135deg, #2E4777 0%, #4A58A0 48%, #7A6EB8 100%);
  --cta-shadow: 0 16px 38px rgba(91, 80, 130, 0.20), 0 8px 22px rgba(59, 89, 152, 0.14);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body,
#app {
  height: 100%;
}

html,
body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  line-height: 1.6;
  color: var(--gray-800);
  background:
    radial-gradient(circle at 16% 10%, rgba(139, 126, 200, 0.12), transparent 26%),
    radial-gradient(circle at 86% 8%, rgba(212, 168, 83, 0.10), transparent 22%),
    #F8F7F4;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

button,
input,
textarea,
select {
  font: inherit;
}

.app-shell {
  display: flex;
  height: 100vh;
  min-height: 100vh;
  overflow: hidden;
  background:
    linear-gradient(180deg, rgba(248, 247, 244, 0.74), rgba(239, 242, 249, 0.80)),
    radial-gradient(circle at 76% 18%, rgba(139, 126, 200, 0.08), transparent 30%);
}

.main-content {
  --page-bg-split: calc((100vw - var(--sidebar-width)) * var(--main-visual-ratio));
  position: relative;
  flex: 1;
  height: 100vh;
  margin-left: var(--sidebar-width);
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: var(--page-bg-fill);
  overflow: hidden;
}

.main-content::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: url('/images/dashboard/main-bg-1.png');
  background-repeat: no-repeat;
  background-position: right top;
  background-size: 100% auto;
  pointer-events: none;
  z-index: 0;
}

.main-content::after {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    var(--page-bg-overlay),
    linear-gradient(var(--page-bg-fill), var(--page-bg-fill));
  background-repeat: no-repeat, no-repeat;
  background-position:
    0 0,
    0 calc(var(--page-bg-split) - var(--main-visual-overlap));
  background-size:
    100% 100%,
    100% calc(100% - var(--page-bg-split) + var(--main-visual-overlap));
  pointer-events: none;
  z-index: 0;
}

.content-body {
  position: relative;
  z-index: 1;
  flex: 1;
  padding: var(--content-padding);
  overflow-y: auto;
  min-width: 0;
}

.content-body.flush {
  padding: 0;
  overflow: hidden;
}

.main-content.page-messages .content-body.flush {
  display: flex;
  flex: 1;
  height: 0;
  min-height: 0;
  overflow: hidden;
}

.main-content:not(.page-index) .smart-hero,
.main-content:not(.page-index) .community-intro,
.main-content:not(.page-index) .orders-header {
  border: 1px solid var(--dashboard-card-border) !important;
  border-radius: 22px !important;
  background:
    radial-gradient(circle at 88% 16%, rgba(124, 140, 255, 0.2), transparent 28%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.84), rgba(238, 246, 255, 0.58)) !important;
  box-shadow: var(--dashboard-card-shadow) !important;
  backdrop-filter: blur(var(--dashboard-card-blur));
  -webkit-backdrop-filter: blur(var(--dashboard-card-blur));
  color: var(--gray-900) !important;
}

.main-content:not(.page-index) .summary-grid article,
.main-content:not(.page-index) .plan-panel,
.main-content:not(.page-index) .next-panel,
.main-content:not(.page-index) .search-box,
.main-content:not(.page-index) .filter-section,
.main-content:not(.page-index) .virtual-list-container,
.main-content:not(.page-index) .pagination-wrap,
.main-content:not(.page-index) .shortage-card,
.main-content:not(.page-index) .shortage-modal-content,
.main-content:not(.page-index) .isbn-quick-section,
.main-content:not(.page-index) .sell-form-wrapper,
.main-content:not(.page-index) .recycle-card-small,
.main-content:not(.page-index) .info-tip-small,
.main-content:not(.page-index) .sidebar-card,
.main-content:not(.page-index) .material-card,
.main-content:not(.page-index) .modal-content,
.main-content:not(.page-index) .chat-container,
.main-content:not(.page-index) .profile-sidebar,
.main-content:not(.page-index) .profile-section,
.main-content:not(.page-index) .order-section,
.main-content:not(.page-index) .order-status-info,
.main-content:not(.page-index) .error-container,
.main-content:not(.page-index) .price-section,
.main-content:not(.page-index) .seller-info,
.main-content:not(.page-index) .transaction-console,
.main-content:not(.page-index) .safety-tips,
.main-content:not(.page-index) .book-meta-info,
.main-content:not(.page-index) .book-card {
  border: 1px solid var(--dashboard-card-border) !important;
  background: var(--dashboard-card-bg) !important;
  box-shadow: var(--dashboard-card-shadow) !important;
  backdrop-filter: blur(var(--dashboard-card-blur));
  -webkit-backdrop-filter: blur(var(--dashboard-card-blur));
}

.main-content:not(.page-index) .chat-sidebar,
.main-content:not(.page-index) .chat-main {
  background: rgba(255, 255, 255, 0.64) !important;
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
}

.main-content:not(.page-index) .course-list article,
.main-content:not(.page-index) .todo-list button,
.main-content:not(.page-index) .status-item,
.main-content:not(.page-index) .transaction-item,
.main-content:not(.page-index) .stat-card,
.main-content:not(.page-index) .detail-item,
.main-content:not(.page-index) .knowledge-item,
.main-content:not(.page-index) .hot-item,
.main-content:not(.page-index) .shortage-item,
.main-content:not(.page-index) .shortage-card-header,
.main-content:not(.page-index) .delivery-info,
.main-content:not(.page-index) .chat-messages,
.main-content:not(.page-index) .message-content,
.main-content:not(.page-index) .conversation,
.main-content:not(.page-index) .demo-reset-wrap,
.main-content:not(.page-index) .form-actions,
.main-content:not(.page-index) .filter-tag,
.main-content:not(.page-index) .filter-tab,
.main-content:not(.page-index) .tab-item,
.main-content:not(.page-index) .page-btn,
.main-content:not(.page-index) .sort-option,
.main-content:not(.page-index) .option-content,
.main-content:not(.page-index) .tag-suggestion,
.main-content:not(.page-index) .material-type,
.main-content:not(.page-index) .tag,
.main-content:not(.page-index) .price-savings {
  border-color: var(--dashboard-subcard-border) !important;
  background: var(--dashboard-subcard-bg) !important;
  box-shadow: none !important;
}

.main-content:not(.page-index) .course-list article,
.main-content:not(.page-index) .status-item,
.main-content:not(.page-index) .transaction-item,
.main-content:not(.page-index) .stat-card,
.main-content:not(.page-index) .hot-item,
.main-content:not(.page-index) .detail-item,
.main-content:not(.page-index) .knowledge-item,
.main-content:not(.page-index) .shortage-item,
.main-content:not(.page-index) .material-card,
.main-content:not(.page-index) .message-content,
.main-content:not(.page-index) .order-card,
.main-content:not(.page-index) .book-meta-info,
.main-content:not(.page-index) .delivery-info,
.main-content:not(.page-index) .conversation,
.main-content:not(.page-index) .book-card,
.main-content:not(.page-index) .virtual-list-container .book-card {
  background: var(--dashboard-subcard-bg) !important;
  border: 1px solid var(--dashboard-subcard-border) !important;
  box-shadow: var(--dashboard-subcard-shadow) !important;
}

.main-content:not(.page-index) .todo-list button,
.main-content:not(.page-index) .filter-tag,
.main-content:not(.page-index) .filter-tab,
.main-content:not(.page-index) .tab-item,
.main-content:not(.page-index) .page-btn,
.main-content:not(.page-index) .sort-option,
.main-content:not(.page-index) .profile-menu-item,
.main-content:not(.page-index) .tag-suggestion,
.main-content:not(.page-index) .material-type,
.main-content:not(.page-index) .tag {
  background: var(--dashboard-pill-bg) !important;
  border: 1px solid var(--dashboard-subcard-border) !important;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.3) !important;
}

.main-content:not(.page-index) .detail-item {
  border-radius: 14px;
  padding: 14px 16px !important;
}

.main-content:not(.page-index) .hot-item,
.main-content:not(.page-index) .transaction-item,
.main-content:not(.page-index) .status-item,
.main-content:not(.page-index) .course-list article {
  border-radius: 16px !important;
}

.main-content:not(.page-index) .summary-grid span,
.main-content:not(.page-index) .course-icon,
.main-content:not(.page-index) .stat-icon,
.main-content:not(.page-index) .status-icon,
.main-content:not(.page-index) .profile-avatar,
.main-content:not(.page-index) .seller-avatar,
.main-content:not(.page-index) .author-avatar,
.main-content:not(.page-index) .conversation-avatar,
.main-content:not(.page-index) .chat-header-avatar,
.main-content:not(.page-index) .message-avatar,
.main-content:not(.page-index) .recycle-card-small .icon {
  background: linear-gradient(135deg, rgba(238, 246, 255, 0.88), rgba(245, 240, 255, 0.78)) !important;
  color: var(--primary-blue) !important;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.52);
}

.main-content:not(.page-index) .message.sent .message-avatar,
.main-content:not(.page-index) .chat-header-avatar,
.main-content:not(.page-index) .conversation-avatar {
  background: var(--cta-gradient) !important;
  color: white !important;
  box-shadow: var(--surface-shadow-soft);
}

.main-content:not(.page-index) .smart-hero h1,
.main-content:not(.page-index) .community-intro h1,
.main-content:not(.page-index) .orders-header h1,
.main-content:not(.page-index) .section-heading h2,
.main-content:not(.page-index) .profile-section h3,
.main-content:not(.page-index) .sidebar-card h3,
.main-content:not(.page-index) .material-body h3,
.main-content:not(.page-index) .book-basic-info h1,
.main-content:not(.page-index) .seller-info h3,
.main-content:not(.page-index) .transaction-console h3,
.main-content:not(.page-index) .safety-tips h4,
.main-content:not(.page-index) .chat-header-name {
  color: var(--gray-900) !important;
}

.main-content:not(.page-index) .smart-hero p,
.main-content:not(.page-index) .community-intro p,
.main-content:not(.page-index) .orders-header p,
.main-content:not(.page-index) .section-heading p,
.main-content:not(.page-index) .course-main p,
.main-content:not(.page-index) .material-description,
.main-content:not(.page-index) .material-meta,
.main-content:not(.page-index) .author-reputation,
.main-content:not(.page-index) .book-author,
.main-content:not(.page-index) .book-meta,
.main-content:not(.page-index) .book-seller,
.main-content:not(.page-index) .transaction-date,
.main-content:not(.page-index) .detail-label,
.main-content:not(.page-index) .detail-value,
.main-content:not(.page-index) .conversation-preview,
.main-content:not(.page-index) .message-time,
.main-content:not(.page-index) .chat-header-status,
.main-content:not(.page-index) .seller-text p,
.main-content:not(.page-index) .delivery-info p,
.main-content:not(.page-index) .safety-tips li {
  color: var(--gray-500) !important;
}

.main-content:not(.page-index) .message.sent .message-content,
.main-content:not(.page-index) .message.sent .message-text {
  color: var(--gray-900) !important;
}

.main-content:not(.page-index) .message.sent .message-time {
  color: rgba(24, 32, 51, 0.72) !important;
}

.main-content:not(.page-index) .search-input,
.main-content:not(.page-index) .price-input,
.main-content:not(.page-index) .page-input,
.main-content:not(.page-index) .form-input,
.main-content:not(.page-index) .form-textarea,
.main-content:not(.page-index) .isbn-input,
.main-content:not(.page-index) .shortage-form-group input,
.main-content:not(.page-index) .shortage-form-group select,
.main-content:not(.page-index) .shortage-form-group textarea,
.main-content:not(.page-index) .upload-form input[type='text'],
.main-content:not(.page-index) .upload-form select,
.main-content:not(.page-index) .upload-form textarea,
.main-content:not(.page-index) .chat-input {
  border: 1px solid var(--surface-border) !important;
  background: rgba(255, 255, 255, 0.66) !important;
  color: var(--gray-700) !important;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.34);
}

.main-content:not(.page-index) .search-input:focus,
.main-content:not(.page-index) .price-input:focus,
.main-content:not(.page-index) .page-input:focus,
.main-content:not(.page-index) .form-input:focus,
.main-content:not(.page-index) .form-textarea:focus,
.main-content:not(.page-index) .isbn-input:focus,
.main-content:not(.page-index) .shortage-form-group input:focus,
.main-content:not(.page-index) .shortage-form-group select:focus,
.main-content:not(.page-index) .shortage-form-group textarea:focus,
.main-content:not(.page-index) .upload-form input[type='text']:focus,
.main-content:not(.page-index) .upload-form select:focus,
.main-content:not(.page-index) .upload-form textarea:focus,
.main-content:not(.page-index) .chat-input:focus {
  outline: none;
  border-color: rgba(124, 140, 255, 0.48) !important;
  box-shadow: 0 0 0 4px rgba(124, 140, 255, 0.08), 0 18px 45px rgba(87, 103, 160, 0.12) !important;
}

.main-content:not(.page-index) .search-btn,
.main-content:not(.page-index) .price-btn-confirm,
.main-content:not(.page-index) .smart-hero button,
.main-content:not(.page-index) .btn-primary,
.main-content:not(.page-index) .isbn-btn-recognize,
.main-content:not(.page-index) .btn-shortage-register,
.main-content:not(.page-index) .btn-download,
.main-content:not(.page-index) .send-btn,
.main-content:not(.page-index) .filter-tag:first-child,
.main-content:not(.page-index) .filter-tab:first-child,
.main-content:not(.page-index) .tab-item:first-child,
.main-content:not(.page-index) .page-btn.active,
.main-content:not(.page-index) .sort-option.active,
.main-content:not(.page-index) .profile-menu-item.active,
.main-content:not(.page-index) .course-status.active,
.main-content:not(.page-index) .transaction-status,
.main-content:not(.page-index) .hot-rank.top {
  background: var(--cta-gradient) !important;
  color: white !important;
  border-color: transparent !important;
  box-shadow: var(--cta-shadow) !important;
}

.main-content:not(.page-index) .search-btn:hover,
.main-content:not(.page-index) .price-btn-confirm:hover,
.main-content:not(.page-index) .smart-hero button:hover,
.main-content:not(.page-index) .btn-primary:hover,
.main-content:not(.page-index) .isbn-btn-recognize:hover,
.main-content:not(.page-index) .btn-shortage-register:hover,
.main-content:not(.page-index) .btn-download:hover,
.main-content:not(.page-index) .send-btn:hover {
  background: var(--cta-gradient-hover) !important;
}

.main-content:not(.page-index) .price-btn-reset,
.main-content:not(.page-index) .btn-outline,
.main-content:not(.page-index) .isbn-btn-scan,
.main-content:not(.page-index) .history-upload-btn,
.main-content:not(.page-index) .chat-action-btn,
.main-content:not(.page-index) .toolbar-btn,
.main-content:not(.page-index) .demo-reset-btn,
.main-content:not(.page-index) .shortage-cancel-btn,
.main-content:not(.page-index) .sort-option,
.main-content:not(.page-index) .page-btn,
.main-content:not(.page-index) .filter-tag,
.main-content:not(.page-index) .filter-tab,
.main-content:not(.page-index) .tab-item,
.main-content:not(.page-index) .profile-menu-item,
.main-content:not(.page-index) .recycle-card-small .btn-sm {
  background: rgba(255, 255, 255, 0.66) !important;
  color: var(--gray-700) !important;
  border: 1px solid var(--surface-border) !important;
  box-shadow: var(--surface-shadow-soft);
}

.main-content:not(.page-index) .sort-option:hover,
.main-content:not(.page-index) .page-btn:hover,
.main-content:not(.page-index) .filter-tag:hover,
.main-content:not(.page-index) .filter-tab:hover,
.main-content:not(.page-index) .tab-item:hover,
.main-content:not(.page-index) .profile-menu-item:hover,
.main-content:not(.page-index) .conversation:hover,
.main-content:not(.page-index) .todo-list button:hover {
  background: rgba(238, 246, 255, 0.82) !important;
  color: var(--primary-blue) !important;
}

@media (max-width: 1024px) {
  .main-content {
    margin-left: 220px;
  }

  :root {
    --sidebar-width: 220px;
    --content-padding: 24px;
  }
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 60px;
  }
}
</style>
