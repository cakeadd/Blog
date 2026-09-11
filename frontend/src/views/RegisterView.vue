<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch, parseApiResponse, showToast } from '../api'

const router = useRouter()
const username = ref('')
const password = ref('')
const passwordConfirm = ref('')
const showPassword = ref(false)
const showPasswordConfirm = ref(false)
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  if (password.value !== passwordConfirm.value) {
    showToast('两次输入的密码不一致。')
    return
  }

  loading.value = true
  try {
    const response = await apiFetch('/api/auth/register/', {
      method: 'POST',
      body: JSON.stringify({
        username: username.value,
        password: password.value,
        password_confirm: passwordConfirm.value,
      }),
    })
    await parseApiResponse(response)
    router.push({ path: '/login', query: { registered: '1' } })
  } catch (err) {
    error.value = err.message
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
          <h1 class="h3 mb-4 text-center">注册 Blog</h1>
          <form @submit.prevent="submit">
            <div class="mb-3">
              <label class="form-label" for="register-username">用户名</label>
              <input
                id="register-username"
                v-model="username"
                class="form-control"
                required
                autocomplete="username"
              />
            </div>
            <div class="mb-3">
              <label class="form-label" for="register-password">密码</label>
              <div class="password-input-group">
                <input
                  id="register-password"
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  class="form-control"
                  required
                  autocomplete="new-password"
                />
                <button type="button" class="password-toggle" :aria-label="showPassword ? '隐藏密码' : '显示密码'" @click="showPassword = !showPassword">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6Z" />
                    <circle cx="12" cy="12" r="2.5" />
                  </svg>
                </button>
              </div>
            </div>
            <div class="mb-4">
              <label class="form-label" for="register-password-confirm">确认密码</label>
              <div class="password-input-group">
                <input
                  id="register-password-confirm"
                  v-model="passwordConfirm"
                  :type="showPasswordConfirm ? 'text' : 'password'"
                  class="form-control"
                  required
                  autocomplete="new-password"
                />
                <button type="button" class="password-toggle" :aria-label="showPasswordConfirm ? '隐藏确认密码' : '显示确认密码'" @click="showPasswordConfirm = !showPasswordConfirm">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6Z" />
                    <circle cx="12" cy="12" r="2.5" />
                  </svg>
                </button>
              </div>
            </div>
            <button class="btn btn-primary w-100" type="submit" :disabled="loading">
              {{ loading ? '注册中...' : '注册' }}
            </button>
            <div class="text-center mt-3">
              <router-link to="/login">返回登录</router-link>
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
