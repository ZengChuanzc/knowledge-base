import DefaultTheme from 'vitepress/theme'
import XmindViewer from './components/XmindViewer.vue'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('XmindViewer', XmindViewer)
  },
}
