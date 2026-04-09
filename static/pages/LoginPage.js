const LoginPage = {
    template: `
    <div class="auth-page">
        <div class="auth-card fade-in">
            <img src="/static/logo.jpg" class="auth-logo" alt="ZenCura">
            <h1 class="auth-title">Welcome Back</h1>
            <p class="auth-subtitle">Sign in to ZenCura Hospital Management</p>
            <form @submit.prevent="login">
                <div class="mb-3">
                    <input type="text" class="form-control" v-model="username" placeholder="Username" required>
                </div>
                <div class="mb-3">
                    <input type="password" class="form-control" v-model="password" placeholder="Password" required>
                </div>
                <div v-if="error" class="alert alert-danger mb-3">{{ error }}</div>
                <button type="submit" class="btn btn-teal w-100" :disabled="loading">
                    <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                    {{ loading ? 'Signing in...' : 'Sign In' }}
                </button>
            </form>
            <p class="auth-footer">
                New patient? <router-link to="/register" class="auth-link">Register here</router-link>
            </p>
        </div>
    </div>
    `,
    setup() {
        const username = Vue.ref('')
        const password = Vue.ref('')
        const error = Vue.ref('')
        const loading = Vue.ref(false)
        const router = VueRouter.useRouter()

        const login = async () => {
            error.value = ''
            loading.value = true
            try {
                const res = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: username.value, password: password.value })
                })
                const data = await res.json()
                if (!res.ok) {
                    error.value = data.msg || 'Login failed'
                    return
                }
                localStorage.setItem('token', data.token)
                localStorage.setItem('role', data.role)
                localStorage.setItem('username', data.username)
                if (data.full_name) localStorage.setItem('full_name', data.full_name)

                if (data.role === 'admin') router.push('/admin')
                else if (data.role === 'doctor') router.push('/doctor')
                else router.push('/patient')
            } catch (e) {
                error.value = 'Something went wrong. Try again.'
            } finally {
                loading.value = false
            }
        }

        return { username, password, error, loading, login }
    }
}
