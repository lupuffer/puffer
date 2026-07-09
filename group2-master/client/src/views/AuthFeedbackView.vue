<template>
  <div class="auth-feedback-page">
    <div class="auth-feedback-card">
      <div class="feedback-icon" :class="feedback.variant">
        <i :class="feedback.icon"></i>
      </div>
      <p class="feedback-eyebrow">{{ feedback.eyebrow }}</p>
      <h1>{{ feedback.title }}</h1>
      <p class="feedback-message">{{ feedback.message }}</p>
      <div class="feedback-actions">
        <button class="primary-btn" type="button" @click="handlePrimaryAction">
          {{ feedback.primaryText }}
        </button>
        <button class="secondary-btn" type="button" @click="handleSecondaryAction">
          {{ feedback.secondaryText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const feedback = computed(() => {
  const type = String(route.query.type || 'sessionExpired')

  const configMap = {
    forbidden: {
      eyebrow: '权限受限',
      title: '当前操作没有访问权限',
      message: '当前操作没有访问权限。',
      icon: 'fas fa-user-lock',
      variant: 'warning',
      primaryText: '返回上一页',
      secondaryText: '回到首页',
      primaryAction: 'back',
      secondaryAction: 'home',
    },
    loginRequired: {
      eyebrow: '需要登录',
      title: '请先登录',
      message: '请先登录后再继续操作。',
      icon: 'fas fa-right-to-bracket',
      variant: 'info',
      primaryText: '前往登录',
      secondaryText: '回到首页',
      primaryAction: 'login',
      secondaryAction: 'home',
    },
    sessionExpired: {
      eyebrow: '会话已过期',
      title: '登录状态已过期',
      message: '登录状态已过期，请重新登录。',
      icon: 'fas fa-clock-rotate-left',
      variant: 'danger',
      primaryText: '重新登录',
      secondaryText: '回到首页',
      primaryAction: 'login',
      secondaryAction: 'home',
    },
  }

  return configMap[type] || configMap.sessionExpired
})

const handlePrimaryAction = () => {
  if (feedback.value.primaryAction === 'back') {
    if (window.history.length > 1) {
      router.back()
      return
    }
    router.push('/')
    return
  }

  if (feedback.value.primaryAction === 'login') {
    router.push({
      path: '/login',
      query: {
        reason: String(route.query.type || 'sessionExpired'),
      },
    })
    return
  }

  router.push('/')
}

const handleSecondaryAction = () => {
  router.push('/')
}
</script>

<style scoped>
.auth-feedback-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background:
    linear-gradient(160deg, rgba(9, 26, 61, 0.88), rgba(34, 74, 138, 0.7)),
    radial-gradient(circle at top left, rgba(255, 196, 92, 0.24), transparent 28%),
    url('/images/dashboard/main-bg-1.png') center top / cover no-repeat;
}

.auth-feedback-card {
  width: min(100%, 540px);
  padding: 40px 36px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 28px 70px rgba(8, 19, 41, 0.28);
  text-align: center;
  backdrop-filter: blur(16px);
}

.feedback-icon {
  width: 84px;
  height: 84px;
  margin: 0 auto 18px;
  border-radius: 24px;
  display: grid;
  place-items: center;
  font-size: 32px;
}

.feedback-icon.info {
  color: #1d4ed8;
  background: linear-gradient(135deg, rgba(219, 234, 254, 0.94), rgba(191, 219, 254, 0.72));
}

.feedback-icon.warning {
  color: #b45309;
  background: linear-gradient(135deg, rgba(254, 243, 199, 0.94), rgba(253, 230, 138, 0.72));
}

.feedback-icon.danger {
  color: #b91c1c;
  background: linear-gradient(135deg, rgba(254, 226, 226, 0.96), rgba(252, 165, 165, 0.76));
}

.feedback-eyebrow {
  margin: 0 0 10px;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: var(--gray-500);
  text-transform: uppercase;
}

h1 {
  margin: 0 0 14px;
  font-size: 30px;
  line-height: 1.2;
  color: var(--gray-900);
}

.feedback-message {
  margin: 0;
  color: var(--gray-600);
  font-size: 15px;
  line-height: 1.75;
}

.feedback-actions {
  margin-top: 28px;
  display: flex;
  justify-content: center;
  gap: 14px;
  flex-wrap: wrap;
}

.primary-btn,
.secondary-btn {
  min-width: 140px;
  padding: 12px 20px;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
}

.primary-btn {
  border: none;
  color: white;
  background: linear-gradient(135deg, #2563eb, #4f46e5);
  box-shadow: 0 16px 30px rgba(37, 99, 235, 0.28);
}

.secondary-btn {
  border: 1px solid rgba(148, 163, 184, 0.38);
  background: white;
  color: var(--gray-700);
}

.primary-btn:hover,
.secondary-btn:hover {
  transform: translateY(-1px);
}

@media (max-width: 640px) {
  .auth-feedback-card {
    padding: 32px 24px;
  }

  h1 {
    font-size: 26px;
  }

  .feedback-actions {
    flex-direction: column;
  }

  .primary-btn,
  .secondary-btn {
    width: 100%;
  }
}
</style>
