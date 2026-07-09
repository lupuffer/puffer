<template>
  <header class="content-header">
    <div class="header-center">
      <form v-if="showSearch" class="header-search" @submit.prevent="submitSearch">
        <i class="fas fa-search search-icon"></i>
        <input v-model="keyword" type="text" :placeholder="displayPlaceholder" class="header-search-input" />
      </form>
    </div>
    <div class="header-right">
      <button class="header-btn btn-notification" :title="notificationTitle" @click="$emit('notification')">
        <i class="fas fa-bell"></i>
        <span v-if="hasNotification" class="notification-badge">{{ notificationBadgeText }}</span>
      </button>
      <button v-if="showPublish" class="header-btn btn-publish secondary-publish" @click="$emit('publish')">
        <i :class="actionIcon"></i>
        <span>{{ actionText }}</span>
      </button>
      <button v-if="secondaryActionText" class="header-btn btn-publish" @click="$emit('secondary-action')">
        <i :class="secondaryActionIcon"></i>
        <span>{{ secondaryActionText }}</span>
      </button>
      <button class="profile-chip" type="button" @click="$emit('profile')">
        <span class="profile-avatar"><i class="fas fa-user"></i></span>
        <span class="profile-copy">
          <strong>{{ displayUserName }}</strong>
          <small>{{ displayUserState }}</small>
        </span>
      </button>
    </div>
  </header>
</template>

<script setup>
import { computed, inject, ref } from 'vue'

const props = defineProps({
  searchPlaceholder: { type: String, default: '' },
  showSearch: { type: Boolean, default: true },
  showPublish: { type: Boolean, default: true },
  hasNotification: { type: Boolean, default: false },
  notificationCount: { type: Number, default: 0 },
  actionText: { type: String, default: '' },
  actionIcon: { type: String, default: 'fas fa-plus' },
  secondaryActionText: { type: String, default: '' },
  secondaryActionIcon: { type: String, default: 'fas fa-comment-dots' },
  site: { type: Object, default: null },
  user: { type: Object, default: null },
})

const emit = defineEmits(['search', 'notification', 'publish', 'secondary-action', 'profile'])

const appData = inject('appData', { value: {} })
const keyword = ref('')

const site = computed(() => props.site ?? appData.value?.site ?? {})
const header = computed(() => site.value.header ?? {})
const displayPlaceholder = computed(() => props.searchPlaceholder || header.value.defaultSearchPlaceholder || '搜索教材、课程或关键词')
const notificationBadgeText = computed(() => (props.notificationCount > 99 ? '99+' : String(props.notificationCount)))
const notificationTitle = computed(() => {
  const baseTitle = header.value.notificationTitle || '消息中心'
  if (!props.hasNotification) return baseTitle
  return `${baseTitle}（${notificationBadgeText.value} 条未读）`
})
const actionText = computed(() => props.actionText || header.value.publishText || '')
const appUser = computed(() => props.user ?? appData.value?.appState?.user ?? {})
const displayUserName = computed(() => (appUser.value?.isLoggedIn && appUser.value?.name ? appUser.value.name : '请先登录'))
const displayUserState = computed(() => (appUser.value?.isLoggedIn ? '已登录' : '游客模式'))

const submitSearch = () => {
  emit('search', keyword.value.trim())
}
</script>

<style scoped>
.content-header {
  min-height: var(--header-height);
  background: transparent;
  border-bottom: none;
  display: grid;
  grid-template-columns: minmax(320px, 1fr) auto;
  align-items: center;
  gap: 16px;
  padding: 12px 32px 8px;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: none;
  backdrop-filter: blur(10px);
}

.header-center {
  display: flex;
  justify-content: flex-start;
  min-width: 0;
}

.header-search {
  position: relative;
  display: flex;
  align-items: center;
  width: min(620px, 100%);
  height: 46px;
  border-radius: 999px;
}

.header-search::before {
  content: '';
  position: absolute;
  inset: -2px;
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.88), rgba(238, 246, 255, 0.78));
  box-shadow: 0 18px 38px rgba(92, 75, 140, 0.1);
  z-index: 0;
}

.header-search .search-icon {
  position: absolute;
  left: 18px;
  top: 50%;
  transform: translateY(-50%);
  color: #7d92a9;
  font-size: 14px;
  z-index: 1;
}

.header-search-input {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  padding: 0 18px 0 44px;
  border: 1px solid rgba(214, 226, 255, 0.7);
  border-radius: 999px;
  font-size: 14px;
  color: var(--gray-700);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.94), rgba(248, 251, 255, 0.9));
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.48);
  backdrop-filter: blur(18px);
  transition: all 0.2s ease;
}

.header-search-input:focus {
  outline: none;
  border-color: rgba(124, 140, 255, 0.48);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(246, 249, 255, 0.94));
  box-shadow: 0 0 0 4px rgba(124, 140, 255, 0.08), 0 18px 45px rgba(87, 103, 160, 0.12);
}

.header-search-input::placeholder {
  color: var(--gray-400);
}

.header-right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
}

.header-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 14px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  background: none;
}

.btn-notification {
  position: relative;
  width: 46px;
  height: 46px;
  padding: 0;
  color: #475569;
  background-color: rgba(255, 255, 255, 0.62);
  box-shadow: 0 16px 40px rgba(92, 75, 140, 0.1);
  backdrop-filter: blur(18px);
}

.btn-notification:hover {
  background-color: rgba(238, 246, 255, 0.86);
  color: var(--primary-blue);
}

.btn-notification i {
  font-size: 18px;
}

.notification-badge {
  position: absolute;
  top: -3px;
  right: -3px;
  min-width: 20px;
  height: 20px;
  padding: 0 5px;
  background: linear-gradient(135deg, #ef4444 0%, #f97316 100%);
  color: white;
  border-radius: 999px;
  border: 2px solid rgba(255, 255, 255, 0.96);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 800;
  line-height: 1;
  box-shadow: 0 8px 16px rgba(239, 68, 68, 0.28);
}

.btn-publish {
  background: linear-gradient(135deg, #2f80ed 0%, #7c8cff 62%, #a78bfa 100%);
  color: white;
  min-height: 46px;
  padding: 10px 20px;
  box-shadow: 0 18px 45px rgba(87, 103, 160, 0.18);
}

.btn-publish:hover {
  background: linear-gradient(135deg, #2563eb 0%, #7c8cff 58%, #a78bfa 100%);
  transform: translateY(-1px);
  box-shadow: 0 20px 48px rgba(92, 75, 140, 0.22);
}

.btn-publish i {
  font-size: 14px;
}

.profile-chip {
  min-height: 46px;
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid rgba(255, 255, 255, 0.55);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.66);
  padding: 5px 12px 5px 5px;
  color: var(--gray-700);
  cursor: pointer;
  box-shadow: 0 16px 40px rgba(92, 75, 140, 0.1);
  backdrop-filter: blur(18px);
  transition: background-color 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
}

.profile-chip:hover {
  transform: translateY(-1px);
  background: rgba(247, 248, 255, 0.9);
  border-color: rgba(124, 140, 255, 0.28);
}

.profile-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: white;
  background: linear-gradient(135deg, #4f6ef7, #7c8cff);
}

.profile-copy {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  line-height: 1.1;
}

.profile-copy strong {
  max-width: 88px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
  font-weight: 800;
}

.profile-copy small {
  margin-top: 3px;
  color: #10b981;
  font-size: 11px;
  font-weight: 700;
}

@media (max-width: 1024px) {
  .content-header {
    grid-template-columns: minmax(180px, 1fr) auto;
    padding: 14px 24px;
  }

  .header-search {
    width: min(520px, 100%);
  }

  .profile-copy,
  .btn-publish span {
    display: none;
  }
}

@media (max-width: 768px) {
  .content-header {
    grid-template-columns: 1fr auto;
    padding: 0 16px;
    min-height: 64px;
  }

  .header-center,
  .profile-chip {
    display: none;
  }

  .header-right {
    gap: 8px;
  }

  .btn-publish {
    padding: 8px 12px;
    font-size: 13px;
  }
}
</style>
