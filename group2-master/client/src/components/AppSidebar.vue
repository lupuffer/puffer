<template>
  <aside class="sidebar">
    <div class="sidebar-brand">
      <div class="logo">
        <span class="logo-mark"><i class="fas fa-book-open"></i></span>
        <span class="logo-copy">
          <strong>{{ brandName }}</strong>
          <small>StarBook Link</small>
        </span>
      </div>
    </div>
    <nav class="sidebar-nav">
      <RouterLink
        v-for="item in navItems"
        :key="item.path || item.legacyHref"
        :to="item.path || '/'"
        class="nav-link"
        :class="{ active: isActive(item) }"
      >
        <span class="nav-icon"><i :class="item.icon"></i></span>
        <span>{{ item.label }}</span>
      </RouterLink>
    </nav>
    <div class="sidebar-user">
      <div class="user-info">
        <div class="user-avatar"><i class="fas fa-user"></i></div>
        <div class="user-details">
          <span class="user-name">{{ displayUserName }}</span>
          <span class="user-badge"><i class="fas fa-check-circle"></i> {{ authBadge }}</span>
        </div>
      </div>
      <button class="user-action" type="button" @click="$emit(appUser.isLoggedIn ? 'logout' : 'login')">
        <i :class="appUser.isLoggedIn ? 'fas fa-sign-out-alt' : 'fas fa-sign-in-alt'"></i>
        <span>{{ authButtonText }}</span>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed, inject } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

const props = defineProps({
  activePath: { type: String, default: '' },
  brand: { type: String, default: '' },
  items: { type: Array, default: () => [] },
  user: { type: Object, default: null },
  authBadgeText: { type: String, default: '' },
  defaultUserName: { type: String, default: '' },
  loginText: { type: String, default: '' },
  logoutText: { type: String, default: '' },
})

defineEmits(['login', 'logout'])

const appData = inject('appData', { value: {} })
const route = useRoute()

const site = computed(() => appData.value?.site ?? {})
const appUser = computed(() => props.user ?? appData.value?.appState?.user ?? {})
const navItems = computed(() => (props.items.length ? props.items : site.value.nav ?? []))
const brandName = computed(() => props.brand || site.value.brand || '星辰书链')
const authBadge = computed(() => props.authBadgeText || site.value.authBadge || (appUser.value?.isLoggedIn ? '已登录' : '游客模式'))
const currentPath = computed(() => props.activePath || route.path)
const authButtonText = computed(() => {
  return appUser.value?.isLoggedIn
    ? props.logoutText || site.value.logoutText || '退出登录'
    : props.loginText || site.value.loginText || '请先登录'
})
const displayUserName = computed(() => {
  if (appUser.value?.isLoggedIn && appUser.value?.name) return appUser.value.name
  return props.defaultUserName || site.value.defaultUserName || '请登录'
})

const isActive = (item) => {
  const path = item.path || ''
  const legacy = item.legacyHref || ''

  if (path === '/') {
    return currentPath.value === '/'
  }

  if (path && currentPath.value.startsWith(path)) {
    return true
  }

  return Boolean(legacy) && currentPath.value.endsWith(legacy)
}
</script>

<style scoped>
.sidebar {
  width: var(--sidebar-width);
  overflow: hidden;
  background: rgba(247, 248, 255, 0.68);
  border-right: 1px solid rgba(255, 255, 255, 0.48);
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 1000;
  box-shadow: 10px 0 34px rgba(92, 75, 140, 0.08);
  backdrop-filter: blur(22px);
}

.sidebar::before {
  content: '';
  position: absolute;
  pointer-events: none;
}

.sidebar::before {
  left: 0;
  right: 0;
  top: 112px;
  bottom: 0;
  background-image: url('/images/dashboard/sidebar-campus.png');
  background-repeat: no-repeat;
  background-size: cover;
  background-position: center bottom;
  opacity: 0.44;
  z-index: 0;
}

.sidebar-brand,
.sidebar-nav,
.sidebar-user {
  position: relative;
  z-index: 1;
}

.sidebar-brand {
  padding: 28px 24px 22px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.52);
}

.sidebar-brand .logo {
  display: flex;
  align-items: center;
  gap: 14px;
  color: var(--primary-blue);
}

.logo-mark {
  width: 46px;
  height: 46px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, rgba(238, 246, 255, 0.9), rgba(246, 240, 255, 0.9));
  box-shadow: inset 0 0 0 1px rgba(124, 140, 255, 0.12), 0 12px 26px rgba(92, 75, 140, 0.08);
}

.logo-mark i {
  font-size: 25px;
}

.logo-copy {
  display: flex;
  flex-direction: column;
  line-height: 1.15;
}

.logo-copy strong {
  font-size: 20px;
  font-weight: 800;
  letter-spacing: 0;
}

.logo-copy small {
  margin-top: 4px;
  font-size: 11px;
  font-weight: 700;
  color: #7b8fb2;
  text-transform: uppercase;
}

.sidebar-nav {
  flex: 1;
  padding: 18px 18px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  overflow-y: auto;
}

.sidebar-nav .nav-link {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 42px;
  padding: 10px 14px;
  text-decoration: none;
  color: rgba(45, 58, 84, 0.86);
  font-weight: 720;
  font-size: 14px;
  border: 1px solid transparent;
  border-radius: 13px;
  transition: color 0.18s ease, background-color 0.18s ease, transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
  white-space: nowrap;
}

.nav-icon {
  width: 24px;
  height: 24px;
  display: grid;
  place-items: center;
  color: currentColor;
}

.nav-icon i {
  width: 20px;
  text-align: center;
  font-size: 16px;
}

.sidebar-nav .nav-link:hover {
  color: var(--primary-blue);
  background-color: rgba(255, 255, 255, 0.42);
  border-color: rgba(255, 255, 255, 0.56);
  transform: translateX(2px);
}

.sidebar-nav .nav-link.active {
  color: #fff;
  background: linear-gradient(135deg, rgba(47, 128, 237, 0.8) 0%, rgba(111, 132, 255, 0.8) 64%, rgba(167, 139, 250, 0.8) 100%);
  font-weight: 800;
  border-color: rgba(118, 133, 255, 0.28);
  box-shadow: 0 12px 28px rgba(92, 75, 140, 0.18);
}

.sidebar-user {
  margin: 0 14px 18px;
  padding: 10px;
  border: 1px solid rgba(255, 255, 255, 0.58);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.6);
  box-shadow: 0 16px 40px rgba(92, 75, 140, 0.1);
  backdrop-filter: blur(18px);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, rgba(238, 246, 255, 0.95), rgba(237, 231, 255, 0.9));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-blue);
  font-size: 18px;
  box-shadow: inset 0 0 0 1px rgba(124, 140, 255, 0.13);
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow: hidden;
}

.user-name {
  font-size: 14px;
  font-weight: 800;
  color: var(--gray-900);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-badge {
  font-size: 12px;
  color: var(--secondary-green);
  display: flex;
  align-items: center;
  gap: 4px;
}

.user-badge i {
  font-size: 10px;
}

.user-action {
  width: 100%;
  margin-top: 12px;
  padding: 10px 12px;
  border: 1px solid rgba(255, 255, 255, 0.58);
  border-radius: 12px;
  background: rgba(247, 248, 255, 0.72);
  color: #506075;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  cursor: pointer;
}

.user-action:hover {
  color: var(--primary-blue);
  background-color: #eaf6ff;
  border-color: rgba(8, 118, 185, 0.28);
}

@media (max-width: 1024px) {
  .sidebar {
    width: var(--sidebar-width);
  }
}

@media (max-width: 768px) {
  .sidebar {
    width: 60px;
    transform: translateX(0);
  }

  .sidebar-brand {
    padding: 16px 0;
    display: flex;
    justify-content: center;
  }

  .logo-copy,
  .sidebar-nav .nav-link > span:not(.nav-icon),
  .user-details,
  .user-action span {
    display: none;
  }

  .sidebar-nav {
    padding: 12px 8px;
    align-items: center;
  }

  .sidebar-nav .nav-link {
    padding: 12px;
    justify-content: center;
  }

  .sidebar-user {
    padding: 12px 0;
    display: flex;
    justify-content: center;
  }
}
</style>
