<template>
  <aside class="profile-sidebar">
    <div class="profile-header">
      <div class="profile-avatar"><i class="fas fa-user-graduate"></i></div>
      <div class="profile-info">
        <h2>{{ summary.name }}</h2>
        <p v-if="summary.username" class="profile-username">@{{ summary.username }}</p>
        <p class="profile-major">{{ summary.major }}</p>
        <div class="profile-reputation"><i class="fas fa-star"></i><span>{{ summary.reputation }}</span></div>
      </div>
    </div>
    <nav class="profile-menu">
      <button
        v-for="item in menu"
        :key="item"
        class="profile-menu-item"
        :class="{ active: item === active }"
        type="button"
        @click="$emit('select', item)"
      >
        <i :class="iconFor(item)"></i>
        <span>{{ item }}</span>
      </button>
    </nav>
  </aside>
</template>

<script setup>
defineProps({
  summary: { type: Object, required: true },
  menu: { type: Array, required: true },
  active: { type: String, required: true },
})

defineEmits(['select'])

const iconFor = (item) => {
  if (item.includes('\u7f3a\u8d27') || item.includes('\u767b\u8bb0')) return 'fas fa-bell'
  if (item.includes('\u4e2a\u4eba')) return 'fas fa-user-circle'
  if (item.includes('\u8ba2\u5355')) return 'fas fa-shopping-cart'
  if (item.includes('\u51fa\u552e')) return 'fas fa-tag'
  if (item.includes('\u6536\u85cf')) return 'fas fa-heart'
  if (item.includes('\u8bbe\u7f6e')) return 'fas fa-cog'
  return 'fas fa-circle'
}
</script>

<style scoped>
.profile-sidebar {
  background-color: white;
  border-radius: 12px;
  box-shadow: var(--shadow-md);
  padding: 24px;
  height: fit-content;
}

.profile-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  margin-bottom: 30px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--gray-200);
}

.profile-avatar {
  width: 80px;
  height: 80px;
  background-color: var(--light-blue);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  color: var(--primary-blue);
  font-size: 32px;
}

.profile-info h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--gray-900);
  margin-bottom: 6px;
}

.profile-username {
  font-size: 13px;
  color: var(--primary-blue);
  margin-bottom: 8px;
}

.profile-major {
  font-size: 14px;
  color: var(--gray-600);
  margin-bottom: 12px;
}

.profile-reputation {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 6px 12px;
  background-color: var(--light-green);
  color: var(--secondary-green);
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.profile-menu {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.profile-menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  color: var(--gray-700);
  border-radius: 8px;
  transition: all 0.2s ease;
  border: none;
  background: transparent;
  cursor: pointer;
  text-align: left;
}

.profile-menu-item.active {
  background-color: var(--light-blue);
  color: var(--primary-blue);
  font-weight: 500;
}

.profile-menu-item i {
  width: 20px;
  text-align: center;
}
</style>
