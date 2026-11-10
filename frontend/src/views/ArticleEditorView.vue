<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiFetch, isGuestMode, parseApiResponse, showToast } from '../api'

const router = useRouter()
const route = useRoute()
const isEditing = computed(() => Boolean(route.params.id))
const categories = ref([])
const title = ref('')
const summary = ref('')
const category = ref('')
const body = ref('')
const error = ref('')
const loading = ref(false)
const guest = ref(isGuestMode())

onMounted(async () => {
  try {
    const response = await apiFetch('/api/categories/')
    categories.value = await parseApiResponse(response)
    if (categories.value.length) category.value = categories.value[0].id
    if (isEditing.value) {
      const articleResponse = await apiFetch(`/api/articles/${route.params.id}/`)
      const article = await parseApiResponse(articleResponse)
      title.value = article.title
      summary.value = article.summary || ''
      category.value = article.category
      body.value = article.content?.body || ''
    }
  } catch (err) {
    error.value = err.message
  }
})

async function saveArticle() {
  if (guest.value) {
    showToast('游客模式下不能发布或编辑文章。')
    return
  }
  error.value = ''
  loading.value = true
  try {
    const response = await apiFetch(
      isEditing.value ? `/api/articles/${route.params.id}/` : '/api/articles/',
      {
      method: isEditing.value ? 'PATCH' : 'POST',
      body: JSON.stringify({
        title: title.value,
        summary: summary.value,
        category: Number(category.value),
        content: { format: 'markdown', body: body.value },
      }),
      },
    )
    await parseApiResponse(response)
    router.push(isEditing.value ? '/account?section=articles' : '/')
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="editor-page mx-auto">
    <h1 class="h2 mb-4">{{ isEditing ? '编辑文章' : '发布文章' }}</h1>
    <div v-if="guest" class="alert alert-secondary">
      当前为游客模式，文章编辑功能已禁用。请登录后再操作。
    </div>
    <div v-if="error" class="text-secondary">暂时无法加载编辑器。</div>
    <form @submit.prevent="saveArticle">
      <div class="mb-3">
        <label class="form-label" for="article-title">标题</label>
        <input id="article-title" v-model="title" class="form-control" :disabled="guest" required maxlength="30" />
        <div class="form-text text-end">{{ title.length }} / 30</div>
      </div>
      <div class="mb-3">
        <label class="form-label" for="article-summary">摘要</label>
        <textarea id="article-summary" v-model="summary" class="form-control" :disabled="guest" rows="3" maxlength="45"></textarea>
        <div class="form-text text-end">{{ summary.length }} / 45</div>
      </div>
      <div class="mb-3">
        <label class="form-label" for="article-category">分类</label>
        <select id="article-category" v-model="category" class="form-select" :disabled="guest" required>
          <option disabled value="">请选择分类</option>
          <option v-for="item in categories" :key="item.id" :value="item.id">
            {{ item.name }}
          </option>
        </select>
      </div>
      <div class="mb-4">
        <label class="form-label" for="article-body">Markdown 正文</label>
        <textarea id="article-body" v-model="body" class="form-control font-monospace" :disabled="guest" rows="18" required></textarea>
      </div>
      <button class="btn btn-primary" type="submit" :disabled="guest || loading || !categories.length">
        {{ loading ? (isEditing ? '保存中...' : '发布中...') : (isEditing ? '保存修改' : '发布文章') }}
      </button>
    </form>
  </div>
</template>

<style scoped>
.editor-page {
  max-width: 900px;
}
</style>
