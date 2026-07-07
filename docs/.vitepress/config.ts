import { defineConfig } from 'vitepress'

export default defineConfig({
  title: "Knowledge Base",
  base: '/knowledge-base/',
  description: 'Java · AI Agent · Machine Learning · 个人学习历程',

  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/knowledge-base/favicon.svg' }],
    ['link', { rel: 'shortcut icon', type: 'image/svg+xml', href: '/knowledge-base/favicon.svg' }],
  ],

  lang: 'zh-CN',

  themeConfig: {
    logo: '/k-icon.svg',

    siteTitle: false,

    nav: [
      { text: '首页', link: '/' },
      { text: '学习路线', link: '/roadmap/' },
      { text: '技术导航', link: '/navigation/' },
      {
        text: '知识体系 📚',
        items: [
          { text: '☕ Java体系', link: '/java/' },
          { text: '🤖 AI Agent', link: '/ai-agent/' },
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
            { text: 'JVM 原理', link: '/java/jvm' },
            { text: '并发编程', link: '/java/concurrent' },
            { text: 'Spring 生态', link: '/java/spring' },
            { text: 'JDK 版本特性 (8~21)', link: '/java/jdk-versions' },
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

      '/navigation/': [
        {
          text: '技术导航',
          items: [
            { text: '常用工具', link: '/navigation/' },
            { text: '学习资源', link: '/navigation/resources' },
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
