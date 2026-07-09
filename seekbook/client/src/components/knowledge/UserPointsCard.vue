<template>
  <section class="points-card">
    <div class="card-head">
      <h3>个人星河卡</h3>
    </div>

    <div class="user-row">
      <div class="avatar"><i class="fas fa-user-astronaut"></i></div>
      <div class="user-copy">
        <div class="name-row">
          <strong>{{ user?.isLoggedIn ? user.name : '请先登录' }}</strong>
          <span class="auth-badge">{{ user?.isLoggedIn ? '已认证' : '访客模式' }}</span>
        </div>
        <p>{{ user?.isLoggedIn ? '今日活跃可获得更多积分' : '登录后可上传、发讨论、签到和查看个人记录' }}</p>
      </div>
    </div>

    <div class="points-panel">
      <div class="points-head">
        <span>Points</span>
        <strong>{{ points }}/{{ maxPoints }}</strong>
      </div>
      <div class="progress-track">
        <div class="progress-fill" :style="{ width: progressWidth }"></div>
      </div>
    </div>

    <button type="button" class="checkin-btn" :disabled="checkedIn || checkingIn" @click="$emit('checkin')">
      {{ checkingIn ? '签到中...' : (checkedIn ? '今日已签到' : '签到 +5') }}
    </button>

    <div class="shortcut-block">
      <h4>快捷入口</h4>
      <div class="shortcut-list">
        <button
          v-for="item in shortcuts"
          :key="item.key"
          type="button"
          class="shortcut-btn"
          :class="{ active: activeShortcutKey === item.key }"
          @click="$emit('shortcut', item.key)"
        >
          <span class="shortcut-icon"><i :class="item.icon"></i></span>
          <span class="shortcut-label">{{ item.label }}</span>
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  user: {
    type: Object,
    default: () => ({}),
  },
  points: {
    type: Number,
    default: 0,
  },
  checkedIn: {
    type: Boolean,
    default: false,
  },
  checkingIn: {
    type: Boolean,
    default: false,
  },
  maxPoints: {
    type: Number,
    default: 100,
  },
  shortcuts: {
    type: Array,
    default: () => [],
  },
  activeShortcutKey: {
    type: String,
    default: '',
  },
})

const progressWidth = computed(() => {
  const max = Math.max(1, Number(props.maxPoints) || 100)
  const value = Math.min(max, Math.max(0, Number(props.points) || 0))
  return `${(value / max) * 100}%`
})

defineEmits(['checkin', 'shortcut'])
</script>

<style scoped>
.points-card {
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 20px;
  border-radius: 22px;
  border: 1px solid rgba(224, 232, 255, 0.96);
  background: #fff;
  box-shadow: 0 18px 40px rgba(90, 107, 162, 0.12);
}

.card-head h3 {
  color: #18233b;
  font-size: 19px;
  font-weight: 700;
  line-height: 1.2;
}

.user-row {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.avatar {
  width: 52px;
  height: 52px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  border-radius: 16px;
  background: linear-gradient(135deg, #edf3ff, #f7efff);
  color: #4f6ef7;
  font-size: 18px;
}

.user-copy {
  min-width: 0;
}

.name-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.name-row strong {
  color: #18233b;
  font-size: 17px;
  line-height: 1.3;
}

.auth-badge {
  display: inline-flex;
  align-items: center;
  min-height: 22px;
  padding: 0 8px;
  border-radius: 999px;
  background: #eef5ff;
  color: #3156cf;
  font-size: 11px;
  font-weight: 700;
}

.user-copy p {
  margin-top: 4px;
  color: #697a94;
  font-size: 13px;
  line-height: 1.55;
}

.points-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 14px 15px;
  border-radius: 18px;
  background: linear-gradient(135deg, #edf3ff 0%, #f7f2ff 100%);
}

.points-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}

.points-head span {
  color: #687a96;
  font-size: 13px;
  font-weight: 700;
}

.points-head strong {
  color: #2847bf;
  font-size: 29px;
  line-height: 1;
  font-weight: 800;
}

.progress-track {
  width: 100%;
  height: 8px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.76);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(135deg, #2f80ed 0%, #6f84ff 64%, #a78bfa 100%);
}

.checkin-btn {
  min-height: 42px;
  border: none;
  border-radius: 14px;
  background: #eef4ff;
  color: #3557d1;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
}

.checkin-btn:disabled {
  background: #edf1f7;
  color: #8b99af;
  cursor: not-allowed;
}

.shortcut-block {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.shortcut-block h4 {
  color: #51637e;
  font-size: 13px;
  font-weight: 700;
}

.shortcut-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.shortcut-btn {
  min-height: 44px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 12px;
  border: none;
  border-radius: 14px;
  background: #f4f7ff;
  color: #425472;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  text-align: left;
  transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
}

.shortcut-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 20px rgba(90, 107, 162, 0.1);
}

.shortcut-btn.active {
  background: linear-gradient(135deg, #2f80ed 0%, #6f84ff 64%, #a78bfa 100%);
  color: #fff;
  box-shadow: 0 12px 24px rgba(92, 75, 140, 0.18);
}

.shortcut-icon {
  width: 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #4e67e5;
  flex-shrink: 0;
}

.shortcut-btn.active .shortcut-icon {
  color: #fff;
}

.shortcut-label {
  flex: 1;
}
</style>
