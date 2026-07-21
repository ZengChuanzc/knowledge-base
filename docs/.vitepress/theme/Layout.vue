<template>
  <div class="vp-wrapper">
    <ParticleBg />
    <MusicPlayer />
    <DefaultTheme.Layout />
  </div>
</template>

<script setup lang="ts">
import DefaultTheme from 'vitepress/theme'
import ParticleBg from './components/ParticleBg.vue'
import MusicPlayer from './components/MusicPlayer.vue'
import { onMounted, watch } from 'vue'
import { useRoute } from 'vitepress'

const route = useRoute()
const PAGE_SIZE = 10

function setupPagination(): void {
  const container = document.getElementById('article-list-container')
  if (!container) return

  const items = container.querySelectorAll<HTMLElement>('.article-page-item')
  if (items.length === 0) return

  const totalPages = Math.ceil(items.length / PAGE_SIZE)
  let currentPage = 1

  function renderPage(page: number): void {
    currentPage = page
    items.forEach((item, i) => {
      const p = Math.floor(i / PAGE_SIZE) + 1
      item.style.display = p === page ? '' : 'none'
    })
    renderPagination()
  }

  function renderPagination(): void {
    const el = document.getElementById('article-pagination')
    if (!el) return
    if (totalPages <= 1) { el.innerHTML = ''; return }

    let h = '<div class="pagination-controls">'
    h += currentPage > 1
      ? '<button class="pagination-btn" onclick="window.__gp(' + (currentPage - 1) + ')">‹ 上一页</button>'
      : '<button class="pagination-btn pagination-btn-disabled" disabled>‹ 上一页</button>'

    for (let i = 1; i <= totalPages; i++) {
      h += i === currentPage
        ? '<span class="pagination-current">' + i + '</span>'
        : '<button class="pagination-btn" onclick="window.__gp(' + i + ')">' + i + '</button>'
    }

    h += currentPage < totalPages
      ? '<button class="pagination-btn" onclick="window.__gp(' + (currentPage + 1) + ')">下一页 ›</button>'
      : '<button class="pagination-btn pagination-btn-disabled" disabled>下一页 ›</button>'

    h += '</div><div class="pagination-info">共 ' + items.length + ' 篇 · 第 ' + currentPage + ' / ' + totalPages + ' 页</div>'
    el.innerHTML = h
  }

  // 清理旧引用，设置新引用
  ;(window as any).__gp = renderPage
  renderPage(1)
}

// 判断当前路由是否为文章列表页
function isArticlesPage(path: string): boolean {
  return path.includes('/articles/') && (path.endsWith('/') || path.endsWith('index.html'))
}

// 首次挂载时设置
onMounted(() => {
  if (isArticlesPage(route.path)) {
    // 用 requestAnimationFrame 确保 DOM 渲染完成
    requestAnimationFrame(() => setupPagination())
  }
})

// 路由变化时重新设置（处理 SPA 导航）
watch(
  () => route.path,
  (path) => {
    if (isArticlesPage(path)) {
      // 下一帧确保 DOM 已更新
      requestAnimationFrame(() => setupPagination())
    }
  }
)
</script>

<style>
.vp-wrapper {
  position: relative;
  min-height: 100vh;
  overflow-x: hidden;
}
</style>
