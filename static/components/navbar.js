const NavBar = {
    template: `
    <nav class="navbar navbar-expand-lg navbar-zen mb-4">
        <div class="container">
            <router-link to="/" class="navbar-brand d-flex align-items-center gap-2">
                <img src="/static/logo.jpg" alt="ZenCura" style="width:38px; height:38px; border-radius:10px; object-fit:contain;">
                ZenCura
            </router-link>
            <div class="d-flex align-items-center gap-3">
                <span class="role-badge" :class="role">{{ role }}</span>
                <span class="d-none d-md-inline text-muted" style="font-size:0.88rem; font-weight:500;">{{ displayName }}</span>
                <button class="btn btn-sm btn-outline-danger" style="border-radius:10px; font-weight:500;" @click="logout">
                    <i class="bi bi-box-arrow-right me-1"></i>Logout
                </button>
            </div>
        </div>
    </nav>
    `,
    setup() {
        const router = VueRouter.useRouter()
        const role = Vue.ref(localStorage.getItem('role') || '')
        const displayName = Vue.ref(localStorage.getItem('full_name') || localStorage.getItem('username') || '')

        const logout = () => {
            localStorage.clear()
            router.push('/login')
        }

        return { role, displayName, logout }
    }
}
