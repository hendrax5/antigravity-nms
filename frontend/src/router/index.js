import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'

const routes = [
    {
        path: '/',
        name: 'Dashboard Overview',
        component: Dashboard
    },
    {
        path: '/inventory',
        name: 'Device Inventory',
        component: () => import('../views/Inventory.vue')
    },
    {
        path: '/configurator',
        name: 'Device Configurator',
        component: () => import('../views/Configurator.vue')
    },
    {
        path: '/history',
        name: 'Config Diff Viewer',
        component: () => import('../views/ConfigDiff.vue')
    },
    {
        path: '/monitoring',
        name: 'Advanced Telemetry',
        component: () => import('../views/Monitoring.vue')
    }
]

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes
})

export default router
