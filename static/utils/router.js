const router = VueRouter.createRouter({
    history: VueRouter.createWebHashHistory(),
    routes: [
        { path: '/', redirect: '/login' },
        { path: '/login', component: () => LoginPage },
        { path: '/register', component: () => RegisterPage },
        { path: '/admin', component: () => AdminDashboard, meta: { requiresAuth: true, role: 'admin' } },
        { path: '/doctor', component: () => DoctorDashboard, meta: { requiresAuth: true, role: 'doctor' } },
        { path: '/patient', component: () => PatientDashboard, meta: { requiresAuth: true, role: 'patient' } }
    ]
})

router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token')
    const role = localStorage.getItem('role')

    if (to.meta.requiresAuth && !token) {
        next('/login')
    } else if (to.meta.role && to.meta.role !== role) {
        next('/' + role)
    } else if ((to.path === '/login' || to.path === '/register') && token) {
        next('/' + role)
    } else {
        next()
    }
})
