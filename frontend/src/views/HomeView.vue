<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch, getCurrentUser, parseApiResponse } from '../api'

const router = useRouter()
const articles = ref([])
const loading = ref(true)
const error = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const hasPrevious = ref(false)
const hasNext = ref(false)
const titleKeyword = ref('')
const categoryKeyword = ref('')
const categories = ref([])
const likeStates = ref({})
const currentUser = ref(getCurrentUser())

async function loadArticles(page = 1) {
  loading.value = true
  error.value = ''
  try {
    const params = new URLSearchParams({ page: String(page) })
    if (titleKeyword.value.trim()) params.set('title', titleKeyword.value.trim())
    if (categoryKeyword.value) params.set('category', categoryKeyword.value)
    const response = await apiFetch(`/api/articles/?${params.toString()}`)
    const data = await parseApiResponse(response)
    articles.value = data.results || data
    await loadLikeStates(articles.value)
    currentPage.value = page
    totalPages.value = Math.max(1, Math.ceil((data.count || articles.value.length) / 10))
    hasPrevious.value = Boolean(data.previous)
    hasNext.value = Boolean(data.next)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

async function loadLikeStates(items) {
  if (currentUser.value?.role !== 'user') return
  await Promise.all(items.map(async (article) => {
    try {
      const response = await apiFetch(`/api/articles/${article.id}/like/`)
      const data = await parseApiResponse(response)
      likeStates.value = {
        ...likeStates.value,
        [article.id]: { liked: data.liked, count: data.likes_count, loading: false },
      }
    } catch {
      likeStates.value = {
        ...likeStates.value,
        [article.id]: { liked: false, count: 0, loading: false },
      }
    }
  }))
}

async function toggleLike(article) {
  const existing = likeStates.value[article.id] || { liked: false, count: 0 }
  if (existing.loading) return
  likeStates.value = {
    ...likeStates.value,
    [article.id]: { ...existing, loading: true },
  }
  try {
    const response = await apiFetch(`/api/articles/${article.id}/like/`, {
      method: existing.liked ? 'DELETE' : 'POST',
    })
    const data = await parseApiResponse(response)
    likeStates.value = {
      ...likeStates.value,
      [article.id]: { liked: data.liked, count: data.likes_count, loading: false },
    }
  } catch {
    likeStates.value = {
      ...likeStates.value,
      [article.id]: { ...existing, loading: false },
    }
  }
}

async function loadCategories() {
  try {
    const response = await apiFetch('/api/categories/')
    categories.value = await parseApiResponse(response)
  } catch (err) {
    error.value = err.message
  }
}

function searchArticles() {
  loadArticles(1)
}

function filterByCategory() {
  loadArticles(1)
}

function previousPage() {
  if (hasPrevious.value) loadArticles(currentPage.value - 1)
}

function nextPage() {
  if (hasNext.value) loadArticles(currentPage.value + 1)
}

function userPath(userId) {
  return currentUser.value?.id === userId ? '/account' : `/users/${userId}`
}

onMounted(() => {
  loadArticles()
  loadCategories()
})
</script>

<template>
  <section>
    <div class="mb-5">
      <h1 class="display-6">我的个人博客</h1>
      <p class="text-secondary mb-0">记录想法，分享经验。</p>
    </div>

    <form class="row g-2 mb-4" @submit.prevent="searchArticles">
      <div class="col">
        <input v-model="titleKeyword" class="form-control" placeholder="搜索文章标题" />
      </div>
      <div class="col-auto">
        <button class="btn btn-primary" type="submit">搜索</button>
      </div>
      <div class="col-auto">
        <select v-model="categoryKeyword" class="form-select" @change="filterByCategory">
          <option value="">全部分类</option>
          <option v-for="category in categories" :key="category.id" :value="category.name">
            {{ category.name }}
          </option>
        </select>
      </div>
    </form>

    <div v-if="loading" class="text-secondary">正在加载文章...</div>
    <div v-else-if="error" class="text-secondary">暂时无法加载文章。</div>
    <div v-else-if="articles.length === 0" class="text-secondary">暂无文章。</div>
    <div v-else class="row g-4">
      <div v-for="article in articles" :key="article.id" class="col-12 col-md-6">
        <article class="card h-100 article-card">
          <div class="card-body pb-3 article-card-body" @click="router.push(`/articles/${article.id}`)">
              <router-link
                :to="userPath(article.author)"
                class="author-link text-secondary text-nowrap small mb-2 d-inline-block"
                @click.stop
              >
                {{ article.author_name }}
              </router-link>
              <h2 class="h4 card-title mb-2">{{ article.title }}</h2>
              <p class="card-text text-secondary mb-0">{{ article.summary || '暂无摘要' }}</p>
          </div>
          <div v-if="currentUser?.role === 'user'" class="card-footer bg-white border-0 pt-0">
            <button
              class="btn btn-link text-decoration-none p-0 like-button"
              :class="{ liked: likeStates[article.id]?.liked }"
              :disabled="likeStates[article.id]?.loading"
              @click.stop.prevent="toggleLike(article)"
            >
              <svg
                class="thumb-icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.8"
                stroke-linecap="round"
                stroke-linejoin="round"
                aria-hidden="true"
              >
                <path d="M7 10v10H4a2 2 0 0 1-2-2v-6a2 2 0 0 1 2-2h3Z" />
                <path d="M7 20h9.4a2 2 0 0 0 1.9-1.4l2.1-6A2 2 0 0 0 18.5 10H15l.8-4.1A2.4 2.4 0 0 0 13.5 3L7 10v10Z" />
              </svg>
              <span class="ms-2">{{ likeStates[article.id]?.count ?? 0 }}</span>
            </button>
          </div>
        </article>
      </div>
      <nav v-if="articles.length" class="d-flex align-items-center justify-content-center gap-3 mt-4" aria-label="文章分页">
        <button class="btn btn-outline-secondary" :disabled="!hasPrevious" @click="previousPage">
          上一页
        </button>
        <span class="text-secondary">第 {{ currentPage }} / {{ totalPages }} 页</span>
        <button class="btn btn-outline-secondary" :disabled="!hasNext" @click="nextPage">
          下一页
        </button>
      </nav>
    </div>
  </section>
</template>

<style scoped>
.article-card {
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.article-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 0.5rem 1rem rgb(0 0 0 / 10%);
}

.article-card-body {
  cursor: pointer;
}

.author-link {
  position: relative;
  z-index: 1;
}

.like-button {
  color: #6c757d;
}

.like-button.liked {
  color: #0d6efd;
}

.thumb-icon {
  width: 1.15rem;
  height: 1.15rem;
  vertical-align: -0.2rem;
}
</style>
