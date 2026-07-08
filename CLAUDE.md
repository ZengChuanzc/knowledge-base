# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

个人知识库网站 — 基于 VitePress 构建的静态站点，涵盖 Java、AI Agent、Machine Learning 等方向的学习笔记与知识沉淀。已部署至 GitHub Pages。

## Commands

| Command | Description |
|---------|-------------|
| `npm run dev` | 启动本地开发服务器 (vitepress dev docs) |
| `npm run build` | 构建生产版本 (vitepress build docs) |
| `npm run preview` | 预览构建产物 (vitepress preview docs) |

## Tech Stack

- **框架**: VitePress ^1.6.4 (Vue 3 + Vite)
- **语言**: 中文 (zh-CN)
- **部署**: GitHub Pages，通过 `.github/workflows/deploy.yml` 自动部署（push 到 master 分支触发）
- **依赖**: vitepress、jsmind、mind-viewer、xmind、xmind-embed-viewer（XMind 脑图渲染）

## Architecture

```
docs/                            # VitePress 根目录
├── .vitepress/
│   ├── config.ts               # 站点配置：导航栏、侧边栏、搜索、主题、社交链接
│   ├── theme/
│   │   ├── index.ts            # 主题入口（扩展默认主题）
│   │   ├── Layout.vue          # 自定义布局（集成粒子背景 + 音乐播放器）
│   │   ├── components/
│   │   │   ├── ParticleBg.vue  # Canvas 粒子鼠标追踪动效
│   │   │   └── MusicPlayer.vue # 浮动音乐播放器（本地 + 网易云在线搜索）
│   │   └── styles/
│   │       └── custom.css      # 大幅覆盖默认样式：导航栏毛玻璃、背景网格+光晕、搜索框
│   ├── cache/                  # VitePress 缓存（勿提交）
│   └── dist/                   # 构建产物
├── index.md                    # 首页（Hero + Feature 卡片）
├── java/                       # Java 体系：JDK版本、JVM、并发、Spring、面试脑图
├── ai-agent/                   # AI Agent：LLM基础、RAG、Spring AI、MCP、Skills
├── ml/                         # 机器学习入门
├── roadmap/                    # 学习路线（Java后端、AI/LLM）
├── articles/                   # 热点技术文章
├── papers/                     # 技术论文笔记
├── github-projects/            # GitHub 开源项目分析
├── showcase/                   # 个人项目展示
├── navigation/                 # 技术导航（工具、资源）
├── about/                      # 关于我
├── public/                     # 静态资源
│   ├── logo.svg / k-icon.svg / favicon.svg
│   └── music/                  # 本地音乐文件（需手动添加 .mp3）
└── xmind-file/                 # XMind 脑图文件（如 interview-core.xmind）
```

## Content Structure

- 每个知识领域（java/、ai-agent/、ml/ 等）都有自己的 `index.md` 作为概览页
- 侧边栏在 `config.ts` 的 `sidebar` 中按路径配置，新增页面需同时更新 sidebar 条目
- 文档使用中文编写，日期显示格式为 `full`（如 "2026年7月7日 星期二"）
- 支持本地全文搜索（`provider: 'local'`），中文搜索标签已配置
- 编辑链接指向 GitHub 仓库，可跳转在线编辑

## Custom Theme Notes

- Layout.vue 通过插槽组合了 ParticleBg（粒子背景）和 MusicPlayer（音乐播放器）
- ParticleBg.vue 使用纯 Canvas + requestAnimationFrame 实现，无需外部依赖
- MusicPlayer.vue 支持本地播放（文件放 public/music/，编辑 localPlaylist 数组）和网易云在线搜索（需自建或配置 API 代理，默认 `https://music-api.codepoint.net`）
- custom.css 对导航栏做了全定制：毛玻璃背景、自定义 Logo、"knowledge" 文字 + 渐变色流光动画、侧边栏 scrollbar 偏移修复

## Adding New Content

1. 在对应目录下创建 `.md` 文件
2. 在 `config.ts` 的 `sidebar` 对应路径下添加链接
3. 如需在首页展示，修改 `docs/index.md` 的 `features` 数组
