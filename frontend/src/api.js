const jsonHeaders = {
  'Content-Type': 'application/json',
}

const messageMap = {
  'No active account found with the given credentials': '用户名或密码错误。',
  'Authentication credentials were not provided.': '请先登录后再操作。',
  'Given token not valid for any token type': '登录状态已失效，请重新登录。',
  'Token is invalid or expired': '登录状态已失效，请重新登录。',
  'Not found.': '请求的内容不存在。',
  'You do not have permission to perform this action.': '你没有权限执行此操作。',
  'Method "GET" not allowed.': '当前操作不支持。',
  'Method "POST" not allowed.': '当前操作不支持。',
  'Method "PATCH" not allowed.': '当前操作不支持。',
  'Method "DELETE" not allowed.': '当前操作不支持。',
  'Network request failed': '网络连接失败，请检查服务是否已启动。',
}

export function showToast(message, type = 'error') {
  const detail = { message, type }
  window.__blogToast = detail
  window.dispatchEvent(new CustomEvent('blog-toast', { detail }))
}

function friendlyMessage(message) {
  const text = String(message || '').trim()
  if (!text) return '操作失败，请稍后重试。'
  if (messageMap[text]) return messageMap[text]
  if (/^This field is required\.$/i.test(text)) return '请填写完整信息。'
  if (/^This field may not be blank\.$/i.test(text)) return '内容不能为空。'
  if (/^Ensure this field has no more than (\d+) characters\.$/i.test(text)) {
    return text.replace(/^Ensure this field has no more than (\d+) characters\.$/i, '内容不能超过 $1 个字符。')
  }
  if (/valid email address/i.test(text)) return '请输入有效的邮箱地址。'
  if (/password/i.test(text) && /too short|at least/i.test(text)) return '密码长度不符合要求。'
  if (/NetworkError|Failed to fetch|fetch failed/i.test(text)) return messageMap['Network request failed']
  return text
}

export function getAccessToken() {
  return localStorage.getItem('access_token')
}

export function getCurrentUser() {
  const raw = localStorage.getItem('current_user')
  return raw ? JSON.parse(raw) : null
}

export function setCurrentUser(user) {
  localStorage.setItem('current_user', JSON.stringify(user))
  window.dispatchEvent(new CustomEvent('blog-user-updated', { detail: user }))
}

export function setSession(data, user = null) {
  localStorage.setItem('access_token', data.access)
  localStorage.setItem('refresh_token', data.refresh)
  if (user) localStorage.setItem('current_user', JSON.stringify(user))
}

export function clearSession() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('current_user')
}

async function refreshAccessToken() {
  const refresh = localStorage.getItem('refresh_token')
  if (!refresh) return false
  const response = await fetch('/api/auth/token/refresh/', {
    method: 'POST',
    headers: jsonHeaders,
    body: JSON.stringify({ refresh }),
  })
  if (!response.ok) {
    clearSession()
    return false
  }
  const data = await response.json()
  localStorage.setItem('access_token', data.access)
  return true
}

export async function apiFetch(path, options = {}, retry = true) {
  const isFormData = options.body instanceof FormData
  const headers = {
    ...(isFormData ? {} : jsonHeaders),
    ...(options.headers || {}),
  }
  const token = getAccessToken()
  if (token) headers.Authorization = `Bearer ${token}`

  let response
  try {
    response = await fetch(path, { ...options, headers })
  } catch (err) {
    const message = friendlyMessage(err.message)
    showToast(message)
    throw new Error(message)
  }
  if (response.status === 401 && retry && await refreshAccessToken()) {
    return apiFetch(path, options, false)
  }
  return response
}

export async function parseApiResponse(response) {
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    const rawMessage = data.detail || Object.values(data).flat().join(' ') || '请求失败'
    const message = friendlyMessage(rawMessage)
    showToast(message)
    throw new Error(message)
  }
  return data
}
