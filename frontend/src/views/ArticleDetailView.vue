<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { apiFetch, getCurrentUser, isGuestMode, parseApiResponse, showToast } from '../api'

const route = useRoute()
const router = useRouter()
const article = ref(null)
const loading = ref(true)
const error = ref('')
const currentUser = ref(getCurrentUser())
const guest = ref(isGuestMode())
const likeState = ref({ liked: false, count: 0, loading: false })
const comments = ref([])
const commentsLoading = ref(true)
const commentsError = ref('')
const commentModal = ref(false)
const commentContent = ref('')
const commentSaving = ref(false)
const deleteCommentTarget = ref(null)
const deleteCommentSaving = ref(false)
const openCommentMenuId = ref(null)

const renderedContent = computed(() => {
  const markdown = article.value?.content?.body || ''
  return DOMPurify.sanitize(marked.parse(markdown))
})

function formatDate(value) {
  if (!value) return '未知'
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

function userPath(userId) {
  return currentUser.value?.id === userId ? '/account' : `/users/${userId}`
}

async function loadLikeState() {
  try {
    const response = await apiFetch(`/api/articles/${route.params.id}/like/`)
    const data = await parseApiResponse(response)
    likeState.value = { liked: data.liked, count: data.likes_count, loading: false }
  } catch {
    likeState.value = { liked: false, count: 0, loading: false }
  }
}

async function toggleLike() {
  if (guest.value) {
    showToast('游客模式下请先登录后再点赞。')
    return
  }
  if (likeState.value.loading || currentUser.value?.role !== 'user') return
  const previous = { ...likeState.value }
  likeState.value = { ...previous, loading: true }
  try {
    const response = await apiFetch(`/api/articles/${route.params.id}/like/`, {
      method: previous.liked ? 'DELETE' : 'POST',
    })
    const data = await parseApiResponse(response)
    likeState.value = { liked: data.liked, count: data.likes_count, loading: false }
  } catch {
    likeState.value = previous
  }
}

async function loadComments() {
  commentsLoading.value = true
  commentsError.value = ''
  try {
    const response = await apiFetch(`/api/articles/${route.params.id}/comments/`)
    comments.value = await parseApiResponse(response)
  } catch (err) {
    commentsError.value = err.message
  } finally {
    commentsLoading.value = false
  }
}

function openCommentModal() {
  commentContent.value = ''
  commentsError.value = ''
  commentModal.value = true
}

function toggleCommentMenu(commentId) {
  openCommentMenuId.value = openCommentMenuId.value === commentId ? null : commentId
}

function closeCommentModal() {
  if (commentSaving.value) return
  commentModal.value = false
}

async function publishComment() {
  if (!commentContent.value.trim()) {
    commentsError.value = '评论内容不能为空。'
    return
  }
  if (commentContent.value.length > 500) {
    commentsError.value = '评论内容不能超过500字。'
    return
  }
  commentSaving.value = true
  commentsError.value = ''
  try {
    const response = await apiFetch(`/api/articles/${route.params.id}/comments/`, {
      method: 'POST',
      body: JSON.stringify({ content: commentContent.value }),
    })
    await parseApiResponse(response)
    commentModal.value = false
    commentContent.value = ''
    await loadComments()
  } catch (err) {
    commentsError.value = err.message
  } finally {
    commentSaving.value = false
  }
}

function openDeleteComment(comment) {
  if (currentUser.value?.id !== comment.author) return
  openCommentMenuId.value = null
  deleteCommentTarget.value = comment
}

function closeDeleteComment() {
  if (deleteCommentSaving.value) return
  deleteCommentTarget.value = null
}

async function deleteComment() {
  if (!deleteCommentTarget.value || deleteCommentSaving.value) return
  deleteCommentSaving.value = true
  commentsError.value = ''
  try {
    const response = await apiFetch(`/api/comments/${deleteCommentTarget.value.id}/`, {
      method: 'DELETE',
    })
    await parseApiResponse(response)
    deleteCommentTarget.value = null
    await loadComments()
  } catch (err) {
    commentsError.value = err.message
  } finally {
    deleteCommentSaving.value = false
  }
}

function handleDocumentClick(event) {
  if (!event.target.closest('.comment-actions')) {
    openCommentMenuId.value = null
  }
}

onMounted(async () => {
  document.addEventListener('click', handleDocumentClick)
  try {
    const response = await apiFetch(`/api/articles/${route.params.id}/`)
    article.value = await parseApiResponse(response)
    await loadLikeState()
    await loadComments()
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocumentClick)
})
</script>

<template>
  <div v-if="loading" class="text-secondary">正在加载文章...</div>
  <div v-else-if="error" class="text-secondary">暂时无法加载文章。</div>
  <article v-else-if="article" class="article-detail mx-auto">
    <button class="btn btn-outline-secondary mb-4" @click="router.push('/')">
      &lt;
    </button>
    <h1 class="display-5 mb-3">{{ article.title }}</h1>
    <div class="article-meta text-secondary border-bottom pb-4 mb-4">
      <span>发布时间：{{ formatDate(article.created_at) }}</span>
      <span v-if="article.updated_at">修改时间：{{ formatDate(article.updated_at) }}</span>
      <span>作者：<router-link :to="userPath(article.author)">{{ article.author_name }}</router-link></span>
      <button
        v-if="currentUser?.role === 'user' || guest"
        class="btn btn-link text-secondary p-0 like-button"
        :class="{ liked: likeState.liked }"
        :disabled="guest || likeState.loading"
        :title="guest ? '登录后才能点赞' : '点赞或取消点赞'"
        aria-label="点赞或取消点赞"
        @click="toggleLike"
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
        <span class="ms-1">{{ likeState.count }}</span>
      </button>
    </div>
    <div class="markdown-body" v-html="renderedContent"></div>

    <section class="comments-section">
      <div class="comments-heading">
        <h2 class="h4 mb-0">评论</h2>
        <button
          v-if="currentUser?.role === 'user' || guest"
          class="btn btn-primary"
          :disabled="guest"
          :title="guest ? '登录后才能发表评论' : ''"
          @click="openCommentModal"
        >
          发布评论
        </button>
      </div>
      <div v-if="commentsLoading" class="text-secondary">正在加载评论...</div>
      <div v-else-if="commentsError" class="text-secondary">暂时无法加载评论。</div>
      <div v-else class="comments-box border rounded">
        <div v-if="comments.length === 0" class="comments-empty text-secondary">暂无评论。</div>
        <div
          v-for="comment in comments"
          :key="comment.id"
          class="comment-item"
        >
          <div class="comment-header">
            <div class="comment-meta">
              <router-link :to="userPath(comment.author)">{{ comment.author_name }}</router-link>
              <span>{{ formatDate(comment.created_at) }}</span>
            </div>
            <div v-if="currentUser?.id === comment.author" class="comment-actions" @click.stop>
              <button
                type="button"
                class="comment-menu-button"
                aria-label="评论操作"
                :aria-expanded="openCommentMenuId === comment.id"
                @click="toggleCommentMenu(comment.id)"
              >
                <span aria-hidden="true">⋮</span>
              </button>
              <div v-if="openCommentMenuId === comment.id" class="comment-menu-dropdown">
                <button type="button" class="comment-menu-item" @click="openDeleteComment(comment)">
                  删除
                </button>
              </div>
            </div>
          </div>
          <div class="comment-content">{{ comment.content }}</div>
        </div>
      </div>
    </section>
  </article>

  <div v-if="commentModal" class="modal-backdrop-custom" @click.self="closeCommentModal">
    <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="comment-title">
      <div class="modal-header-custom">
        <h2 id="comment-title" class="h5 mb-0">发布评论</h2>
        <button class="btn-close" aria-label="关闭" @click="closeCommentModal"></button>
      </div>
      <form @submit.prevent="publishComment">
        <div class="modal-body-custom">
          <label class="form-label" for="comment-content">评论内容</label>
          <textarea
            id="comment-content"
            v-model="commentContent"
            class="form-control"
            rows="5"
            maxlength="500"
            required
          ></textarea>
          <div class="text-end text-secondary small mt-1">{{ commentContent.length }}/500</div>
        </div>
        <div class="modal-footer-custom">
          <button type="button" class="btn btn-outline-secondary" :disabled="commentSaving" @click="closeCommentModal">
            取消
          </button>
          <button type="submit" class="btn btn-primary" :disabled="commentSaving">
            {{ commentSaving ? '发布中...' : '发布' }}
          </button>
        </div>
      </form>
    </div>
  </div>

  <div v-if="deleteCommentTarget" class="modal-backdrop-custom" @click.self="closeDeleteComment">
    <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="delete-comment-title">
      <div class="modal-header-custom">
        <h2 id="delete-comment-title" class="h5 mb-0">删除评论</h2>
        <button class="btn-close" aria-label="关闭" @click="closeDeleteComment"></button>
      </div>
      <div class="modal-body-custom">确定要删除这条评论吗？</div>
      <div class="modal-footer-custom">
        <button class="btn btn-outline-secondary" :disabled="deleteCommentSaving" @click="closeDeleteComment">
          取消
        </button>
        <button class="btn btn-danger" :disabled="deleteCommentSaving" @click="deleteComment">
          {{ deleteCommentSaving ? '删除中...' : '确认删除' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.article-detail {
  max-width: 820px;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  flex-wrap: wrap;
}

.like-button {
  text-decoration: none;
}

.like-button.liked {
  color: #0d6efd !important;
}

.thumb-icon {
  width: 1.1rem;
  height: 1.1rem;
  vertical-align: -0.2rem;
}

.comments-section {
  margin-top: 3rem;
}

.comments-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.comments-box {
  min-height: 180px;
  overflow: hidden;
}

.comments-empty {
  padding: 2rem;
  text-align: center;
}

.comment-item {
  padding: 1rem 1.25rem;
}

.comment-item + .comment-item {
  border-top: 1px solid #dee2e6;
}

.comment-meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.5rem;
  color: #6c757d;
  font-size: 0.875rem;
}

.comment-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.comment-actions {
  position: relative;
}

.comment-menu-button {
  width: 2rem;
  height: 2rem;
  padding: 0;
  border: 0;
  background: transparent;
  color: #6c757d;
  font-size: 1.5rem;
  line-height: 1;
}

.comment-menu-button:hover,
.comment-menu-button:focus-visible {
  color: #212529;
}

.comment-menu-dropdown {
  position: absolute;
  top: 2rem;
  right: 0;
  z-index: 10;
  min-width: 5rem;
  padding: 0.25rem 0;
  background: #fff;
  border: 1px solid #dee2e6;
  border-radius: 0.375rem;
  box-shadow: 0 0.25rem 0.75rem rgb(0 0 0 / 15%);
}

.comment-menu-item {
  display: block;
  width: 100%;
  padding: 0.375rem 0.75rem;
  border: 0;
  background: transparent;
  color: #dc3545;
  text-align: left;
}

.comment-menu-item:hover,
.comment-menu-item:focus-visible {
  background: #f8d7da;
}

.comment-content {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
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

.modal-card {
  width: min(100%, 480px);
  background: #fff;
  border-radius: 0.5rem;
  box-shadow: 0 0.5rem 1rem rgb(0 0 0 / 15%);
}

.modal-header-custom,
.modal-footer-custom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #dee2e6;
}

.modal-body-custom {
  padding: 1.25rem;
}

.modal-footer-custom {
  justify-content: flex-end;
  gap: 0.5rem;
  border-top: 1px solid #dee2e6;
  border-bottom: 0;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3) {
  margin-top: 1.75rem;
}

.markdown-body :deep(pre) {
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 0.375rem;
}

.markdown-body :deep(code) {
  color: #d63384;
}
</style>
