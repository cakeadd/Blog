<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiFetch, getCurrentUser, parseApiResponse } from '../api'

const route = useRoute()
const router = useRouter()
const currentUser = ref(getCurrentUser())
const profile = ref(null)
const activeSection = ref(route.query.section || 'profile')
const loading = ref(true)
const error = ref('')
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
const avatarPreview = ref('')

const userId = computed(() => route.params.id)

function formatDate(value) {
  if (!value) return '未知'
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

function openAvatarPreview(url) {
  if (url) avatarPreview.value = url
}

function closeAvatarPreview() {
  avatarPreview.value = ''
}

async function loadProfile() {
  loading.value = true
  error.value = ''
  try {
    const response = await apiFetch(`/api/users/${userId.value}/`)
    profile.value = await parseApiResponse(response)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

async function loadArticles(page = 1) {
  articlesLoading.value = true
  articlesError.value = ''
  try {
    const response = await apiFetch(`/api/articles/?author=${userId.value}&page=${page}`)
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

async function loadLikes(page = 1) {
  likesLoading.value = true
  likesError.value = ''
  try {
    const response = await apiFetch(`/api/users/${userId.value}/likes/?page=${page}`)
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

function selectSection(section) {
  activeSection.value = section
  if (section === 'articles') loadArticles()
  if (section === 'likes') loadLikes()
}

function openArticle(article) {
  router.push(`/articles/${article.id}`)
}

function previousArticlePage() {
  if (articleHasPrevious.value) loadArticles(articlePage.value - 1)
}

function nextArticlePage() {
  if (articleHasNext.value) loadArticles(articlePage.value + 1)
}

function previousLikesPage() {
  if (likesHasPrevious.value) loadLikes(likesPage.value - 1)
}

function nextLikesPage() {
  if (likesHasNext.value) loadLikes(likesPage.value + 1)
}

onMounted(async () => {
  await loadProfile()
  if (activeSection.value === 'articles') await loadArticles()
  if (activeSection.value === 'likes') await loadLikes()
})
</script>

<template>
  <div class="public-profile-layout">
    <aside class="public-profile-sidebar border rounded bg-white">
      <button class="sidebar-home-button" aria-label="返回主页" @click="router.push('/')">
        &lt;
      </button>
      <button
        class="profile-nav-item"
        :class="{ active: activeSection === 'profile' }"
        @click="selectSection('profile')"
      >
        用户信息
      </button>
      <button
        class="profile-nav-item text-secondary"
        :class="{ active: activeSection === 'articles' }"
        @click="selectSection('articles')"
      >
        Ta的文章
      </button>
      <button
        class="profile-nav-item text-secondary"
        :class="{ active: activeSection === 'likes' }"
        @click="selectSection('likes')"
      >
        Ta的点赞
      </button>
    </aside>

    <section class="public-profile-content">
      <div v-if="loading" class="text-secondary">正在加载用户信息...</div>
      <div v-else-if="error" class="text-secondary">暂时无法加载用户主页。</div>

      <template v-else-if="activeSection === 'profile' && profile">
        <div class="profile-card border rounded p-4">
          <div class="profile-row avatar-row">
            <span class="profile-label">用户头像</span>
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
          </div>
          <div class="profile-row">
            <span class="profile-label">用户名</span>
            <span>{{ profile.username }}</span>
          </div>
          <div class="profile-row">
            <span class="profile-label">邮箱</span>
            <span>{{ profile.email || '未设置' }}</span>
          </div>
          <div class="profile-row">
            <span class="profile-label">注册时间</span>
            <span>{{ formatDate(profile.date_joined) }}</span>
          </div>
        </div>
      </template>

      <template v-else-if="activeSection === 'articles'">
        <div v-if="articlesLoading" class="text-secondary">正在加载文章...</div>
        <div v-else-if="articlesError" class="text-secondary">暂时无法加载文章。</div>
        <div v-else-if="articles.length === 0" class="text-secondary">暂无文章。</div>
        <div v-else class="public-article-list">
          <div
            v-for="article in articles"
            :key="article.id"
            class="public-article-row border rounded"
            @click="openArticle(article)"
          >
            {{ article.title }}
          </div>
          <div class="d-flex align-items-center justify-content-center gap-3 mt-4">
            <button class="btn btn-outline-secondary" :disabled="!articleHasPrevious" @click="previousArticlePage">上一页</button>
            <span class="text-secondary">第 {{ articlePage }} / {{ articleTotalPages }} 页</span>
            <button class="btn btn-outline-secondary" :disabled="!articleHasNext" @click="nextArticlePage">下一页</button>
          </div>
        </div>
      </template>

      <template v-else-if="activeSection === 'likes'">
        <div v-if="likesLoading" class="text-secondary">正在加载点赞文章...</div>
        <div v-else-if="likesError" class="text-secondary">暂时无法加载点赞内容。</div>
        <div v-else-if="likedArticles.length === 0" class="text-secondary">暂无点赞文章。</div>
        <div v-else class="public-article-list">
          <div
            v-for="article in likedArticles"
            :key="article.id"
            class="public-article-row border rounded"
            @click="openArticle(article)"
          >
            {{ article.title }}
          </div>
          <div class="d-flex align-items-center justify-content-center gap-3 mt-4">
            <button class="btn btn-outline-secondary" :disabled="!likesHasPrevious" @click="previousLikesPage">上一页</button>
            <span class="text-secondary">第 {{ likesPage }} / {{ likesTotalPages }} 页</span>
            <button class="btn btn-outline-secondary" :disabled="!likesHasNext" @click="nextLikesPage">下一页</button>
          </div>
        </div>
      </template>
    </section>
  </div>

  <div v-if="avatarPreview" class="modal-backdrop-custom" @click.self="closeAvatarPreview">
    <div class="avatar-preview-modal" role="dialog" aria-modal="true" aria-label="查看用户头像">
      <button class="btn-close avatar-preview-close" aria-label="关闭" @click="closeAvatarPreview"></button>
      <img :src="avatarPreview" class="avatar-large" alt="用户头像大图" />
    </div>
  </div>
</template>

<style scoped>
.public-profile-layout {
  display: grid;
  grid-template-columns: 220px minmax(0, 1fr);
  gap: 2rem;
  max-width: 1000px;
  margin: 0 auto;
}

.public-profile-sidebar {
  align-self: start;
  overflow: hidden;
}

.sidebar-home-button,
.profile-nav-item {
  display: block;
  width: 100%;
  border: 0;
  border-bottom: 1px solid #e9ecef;
  background: #fff;
  text-align: left;
}

.sidebar-home-button {
  padding: 0.65rem 1rem;
  color: #6c757d;
  font-size: 1.5rem;
  line-height: 1;
}

.profile-nav-item {
  padding: 0.85rem 1rem;
}

.sidebar-home-button:hover,
.profile-nav-item:not(.active):hover {
  background: #f8f9fa;
}

.profile-nav-item.active {
  background: #e7f1ff;
  color: #0d6efd;
}

.profile-card {
  background: #fff;
}

.avatar-row {
  min-height: 86px;
}

.avatar-preview-button {
  width: fit-content;
  padding: 0;
  border: 0;
  border-radius: 50%;
  background: transparent;
}

.profile-avatar {
  width: 3.5rem;
  height: 3.5rem;
  border-radius: 50%;
  object-fit: cover;
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

.profile-row {
  display: grid;
  grid-template-columns: 100px minmax(0, 1fr);
  gap: 1rem;
  align-items: center;
  min-height: 54px;
  border-bottom: 1px solid #e9ecef;
}

.profile-row:last-child {
  border-bottom: 0;
}

.profile-label {
  color: #6c757d;
}

.public-article-list {
  display: grid;
  gap: 0.75rem;
}

.public-article-row {
  padding: 0.9rem 1rem;
  cursor: pointer;
  transition: background-color 0.15s ease, box-shadow 0.15s ease;
}

.public-article-row:hover {
  background: #f8f9fa;
  box-shadow: 0 0.25rem 0.75rem rgb(0 0 0 / 8%);
}

@media (max-width: 767.98px) {
  .public-profile-layout {
    grid-template-columns: 1fr;
    gap: 1.25rem;
  }
}
</style>
