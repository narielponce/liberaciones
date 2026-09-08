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
    name: 'home',
    redirect: () => {
      const authStore = useAuthStore()
      if (!authStore.isAuthenticated) return { name: 'login' }
      if (authStore.userRole === 'supervisor') return { name: 'history' }
      return { name: 'scan' }
    },
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
    meta: { requiresAuth: true, allowedRoles: ['operador', 'admin'] },
  },
  {
    path: '/release/:code',
    name: 'release-form',
    component: ReleaseFormView,
    meta: { requiresAuth: true, allowedRoles: ['operador', 'admin'] },
  },
  {
    path: '/history',
    name: 'history',
    component: HistoryView,
    meta: { requiresAuth: true, allowedRoles: ['supervisor', 'admin'] },
  },
  {
    path: '/admin/machines',
    name: 'admin-machines',
    component: AdminMachinesView,
    meta: { requiresAuth: true, allowedRoles: ['admin'] },
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // 1. Unauthenticated users trying to access protected routes
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next({ name: 'login' })
  }

  // 2. Authenticated users trying to access login page
  if (to.name === 'login' && authStore.isAuthenticated) {
    if (authStore.userRole === 'supervisor') {
      return next({ name: 'history' })
    }
    return next({ name: 'scan' })
  }

  // 3. Strict Role-based access control
  if (to.meta.allowedRoles && !to.meta.allowedRoles.includes(authStore.userRole)) {
    if (authStore.userRole === 'supervisor') {
      return next({ name: 'history' })
    }
    return next({ name: 'scan' })
  }

  next()
})

export default router
