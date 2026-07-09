<template>
  <div class="messages-page">
    <div class="chat-container">
      <ConversationList
        :title="messages.sidebarTitle"
        :conversations="mergedConversations"
        :active-id="activeId"
        @select="handleSelectConversation"
      />
      <ChatPanel
        v-if="hasConversations"
        :conversation="activeConversation"
        :messages="messages"
        :current-user="currentUser"
        @send-message="handleSendMessage"
      />
      <section v-else class="empty-state">
        <h3>{{ emptyState.title }}</h3>
        <p>{{ emptyState.description }}</p>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import ChatPanel from '../components/messages/ChatPanel.vue'
import ConversationList from '../components/messages/ConversationList.vue'
import { useGlobalState } from '../composables/useGlobalState'

const props = defineProps({
  data: { type: Object, default: () => ({}) },
})

const route = useRoute()
const {
  currentUser,
  chatMessages,
  chatSessions,
  getSessionMessages,
  sendMessage,
} = useGlobalState()

const activeId = ref('')
const pollTimer = ref(null)
const messages = computed(() => props.data.messages ?? {})
const emptyState = computed(() => ({
  title: messages.value.emptyTitle || '还没有聊天记录',
  description: messages.value.emptyDescription || '联系卖家或买家后，这里会显示你们的真实对话。',
}))

const mergedConversations = computed(() =>
  chatSessions.value.map((session) => ({
    id: session.id,
    name: session.name,
    time: session.time,
    preview: session.preview || `关于《${session.bookTitle}》的咨询`,
    unread: session.unread || 0,
    role: session.role || 'seller',
    isSystemSession: Boolean(session.isSystemSession),
    messages: chatMessages.value[session.id] || [],
    bookTitle: session.bookTitle,
    bookId: session.bookId,
    buyerId: session.buyerId,
    sellerId: session.sellerId,
    price: session.price,
  })),
)

const hasConversations = computed(() => mergedConversations.value.length > 0)

const activeConversation = computed(() => {
  const conversation = mergedConversations.value.find((item) => item.id === activeId.value)
  return conversation || { id: '', name: '', messages: [], isSystemSession: false }
})

const loadConversationMessages = async (sessionId) => {
  if (!sessionId) return
  await getSessionMessages(sessionId)
}

const handleSelectConversation = async (sessionId) => {
  activeId.value = sessionId
  await loadConversationMessages(sessionId)
}

const stopPolling = () => {
  if (pollTimer.value) {
    clearInterval(pollTimer.value)
    pollTimer.value = null
  }
}

const startPolling = () => {
  stopPolling()
  if (!activeId.value) return
  pollTimer.value = setInterval(() => {
    getSessionMessages(activeId.value)
  }, 15000)
}

const handleVisibilityChange = () => {
  if (document.hidden) {
    stopPolling()
  } else if (activeId.value) {
    getSessionMessages(activeId.value).then(() => startPolling())
  }
}

const handleSendMessage = (text) => {
  if (!text.trim() || !activeId.value) return
  sendMessage(activeId.value, text)
}

onMounted(async () => {
  const sessionId = route.query.sessionId
  if (sessionId) {
    activeId.value = String(sessionId)
    await loadConversationMessages(activeId.value)
  }
  document.addEventListener('visibilitychange', handleVisibilityChange)
})

onUnmounted(() => {
  stopPolling()
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})

watch(
  () => route.query.sessionId,
  async (sessionId) => {
    if (!sessionId) return
    activeId.value = String(sessionId)
    await loadConversationMessages(activeId.value)
  },
)

watch(
  () => mergedConversations.value,
  async (list) => {
    if (list.length === 0) {
      activeId.value = ''
      return
    }

    const hasActiveConversation = list.some((item) => item.id === activeId.value)
    if (!hasActiveConversation) {
      activeId.value = list[0].id
      await loadConversationMessages(list[0].id)
    }
  },
  { immediate: true },
)

watch(
  () => activeId.value,
  (newId) => {
    if (newId) {
      startPolling()
    } else {
      stopPolling()
    }
  },
)
</script>

<style scoped>
.messages-page {
  display: flex;
  flex: 1;
  height: 100%;
  min-height: 0;
  padding: 8px 28px 28px 28px;
  overflow: hidden;
}

.chat-container {
  flex: 1;
  display: grid;
  grid-template-columns: 336px minmax(0, 1fr);
  gap: 0;
  height: 100%;
  max-height: 100%;
  min-height: 0;
  border-radius: 12px;
  overflow: hidden;
}

.empty-state {
  display: grid;
  place-content: center;
  gap: 12px;
  padding: 32px;
  text-align: center;
  background:
    radial-gradient(circle at top, rgba(59, 130, 246, 0.08), transparent 45%),
    linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
}

.empty-state h3 {
  margin: 0;
  font-size: 22px;
  color: var(--gray-900);
}

.empty-state p {
  margin: 0;
  max-width: 360px;
  color: var(--gray-600);
  line-height: 1.6;
}

@media (max-width: 1180px) {
  .chat-container {
    grid-template-columns: 304px minmax(0, 1fr);
  }
}

@media (max-width: 768px) {
  .messages-page {
    padding: 8px 16px 16px;
  }

  .chat-container {
    grid-template-columns: 1fr;
  }
}
</style>
