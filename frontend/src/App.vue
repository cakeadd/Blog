<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { clearSession, getAccessToken, getCurrentUser } from './api'

const router = useRouter()
const route = useRoute()
const loggedIn = ref(Boolean(getAccessToken()))
const user = ref(getCurrentUser())
const toast = ref(null)
let toastTimer = null

const showBar = computed(() => (
  route.path !== '/login'
  && !route.path.startsWith('/admin')
  && route.path !== '/articles/new'
  && !route.path.endsWith('/edit')
  && loggedIn.value
))

watch(() => route.path, () => {
  loggedIn.value = Boolean(getAccessToken())
  user.value = getCurrentUser()
})

function logout() {
  clearSession()
  loggedIn.value = false
  user.value = null
  router.push('/login')
}

function handleUserUpdated(event) {
  user.value = event.detail
}

function handleToast(event) {
  toast.value = event.detail
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => {
    toast.value = null
    toastTimer = null
  }, 5000)
}

onMounted(() => {
  window.addEventListener('blog-user-updated', handleUserUpdated)
  window.addEventListener('blog-toast', handleToast)
  if (window.__blogToast) {
    handleToast({ detail: window.__blogToast })
    window.__blogToast = null
  }
})
onBeforeUnmount(() => {
  window.removeEventListener('blog-user-updated', handleUserUpdated)
  window.removeEventListener('blog-toast', handleToast)
  if (toastTimer) clearTimeout(toastTimer)
})
</script>

<template>
  <div>
    <div v-if="toast" class="global-toast" :class="`toast-${toast.type}`" role="alert">
      {{ toast.message }}
    </div>
    <header v-if="showBar" class="blog-bar border-bottom">
      <div class="container d-flex align-items-center justify-content-between py-3">
        <div v-if="route.path === '/' && user?.role === 'user'" class="d-flex gap-2">
          <button class="btn btn-primary" @click="router.push('/articles/new')">
            发布文章
          </button>
          <button class="btn btn-outline-primary" @click="router.push('/categories/new')">
            添加分类
          </button>
        </div>
        <span v-else-if="user?.role === 'admin'" class="text-secondary small">管理员页面暂未实现</span>
        <div class="d-flex align-items-center gap-3 ms-auto">
          <router-link class="user-link" to="/account">
            <img v-if="user?.avatar_url" :src="user.avatar_url" class="header-avatar" alt="用户头像" />
            <span v-else>{{ user?.username || '用户' }}</span>
          </router-link>
          <button class="btn btn-sm btn-outline-secondary" @click="logout">退出</button>
        </div>
      </div>
    </header>
    <main class="container py-5">
      <router-view @logged-in="(payload) => { loggedIn = true; user = payload }" />
    </main>
  </div>
</template>

<style scoped>
.blog-bar {
  background: #ffffff;
}

.user-link {
  color: #212529;
  text-decoration: none;
}

.user-link:hover {
  color: #0d6efd;
}

.header-avatar {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  object-fit: cover;
  vertical-align: middle;
}

.global-toast {
  position: fixed;
  top: 1.25rem;
  left: 50%;
  z-index: 2000;
  max-width: min(90vw, 520px);
  padding: 0.75rem 1.25rem;
  border: 1px solid transparent;
  border-radius: 0.375rem;
  box-shadow: 0 0.25rem 0.75rem rgb(0 0 0 / 15%);
  transform: translateX(-50%);
}

.toast-error {
  border-color: #f1aeb5;
  background: #f8d7da;
  color: #842029;
}

.toast-success {
  border-color: #badbcc;
  background: #d1e7dd;
  color: #0f5132;
}
</style>
