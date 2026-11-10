<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiFetch, parseApiResponse, setGuestMode, setSession, showToast } from '../api'

const router = useRouter()
const route = useRoute()
const username = ref('')
const password = ref('')
const showPassword = ref(false)
const error = ref('')
const loading = ref(false)

onMounted(() => {
  if (route.query.registered) showToast('注册成功，请登录。', 'success')
})

async function submit() {
  error.value = ''
  loading.value = true
  try {
    const loginResponse = await apiFetch('/api/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ username: username.value, password: password.value }),
    })
    const tokenData = await parseApiResponse(loginResponse)
    const userResponse = await apiFetch('/api/auth/me/', {
      headers: { Authorization: `Bearer ${tokenData.access}` },
    })
    const user = await parseApiResponse(userResponse)
    setSession(tokenData, user)
    router.push(user.role === 'admin' ? '/admin' : (route.query.next || '/'))
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

function browseAsGuest() {
  setGuestMode()
  router.push('/')
}
</script>

<template>
  <div class="row justify-content-center">
    <div class="col-12 col-md-6 col-lg-4">
      <div class="card shadow-sm">
        <div class="card-body p-4">
          <h1 class="h3 mb-4 text-center">登录 Blog</h1>
          <form @submit.prevent="submit">
            <div class="mb-3">
              <label class="form-label" for="username">用户名</label>
              <input id="username" v-model="username" class="form-control" required autocomplete="username" />
            </div>
            <div class="mb-4">
              <label class="form-label" for="password">密码</label>
              <div class="password-input-group">
                <input id="password" v-model="password" :type="showPassword ? 'text' : 'password'" class="form-control" required autocomplete="current-password" />
                <button type="button" class="password-toggle" :aria-label="showPassword ? '隐藏密码' : '显示密码'" @click="showPassword = !showPassword">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6Z" />
                    <circle cx="12" cy="12" r="2.5" />
                  </svg>
                </button>
              </div>
            </div>
            <button class="btn btn-primary w-100" type="submit" :disabled="loading">
              {{ loading ? '登录中...' : '登录' }}
            </button>
            <div class="text-center mt-3">
              <span class="text-secondary">没有账号？</span>
              <router-link class="ms-1" to="/register">立即注册</router-link>
            </div>
            <div class="text-center mt-2">
              <a href="/admin/login">管理员登录</a>
            </div>
            <div class="text-center mt-2">
              <button type="button" class="btn btn-link p-0" @click="browseAsGuest">
                以游客身份浏览
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
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
</style>
