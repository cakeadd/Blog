<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch, parseApiResponse, showToast } from '../api'

const router = useRouter()
const username = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const initialized = ref(false)

onMounted(async () => {
  try {
    const response = await apiFetch('/api/admin/setup/')
    const data = await parseApiResponse(response)
    initialized.value = data.initialized
  } catch {
    // 请求错误由统一提示处理。
  }
})

async function submit() {
  loading.value = true
  try {
    const response = await apiFetch('/api/admin/setup/', {
      method: 'POST',
      body: JSON.stringify({ username: username.value, password: password.value }),
    })
    await parseApiResponse(response)
    router.push({ path: '/admin/login', query: { registered: '1' } })
  } catch {
    // 请求错误由统一提示处理。
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="row justify-content-center">
    <div class="col-12 col-md-6 col-lg-4">
      <div class="card shadow-sm">
        <div class="card-body p-4">
          <h1 class="h3 mb-4 text-center">注册 Admin</h1>
          <div v-if="initialized" class="text-secondary mb-3">管理员账号已经存在，不能重复注册。</div>
          <form v-else @submit.prevent="submit">
            <div class="mb-3">
              <label class="form-label" for="admin-register-username">用户名</label>
              <input id="admin-register-username" v-model="username" class="form-control" required autocomplete="username" />
            </div>
            <div class="mb-4">
              <label class="form-label" for="admin-register-password">密码</label>
              <div class="password-input-group">
                <input id="admin-register-password" v-model="password" :type="showPassword ? 'text' : 'password'" class="form-control" required autocomplete="new-password" />
                <button type="button" class="password-toggle" :aria-label="showPassword ? '隐藏密码' : '显示密码'" @click="showPassword = !showPassword">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6Z" /><circle cx="12" cy="12" r="2.5" />
                  </svg>
                </button>
              </div>
            </div>
            <button class="btn btn-primary w-100" type="submit" :disabled="loading">
              {{ loading ? '注册中...' : '注册' }}
            </button>
          </form>
          <div class="text-center mt-3">
            <router-link to="/admin/login">返回 Admin 登录</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.password-input-group { position: relative; }
.password-input-group .form-control { padding-right: 2.75rem; }
.password-toggle { position: absolute; top: 50%; right: 0.65rem; display: inline-flex; padding: 0; border: 0; background: transparent; color: #6c757d; transform: translateY(-50%); }
.password-toggle svg { width: 1.15rem; height: 1.15rem; }
</style>
