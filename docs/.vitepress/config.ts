import { defineConfig } from 'vitepress'
import fs from 'fs'
import path from 'path'

// @ts-ignore
// @ts-ignore
export default defineConfig({
  title: "Knowledge Base",
  base: '/knowledge-base/',
  description: 'Java · AI Agent · Machine Learning · 个人学习历程',

  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/knowledge-base/favicon.svg' }],
    ['link', { rel: 'shortcut icon', type: 'image/svg+xml', href: '/knowledge-base/favicon.svg' }],
    // 内联自定义样式（避免 CSS 文件导入在构建时未被处理的问题）
    ['style', {}, (() => {
      try {
        const cssPath = path.resolve(__dirname, './theme/styles/custom.css')
        const css = fs.readFileSync(cssPath, 'utf-8')
        // 修正 CSS 中的资源路径（内联注入时 Vite 不会自动处理 base 路径）
        return css.replace(/url\(\s*['"]?\/k-icon\.svg['"]?\s*\)/g, "url('/knowledge-base/k-icon.svg')")
      } catch {
        return ''
      }
    })()],
  ],

  lang: 'zh-CN',

  themeConfig: {
    logo: '/k-icon.svg',

    siteTitle: false,

    nav: [
      { text: '首页', link: '/' },
      { text: '学习路线', link: '/roadmap/' },
      { text: '项目实践', link: '/projects/' },
      {
        text: '知识体系 📚',
        items: [
          { text: '☕ Java体系', link: '/java/' },
          { text: '🤖 AI 应用', link: '/ai-agent/' },
          { text: '📊 机器学习', link: '/ml/' },
        ]
      },
      { text: '热点文章', link: '/articles/' },
      { text: '技术论文', link: '/papers/' },
      { text: '开源项目', link: '/github-projects/' },
      { text: '项目展示', link: '/showcase/' },
      { text: '关于', link: '/about/' },
    ],

    search: {
      provider: 'local',
      options: {
        translations: {
          button: {
            buttonText: '搜索文章...',
            buttonAriaLabel: '搜索文章'
          },
          modal: {
            noResultsText: '未找到相关结果',
            resetButtonTitle: '清除搜索条件',
            footer: {
              selectText: '选择',
              navigateText: '切换',
              closeText: '关闭'
            }
          }
        }
      }
    },

    sidebar: {
      '/java/': [
        {
          text: 'Java 体系',
          items: [
            { text: '概述', link: '/java/' },
            { text: 'JDK 版本特性 (8~21)', link: '/java/jdk-versions' },
            { text: 'JVM 原理', link: '/java/jvm' },
            { text: '并发编程', link: '/java/concurrent' },
            { text: 'Spring 生态', link: '/java/spring' },
            { text: '技能要点 (脑图)', link: '/java/interview' },
          ]
        }
      ],

      '/ai-agent/': [
        {
          text: 'AI Agent',
          items: [
            { text: '概述', link: '/ai-agent/' },
            { text: 'LLM 基础', link: '/ai-agent/llm-basic' },
            { text: 'RAG 系统', link: '/ai-agent/rag' },
            { text: 'Spring AI', link: '/ai-agent/spring-ai' },
            { text: 'MCP 协议', link: '/ai-agent/mcp' },
            { text: 'Agent Skills', link: '/ai-agent/skills' },
          ]
        }
      ],

      '/ml/': [
        {
          text: '机器学习',
          items: [
            { text: '概述', link: '/ml/' },
            { text: '机器学习入门', link: '/ml/ml-intro' },
          ]
        }
      ],

      '/roadmap/': [
        {
          text: '学习路线',
          items: [
            { text: 'Java 后端路线', link: '/roadmap/' },
            { text: 'AI / LLM 路线', link: '/roadmap/ai-ml-roadmap' },
          ]
        }
      ],

      '/projects/': [
        {
          text: '企业级项目实践',
          items: [
            { text: '项目概览', link: '/projects/' },
            { text: '赫兹运力平台系统', link: '/projects/hezi-transport' },
            { text: '数字化移交通道管理平台', link: '/projects/digital-handover' },
            { text: '基建智慧工程管控项目', link: '/projects/smart-construction' },
          ]
        }
      ],

      '/articles/': [
        {
          text: '热点技术文章',
          items: [
            { text: '📰 文章列表', link: '/articles/' },
          ]
        }
      ],
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/ZengChuanzc' },
    ],

    footer: {
      message: '学无止境 · 行以致远',
      copyright: 'Copyright © 2026 ZengChuan'
    },

    editLink: {
      pattern: 'https://github.com/ZengChuanzc/knowledge-base/edit/main/docs/:path',
      text: '在 GitHub 上编辑此页'
    },

    lastUpdated: {
      text: '最后更新于',
      formatOptions: {
        dateStyle: 'full',
        timeStyle: 'short'
      }
    },

    docFooter: {
      prev: '上一页',
      next: '下一页'
    },

    outline: {
      label: '页面导航'
    },

    returnToTopLabel: '返回顶部',
    sidebarMenuLabel: '菜单',
    darkModeSwitchLabel: '主题',
    lightModeSwitchTitle: '切换到浅色模式',
    darkModeSwitchTitle: '切换到深色模式',
  },
})
