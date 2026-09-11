<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch, clearSession, getCurrentUser, parseApiResponse, setCurrentUser, showToast } from '../api'

const router = useRouter()
const currentUser = ref(getCurrentUser())
const activeSection = ref('users')
const dropdownOpen = ref(false)
const menuRef = ref(null)
const profileModal = ref(false)
const passwordModal = ref(false)
const profileDraft = ref({ username: '' })
const passwordDraft = ref({ old_password: '', new_password: '', confirm_password: '' })
const passwordVisibility = ref({ old: false, new: false, confirm: false })
const saving = ref(false)

const sections = {
  users: { label: '用户', endpoint: '/api/admin/users/' },
  articles: { label: '文章', endpoint: '/api/admin/articles/' },
  comments: { label: '评论', endpoint: '/api/admin/comments/' },
}

const sectionState = ref({
  users: { items: [], search: '', page: 1, totalPages: 1, previous: false, next: false, loading: false, error: '' },
  articles: { items: [], search: '', page: 1, totalPages: 1, previous: false, next: false, loading: false, error: '' },
  comments: { items: [], search: '', page: 1, totalPages: 1, previous: false, next: false, loading: false, error: '' },
})

const currentState = computed(() => sectionState.value[activeSection.value])

async function loadSection(section = activeSection.value, page = 1) {
  const state = sectionState.value[section]
  state.loading = true
  state.error = ''
  try {
    const params = new URLSearchParams({ page: String(page) })
    if (state.search.trim()) params.set('search', state.search.trim())
    const response = await apiFetch(`${sections[section].endpoint}?${params.toString()}`)
    const data = await parseApiResponse(response)
    state.items = data.results || data
    state.page = page
    state.totalPages = Math.max(1, Math.ceil((data.count || state.items.length) / 5))
    state.previous = Boolean(data.previous)
    state.next = Boolean(data.next)
  } catch (err) {
    state.error = err.message
  } finally {
    state.loading = false
  }
}

function selectSection(section) {
  activeSection.value = section
  loadSection(section)
}

function searchSection() {
  loadSection(activeSection.value, 1)
}

function previousPage() {
  if (currentState.value.previous) loadSection(activeSection.value, currentState.value.page - 1)
}

function nextPage() {
  if (currentState.value.next) loadSection(activeSection.value, currentState.value.page + 1)
}

async function changeStatus(section, item, action) {
  const endpoint = `${sections[section].endpoint}${item.id}/${action === 'delete' ? '' : 'restore/'}`
  try {
    const response = await apiFetch(endpoint, { method: action === 'delete' ? 'DELETE' : 'PATCH' })
    await parseApiResponse(response)
    await loadSection(section, currentState.value.page)
    showToast(action === 'delete' ? '删除成功。' : '恢复成功。', 'success')
  } catch {
    // 统一提示已处理接口错误。
  }
}

function logout() {
  clearSession()
  router.push('/admin/login')
}

function closeDropdownOutside(event) {
  if (menuRef.value && !menuRef.value.contains(event.target)) {
    dropdownOpen.value = false
  }
}

function openProfileModal() {
  profileDraft.value = { username: currentUser.value?.username || '' }
  profileModal.value = true
  dropdownOpen.value = false
}

function closeProfileModal() {
  if (!saving.value) profileModal.value = false
}

async function saveProfile() {
  saving.value = true
  try {
    const response = await apiFetch('/api/admin/profile/', {
      method: 'PATCH',
      body: JSON.stringify(profileDraft.value),
    })
    const user = await parseApiResponse(response)
    currentUser.value = user
    setCurrentUser(user)
    profileModal.value = false
    showToast('管理员资料保存成功。', 'success')
  } catch {
    // 统一提示已处理接口错误。
  } finally {
    saving.value = false
  }
}

function openPasswordModal() {
  passwordDraft.value = { old_password: '', new_password: '', confirm_password: '' }
  passwordVisibility.value = { old: false, new: false, confirm: false }
  passwordModal.value = true
  dropdownOpen.value = false
}

function closePasswordModal() {
  if (!saving.value) passwordModal.value = false
}

async function changePassword() {
  saving.value = true
  try {
    const response = await apiFetch('/api/admin/password/', {
      method: 'POST',
      body: JSON.stringify(passwordDraft.value),
    })
    await parseApiResponse(response)
    passwordModal.value = false
    showToast('管理员密码修改成功。', 'success')
  } catch {
    // 统一提示已处理接口错误。
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', closeDropdownOutside)
  if (currentUser.value?.role !== 'admin') {
    router.push('/')
    return
  }
  loadSection('users')
})
onBeforeUnmount(() => document.removeEventListener('click', closeDropdownOutside))
</script>

<template>
  <div class="admin-page">
    <header class="admin-header border-bottom">
      <div class="admin-brand">Admin 后台</div>
      <div ref="menuRef" class="admin-user-menu">
        <button class="admin-user-button" @click.stop="dropdownOpen = !dropdownOpen">
          {{ currentUser?.username || '管理员' }}
          <span class="ms-1">⌄</span>
        </button>
        <div v-if="dropdownOpen" class="admin-dropdown border rounded shadow-sm">
          <button @click="openProfileModal">编辑资料</button>
          <button @click="openPasswordModal">修改密码</button>
          <button @click="logout">退出登录</button>
        </div>
      </div>
    </header>

    <div class="admin-layout">
      <aside class="admin-sidebar border rounded bg-white">
        <button
          v-for="(section, key) in sections"
          :key="key"
          class="admin-nav-item"
          :class="{ active: activeSection === key }"
          @click="selectSection(key)"
        >
          {{ section.label }}
        </button>
      </aside>

      <main class="admin-content">
        <form class="search-row mb-4" @submit.prevent="searchSection">
          <input v-model="currentState.search" class="form-control" :placeholder="`搜索${sections[activeSection].label}`" />
          <button class="btn btn-primary" type="submit">搜索</button>
        </form>

        <div v-if="currentState.loading" class="text-secondary">正在加载数据...</div>
        <div v-else-if="currentState.error" class="text-secondary">暂时无法加载数据。</div>
        <div v-else-if="currentState.items.length === 0" class="text-secondary">暂无数据。</div>
        <div v-else class="admin-list border rounded bg-white">
          <div v-for="item in currentState.items" :key="item.id" class="admin-list-row">
            <div class="admin-item-main">
              <template v-if="activeSection === 'users'">
                <strong>{{ item.username }}</strong>
                <small>{{ item.email || '未设置邮箱' }} · {{ item.is_active ? '启用' : '已停用' }}</small>
              </template>
              <template v-else-if="activeSection === 'articles'">
                <strong>{{ item.title }}</strong>
                <small>作者：{{ item.author_name }} · {{ item.is_deleted ? '已删除' : '正常' }}</small>
              </template>
              <template v-else>
                <strong>{{ item.content }}</strong>
                <small>评论者：{{ item.author_name }} · {{ item.is_deleted ? '已删除' : '正常' }}</small>
              </template>
            </div>
            <div class="admin-actions">
              <button class="btn btn-sm btn-outline-danger" @click="changeStatus(activeSection, item, 'delete')">删除</button>
              <button class="btn btn-sm btn-outline-success" @click="changeStatus(activeSection, item, 'restore')">恢复</button>
            </div>
          </div>
        </div>

        <div class="d-flex align-items-center justify-content-center gap-3 mt-4">
          <button class="btn btn-outline-secondary" :disabled="!currentState.previous" @click="previousPage">上一页</button>
          <span class="text-secondary">第 {{ currentState.page }} / {{ currentState.totalPages }} 页</span>
          <button class="btn btn-outline-secondary" :disabled="!currentState.next" @click="nextPage">下一页</button>
        </div>
      </main>
    </div>
  </div>

  <div v-if="profileModal" class="modal-backdrop-custom" @click.self="closeProfileModal">
    <div class="modal-card" role="dialog" aria-modal="true">
      <div class="modal-header-custom"><h2 class="h5 mb-0">编辑管理员资料</h2><button class="btn-close" @click="closeProfileModal"></button></div>
      <form @submit.prevent="saveProfile">
        <div class="modal-body-custom"><label class="form-label" for="admin-edit-username">用户名</label><input id="admin-edit-username" v-model="profileDraft.username" class="form-control" required /></div>
        <div class="modal-footer-custom"><button type="button" class="btn btn-outline-secondary" @click="closeProfileModal">取消</button><button class="btn btn-primary" :disabled="saving">保存</button></div>
      </form>
    </div>
  </div>

  <div v-if="passwordModal" class="modal-backdrop-custom" @click.self="closePasswordModal">
    <div class="modal-card" role="dialog" aria-modal="true">
      <div class="modal-header-custom"><h2 class="h5 mb-0">修改管理员密码</h2><button class="btn-close" @click="closePasswordModal"></button></div>
      <form @submit.prevent="changePassword">
        <div class="modal-body-custom">
          <div v-for="field in [{key: 'old', label: '旧密码', model: 'old_password'}, {key: 'new', label: '新密码', model: 'new_password'}, {key: 'confirm', label: '确认密码', model: 'confirm_password'}]" :key="field.key" class="mb-3">
            <label class="form-label" :for="`admin-${field.key}-password`">{{ field.label }}</label>
            <div class="password-input-group"><input :id="`admin-${field.key}-password`" v-model="passwordDraft[field.model]" :type="passwordVisibility[field.key] ? 'text' : 'password'" class="form-control" required /><button type="button" class="password-toggle" @click="passwordVisibility[field.key] = !passwordVisibility[field.key]"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6Z" /><circle cx="12" cy="12" r="2.5" /></svg></button></div>
          </div>
        </div>
        <div class="modal-footer-custom"><button type="button" class="btn btn-outline-secondary" @click="closePasswordModal">取消</button><button class="btn btn-primary" :disabled="saving">保存</button></div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.admin-page { min-height: 100vh; }
.admin-header { display: flex; align-items: center; justify-content: space-between; padding: 1rem 0; }
.admin-brand { font-size: 1.25rem; font-weight: 600; }
.admin-user-menu { position: relative; }
.admin-user-button { border: 0; background: transparent; color: #212529; }
.admin-dropdown { position: absolute; top: calc(100% + 0.5rem); right: 0; z-index: 10; min-width: 150px; overflow: hidden; background: #fff; }
.admin-dropdown button { display: block; width: 100%; padding: 0.65rem 1rem; border: 0; background: #fff; text-align: left; }
.admin-dropdown button:hover { background: #f8f9fa; }
.admin-layout { display: grid; grid-template-columns: 180px minmax(0, 1fr); gap: 2rem; padding-top: 2rem; }
.admin-sidebar { align-self: start; overflow: hidden; }
.admin-nav-item { display: block; width: 100%; padding: 0.85rem 1rem; border: 0; border-bottom: 1px solid #e9ecef; background: #fff; text-align: left; }
.admin-nav-item.active { background: #e7f1ff; color: #0d6efd; }
.admin-nav-item:hover { background: #f8f9fa; }
.search-row { display: flex; gap: 0.75rem; }
.admin-list { overflow: hidden; }
.admin-list-row { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: 1rem; border-bottom: 1px solid #e9ecef; }
.admin-list-row:last-child { border-bottom: 0; }
.admin-item-main { min-width: 0; }
.admin-item-main strong, .admin-item-main small { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.admin-item-main small { margin-top: 0.3rem; color: #6c757d; }
.admin-actions { display: flex; flex-shrink: 0; gap: 0.5rem; }
.modal-backdrop-custom { position: fixed; inset: 0; z-index: 1050; display: flex; align-items: center; justify-content: center; padding: 1rem; background: rgb(0 0 0 / 50%); }
.modal-card { width: min(100%, 480px); background: #fff; border-radius: 0.5rem; box-shadow: 0 0.5rem 1rem rgb(0 0 0 / 15%); }
.modal-header-custom, .modal-footer-custom { display: flex; align-items: center; justify-content: space-between; padding: 1rem 1.25rem; border-bottom: 1px solid #dee2e6; }
.modal-body-custom { padding: 1.25rem; }
.modal-footer-custom { justify-content: flex-end; gap: 0.5rem; border-top: 1px solid #dee2e6; border-bottom: 0; }
.password-input-group { position: relative; }
.password-input-group .form-control { padding-right: 2.75rem; }
.password-toggle { position: absolute; top: 50%; right: 0.65rem; display: inline-flex; padding: 0; border: 0; background: transparent; color: #6c757d; transform: translateY(-50%); }
.password-toggle svg { width: 1.15rem; height: 1.15rem; }
@media (max-width: 767.98px) { .admin-layout { grid-template-columns: 1fr; } }
</style>
