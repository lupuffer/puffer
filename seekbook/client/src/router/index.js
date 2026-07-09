import { createRouter, createWebHistory } from 'vue-router'
import BuyView from '../views/BuyView.vue'
import BookDetailView from '../views/BookDetailView.vue'
import DiscussionDetailView from '../views/DiscussionDetailView.vue'
import HomeView from '../views/HomeView.vue'
import KnowledgeView from '../views/KnowledgeView.vue'
import LoginView from '../views/LoginView.vue'
import MaterialDetailView from '../views/MaterialDetailView.vue'
import MessagesView from '../views/MessagesView.vue'
import OrdersView from '../views/OrdersView.vue'
import ProfileView from '../views/ProfileView.vue'
import SellView from '../views/SellView.vue'
import SmartListView from '../views/SmartListView.vue'
import AuthFeedbackView from '../views/AuthFeedbackView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView, meta: { pageKey: 'index', activePath: '/' } },
    { path: '/smart-list', name: 'smartList', component: SmartListView, meta: { pageKey: 'smartList', activePath: '/smart-list' } },
    { path: '/buy', name: 'buy', component: BuyView, meta: { pageKey: 'buy', activePath: '/buy' } },
    { path: '/sell', name: 'sell', component: SellView, meta: { pageKey: 'sell', activePath: '/sell', showPublish: false } },
    { path: '/knowledge', name: 'knowledge', component: KnowledgeView, meta: { pageKey: 'knowledge', activePath: '/knowledge', actionIcon: 'fas fa-cloud-upload-alt' } },
    {
      path: '/knowledge/material/:id',
      name: 'knowledgeMaterialDetail',
      component: MaterialDetailView,
      meta: { pageKey: 'knowledge', activePath: '/knowledge', actionIcon: 'fas fa-cloud-upload-alt' },
    },
    {
      path: '/knowledge/discussion/:id',
      name: 'knowledgeDiscussionDetail',
      component: DiscussionDetailView,
      meta: { pageKey: 'knowledge', activePath: '/knowledge', actionIcon: 'fas fa-cloud-upload-alt' },
    },
    { path: '/messages', name: 'messages', component: MessagesView, meta: { pageKey: 'messages', activePath: '/messages', flush: true } },
    { path: '/profile', name: 'profile', component: ProfileView, meta: { pageKey: 'profile', activePath: '/profile' } },
    { path: '/orders', name: 'orders', component: OrdersView, meta: { pageKey: 'orders', activePath: '/profile' } },
    { path: '/publish-sell', name: 'publishSell', component: SellView, meta: { pageKey: 'publishSell', activePath: '/sell', showPublish: false } },
    { path: '/book-detail', name: 'bookDetail', component: BookDetailView, meta: { pageKey: 'bookDetail', activePath: '/buy' } },
    { path: '/login', name: 'login', component: LoginView, meta: { pageKey: 'login', standalone: true, showSearch: false, showPublish: false } },
    { path: '/auth-feedback', name: 'authFeedback', component: AuthFeedbackView, meta: { pageKey: 'login', standalone: true, showSearch: false, showPublish: false } },
  ],
})

export default router
