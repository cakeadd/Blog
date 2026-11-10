<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiFetch, isGuestMode, parseApiResponse, setCurrentUser, showToast as globalShowToast } from '../api'

const router = useRouter()
const route = useRoute()
const profile = ref(null)
const guest = ref(isGuestMode())
const draft = ref({ username: '', email: '' })
const activeSection = ref('profile')
const editing = ref(false)
const passwordModal = ref(false)
const passwordDraft = ref({ old_password: '', new_password: '', confirm_password: '' })
const loading = ref(true)
const saving = ref(false)
const passwordSaving = ref(false)
const error = ref('')
const passwordError = ref('')
const articles = ref([])
const articlesLoading = ref(false)
const articlesError = ref('')
const articlePage = ref(1)
const articleTotalPages = ref(1)
const articleHasPrevious = ref(false)
const articleHasNext = ref(false)
const likedArticles = ref([])
const likesLoading = ref(false)
const likesError = ref('')
const likesPage = ref(1)
const likesTotalPages = ref(1)
const likesHasPrevious = ref(false)
const likesHasNext = ref(false)
const deleteTarget = ref(null)
const deleteSaving = ref(false)
const toastMessage = ref('')
const passwordVisibility = ref({ old: false, new: false, confirm: false })
const avatarInput = ref(null)
const avatarUploading = ref(false)
const avatarPreview = ref('')
let toastTimer = null

async function loadProfile() {
  if (guest.value) {
    loading.value = false
    return
  }
  loading.value = true
  error.value = ''
  try {
    const response = await apiFetch('/api/auth/me/')
    profile.value = await parseApiResponse(response)
    draft.value = {
      username: profile.value.username,
      email: profile.value.email || '',
    }
    setCurrentUser(profile.value)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

async function loadMyArticles(page = 1) {
  if (!profile.value) return
  articlesLoading.value = true
  articlesError.value = ''
  try {
    const response = await apiFetch(`/api/articles/?author=${profile.value.id}&page=${page}`)
    const data = await parseApiResponse(response)
    articles.value = data.results || data
    articlePage.value = page
    articleTotalPages.value = Math.max(1, Math.ceil((data.count || articles.value.length) / 10))
    articleHasPrevious.value = Boolean(data.previous)
    articleHasNext.value = Boolean(data.next)
  } catch (err) {
    articlesError.value = err.message
  } finally {
    articlesLoading.value = false
  }
}

async function loadMyLikes(page = 1) {
  likesLoading.value = true
  likesError.value = ''
  try {
    const response = await apiFetch(`/api/likes/?page=${page}`)
    const data = await parseApiResponse(response)
    likedArticles.value = data.results || data
    likesPage.value = page
    likesTotalPages.value = Math.max(1, Math.ceil((data.count || likedArticles.value.length) / 10))
    likesHasPrevious.value = Boolean(data.previous)
    likesHasNext.value = Boolean(data.next)
  } catch (err) {
    likesError.value = err.message
  } finally {
    likesLoading.value = false
  }
}

function startEditing() {
  error.value = ''
  draft.value = {
    username: profile.value.username,
    email: profile.value.email || '',
  }
  editing.value = true
}

function cancelEditing() {
  error.value = ''
  editing.value = false
  draft.value = {
    username: profile.value.username,
    email: profile.value.email || '',
  }
}

function openPasswordModal() {
  passwordError.value = ''
  passwordDraft.value = { old_password: '', new_password: '', confirm_password: '' }
  passwordVisibility.value = { old: false, new: false, confirm: false }
  passwordModal.value = true
}

function closePasswordModal() {
  if (passwordSaving.value) return
  passwordModal.value = false
  passwordError.value = ''
}

function showToast(message) {
  toastMessage.value = message
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => {
    toastMessage.value = ''
    toastTimer = null
  }, 5000)
}

function chooseAvatar() {
  avatarInput.value?.click()
}

function openAvatarPreview(url) {
  if (url) avatarPreview.value = url
}

function closeAvatarPreview() {
  avatarPreview.value = ''
}

async function uploadAvatar(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return
  if (!['image/jpeg', 'image/png'].includes(file.type)) {
    globalShowToast('头像只能使用 JPG 或 PNG 图片。')
    return
  }
  if (file.size > 3 * 1024 * 1024) {
    globalShowToast('头像图片大小不能超过 3MB。')
    return
  }

  avatarUploading.value = true
  error.value = ''
  try {
    const formData = new FormData()
    formData.append('avatar', file)
    const response = await apiFetch('/api/auth/avatar/', {
      method: 'POST',
      body: formData,
    })
    profile.value = await parseApiResponse(response)
    setCurrentUser(profile.value)
    showToast('头像上传成功。')
  } catch (err) {
    error.value = err.message
  } finally {
    avatarUploading.value = false
  }
}

async function changePassword() {
  passwordSaving.value = true
  passwordError.value = ''
  try {
    const response = await apiFetch('/api/auth/password/', {
      method: 'POST',
      body: JSON.stringify(passwordDraft.value),
    })
    await parseApiResponse(response)
    passwordDraft.value = { old_password: '', new_password: '', confirm_password: '' }
    passwordModal.value = false
    showToast('密码修改成功。')
  } catch (err) {
    passwordError.value = err.message
  } finally {
    passwordSaving.value = false
  }
}

async function saveProfile() {
  saving.value = true
  error.value = ''
  try {
    const response = await apiFetch('/api/auth/me/', {
      method: 'PATCH',
      body: JSON.stringify(draft.value),
    })
    profile.value = await parseApiResponse(response)
    draft.value = {
      username: profile.value.username,
      email: profile.value.email || '',
    }
    setCurrentUser(profile.value)
    editing.value = false
    showToast('用户信息保存成功。')
  } catch (err) {
    error.value = err.message
  } finally {
    saving.value = false
  }
}

function selectSection(section) {
  activeSection.value = section
  error.value = ''
  if (guest.value) return
  if (section === 'articles') loadMyArticles()
  if (section === 'likes') loadMyLikes()
}

function openArticle(article) {
  router.push(`/articles/${article.id}`)
}

function editArticle(article) {
  router.push(`/articles/${article.id}/edit`)
}

async function deleteArticle(article) {
  deleteTarget.value = article
}

function cancelDelete() {
  if (deleteSaving.value) return
  deleteTarget.value = null
}

async function confirmDelete() {
  if (!deleteTarget.value || deleteSaving.value) return
  deleteSaving.value = true
  articlesError.value = ''
  try {
    const response = await apiFetch(`/api/articles/${deleteTarget.value.id}/`, { method: 'DELETE' })
    await parseApiResponse(response)
    const nextPage = articles.value.length === 1 && articlePage.value > 1
      ? articlePage.value - 1
      : articlePage.value
    deleteTarget.value = null
    await loadMyArticles(nextPage)
    showToast('文章删除成功。')
  } catch (err) {
    articlesError.value = err.message
  }
  finally {
    deleteSaving.value = false
  }
}

function previousArticlePage() {
  if (articleHasPrevious.value) loadMyArticles(articlePage.value - 1)
}

function nextArticlePage() {
  if (articleHasNext.value) loadMyArticles(articlePage.value + 1)
}

function previousLikesPage() {
  if (likesHasPrevious.value) loadMyLikes(likesPage.value - 1)
}

function nextLikesPage() {
  if (likesHasNext.value) loadMyLikes(likesPage.value + 1)
}

onMounted(async () => {
  await loadProfile()
  if (route.query.section === 'articles') {
    activeSection.value = 'articles'
    await loadMyArticles()
  }
})
onBeforeUnmount(() => {
  if (toastTimer) clearTimeout(toastTimer)
})
</script>

<template>
  <div class="account-layout">
    <aside class="account-sidebar border rounded bg-white">
      <button class="sidebar-home-button" aria-label="返回主页" @click="router.push('/')">
        &lt;
      </button>
      <button
        class="account-nav-item"
        :class="{ active: activeSection === 'profile' }"
        @click="selectSection('profile')"
      >
        用户信息
      </button>
      <button
        class="account-nav-item text-secondary"
        :class="{ active: activeSection === 'articles' }"
        :disabled="guest"
        :title="guest ? '登录后才能查看我的文章' : ''"
        @click="selectSection('articles')"
      >
        我的文章
      </button>
      <button
        class="account-nav-item text-secondary"
        :class="{ active: activeSection === 'likes' }"
        :disabled="guest"
        :title="guest ? '登录后才能查看我的点赞' : ''"
        @click="selectSection('likes')"
      >
        我的点赞
      </button>
    </aside>

    <section class="account-content">
      <div v-if="guest" class="guest-panel border rounded p-5 text-center">
        <i class="bi bi-person-circle guest-panel-icon" aria-hidden="true"></i>
        <h2 class="h4 mt-3">当前为游客模式</h2>
        <p class="text-secondary">登录后才能查看和管理个人文章、点赞及用户信息。</p>
        <router-link class="btn btn-primary me-2" to="/login">登录</router-link>
        <router-link class="btn btn-outline-primary" to="/register">注册</router-link>
      </div>
      <div v-else-if="loading" class="text-secondary">正在加载用户信息...</div>
      <div v-else-if="error && !profile" class="text-secondary">暂时无法加载用户信息。</div>

      <template v-else-if="activeSection === 'profile' && profile">
        <div class="profile-card border rounded p-4">
          <div class="profile-row avatar-row">
            <span class="profile-label">用户头像</span>
            <div class="avatar-actions">
              <button
                v-if="profile.avatar_url"
                class="avatar-preview-button"
                type="button"
                aria-label="查看用户头像"
                @click="openAvatarPreview(profile.avatar_url)"
              >
                <img :src="profile.avatar_url" class="profile-avatar" alt="用户头像" />
              </button>
              <span v-else class="text-secondary">未上传</span>
              <button class="btn btn-outline-primary" type="button" :disabled="avatarUploading" @click="chooseAvatar">
                {{ avatarUploading ? '上传中...' : '上传文件' }}
              </button>
              <input ref="avatarInput" type="file" accept="image/jpeg,image/png" hidden @change="uploadAvatar" />
            </div>
          </div>
          <div class="profile-row">
            <label for="account-username">用户名</label>
            <span id="account-username">{{ profile.username }}</span>
          </div>
          <div class="profile-row">
            <label for="account-email">邮箱</label>
            <span id="account-email">{{ profile.email || '未设置' }}</span>
          </div>
        </div>

        <div class="text-center mt-4">
          <button class="btn btn-primary me-2" @click="startEditing">编辑</button>
          <button class="btn btn-outline-secondary" @click="openPasswordModal">修改密码</button>
        </div>
      </template>

      <template v-else-if="activeSection === 'articles'">
        <div v-if="articlesLoading" class="text-secondary">正在加载我的文章...</div>
        <div v-else-if="articlesError" class="text-secondary">暂时无法加载文章。</div>
        <div v-else-if="articles.length === 0" class="text-secondary">暂无已发布文章。</div>
        <div v-else class="my-articles-list">
          <div
            v-for="article in articles"
            :key="article.id"
            class="my-article-row border rounded"
            @click="openArticle(article)"
          >
            <span class="my-article-title">{{ article.title }}</span>
            <div class="my-article-actions">
              <button class="btn btn-sm btn-outline-primary" @click.stop="editArticle(article)">
                编辑
              </button>
              <button class="btn btn-sm btn-outline-danger" @click.stop="deleteArticle(article)">
                删除
              </button>
            </div>
          </div>
          <div class="d-flex align-items-center justify-content-center gap-3 mt-4">
            <button class="btn btn-outline-secondary" :disabled="!articleHasPrevious" @click="previousArticlePage">
              上一页
            </button>
            <span class="text-secondary">第 {{ articlePage }} / {{ articleTotalPages }} 页</span>
            <button class="btn btn-outline-secondary" :disabled="!articleHasNext" @click="nextArticlePage">
              下一页
            </button>
          </div>
        </div>
      </template>

      <template v-else-if="activeSection === 'likes'">
        <div v-if="likesLoading" class="text-secondary">正在加载我的点赞...</div>
        <div v-else-if="likesError" class="text-secondary">暂时无法加载点赞内容。</div>
        <div v-else-if="likedArticles.length === 0" class="text-secondary">暂无点赞文章。</div>
        <div v-else class="my-articles-list">
          <div
            v-for="article in likedArticles"
            :key="article.id"
            class="my-article-row border rounded"
            @click="openArticle(article)"
          >
            <span class="my-article-title">{{ article.title }}</span>
          </div>
          <div class="d-flex align-items-center justify-content-center gap-3 mt-4">
            <button class="btn btn-outline-secondary" :disabled="!likesHasPrevious" @click="previousLikesPage">
              上一页
            </button>
            <span class="text-secondary">第 {{ likesPage }} / {{ likesTotalPages }} 页</span>
            <button class="btn btn-outline-secondary" :disabled="!likesHasNext" @click="nextLikesPage">
              下一页
            </button>
          </div>
        </div>
      </template>

      <div v-else class="placeholder-panel border rounded p-5 text-center text-secondary">
        暂无内容。
      </div>
    </section>
  </div>

  <div v-if="toastMessage" class="success-toast" role="alert">
    {{ toastMessage }}
  </div>

  <div v-if="editing" class="modal-backdrop-custom" @click.self="cancelEditing">
    <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="edit-profile-title">
      <div class="modal-header-custom">
        <h2 id="edit-profile-title" class="h5 mb-0">编辑用户信息</h2>
        <button class="btn-close" aria-label="关闭" @click="cancelEditing"></button>
      </div>
      <form @submit.prevent="saveProfile">
        <div class="modal-body-custom">
          <div class="mb-3">
            <label class="form-label" for="edit-username">用户名</label>
            <input id="edit-username" v-model="draft.username" class="form-control" required />
          </div>
          <div>
            <label class="form-label" for="edit-email">邮箱</label>
            <input id="edit-email" v-model="draft.email" class="form-control" type="email" required />
          </div>
        </div>
        <div class="modal-footer-custom">
          <button type="button" class="btn btn-outline-secondary" :disabled="saving" @click="cancelEditing">
            取消
          </button>
          <button type="submit" class="btn btn-primary" :disabled="saving">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </form>
    </div>
  </div>

  <div v-if="passwordModal" class="modal-backdrop-custom" @click.self="closePasswordModal">
    <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="password-title">
      <div class="modal-header-custom">
        <h2 id="password-title" class="h5 mb-0">修改密码</h2>
        <button class="btn-close" aria-label="关闭" @click="closePasswordModal"></button>
      </div>
      <form @submit.prevent="changePassword">
        <div class="modal-body-custom">
          <div class="mb-3">
            <label class="form-label" for="old-password">旧密码</label>
            <div class="password-input-group">
              <input id="old-password" v-model="passwordDraft.old_password" class="form-control" :type="passwordVisibility.old ? 'text' : 'password'" required />
              <button type="button" class="password-toggle" :aria-label="passwordVisibility.old ? '隐藏旧密码' : '显示旧密码'" @click="passwordVisibility.old = !passwordVisibility.old">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                  <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6Z" />
                  <circle cx="12" cy="12" r="2.5" />
                </svg>
              </button>
            </div>
          </div>
          <div class="mb-3">
            <label class="form-label" for="new-password">新密码</label>
            <div class="password-input-group">
              <input id="new-password" v-model="passwordDraft.new_password" class="form-control" :type="passwordVisibility.new ? 'text' : 'password'" required />
              <button type="button" class="password-toggle" :aria-label="passwordVisibility.new ? '隐藏新密码' : '显示新密码'" @click="passwordVisibility.new = !passwordVisibility.new">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                  <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6Z" />
                  <circle cx="12" cy="12" r="2.5" />
                </svg>
              </button>
            </div>
          </div>
          <div>
            <label class="form-label" for="confirm-password">确认密码</label>
            <div class="password-input-group">
              <input id="confirm-password" v-model="passwordDraft.confirm_password" class="form-control" :type="passwordVisibility.confirm ? 'text' : 'password'" required />
              <button type="button" class="password-toggle" :aria-label="passwordVisibility.confirm ? '隐藏确认密码' : '显示确认密码'" @click="passwordVisibility.confirm = !passwordVisibility.confirm">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                  <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6Z" />
                  <circle cx="12" cy="12" r="2.5" />
                </svg>
              </button>
            </div>
          </div>
        </div>
        <div class="modal-footer-custom">
          <button type="button" class="btn btn-outline-secondary" :disabled="passwordSaving" @click="closePasswordModal">
            取消
          </button>
          <button type="submit" class="btn btn-primary" :disabled="passwordSaving">
            {{ passwordSaving ? '提交中...' : '确认修改' }}
          </button>
        </div>
      </form>
    </div>
  </div>

  <div v-if="deleteTarget" class="modal-backdrop-custom" @click.self="cancelDelete">
    <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="delete-article-title">
      <div class="modal-header-custom">
        <h2 id="delete-article-title" class="h5 mb-0">删除文章</h2>
        <button class="btn-close" aria-label="关闭" @click="cancelDelete"></button>
      </div>
      <div class="modal-body-custom">
        确定要删除《{{ deleteTarget.title }}》吗？
      </div>
      <div class="modal-footer-custom">
        <button class="btn btn-outline-secondary" :disabled="deleteSaving" @click="cancelDelete">
          取消
        </button>
        <button class="btn btn-danger" :disabled="deleteSaving" @click="confirmDelete">
          {{ deleteSaving ? '删除中...' : '确认删除' }}
        </button>
      </div>
    </div>
  </div>

  <div v-if="avatarPreview" class="modal-backdrop-custom" @click.self="closeAvatarPreview">
    <div class="avatar-preview-modal" role="dialog" aria-modal="true" aria-label="查看用户头像">
      <button class="btn-close avatar-preview-close" aria-label="关闭" @click="closeAvatarPreview"></button>
      <img :src="avatarPreview" class="avatar-large" alt="用户头像大图" />
    </div>
  </div>
</template>

<style scoped>
.account-layout {
  display: grid;
  grid-template-columns: 220px minmax(0, 1fr);
  gap: 2rem;
  max-width: 1000px;
  margin: 0 auto;
}

.account-sidebar {
  align-self: start;
  overflow: hidden;
}

.sidebar-home-button {
  display: block;
  width: 100%;
  padding: 0.65rem 1rem;
  border: 0;
  border-bottom: 1px solid #e9ecef;
  background: #fff;
  color: #6c757d;
  font-size: 1.5rem;
  line-height: 1;
  text-align: left;
}

.sidebar-home-button:hover {
  background: #f8f9fa;
  color: #212529;
}

.account-nav-item {
  display: block;
  width: 100%;
  padding: 0.85rem 1rem;
  border: 0;
  border-bottom: 1px solid #e9ecef;
  background: #fff;
  text-align: left;
}

.account-nav-item:last-child {
  border-bottom: 0;
}

.account-nav-item.active {
  background: #e7f1ff;
  color: #0d6efd;
}

.account-nav-item:not(.active):hover {
  background: #f8f9fa;
}

.profile-card {
  background: #fff;
}

.guest-panel {
  background: #fff;
}

.guest-panel-icon {
  color: #6c757d;
  font-size: 3rem;
}

.profile-row {
  display: grid;
  grid-template-columns: 100px minmax(0, 1fr);
  align-items: center;
  gap: 1rem;
  min-height: 54px;
  border-bottom: 1px solid #e9ecef;
}

.profile-row:last-child {
  border-bottom: 0;
}

.profile-row label {
  color: #6c757d;
}

.avatar-row {
  min-height: 86px;
}

.avatar-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.avatar-preview-button {
  padding: 0;
  border: 0;
  border-radius: 50%;
  background: transparent;
}

.profile-avatar,
.header-avatar {
  width: 3.5rem;
  height: 3.5rem;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-preview-modal {
  position: relative;
  max-width: min(90vw, 720px);
  max-height: 90vh;
  padding: 1.5rem;
  border-radius: 0.5rem;
  background: #fff;
}

.avatar-preview-close {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
}

.avatar-large {
  display: block;
  max-width: min(80vw, 640px);
  max-height: 80vh;
  object-fit: contain;
}

.placeholder-panel {
  min-height: 180px;
}

.my-articles-list {
  display: grid;
  gap: 0.75rem;
}

.my-article-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.85rem 1rem;
  cursor: pointer;
  transition: background-color 0.15s ease, box-shadow 0.15s ease;
}

.my-article-row:hover {
  background: #f8f9fa;
  box-shadow: 0 0.25rem 0.75rem rgb(0 0 0 / 8%);
}

.my-article-title {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.my-article-actions {
  display: flex;
  flex-shrink: 0;
  gap: 0.5rem;
}

.modal-backdrop-custom {
  position: fixed;
  inset: 0;
  z-index: 1050;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgb(0 0 0 / 50%);
}

.modal-card {
  width: min(100%, 480px);
  background: #fff;
  border-radius: 0.5rem;
  box-shadow: 0 0.5rem 1rem rgb(0 0 0 / 15%);
}

.modal-header-custom,
.modal-footer-custom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #dee2e6;
}

.modal-body-custom {
  padding: 1.25rem;
}

.modal-footer-custom {
  justify-content: flex-end;
  gap: 0.5rem;
  border-top: 1px solid #dee2e6;
  border-bottom: 0;
}

.success-toast {
  position: fixed;
  top: 1.25rem;
  left: 50%;
  z-index: 1100;
  padding: 0.75rem 1.25rem;
  border: 1px solid #badbcc;
  border-radius: 0.375rem;
  background: #d1e7dd;
  color: #0f5132;
  box-shadow: 0 0.25rem 0.75rem rgb(0 0 0 / 15%);
  transform: translateX(-50%);
}

.password-input-group {
  position: relative;
}

.password-input-group .form-control {
  padding-right: 2.75rem;
}

.password-toggle {
  position: absolute;
  top: 50%;
  right: 0.65rem;
  display: inline-flex;
  padding: 0;
  border: 0;
  background: transparent;
  color: #6c757d;
  transform: translateY(-50%);
}

.password-toggle:hover {
  color: #212529;
}

.password-toggle svg {
  width: 1.15rem;
  height: 1.15rem;
}

@media (max-width: 767.98px) {
  .account-layout {
    grid-template-columns: 1fr;
    gap: 1.25rem;
  }
}
</style>
