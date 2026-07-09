import { clearStoredAuthUser, getStoredAuthUser, setStoredAuthUser } from '../utils/authStorage'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '')
const AUTH_INVALIDATED_EVENT = 'starbook-auth-invalidated'
const APP_FEEDBACK_EVENT = 'starbook-app-feedback'
const RETRYABLE_STATUS_CODES = new Set([502, 503, 504])
const AUTH_INVALIDATION_CODES = new Set(['AUTH_REQUIRED', 'TOKEN_INVALID', 'TOKEN_REVOKED', 'USER_NOT_FOUND'])
const TOKEN_REFRESHABLE_CODES = new Set(['TOKEN_EXPIRED'])
const REFRESH_ENDPOINT = '/auth/refresh'

let refreshPromise = null

class ApiError extends Error {
  constructor(message, { code = '', status = 500, details = null } = {}) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.status = status
    this.details = details
  }
}

function buildApiUrl(path = '') {
  if (path.startsWith('http')) return path
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${API_BASE_URL}${normalizedPath}`
}

function getAuthHeaders() {
  const authUser = getStoredAuthUser()
  const accessToken = authUser?.accessToken
  if (!accessToken) return {}
  return {
    Authorization: `${authUser?.tokenType || 'Bearer'} ${accessToken}`,
  }
}

function dispatchAuthInvalidated(errorPayload) {
  if (typeof window === 'undefined') return
  window.dispatchEvent(new CustomEvent(AUTH_INVALIDATED_EVENT, { detail: errorPayload }))
}

function dispatchAppFeedback(feedbackPayload) {
  if (typeof window === 'undefined') return
  window.dispatchEvent(new CustomEvent(APP_FEEDBACK_EVENT, { detail: feedbackPayload }))
}

function delay(ms) {
  return new Promise((resolve) => window.setTimeout(resolve, ms))
}

function shouldTryRefresh(errorCode, options = {}, fullUrl = '') {
  const authUser = getStoredAuthUser()
  if (!TOKEN_REFRESHABLE_CODES.has(errorCode)) return false
  if (options._skipAuthRefresh) return false
  if (!authUser?.refreshToken) return false
  return !fullUrl.endsWith(REFRESH_ENDPOINT)
}

async function parseResponseData(response) {
  const rawText = await response.text()
  if (!rawText) return null

  try {
    return JSON.parse(rawText)
  } catch {
    throw new ApiError('后端返回了无法解析的响应，请确认服务已正确启动。', {
      status: response.status,
      code: 'INVALID_RESPONSE',
    })
  }
}

function updateStoredTokens(nextAuthData) {
  const currentUser = getStoredAuthUser()
  const mergedUser = {
    ...currentUser,
    ...nextAuthData,
    isLoggedIn: true,
  }
  setStoredAuthUser(mergedUser)
  return mergedUser
}

async function fetchWithRetry(url, options, maxAttempts = 2) {
  let lastError = null

  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    try {
      const response = await fetch(url, options)
      if (RETRYABLE_STATUS_CODES.has(response.status) && attempt < maxAttempts) {
        await delay(450)
        continue
      }
      return response
    } catch (error) {
      lastError = error
      if (attempt < maxAttempts) {
        await delay(450)
        continue
      }
    }
  }

  throw lastError || new Error('后端服务暂时不可用，请稍后重试。')
}

async function refreshAccessToken() {
  if (refreshPromise) return refreshPromise

  refreshPromise = (async () => {
    const authUser = getStoredAuthUser()
    if (!authUser?.refreshToken) {
      throw new ApiError('缺少刷新凭证，请重新登录。', { status: 401, code: 'REFRESH_TOKEN_REQUIRED' })
    }

    let response
    try {
      response = await fetchWithRetry(
        buildApiUrl(REFRESH_ENDPOINT),
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ refreshToken: authUser.refreshToken }),
        },
        2,
      )
    } catch {
      throw new ApiError('后端服务暂时不可用，请稍后重试。', { status: 503, code: 'NETWORK_UNAVAILABLE' })
    }

    const data = await parseResponseData(response)
    if (!response.ok) {
      const errorCode = data?.error || (typeof data?.code === 'string' ? data.code : '') || 'TOKEN_EXPIRED'
      const errorMessage = data?.message || `请求失败，状态码：${response.status}`
      clearStoredAuthUser()
      dispatchAuthInvalidated({ code: errorCode, message: errorMessage })
      throw new ApiError(errorMessage, {
        code: errorCode,
        status: response.status,
        details: data?.details || null,
      })
    }

    return updateStoredTokens(data?.data || {})
  })()

  try {
    return await refreshPromise
  } finally {
    refreshPromise = null
  }
}

async function request(url, options = {}) {
  const fullUrl = buildApiUrl(url)
  const authHeaders = getAuthHeaders()
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders,
    },
  }

  let response
  try {
    response = await fetchWithRetry(
      fullUrl,
      {
        ...defaultOptions,
        ...options,
        headers: {
          ...defaultOptions.headers,
          ...options.headers,
        },
      },
      2,
    )
  } catch {
    throw new ApiError('后端服务暂时不可用，请确认后端已启动或稍后重试。', {
      status: 503,
      code: 'NETWORK_UNAVAILABLE',
    })
  }

  const data = await parseResponseData(response)

  if (!response.ok) {
    if (RETRYABLE_STATUS_CODES.has(response.status)) {
      throw new ApiError('后端服务暂时不可用，请确认后端已启动或稍后重试。', {
        status: response.status,
        code: 'BACKEND_UNAVAILABLE',
      })
    }

    const errorCode = data?.error || (typeof data?.code === 'string' ? data.code : '') || (response.status === 403 ? 'FORBIDDEN' : '')
    const errorMessage = data?.message || `请求失败，状态码：${response.status}`

    if (shouldTryRefresh(errorCode, options, fullUrl)) {
      await refreshAccessToken()
      return request(url, { ...options, _skipAuthRefresh: true })
    }

    const apiError = new ApiError(errorMessage, {
      code: errorCode,
      status: response.status,
      details: data?.details || null,
    })

    if (AUTH_INVALIDATION_CODES.has(errorCode) || TOKEN_REFRESHABLE_CODES.has(errorCode)) {
      clearStoredAuthUser()
      dispatchAuthInvalidated({ code: errorCode, message: errorMessage })
    }

    if (errorCode === 'FORBIDDEN') {
      dispatchAppFeedback({ type: 'forbidden', code: errorCode, message: errorMessage })
    }

    throw apiError
  }

  if (!data) {
    throw new ApiError('后端返回了空响应，请确认服务已正确启动。', {
      status: response.status,
      code: 'EMPTY_RESPONSE',
    })
  }

  return data
}

export function registerUser(userData) {
  return request('/auth/register', {
    method: 'POST',
    body: JSON.stringify(userData),
  })
}

export function loginByUsername(username, password, rememberMe = false) {
  return request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password, rememberMe }),
  })
}

export function logoutUser() {
  const refreshToken = getStoredAuthUser()?.refreshToken || ''
  return request('/auth/logout', {
    _skipAuthRefresh: true,
    method: 'POST',
    body: JSON.stringify({ refreshToken }),
  })
}

export function getCurrentUser() {
  return request('/user/current')
}

export function updateUserProfile(profileData) {
  return request('/user/profile', {
    method: 'PUT',
    body: JSON.stringify(profileData),
  })
}

export function getBooks(params = {}) {
  const queryString = new URLSearchParams(params).toString()
  return request(`/books?${queryString}`)
}

export function getBookDetail(bookId) {
  return request(`/books/${bookId}`)
}

export function createBook(bookData) {
  return request('/books', {
    method: 'POST',
    body: JSON.stringify(bookData),
  })
}

export function updateBook(bookId, bookData) {
  return request(`/books/${bookId}`, {
    method: 'PUT',
    body: JSON.stringify(bookData),
  })
}

export function deleteBook(bookId) {
  return request(`/books/${bookId}`, {
    method: 'DELETE',
  })
}

export function getMyBooks() {
  return request('/books/my')
}

export function searchBooksForNotes(keyword) {
  return request(`/books?keyword=${encodeURIComponent(keyword)}`)
}

export function recognizeBookByISBN(imageFile) {
  const formData = new FormData()
  formData.append('image', imageFile)

  return fetch(buildApiUrl('/books/scan'), {
    method: 'POST',
    body: formData,
  }).then((res) => res.json())
}

export function getFavorites() {
  return request('/favorites')
}

export function addFavorite(bookId) {
  return request('/favorites', {
    method: 'POST',
    body: JSON.stringify({ bookId }),
  })
}

export function removeFavorite(bookId) {
  return request(`/favorites/${bookId}`, {
    method: 'DELETE',
  })
}

export function checkFavorite(bookId) {
  return request(`/favorites/${bookId}/check`)
}

export function getChatSessions() {
  return request('/chat/sessions')
}

export function createChatSession(sessionData) {
  return request('/chat/sessions', {
    method: 'POST',
    body: JSON.stringify(sessionData),
  })
}

export function getMessages(sessionId) {
  return request(`/chat/sessions/${sessionId}/messages`)
}

export function sendMessage(messageData) {
  return request('/chat/messages', {
    method: 'POST',
    body: JSON.stringify(messageData),
  })
}

export function getOrders(type = 'all') {
  return request(`/orders?type=${type}`)
}

export function getShortageRegistrations() {
  return request('/shortage-registrations')
}

export function createShortageRegistration(registrationData) {
  return request('/shortage-registrations', {
    method: 'POST',
    body: JSON.stringify(registrationData),
  })
}

export function deleteShortageRegistration(registrationId) {
  return request(`/shortage-registrations/${registrationId}`, {
    method: 'DELETE',
  })
}

export function getOrdersByBookId(bookId) {
  return request(`/orders?book_id=${bookId}`)
}

export function createOrder(orderData) {
  return request('/orders', {
    method: 'POST',
    body: JSON.stringify(orderData),
  })
}

export function getOrderDetail(orderId) {
  return request(`/orders/${orderId}`)
}

export function updateOrderStatus(orderId, status) {
  return request(`/orders/${orderId}/status`, {
    method: 'PUT',
    body: JSON.stringify({ status }),
  })
}

export function confirmMeet(orderId, meetTime, meetPlace) {
  return request(`/orders/${orderId}/confirm_meet`, {
    method: 'POST',
    body: JSON.stringify({ meetTime, meetPlace }),
  })
}

export function completeOrder(orderId) {
  return request(`/orders/${orderId}/complete`, {
    method: 'POST',
  })
}

export function cancelOrder(orderId) {
  return request(`/orders/${orderId}/cancel`, {
    method: 'POST',
  })
}

export function getNotes() {
  return request('/notes')
}

export function createNote(noteData) {
  return request('/notes', {
    method: 'POST',
    body: JSON.stringify(noteData),
  })
}

export function uploadFile(file) {
  const formData = new FormData()
  formData.append('file', file)

  return fetch(buildApiUrl('/upload'), {
    method: 'POST',
    body: formData,
  }).then((res) => res.json())
}

export function uploadImage(file) {
  const formData = new FormData()
  formData.append('file', file)

  return fetch(buildApiUrl('/upload/image'), {
    method: 'POST',
    body: formData,
  }).then((res) => res.json())
}

export function parseScheduleFile(file) {
  const formData = new FormData()
  formData.append('file', file)

  return fetch(buildApiUrl('/schedule/parse'), {
    method: 'POST',
    body: formData,
  }).then((res) => res.json())
}

export function submitManualCourses(courses) {
  return request('/schedule/manual', {
    method: 'POST',
    body: JSON.stringify({ courses }),
  })
}

export function getCommunityNotes() {
  return request('/community/notes')
}

export function createCommunityNote(noteData) {
  return request('/community/notes', {
    method: 'POST',
    body: JSON.stringify(noteData),
  })
}

export function getNoteComments(noteId) {
  return request(`/notes/${noteId}/comments`)
}

export function createNoteComment(commentData) {
  return request('/notes/comment', {
    method: 'POST',
    body: JSON.stringify(commentData),
  })
}

export function getKnowledgeMaterials(params = {}) {
  const queryString = new URLSearchParams(params).toString()
  return request(`/knowledge/materials${queryString ? `?${queryString}` : ''}`)
}

export function createKnowledgeMaterial(materialData) {
  return request('/knowledge/materials', {
    method: 'POST',
    body: JSON.stringify(materialData),
  })
}

export function deleteKnowledgeMaterial(materialId) {
  return request(`/knowledge/materials/${materialId}`, {
    method: 'DELETE',
  })
}

export function downloadMaterial(id) {
  return request(`/knowledge/materials/${id}/download`, {
    method: 'POST',
  })
}

export function toggleKnowledgeMaterialLike(materialId) {
  return request(`/knowledge/materials/${materialId}/like`, {
    method: 'POST',
  })
}

export function getKnowledgeRanks() {
  return request('/knowledge/ranks')
}

export function getKnowledgeOverview() {
  return request('/knowledge/me/overview')
}

export function getMyKnowledgeUploads(params = {}) {
  const queryString = new URLSearchParams(params).toString()
  return request(`/knowledge/me/uploads${queryString ? `?${queryString}` : ''}`)
}

export function getMyKnowledgeDiscussions(params = {}) {
  const queryString = new URLSearchParams(params).toString()
  return request(`/knowledge/me/discussions${queryString ? `?${queryString}` : ''}`)
}

export function getMyKnowledgeFavorites(params = {}) {
  const queryString = new URLSearchParams(params).toString()
  return request(`/knowledge/me/favorites${queryString ? `?${queryString}` : ''}`)
}

export function getMyKnowledgeRedeems(params = {}) {
  const queryString = new URLSearchParams(params).toString()
  return request(`/knowledge/me/redeems${queryString ? `?${queryString}` : ''}`)
}

export function getKnowledgeDiscussions(params = {}) {
  const queryString = new URLSearchParams(params).toString()
  return request(`/knowledge/discussions${queryString ? `?${queryString}` : ''}`)
}

export function createKnowledgeDiscussion(discussionData) {
  return request('/knowledge/discussions', {
    method: 'POST',
    body: JSON.stringify(discussionData),
  })
}

export function deleteKnowledgeDiscussion(discussionId) {
  return request(`/knowledge/discussions/${discussionId}`, {
    method: 'DELETE',
  })
}

export function createKnowledgeComment(commentData) {
  return request('/knowledge/comments', {
    method: 'POST',
    body: JSON.stringify(commentData),
  })
}

export function deleteKnowledgeComment(commentId) {
  return request(`/knowledge/comments/${commentId}`, {
    method: 'DELETE',
  })
}

export function toggleKnowledgeFavorite(materialId) {
  return request(`/knowledge/materials/${materialId}/favorite`, {
    method: 'POST',
  })
}

export function toggleKnowledgeDiscussionLike(discussionId) {
  return request(`/knowledge/discussions/${discussionId}/like`, {
    method: 'POST',
  })
}

export function getKnowledgePoints() {
  return request('/knowledge/points')
}

export function checkinKnowledge() {
  return request('/knowledge/checkin', {
    method: 'POST',
  })
}

export function uploadTimetableFile(file) {
  const formData = new FormData()
  formData.append('file', file)

  return fetch(buildApiUrl('/timetable/upload-file'), {
    method: 'POST',
    body: formData,
  }).then((res) => res.json())
}

export function getCatalogData(params = {}) {
  const queryString = new URLSearchParams(params).toString()
  return request(`/data/catalog${queryString ? `?${queryString}` : ''}`)
}

export function initDatabase() {
  return request('/init', {
    method: 'POST',
  })
}

export function rateOrder(orderId, rating, comment) {
  return request(`/orders/${orderId}/rate`, {
    method: 'POST',
    body: JSON.stringify({ rating, comment }),
  })
}

export function getDrafts() {
  return request('/books/drafts')
}

export function saveDraft(draftData) {
  return request('/books/drafts', {
    method: 'POST',
    body: JSON.stringify(draftData),
  })
}

export function deleteDraft(draftId) {
  return request(`/books/drafts/${draftId}`, {
    method: 'DELETE',
  })
}

export function getUserStats() {
  return request('/user/stats')
}

export function getCreditAudits() {
  return request('/user/credit-audits')
}

export function changePassword(currentPassword, newPassword) {
  return request('/user/password', {
    method: 'PUT',
    body: JSON.stringify({ currentPassword, newPassword }),
  })
}

export function updateAvatar(avatar) {
  return request('/user/avatar', {
    method: 'PUT',
    body: JSON.stringify({ avatar }),
  })
}

export function generateMockSchedule() {
  return request('/schedule/mock', {
    method: 'POST',
  })
}

export function getNotifications() {
  return request('/notifications')
}

export function healthCheck() {
  return request('/health')
}
