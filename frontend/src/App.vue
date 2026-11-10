<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { clearSession, getAccessToken, getCurrentUser, isGuestMode } from './api'

const router = useRouter()
const route = useRoute()
const loggedIn = ref(Boolean(getAccessToken()))
const guest = ref(isGuestMode())
const user = ref(getCurrentUser())
const guestMenuOpen = ref(false)
const guestMenuRef = ref(null)
const toast = ref(null)
let toastTimer = null

const showBar = computed(() => (
  route.path !== '/login'
  && !route.path.startsWith('/admin')
  && route.path !== '/articles/new'
  && !route.path.endsWith('/edit')
  && (loggedIn.value || guest.value)
))

watch(() => route.path, () => {
  loggedIn.value = Boolean(getAccessToken())
  guest.value = isGuestMode()
  user.value = getCurrentUser()
})

function logout() {
  clearSession()
  loggedIn.value = false
  user.value = null
  guest.value = false
  router.push('/login')
}

function closeGuestMenuOutside(event) {
  if (guestMenuRef.value && !guestMenuRef.value.contains(event.target)) {
    guestMenuOpen.value = false
  }
}

function handleUserUpdated(event) {
  user.value = event.detail
}

function handleAuthUpdated() {
  loggedIn.value = Boolean(getAccessToken())
  guest.value = isGuestMode()
  user.value = getCurrentUser()
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
  window.addEventListener('blog-auth-updated', handleAuthUpdated)
  document.addEventListener('click', closeGuestMenuOutside)
  if (window.__blogToast) {
    handleToast({ detail: window.__blogToast })
    window.__blogToast = null
  }
})
onBeforeUnmount(() => {
  window.removeEventListener('blog-user-updated', handleUserUpdated)
  window.removeEventListener('blog-toast', handleToast)
  window.removeEventListener('blog-auth-updated', handleAuthUpdated)
  document.removeEventListener('click', closeGuestMenuOutside)
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
        <div v-if="route.path === '/' && (user?.role === 'user' || guest)" class="d-flex gap-2">
          <button class="btn btn-primary" :disabled="guest" :title="guest ? '登录后才能发布文章' : ''" @click="router.push('/articles/new')">
            发布文章
          </button>
          <button class="btn btn-outline-primary" :disabled="guest" :title="guest ? '登录后才能添加分类' : ''" @click="router.push('/categories/new')">
            添加分类
          </button>
        </div>
        <span v-else-if="user?.role === 'admin'" class="text-secondary small">管理员页面暂未实现</span>
        <div class="d-flex align-items-center gap-3 ms-auto">
          <router-link v-if="!guest" class="user-link" to="/account">
            <img v-if="user?.avatar_url" :src="user.avatar_url" class="header-avatar" alt="用户头像" />
            <span v-else>{{ user?.username || '用户' }}</span>
          </router-link>
          <div v-else ref="guestMenuRef" class="guest-menu">
            <button class="btn btn-sm btn-outline-secondary" @click.stop="guestMenuOpen = !guestMenuOpen">
              <i class="bi bi-person" aria-hidden="true"></i>
              <span class="ms-1">游客</span>
              <i class="bi bi-chevron-down ms-1" aria-hidden="true"></i>
            </button>
            <div v-if="guestMenuOpen" class="guest-dropdown border rounded shadow-sm">
              <div class="guest-dropdown-label">当前为游客模式</div>
              <router-link to="/login" @click="guestMenuOpen = false">登录</router-link>
              <router-link to="/register" @click="guestMenuOpen = false">注册</router-link>
            </div>
          </div>
          <button v-if="!guest" class="btn btn-sm btn-outline-secondary" @click="logout">退出</button>
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

.guest-menu {
  position: relative;
}

.guest-dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  z-index: 1000;
  min-width: 9rem;
  padding: 0.35rem 0;
  background: #fff;
}

.guest-dropdown-label {
  padding: 0.4rem 0.75rem;
  color: #6c757d;
  font-size: 0.85rem;
}

.guest-dropdown a {
  display: block;
  padding: 0.4rem 0.75rem;
  color: #212529;
  text-decoration: none;
}

.guest-dropdown a:hover {
  background: #f8f9fa;
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
