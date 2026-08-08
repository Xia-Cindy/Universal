import { createApp } from 'vue'
import { router } from './router'
import App from './App.vue'
import './styles.css'
import './universe.css'

createApp(App).use(router).mount('#app')
