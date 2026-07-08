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
</script>

<style>
.vp-wrapper {
  position: relative;
  min-height: 100vh;
  overflow-x: hidden;
}
</style>
