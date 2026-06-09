<template>
  <div class="music-player" :class="{ expanded }">
    <!-- 悬浮按钮（收起状态） -->
    <button
      class="player-toggle"
      :class="{ playing: isPlaying }"
      @click="toggleExpand"
      :title="isPlaying ? currentSong?.name || '音乐播放中' : '打开音乐播放器'"
    >
      <span class="icon-note">🎵</span>
      <span v-if="isPlaying" class="icon-equalizer">
        <span></span><span></span><span></span>
      </span>
    </button>

    <!-- 展开面板 -->
    <transition name="slide">
      <div v-show="expanded" class="player-panel">
        <!-- 顶部 -->
        <div class="panel-header">
          <span class="panel-title">🎶 音乐</span>
          <div class="header-tabs">
            <button :class="{ active: tab === 'local' }" @click="tab = 'local'">本地</button>
            <button :class="{ active: tab === 'search' }" @click="tab = 'search'">在线</button>
          </div>
          <button class="btn-close" @click="expanded = false">✕</button>
        </div>

        <!-- 当前播放 -->
        <div class="now-playing">
          <div class="cover-placeholder">
            <img v-if="currentSong?.cover" :src="currentSong.cover" alt="" />
            <span v-else>{{ currentSong ? currentSong.name[0] : '?' }}</span>
          </div>
          <div class="song-info">
            <p class="song-name">{{ currentSong?.name || '未播放' }}</p>
            <p class="song-artist">{{ currentSong?.artist || '搜索在线音乐' }}</p>
          </div>
        </div>

        <!-- 播放控制 -->
        <div class="controls">
          <button class="ctrl-btn" @click="prev" title="上一首">⏮</button>
          <button class="ctrl-btn play-btn" @click="togglePlay" title="播放/暂停">
            {{ isPlaying ? '⏸' : '▶️' }}
          </button>
          <button class="ctrl-btn" @click="next" title="下一首">⏭</button>
        </div>

        <!-- 进度条 -->
        <div class="progress-area">
          <span class="time">{{ formatTime(currentTime) }}</span>
          <input
            type="range"
            class="progress-bar"
            min="0"
            :max="duration || 0"
            :value="currentTime"
            @input="seek"
          />
          <span class="time">{{ formatTime(duration) }}</span>
        </div>

        <!-- 音量 -->
        <div class="volume-area">
          <span>🔊</span>
          <input
            type="range"
            class="volume-bar"
            min="0" max="1" step="0.05"
            :value="volume"
            @input="setVolume"
          />
        </div>

        <!-- ======== 本地歌单 ======== -->
        <div v-show="tab === 'local'" class="playlist">
          <div
            v-for="(song, i) in localPlaylist"
            :key="'l' + i"
            class="playlist-item"
            :class="{ active: i === currentIndex && mode === 'local' }"
            @click="playLocal(i)"
          >
            <span class="item-idx">{{ i + 1 }}</span>
            <span class="item-name">{{ song.name }}</span>
            <span class="item-artist">{{ song.artist }}</span>
          </div>
          <div v-if="localPlaylist.length === 0" class="playlist-empty">
            暂无本地音乐 · 将 .mp3 放入 <code>public/music/</code> 并编辑歌单
          </div>
        </div>

        <!-- ======== 在线搜索 ======== -->
        <div v-show="tab === 'search'" class="playlist search-panel">
          <div class="search-box">
            <input
              ref="searchInput"
              v-model="searchQuery"
              type="text"
              placeholder="搜索歌曲（模糊匹配）…"
              @keydown.enter="doSearch"
            />
            <button class="search-btn" @click="doSearch" :disabled="searching">
              {{ searching ? '…' : '🔍' }}
            </button>
          </div>

          <div v-if="searchError" class="search-status error">{{ searchError }}</div>
          <div v-if="searching" class="search-status">搜索中…</div>
          <div v-if="!searching && searchDone && searchResults.length === 0" class="search-status">
            未找到结果
          </div>

          <div
            v-for="(song, i) in searchResults"
            :key="'s' + song.id"
            class="playlist-item"
            :class="{ active: song.id === currentIndex && mode === 'online' }"
            @click="playOnline(song, i)"
          >
            <span class="item-idx">{{ i + 1 }}</span>
            <span class="item-name">{{ song.name }}</span>
            <span class="item-artist">{{ song.artist }}</span>
          </div>
        </div>

        <!-- 底部 -->
        <div class="panel-footer">
          在线音乐由 网易云音乐 提供 · 仅限个人学习
        </div>
      </div>
    </transition>

    <audio
      ref="audioEl"
      @timeupdate="onTimeUpdate"
      @loadedmetadata="onLoaded"
      @ended="next"
      @error="onAudioError"
    ></audio>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

/* ============================================================
   配置区 — 按需修改
   ============================================================ */

/** 网易云音乐 API 代理地址
 *  - 推荐自建: https://github.com/Binaryify/NeteaseCloudMusicApi
 *  - 也可使用公开代理（稳定性自测）
 */
const API_BASE = 'https://music-api.codepoint.net'

/* ============================================================ */

/* ---- 类型 ---- */
interface Song {
  id: number | string
  name: string
  artist: string
  src?: string
  cover?: string
}

/* ---- 本地歌单 ---- */
const localPlaylist: Song[] = [
  // 例: { name: '七里香', artist: '周杰伦', src: '/music/七里香.mp3' },
]

/* ============================================================ */

/* ---- 状态 ---- */
const expanded = ref(false)
const isPlaying = ref(false)
const currentIndex = ref(0)
const currentTime = ref(0)
const duration = ref(0)
const volume = ref(0.5)
const audioEl = ref<HTMLAudioElement | null>(null)
const tab = ref<'local' | 'search'>('local')
const mode = ref<'local' | 'online'>('local')

/* 在线搜索 */
const searchQuery = ref('')
const searchInput = ref<HTMLInputElement | null>(null)
const searchResults = ref<Song[]>([])
const searching = ref(false)
const searchDone = ref(false)
const searchError = ref('')

/* 缓存已获取的歌曲 URL 避免重复请求 */
const urlCache = new Map<number | string, string>()

const currentSong = computed(() => {
  if (mode.value === 'local') return localPlaylist[currentIndex.value] || null
  return searchResults.value[currentIndex.value] || null
})

/* ============================================================ */

/* ---- 本地播放 ---- */
function playLocal(i: number) {
  const song = localPlaylist[i]
  if (!song || !audioEl.value) return
  mode.value = 'local'
  currentIndex.value = i
  currentTime.value = 0
  duration.value = 0
  audioEl.value.src = song.src || ''
  audioEl.value.load()
  audioEl.value.play().then(() => { isPlaying.value = true }).catch(() => {})
}

/* ---- 在线搜索 ---- */
async function doSearch() {
  const q = searchQuery.value.trim()
  if (!q) return

  searching.value = true
  searchError.value = ''
  searchDone.value = false

  try {
    const res = await fetch(`${API_BASE}/search?keywords=${encodeURIComponent(q)}&limit=30`, {
      signal: AbortSignal.timeout(8000),
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const json = await res.json()

    const songs = json?.result?.songs
    if (!songs || !Array.isArray(songs)) {
      searchResults.value = []
      searchDone.value = true
      return
    }

    searchResults.value = songs.map((s: any) => ({
      id: s.id,
      name: s.name || '未知',
      artist: s.artists?.map((a: any) => a.name).join(', ') || '未知',
      cover: s.album?.picUrl || '',
    }))
    searchDone.value = true

    // 自动切到第一个结果
    if (searchResults.value.length > 0) {
      playOnline(searchResults.value[0], 0)
    }
  } catch (e: any) {
    if (e.name === 'TimeoutError') {
      searchError.value = '请求超时，API 地址可能不可用'
    } else if (e.name === 'AbortError') {
      return
    } else {
      searchError.value = `搜索失败: ${e.message}`
    }
    searchResults.value = []
  } finally {
    searching.value = false
  }
}

async function playOnline(song: Song, i: number) {
  if (!audioEl.value) return
  mode.value = 'online'
  currentIndex.value = i
  currentTime.value = 0
  duration.value = 0

  // 优先从缓存取
  let url = urlCache.get(song.id)
  if (!url) {
    try {
      const res = await fetch(`${API_BASE}/song/url?id=${song.id}`, {
        signal: AbortSignal.timeout(6000),
      })
      const json = await res.json()
      url = json?.data?.[0]?.url || ''
      if (url) urlCache.set(song.id, url)
    } catch {
      url = ''
    }
  }

  if (!url) {
    searchError.value = '⚠️ 无法获取播放地址（歌曲可能需要版权或 API 受限）'
    return
  }

  audioEl.value.src = url
  audioEl.value.load()
  audioEl.value.play().then(() => { isPlaying.value = true }).catch(() => {})
}

/* ---- 通用控制 ---- */
function toggleExpand() {
  expanded.value = !expanded.value
  if (expanded.value && tab.value === 'search') {
    setTimeout(() => searchInput.value?.focus(), 300)
  }
}

function togglePlay() {
  if (!audioEl.value || !currentSong.value) return
  if (isPlaying.value) {
    audioEl.value.pause()
    isPlaying.value = false
  } else {
    audioEl.value.play().then(() => { isPlaying.value = true }).catch(() => {})
  }
}

function prev() {
  const list = mode.value === 'local' ? localPlaylist : searchResults.value
  if (list.length === 0) return
  const i = (currentIndex.value - 1 + list.length) % list.length
  if (mode.value === 'local') playLocal(i)
  else playOnline(list[i], i)
}

function next() {
  const list = mode.value === 'local' ? localPlaylist : searchResults.value
  if (list.length === 0) return
  const i = (currentIndex.value + 1) % list.length
  if (mode.value === 'local') playLocal(i)
  else playOnline(list[i], i)
}

function seek(e: Event) {
  const val = parseFloat((e.target as HTMLInputElement).value)
  if (audioEl.value) audioEl.value.currentTime = val
  currentTime.value = val
}

function setVolume(e: Event) {
  const val = parseFloat((e.target as HTMLInputElement).value)
  if (audioEl.value) audioEl.value.volume = val
  volume.value = val
}

function onTimeUpdate() {
  if (audioEl.value) currentTime.value = audioEl.value.currentTime
}

function onLoaded() {
  if (audioEl.value) duration.value = audioEl.value.duration
}

function onAudioError() {
  if (mode.value === 'online') {
    searchError.value = '⚠️ 播放失败，可能版权受限或链接已过期'
  }
}

function formatTime(t: number): string {
  if (!t || isNaN(t)) return '00:00'
  const m = Math.floor(t / 60)
  const s = Math.floor(t % 60)
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

onMounted(() => {
  document.addEventListener('visibilitychange', () => {})
})
</script>

<style scoped>
/* ===== 容器 ===== */
.music-player {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 200;
  font-family: -apple-system, BlinkMacSystemFont, sans-serif;
}

/* ===== 悬浮按钮 ===== */
.player-toggle {
  width: 48px; height: 48px;
  border-radius: 50%;
  border: none;
  background: var(--vp-c-brand-1);
  color: #fff;
  font-size: 20px;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  transition: all 0.3s ease;
  display: flex; align-items: center; justify-content: center;
  position: relative;
}
.player-toggle:hover {
  transform: scale(1.08);
  box-shadow: 0 6px 24px rgba(0,0,0,0.2);
}
.player-toggle.playing {
  animation: pulse-glow 2s ease-in-out infinite;
}
@keyframes pulse-glow {
  0%,100% { box-shadow: 0 4px 16px rgba(0,0,0,0.15); }
  50% { box-shadow: 0 4px 24px var(--vp-c-brand-1); }
}
.icon-equalizer {
  position: absolute;
  bottom: 6px; right: 6px;
  display: flex; gap: 2px; align-items: end; height: 10px;
}
.icon-equalizer span {
  width: 2.5px;
  background: #fff;
  border-radius: 2px;
  animation: equalizer 0.8s ease-in-out infinite alternate;
}
.icon-equalizer span:nth-child(1) { height: 6px; animation-delay: 0s; }
.icon-equalizer span:nth-child(2) { height: 10px; animation-delay: 0.15s; }
.icon-equalizer span:nth-child(3) { height: 4px; animation-delay: 0.3s; }
@keyframes equalizer {
  0% { transform: scaleY(0.5); }
  100% { transform: scaleY(1); }
}

/* ===== 展开面板 ===== */
.player-panel {
  position: absolute;
  right: 0;
  bottom: 60px;
  width: 340px;
  max-height: 520px;
  background: var(--vp-c-bg-elv);
  border: 1px solid var(--vp-c-divider);
  border-radius: 14px;
  box-shadow: 0 12px 48px rgba(0,0,0,0.15);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.dark .player-panel {
  box-shadow: 0 12px 48px rgba(0,0,0,0.5);
}

/* --- 头部 --- */
.panel-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px 10px;
  border-bottom: 1px solid var(--vp-c-divider);
}
.panel-title { font-weight: 600; font-size: 14px; color: var(--vp-c-text-1); }
.header-tabs { display: flex; gap: 4px; margin-left: auto; }
.header-tabs button {
  border: none;
  background: transparent;
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 6px;
  cursor: pointer;
  color: var(--vp-c-text-3);
  transition: all 0.15s;
}
.header-tabs button.active {
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand-1);
  font-weight: 600;
}
.header-tabs button:hover:not(.active) { background: var(--vp-c-bg-soft); }
.btn-close {
  border: none; background: transparent; color: var(--vp-c-text-3);
  cursor: pointer; font-size: 14px; padding: 4px; border-radius: 4px;
}
.btn-close:hover { background: var(--vp-c-bg-soft); color: var(--vp-c-text-1); }

/* --- 当前播放 --- */
.now-playing {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 16px;
}
.cover-placeholder {
  width: 44px; height: 44px; border-radius: 10px;
  background: var(--vp-c-brand-soft);
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; font-weight: 700; color: var(--vp-c-brand-1);
  flex-shrink: 0; overflow: hidden;
}
.cover-placeholder img { width: 100%; height: 100%; object-fit: cover; }
.song-info { flex: 1; min-width: 0; }
.song-name {
  font-size: 14px; font-weight: 600; color: var(--vp-c-text-1);
  margin: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.song-artist {
  font-size: 12px; color: var(--vp-c-text-3);
  margin: 2px 0 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

/* --- 控制按钮 --- */
.controls {
  display: flex; align-items: center; justify-content: center;
  gap: 16px; padding: 6px 16px 10px;
}
.ctrl-btn {
  border: none; background: transparent; color: var(--vp-c-text-2);
  font-size: 18px; cursor: pointer; padding: 6px; border-radius: 8px;
  line-height: 1; transition: all 0.15s;
}
.ctrl-btn:hover { color: var(--vp-c-brand-1); background: var(--vp-c-brand-soft); }
.play-btn {
  font-size: 26px; width: 44px; height: 44px;
  display: flex; align-items: center; justify-content: center;
  background: var(--vp-c-brand-1); color: #fff; border-radius: 50%;
}
.play-btn:hover { background: var(--vp-c-brand-2); transform: scale(1.05); }

/* --- 进度条 --- */
.progress-area {
  display: flex; align-items: center; gap: 8px; padding: 0 16px 6px;
}
.time { font-size: 11px; color: var(--vp-c-text-3); font-variant-numeric: tabular-nums; min-width: 36px; }
.progress-bar { flex: 1; height: 4px; -webkit-appearance: none; appearance: none; background: var(--vp-c-divider); border-radius: 2px; outline: none; cursor: pointer; }
.progress-bar::-webkit-slider-thumb { -webkit-appearance: none; width: 12px; height: 12px; border-radius: 50%; background: var(--vp-c-brand-1); border: 2px solid var(--vp-c-bg); box-shadow: 0 1px 4px rgba(0,0,0,0.15); }
.progress-bar::-moz-range-thumb { width: 12px; height: 12px; border-radius: 50%; background: var(--vp-c-brand-1); border: 2px solid var(--vp-c-bg); cursor: pointer; }

/* --- 音量 --- */
.volume-area {
  display: flex; align-items: center; gap: 8px;
  padding: 2px 16px 8px; font-size: 12px; color: var(--vp-c-text-3);
}
.volume-bar { flex: 1; height: 3px; -webkit-appearance: none; appearance: none; background: var(--vp-c-divider); border-radius: 2px; outline: none; cursor: pointer; max-width: 120px; }
.volume-bar::-webkit-slider-thumb { -webkit-appearance: none; width: 10px; height: 10px; border-radius: 50%; background: var(--vp-c-brand-1); }

/* --- 歌单 & 搜索面板 --- */
.playlist { flex: 1; overflow-y: auto; border-top: 1px solid var(--vp-c-divider); max-height: 200px; }
.playlist-item {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 16px; cursor: pointer; transition: background 0.15s; font-size: 13px;
}
.playlist-item:hover { background: var(--vp-c-bg-soft); }
.playlist-item.active { background: var(--vp-c-brand-soft); color: var(--vp-c-brand-1); }
.item-idx { width: 20px; text-align: center; color: var(--vp-c-text-3); font-size: 11px; flex-shrink: 0; }
.playlist-item.active .item-idx { color: var(--vp-c-brand-1); font-weight: 700; }
.item-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.item-artist { color: var(--vp-c-text-3); font-size: 11px; flex-shrink: 0; max-width: 80px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.playlist-empty { padding: 24px 16px; text-align: center; font-size: 12px; color: var(--vp-c-text-3); line-height: 1.6; }
.playlist-empty code { font-size: 11px; background: var(--vp-c-bg-soft); padding: 1px 6px; border-radius: 4px; }

/* --- 搜索 --- */
.search-panel { max-height: 280px; }
.search-box {
  display: flex; gap: 6px; padding: 10px 16px;
  border-bottom: 1px solid var(--vp-c-divider);
  position: sticky; top: 0; background: var(--vp-c-bg-elv); z-index: 1;
}
.search-box input {
  flex: 1;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  padding: 6px 10px;
  font-size: 13px;
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-1);
  outline: none;
  transition: border-color 0.2s;
}
.search-box input:focus { border-color: var(--vp-c-brand-1); }
.search-box input::placeholder { color: var(--vp-c-text-3); }
.search-btn {
  border: none;
  background: var(--vp-c-brand-1);
  color: #fff;
  font-size: 14px;
  padding: 4px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: opacity 0.2s;
}
.search-btn:disabled { opacity: 0.5; cursor: default; }
.search-status {
  padding: 12px 16px; text-align: center; font-size: 12px; color: var(--vp-c-text-3);
}
.search-status.error { color: #e43e2b; }

/* --- 底部 --- */
.panel-footer {
  padding: 8px 16px; font-size: 11px; color: var(--vp-c-text-3);
  border-top: 1px solid var(--vp-c-divider); text-align: center;
}

/* ===== 动画 ===== */
.slide-enter-active, .slide-leave-active { transition: all 0.25s ease; }
.slide-enter-from, .slide-leave-to { opacity: 0; transform: translateY(12px) scale(0.96); }
</style>
