import { nextTick, ref } from 'vue'
import {
  addFavorite as apiAddFavorite,
  checkFavorite as apiCheckFavorite,
  createBook as apiCreateBook,
  createChatSession as apiCreateChatSession,
  getChatSessions,
  getCurrentUser,
  getFavorites as apiGetFavorites,
  getMessages as apiGetMessages,
  getMyBooks,
  removeFavorite as apiRemoveFavorite,
  sendMessage as apiSendMessage,
  updateUserProfile as apiUpdateUserProfile,
} from '../services/api'
import {
  getStoredAuthUser as loadStoredAuthUser,
  setStoredAuthUser,
  clearStoredAuthUser,
} from '../utils/authStorage'

const STORAGE_PREFIX = {
  chatSessions: 'starbook_chat_sessions',
  chatMessages: 'starbook_chat_messages',
  favorites: 'starbook_favorites',
  userBooks: 'starbook_user_books',
}

const createAnonymousUser = () => ({
  id: null,
  username: '',
  email: '',
  college: '',
  grade: '',
  campus: '',
  phone: '',
  name: '请登录',
  role: 'buyer',
  avatar: null,
  reputation: 'A',
  accessToken: '',
  refreshToken: '',
  tokenType: 'Bearer',
  expiresAt: '',
  refreshExpiresAt: '',
  rememberMe: false,
  isLoggedIn: false,
})

const currentUser = ref(createAnonymousUser())
const chatSessions = ref([])
const chatMessages = ref({})
const userBooks = ref([])
const favorites = ref([])
const catalogBooks = ref([])

function loadJson(key, fallback) {
  try {
    const raw = localStorage.getItem(key)
    return raw ? JSON.parse(raw) : fallback
  } catch {
    return fallback
  }
}

function saveJson(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value))
  } catch {
    // ignore local storage errors
  }
}

function normalizeUser(user) {
  if (!user?.id) {
    return createAnonymousUser()
  }

  return {
    id: user.id,
    username: user.username || '',
    email: user.email || '',
    college: user.college || '',
    grade: user.grade || '',
    campus: user.campus || '',
    phone: user.phone || '',
    name: user.name || user.username || '用户',
    role: user.role || 'buyer',
    avatar: user.avatar || null,
    reputation: user.reputation || 'A',
    accessToken: user.accessToken || '',
    refreshToken: user.refreshToken || '',
    tokenType: user.tokenType || 'Bearer',
    expiresAt: user.expiresAt || '',
    refreshExpiresAt: user.refreshExpiresAt || '',
    rememberMe: Boolean(user.rememberMe),
    isLoggedIn: user.isLoggedIn !== false,
  }
}

function getScopedStorageKey(kind, userId = currentUser.value.id) {
  return `${STORAGE_PREFIX[kind]}_${userId || 'guest'}`
}

function hydrateLocalUserState() {
  chatSessions.value = loadJson(getScopedStorageKey('chatSessions'), [])
  chatMessages.value = loadJson(getScopedStorageKey('chatMessages'), {})
  userBooks.value = loadJson(getScopedStorageKey('userBooks'), [])
  favorites.value = currentUser.value.id ? loadJson(getScopedStorageKey('favorites'), []) : []
}

function persistLocalUserState() {
  saveJson(getScopedStorageKey('chatSessions'), chatSessions.value)
  saveJson(getScopedStorageKey('chatMessages'), chatMessages.value)
  saveJson(getScopedStorageKey('userBooks'), userBooks.value)
  saveJson(getScopedStorageKey('favorites'), favorites.value)
}

async function fetchChatSessionsState({ silent = false } = {}) {
  if (!currentUser.value.id) {
    chatSessions.value = []
    persistLocalUserState()
    return []
  }

  try {
    const sessionsRes = await getChatSessions()
    if (sessionsRes?.code === 200 && Array.isArray(sessionsRes.data)) {
      const localSessionMap = new Map(chatSessions.value.map((session) => [session.id, session]))
      chatSessions.value = sessionsRes.data.map((session) => ({
        ...(localSessionMap.get(session.id) || {}),
        ...session,
        unread: Number(session.unread || 0),
      }))
      persistLocalUserState()
    }
  } catch (error) {
    console.error('加载聊天会话失败:', error)
    if (!silent) throw error
  }

  return chatSessions.value
}

async function setAuthenticatedUser(user) {
  const nextUser = normalizeUser({ ...user, isLoggedIn: true })
  currentUser.value = nextUser
  setStoredAuthUser(nextUser)
  hydrateLocalUserState()
  await refreshRemoteUserState()
  return nextUser
}

async function clearAuthenticatedUser() {
  clearStoredAuthUser()
  currentUser.value = createAnonymousUser()
  hydrateLocalUserState()
}

async function refreshRemoteUserState() {
  if (!currentUser.value.id) return

  try {
    const userRes = await getCurrentUser()
    if (userRes?.code === 200 && userRes.data) {
      currentUser.value = normalizeUser({
        ...loadStoredAuthUser(),
        ...currentUser.value,
        ...userRes.data,
        isLoggedIn: true,
      })
      setStoredAuthUser(currentUser.value)
    }
  } catch (error) {
    console.error('加载当前用户失败:', error)
  }

  try {
    const booksRes = await getMyBooks()
    if (booksRes?.code === 200 && booksRes.data) {
      userBooks.value = booksRes.data.filter((book) => book.status !== 'draft')
    }
  } catch (error) {
    console.error('加载用户书籍失败:', error)
  }

  try {
    const favoritesRes = await apiGetFavorites()
    if (favoritesRes?.code === 200 && favoritesRes.data) {
      favorites.value = favoritesRes.data
    }
  } catch (error) {
    console.error('加载收藏失败:', error)
  }

  try {
    const sessionsRes = await getChatSessions()
    if (sessionsRes?.code === 200 && sessionsRes.data) {
      chatSessions.value = sessionsRes.data
    }
  } catch (error) {
    console.error('加载聊天会话失败:', error)
  }

  persistLocalUserState()
}

async function initGlobalState() {
  currentUser.value = normalizeUser(loadStoredAuthUser())
  hydrateLocalUserState()

  if (currentUser.value.id) {
    await refreshRemoteUserState()
  }
}

function getCurrentTime() {
  const now = new Date()
  const hours = now.getHours().toString().padStart(2, '0')
  const minutes = now.getMinutes().toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2)
}

async function getOrCreateSession(bookId, sellerId, counterpartName, bookTitle, options = {}) {
  const currentUserId = currentUser.value.id
  const requestedBuyerId = options?.buyerId ? String(options.buyerId) : ''
  const isSellerInitiated = String(sellerId) === String(currentUserId) && Boolean(requestedBuyerId)
  const buyerId = isSellerInitiated ? requestedBuyerId : currentUserId
  const sessionId = `session_${bookId}_${sellerId}_${buyerId}`
  let session = chatSessions.value.find((item) => item.id === sessionId)

  if (!session) {
    try {
      const payload = { bookId, sellerId, bookTitle }
      if (requestedBuyerId) {
        payload.buyerId = requestedBuyerId
      }

      const res = await apiCreateChatSession(payload)
      if (res?.code === 200 && res.data) {
        session = {
          ...res.data,
          name: res.data.name || counterpartName,
          time: res.data.time || getCurrentTime(),
          preview: res.data.preview || '',
          unread: res.data.unread || 0,
        }
      }
    } catch (error) {
      console.error('创建会话失败:', error)
    }
  }

  if (!session) {
    session = {
      id: sessionId,
      bookId,
      sellerId,
      buyerId,
      name: counterpartName,
      bookTitle,
      time: getCurrentTime(),
      preview: '',
      unread: 0,
      role: isSellerInitiated ? 'buyer' : 'seller',
    }
  }

  const exists = chatSessions.value.find((item) => item.id === session.id)
  if (!exists) {
    chatSessions.value.unshift(session)
  }
  if (!chatMessages.value[session.id]) {
    chatMessages.value[session.id] = []
  }

  persistLocalUserState()
  return session
}

async function sendMessage(sessionId, text) {
  if (!chatMessages.value[sessionId]) {
    chatMessages.value[sessionId] = []
  }

  const currentRole = currentUser.value.role || 'buyer'
  const currentUserId = currentUser.value.id || 'unknown'

  let message = {
    id: generateId(),
    type: 'sent',
    text,
    time: getCurrentTime(),
    senderRole: currentRole,
    senderId: currentUserId,
    isSystem: false,
  }

  try {
    const res = await apiSendMessage({ sessionId, text })
    if (res?.code === 200 && res.data) {
      message = {
        id: res.data.id,
        type: res.data.senderId === currentUserId ? 'sent' : 'received',
        text: res.data.text,
        time: res.data.time,
        senderRole: res.data.senderRole,
        senderId: res.data.senderId,
        isSystem: res.data.isSystem,
      }
    }
  } catch (error) {
    console.error('发送消息失败:', error)
  }

  chatMessages.value[sessionId].push(message)

  const sessionIndex = chatSessions.value.findIndex((item) => item.id === sessionId)
  if (sessionIndex >= 0) {
    const nextSession = {
      ...chatSessions.value[sessionIndex],
      preview: text,
      time: message.time || getCurrentTime(),
    }
    chatSessions.value.splice(sessionIndex, 1)
    chatSessions.value.unshift(nextSession)
  }

  persistLocalUserState()
  return message
}

async function getSessionMessages(sessionId) {
  try {
    const res = await apiGetMessages(sessionId)
    if (res?.code === 200 && res.data) {
      const messages = res.data.map((msg) => ({
        id: msg.id,
        type: msg.senderId === currentUser.value.id ? 'sent' : 'received',
        text: msg.text,
        time: msg.time,
        senderRole: msg.senderRole,
        senderId: msg.senderId,
        isSystem: msg.isSystem,
      }))

      chatMessages.value[sessionId] = messages

      const sessionIndex = chatSessions.value.findIndex((item) => item.id === sessionId)
      if (sessionIndex >= 0) {
        chatSessions.value[sessionIndex] = {
          ...chatSessions.value[sessionIndex],
          unread: 0,
        }
      }

      persistLocalUserState()
      return messages
    }
  } catch (error) {
    console.error('加载会话消息失败:', error)
  }

  return chatMessages.value[sessionId] || []
}

async function addUserBook(bookData) {
  try {
    const res = await apiCreateBook(bookData)
    if (res?.code === 200 && res.data) {
      userBooks.value.unshift(res.data)
      persistLocalUserState()
      return res.data
    }
  } catch (error) {
    console.error('发布书籍失败:', error)
    throw error
  }

  return null
}

async function updateCurrentUserProfile(profileData) {
  const res = await apiUpdateUserProfile(profileData)
  if (res?.code === 200 && res.data) {
    currentUser.value = normalizeUser({
      ...loadStoredAuthUser(),
      ...currentUser.value,
      ...res.data,
      isLoggedIn: true,
    })
    setStoredAuthUser(currentUser.value)
    return currentUser.value
  }

  return null
}

async function toggleFavorite(bookId) {
  if (!currentUser.value?.id) {
    throw new Error('请先登录后再收藏书籍')
  }

  const index = favorites.value.indexOf(bookId)
  const isFavoritedNow = index > -1

  try {
    if (isFavoritedNow) {
      await apiRemoveFavorite(bookId)
      favorites.value.splice(index, 1)
    } else {
      await apiAddFavorite(bookId)
      favorites.value.push(bookId)
    }
  } catch (error) {
    console.error('切换收藏失败:', error)
    throw error
  }

  persistLocalUserState()
  return !isFavoritedNow
}

async function isFavorited(bookId) {
  if (!currentUser.value?.id) {
    return false
  }

  if (favorites.value.includes(bookId)) {
    return true
  }

  try {
    const res = await apiCheckFavorite(bookId)
    if (res?.code === 200 && res.data) {
      return res.data.isFavorited
    }
  } catch (error) {
    console.error('检查收藏状态失败:', error)
  }

  return false
}

function getFavorites() {
  return favorites.value
}

function scrollChatToBottom(containerRef) {
  nextTick(() => {
    if (containerRef?.value) {
      containerRef.value.scrollTop = containerRef.value.scrollHeight
    }
  })
}

export const useGlobalState = () => ({
  currentUser,
  chatSessions,
  chatMessages,
  userBooks,
  favorites,
  catalogBooks,
  initGlobalState,
  refreshRemoteUserState,
  fetchChatSessionsState,
  setAuthenticatedUser,
  clearAuthenticatedUser,
  getOrCreateSession,
  sendMessage,
  getSessionMessages,
  addUserBook,
  updateCurrentUserProfile,
  toggleFavorite,
  isFavorited,
  getFavorites,
  scrollChatToBottom,
  generateId,
  getCurrentTime,
})
