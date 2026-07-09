<template>
  <aside class="chat-sidebar">
    <div class="chat-sidebar-header">
      <h3>{{ title }}</h3>
    </div>
    <div class="conversation-list">
      <button
        v-for="conversation in conversations"
        :key="conversation.id"
        class="conversation"
        :class="{ active: conversation.id === activeId }"
        type="button"
        @click="$emit('select', conversation.id)"
      >
        <div class="conversation-avatar"><i class="fas fa-user"></i></div>
        <div class="conversation-info">
          <div class="conversation-name">
            <span>
              {{ conversation.name }}
              <small v-if="conversation.role" class="conversation-role">
                {{ roleLabel(conversation.role) }}
              </small>
              <span v-if="conversation.unread" class="unread-badge">{{ conversation.unread }}</span>
            </span>
            <span class="conversation-time">{{ conversation.time }}</span>
          </div>
          <div class="conversation-preview">{{ conversation.preview }}</div>
        </div>
      </button>
    </div>
  </aside>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  conversations: { type: Array, required: true },
  activeId: { type: String, default: '' },
})

defineEmits(['select'])

function roleLabel(role) {
  if (role === 'system') return '系统'
  return role === 'seller' ? '卖家' : '买家'
}
</script>

<style scoped>
.chat-sidebar {
  min-width: 0;
  min-height: 0;
  border-right: 1px solid var(--gray-200);
  display: flex;
  flex-direction: column;
}

.chat-sidebar-header {
  flex-shrink: 0;
  padding: 24px 26px;
  border-bottom: 1px solid var(--gray-200);
}

.chat-sidebar-header h3 {
  margin: 0;
  font-size: 17px;
  font-weight: 700;
  color: var(--gray-900);
}

.conversation-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

.conversation {
  width: 100%;
  display: flex;
  gap: 14px;
  padding: 20px 22px;
  border: 0;
  border-bottom: 1px solid var(--gray-100);
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
  background: transparent;
}

.conversation:hover,
.conversation.active {
  background: var(--light-blue);
}

.conversation-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-blue) 0%, #3b82f6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
  font-size: 22px;
}

.conversation-info {
  flex: 1;
  min-width: 0;
}

.conversation-name {
  font-weight: 700;
  font-size: 16px;
  color: var(--gray-900);
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.conversation-time {
  flex-shrink: 0;
  font-size: 13px;
  color: var(--gray-400);
  font-weight: 500;
}

.conversation-preview {
  font-size: 14px;
  color: var(--gray-500);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conversation-role {
  margin-left: 8px;
  font-size: 12px;
  color: var(--gray-400);
}

.unread-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 22px;
  height: 22px;
  padding: 0 8px;
  margin-left: 8px;
  border-radius: 999px;
  background: #ef4444;
  color: white;
  font-size: 12px;
}
</style>
