import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { useGlobalState } from './composables/useGlobalState'

const initApp = async () => {
  const app = createApp(App)
  app.use(router)
  
  // 初始化全局状态
  const { initGlobalState } = useGlobalState()
  await initGlobalState()
  
  app.mount('#app')
}

initApp().catch(console.error)