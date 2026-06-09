<template>
  <canvas ref="canvasRef" class="particle-canvas"></canvas>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const canvasRef = ref<HTMLCanvasElement | null>(null)

/* ---- Types ---- */
interface Sparkle {
  x: number; y: number
  vx: number; vy: number
  life: number       // 1 → 0
  maxLife: number
  size: number
  r: number; g: number; b: number
  drift: number      // horizontal drift direction
}

/* ---- State ---- */
let sparkles: Sparkle[] = []
let mx = -2000, my = -2000      // raw mouse
let sx = -2000, sy = -2000      // smoothed cursor glow
let ctx: CanvasRenderingContext2D | null = null
let animId: number | null = null
let cw = 0, ch = 0
let tick = 0

/* ---- Palette cycling ---- */
const PALETTE: [number, number, number][] = [
  [100, 108, 255],   // indigo
  [65,  209, 255],   // cyan
  [167, 139, 250],   // violet
  [251, 146, 60 ],   // warm orange
  [52,  211, 153],   // emerald
]

function pickColor(t: number): [number, number, number] {
  const idx = Math.floor(t / 120) % PALETTE.length
  const next = (idx + 1) % PALETTE.length
  const frac = (t % 120) / 120
  const c0 = PALETTE[idx]
  const c1 = PALETTE[next]
  return [
    Math.round(c0[0] + (c1[0] - c0[0]) * frac),
    Math.round(c0[1] + (c1[1] - c0[1]) * frac),
    Math.round(c0[2] + (c1[2] - c0[2]) * frac),
  ]
}

/* ---- Core ---- */
function emit(x: number, y: number, count: number) {
  const [r, g, b] = pickColor(tick)
  for (let i = 0; i < count; i++) {
    const angle = Math.random() * Math.PI * 2
    const speed = 0.3 + Math.random() * 1.2
    const life = 0.6 + Math.random() * 0.4
    sparkles.push({
      x, y,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed - 0.4, // slight upward bias
      life,
      maxLife: life,
      size: 1.2 + Math.random() * 2.5,
      r, g, b,
      drift: (Math.random() - 0.5) * 0.5,
    })
  }
}

function updateAndDraw() {
  if (!ctx || !canvasRef.value) return
  const w = cw, h = ch
  ctx.clearRect(0, 0, w, h)
  tick++

  const [cr, cg, cb] = pickColor(tick)

  // -------- Smooth cursor glow --------
  sx += (mx - sx) * 0.12
  sy += (my - sy) * 0.12

  // If mouse is on screen, emit sparkles
  if (mx > 0 && mx < w && my > 0 && my < h) {
    emit(mx, my, 1)
  }

  // Also emit from the smoothed position occasionally
  if (tick % 2 === 0 && Math.hypot(mx - sx, my - sy) > 10) {
    emit(sx, sy, 1)
  }

  // -------- Draw cursor glow (soft aura) --------
  const glowRadius = 60 + Math.sin(tick * 0.02) * 10
  const grad = ctx.createRadialGradient(sx, sy, 0, sx, sy, glowRadius)
  grad.addColorStop(0, `rgba(${cr}, ${cg}, ${cb}, 0.15)`)
  grad.addColorStop(0.4, `rgba(${cr}, ${cg}, ${cb}, 0.06)`)
  grad.addColorStop(1, `rgba(${cr}, ${cg}, ${cb}, 0)`)

  ctx.beginPath()
  ctx.arc(sx, sy, glowRadius, 0, Math.PI * 2)
  ctx.fillStyle = grad
  ctx.fill()

  // Inner brighter core
  const coreGrad = ctx.createRadialGradient(sx, sy, 0, sx, sy, 18)
  coreGrad.addColorStop(0, `rgba(${cr}, ${cg}, ${cb}, 0.25)`)
  coreGrad.addColorStop(1, `rgba(${cr}, ${cg}, ${cb}, 0)`)
  ctx.beginPath()
  ctx.arc(sx, sy, 18, 0, Math.PI * 2)
  ctx.fillStyle = coreGrad
  ctx.fill()

  // -------- Update & draw sparkles --------
  // Prune dead sparkles
  const alive: Sparkle[] = []
  for (const s of sparkles) {
    // Update
    s.x += s.vx
    s.y += s.vy
    s.vy += 0.008                        // gravity
    s.vx += Math.sin(tick * 0.01 + s.drift) * 0.005  // gentle sway
    s.life -= 1 / (s.maxLife * 120)      // fade

    if (s.life <= 0 || s.y < -20 || s.y > ch + 20) continue
    alive.push(s)

    const alpha = Math.max(0, s.life * 0.7)
    const radius = s.size * (0.3 + s.life * 0.7)

    // Outer glow
    ctx.beginPath()
    ctx.arc(s.x, s.y, radius + 4, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(${s.r}, ${s.g}, ${s.b}, ${alpha * 0.15})`
    ctx.fill()

    // Core dot
    ctx.beginPath()
    ctx.arc(s.x, s.y, radius, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(${s.r}, ${s.g}, ${s.b}, ${alpha})`
    ctx.fill()
  }
  sparkles = alive

  // -------- Occasional ambient sparkles --------
  if (tick % 8 === 0) {
    const ax = Math.random() * w
    const ay = Math.random() * h
    const [ar, ag, ab] = pickColor(tick + 60)
    sparkles.push({
      x: ax, y: ay,
      vx: (Math.random() - 0.5) * 0.15,
      vy: -0.1 - Math.random() * 0.2,
      life: 1,
      maxLife: 1.5 + Math.random(),
      size: 0.8 + Math.random() * 1.2,
      r: ar, g: ag, b: ab,
      drift: (Math.random() - 0.5) * 0.3,
    })
  }
}

function loop(time: number) {
  updateAndDraw()
  animId = requestAnimationFrame(loop)
}

/* ---- Events ---- */
function onMove(e: MouseEvent) {
  mx = e.clientX
  my = e.clientY
}
function onLeave() {
  mx = -2000; my = -2000
  sx = -2000; sy = -2000
}
function onResize() {
  if (!canvasRef.value) return
  const dpr = window.devicePixelRatio || 1
  cw = window.innerWidth
  ch = window.innerHeight
  canvasRef.value.width = cw * dpr
  canvasRef.value.height = ch * dpr
  canvasRef.value.style.width = cw + 'px'
  canvasRef.value.style.height = ch + 'px'
  ctx = canvasRef.value.getContext('2d')!
  ctx.scale(dpr, dpr)
}

/* ---- Lifecycle ---- */
onMounted(() => {
  onResize()
  animId = requestAnimationFrame(loop)
  window.addEventListener('resize', onResize)
  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseleave', onLeave)
})

onUnmounted(() => {
  if (animId) cancelAnimationFrame(animId)
  window.removeEventListener('resize', onResize)
  window.removeEventListener('mousemove', onMove)
  window.removeEventListener('mouseleave', onLeave)
})
</script>

<style scoped>
.particle-canvas {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
}
</style>
