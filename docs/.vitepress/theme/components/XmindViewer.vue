<template>
  <div class="xmind-wrapper">
    <div ref="container" class="xmind-container" :style="{ height: pxHeight }"></div>
    <p v-if="loading" class="xmind-status loading">⏳ 加载中...</p>
    <p v-if="error" class="xmind-status error">⚠️ 加载失败：{{ error }}</p>
    <p v-if="!loading && !error" class="xmind-hint">💡 右键拖拽平移 · 滚轮缩放</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  src: { type: String, required: true },
  height: { type: [String, Number], default: 700 },
})

const pxHeight = computed(() =>
  typeof props.height === 'number' ? props.height + 'px' : props.height
)

const container = ref(null)
const loading = ref(true)
const error = ref(null)
let viewer = null

async function loadFile(url) {
  loading.value = true
  error.value = null
  try {
    const response = await fetch(url)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const arrayBuffer = await response.arrayBuffer()
    viewer.load(arrayBuffer)
  } catch (e) {
    error.value = e.message
  }
}

onMounted(async () => {
  if (!container.value) return

  try {
    const mod = await import('xmind-embed-viewer')
    const { XMindEmbedViewer } = mod.default || mod

    viewer = new XMindEmbedViewer({
      el: container.value,
      region: 'cn',
      styles: {
        height: pxHeight.value,
        width: '100%',
      },
    })

    viewer.addEventListener('map-ready', () => {
      viewer.setFitMap()
      loading.value = false
    })

    await loadFile(props.src)
  } catch (e) {
    error.value = e.message
    loading.value = false
  }
})

watch(() => props.src, (newSrc) => {
  if (viewer) loadFile(newSrc)
})

onUnmounted(() => {
  viewer = null
})
</script>

<style scoped>
.xmind-wrapper {
  margin: 1.5rem 0;
}
.xmind-container {
  width: 100%;
  min-height: 400px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}
.xmind-status {
  font-size: 0.9rem;
  margin-top: 0.5rem;
}
.xmind-status.loading {
  color: var(--vp-c-text-2);
}
.xmind-status.error {
  color: var(--vp-c-danger-1);
}
.xmind-hint {
  font-size: 0.85rem;
  color: var(--vp-c-text-3);
  margin-top: 0.4rem;
}
</style>
