<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch, parseApiResponse } from '../api'

const router = useRouter()
const name = ref('')
const error = ref('')
const loading = ref(false)

async function createCategory() {
  error.value = ''
  loading.value = true
  try {
    const response = await apiFetch('/api/categories/', {
      method: 'POST',
      body: JSON.stringify({ name: name.value }),
    })
    await parseApiResponse(response)
    router.push('/')
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="category-editor mx-auto">
    <h1 class="h2 mb-4">添加分类</h1>
    <div v-if="error" class="text-secondary">暂时无法加载分类编辑器。</div>
    <form @submit.prevent="createCategory">
      <div class="mb-4">
        <label class="form-label" for="category-name">分类名称</label>
        <input id="category-name" v-model="name" class="form-control" required maxlength="100" />
      </div>
      <button class="btn btn-primary" type="submit" :disabled="loading">
        {{ loading ? '保存中...' : '保存分类' }}
      </button>
    </form>
  </div>
</template>

<style scoped>
.category-editor {
  max-width: 600px;
}
</style>
