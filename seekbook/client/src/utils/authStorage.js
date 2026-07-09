const AUTH_USER_STORAGE_KEY = 'starbook_auth_user'

function getStorage(type) {
  if (typeof window === 'undefined') return null
  return type === 'local' ? window.localStorage : window.sessionStorage
}

function readJson(storage) {
  if (!storage) return null

  try {
    return JSON.parse(storage.getItem(AUTH_USER_STORAGE_KEY) || 'null')
  } catch {
    return null
  }
}

function writeJson(storage, value) {
  if (!storage) return

  try {
    storage.setItem(AUTH_USER_STORAGE_KEY, JSON.stringify(value))
  } catch {
    // ignore storage errors
  }
}

function removeKey(storage) {
  if (!storage) return

  try {
    storage.removeItem(AUTH_USER_STORAGE_KEY)
  } catch {
    // ignore storage errors
  }
}

export function getStoredAuthUser() {
  const sessionValue = readJson(getStorage('session'))
  if (sessionValue?.id) {
    return sessionValue
  }

  const localValue = readJson(getStorage('local'))
  if (localValue?.id) {
    writeJson(getStorage('session'), localValue)
    return localValue
  }

  return null
}

export function setStoredAuthUser(authUser) {
  const nextUser = authUser || null
  if (!nextUser) {
    clearStoredAuthUser()
    return
  }

  writeJson(getStorage('session'), nextUser)

  if (nextUser.rememberMe) {
    writeJson(getStorage('local'), nextUser)
  } else {
    removeKey(getStorage('local'))
  }
}

export function clearStoredAuthUser() {
  removeKey(getStorage('session'))
  removeKey(getStorage('local'))
}
