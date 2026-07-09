const STORAGE_PREFIX = 'starbook_smart_schedule'
export const SMART_SCHEDULE_UPDATED_EVENT = 'starbook-smart-schedule-updated'

function getStorageKey(userId) {
  return `${STORAGE_PREFIX}_${userId}`
}

export function normalizeCourseName(value) {
  return String(value || '')
    .trim()
    .toLocaleLowerCase('zh-CN')
    .replace(/[\s,，。.!！?？、:：;；()（）[\]【】{}《》<>·•_-]+/g, '')
}

export function loadSmartSchedule(userId) {
  if (!userId) return null

  try {
    const raw = localStorage.getItem(getStorageKey(userId))
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function saveSmartSchedule(userId, payload) {
  if (!userId || !payload || !Array.isArray(payload.courses)) return

  try {
    localStorage.setItem(getStorageKey(userId), JSON.stringify(payload))
    window.dispatchEvent(new CustomEvent(SMART_SCHEDULE_UPDATED_EVENT, { detail: { userId, payload } }))
  } catch {
    // Ignore unavailable or full local storage.
  }
}

export function clearSmartSchedule(userId) {
  if (!userId) return

  try {
    localStorage.removeItem(getStorageKey(userId))
    window.dispatchEvent(new CustomEvent(SMART_SCHEDULE_UPDATED_EVENT, { detail: { userId, payload: null } }))
  } catch {
    // Ignore unavailable local storage.
  }
}
