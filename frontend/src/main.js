import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import 'bootstrap-icons/font/bootstrap-icons.css'

import App from './App.vue'
import HomeView from './views/HomeView.vue'
import LoginView from './views/LoginView.vue'
import RegisterView from './views/RegisterView.vue'
import ArticleDetailView from './views/ArticleDetailView.vue'
import ArticleEditorView from './views/ArticleEditorView.vue'
import CategoryEditorView from './views/CategoryEditorView.vue'
import AccountView from './views/AccountView.vue'
import UserProfileView from './views/UserProfileView.vue'
import AdminLoginView from './views/AdminLoginView.vue'
import AdminRegisterView from './views/AdminRegisterView.vue'
import AdminView from './views/AdminView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: LoginView },
    { path: '/register', component: RegisterView },
    { path: '/admin/login', component: AdminLoginView },
    { path: '/admin/register', component: AdminRegisterView },
    { path: '/admin', component: AdminView, meta: { requiresAuth: true } },
    { path: '/', component: HomeView },
    { path: '/articles/new', component: ArticleEditorView },
    { path: '/categories/new', component: CategoryEditorView },
    { path: '/articles/:id/edit', component: ArticleEditorView },
    { path: '/articles/:id', component: ArticleDetailView },
    { path: '/account', component: AccountView },
    { path: '/users/:id', component: UserProfileView },
  ],
})

router.beforeEach((to) => {
  const accessToken = localStorage.getItem('access_token')
  const guestMode = localStorage.getItem('guest_mode') === 'true'
  const publicPaths = ['/login', '/register', '/admin/login', '/admin/register']
  if (to.path === '/admin' && (!accessToken || guestMode)) {
    return { path: '/admin/login', query: { next: to.fullPath } }
  }
  if (!accessToken && !guestMode && !publicPaths.includes(to.path)) {
    return { path: '/login', query: { next: to.fullPath } }
  }
  if (publicPaths.includes(to.path) && accessToken) {
    return '/'
  }
})

createApp(App).use(router).mount('#app')
