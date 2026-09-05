import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LoginView from '../views/LoginView.vue'
import ScanView from '../views/ScanView.vue'
import ReleaseFormView from '../views/ReleaseFormView.vue'
import HistoryView from '../views/HistoryView.vue'
import AdminMachinesView from '../views/AdminMachinesView.vue'

const routes = [
  {
    path: '/',
    redirect: '/scan',
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
  },
  {
    path: '/scan',
    name: 'scan',
    component: ScanView,
    meta: { requiresAuth: true },
  },
  {
    path: '/release/:code',
    name: 'release-form',
    component: ReleaseFormView,
    meta: { requiresAuth: true },
  },
  {
    path: '/history',
    name: 'history',
    component: HistoryView,
    meta: { requiresAuth: true },
  },
  {
    path: '/admin/machines',
    name: 'admin-machines',
    component: AdminMachinesView,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next({ name: 'login' })
  }
  
  if (to.meta.requiresAdmin && authStore.userRole !== 'admin') {
    return next({ name: 'scan' })
  }

  if (to.name === 'login' && authStore.isAuthenticated) {
    return next({ name: 'scan' })
  }

  next()
})

export default router
