const { createApp, ref, reactive, onMounted } = Vue
const { createRouter, createWebHashHistory } = VueRouter

const LoginPage = {
    template: `
    <div class="auth-page">
        <div class="auth-card fade-in">
            <img src="/static/logo.jpg" class="auth-logo" alt="ZenCura">
            <h1 class="auth-title">Welcome Back</h1>
            <p class="auth-subtitle">Sign in to ZenCura Hospital Management</p>
            <form @submit.prevent="login">
                <div class="mb-3 input-icon-wrap">
                    <i class="bi bi-person"></i>
                    <input type="text" class="form-control" v-model="username" placeholder="Username" required>
                </div>
                <div class="mb-3 input-icon-wrap">
                    <i class="bi bi-lock"></i>
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
        const username = ref('')
        const password = ref('')
        const error = ref('')
        const loading = ref(false)
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

const RegisterPage = {
    template: `
    <div class="auth-page">
        <div class="auth-card register-card fade-in">
            <img src="/static/logo.jpg" class="auth-logo" alt="ZenCura">
            <h1 class="auth-title">Patient Registration</h1>
            <p class="auth-subtitle">Create your ZenCura account</p>
            <form @submit.prevent="register">
                <p class="section-label">Account Details</p>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <input type="text" class="form-control" v-model="form.username" placeholder="Username" required>
                    </div>
                    <div class="col-md-6 mb-3">
                        <input type="email" class="form-control" v-model="form.email" placeholder="Email" required>
                    </div>
                </div>
                <div class="mb-3">
                    <input type="password" class="form-control" v-model="form.password" placeholder="Password" required minlength="6">
                </div>
                <p class="section-label mt-2">Personal Information</p>
                <div class="mb-3">
                    <input type="text" class="form-control" v-model="form.full_name" placeholder="Full Name" required>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <input type="text" class="form-control" v-model="form.contact" placeholder="Contact Number" required>
                    </div>
                    <div class="col-md-6 mb-3">
                        <select class="form-select" v-model="form.gender">
                            <option value="" disabled selected>Gender</option>
                            <option>Male</option>
                            <option>Female</option>
                            <option>Other</option>
                        </select>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <input type="date" class="form-control" v-model="form.dob">
                    </div>
                    <div class="col-md-6 mb-3">
                        <select class="form-select" v-model="form.blood_group">
                            <option value="" disabled selected>Blood Group</option>
                            <option>A+</option><option>A-</option>
                            <option>B+</option><option>B-</option>
                            <option>AB+</option><option>AB-</option>
                            <option>O+</option><option>O-</option>
                        </select>
                    </div>
                </div>
                <div class="mb-3">
                    <textarea class="form-control" v-model="form.address" placeholder="Address" rows="2"></textarea>
                </div>
                <div v-if="error" class="alert alert-danger mb-3">{{ error }}</div>
                <div v-if="success" class="alert alert-success mb-3">{{ success }}</div>
                <button type="submit" class="btn btn-teal w-100" :disabled="loading">
                    <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                    {{ loading ? 'Registering...' : 'Create Account' }}
                </button>
            </form>
            <p class="auth-footer">
                Already have an account? <router-link to="/login" class="auth-link">Sign in</router-link>
            </p>
        </div>
    </div>
    `,
    setup() {
        const form = reactive({
            username: '', email: '', password: '', full_name: '',
            contact: '', gender: '', dob: '', blood_group: '', address: ''
        })
        const error = ref('')
        const success = ref('')
        const loading = ref(false)
        const router = VueRouter.useRouter()

        const register = async () => {
            error.value = ''
            success.value = ''
            loading.value = true
            try {
                const res = await fetch('/api/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(form)
                })
                const data = await res.json()
                if (!res.ok) {
                    error.value = data.msg || 'Registration failed'
                    return
                }
                success.value = data.msg
                setTimeout(() => router.push('/login'), 1500)
            } catch (e) {
                error.value = 'Something went wrong. Try again.'
            } finally {
                loading.value = false
            }
        }

        return { form, error, success, loading, register }
    }
}

// NavBar and AdminDashboard are loaded via separate scripts

const DoctorDashboard = {
    components: { NavBar },
    template: `
    <div class="dash-page">
        <NavBar />
        <div class="container py-4">
            <div class="dash-welcome fade-in">
                <h2><i class="bi bi-heart-pulse me-2"></i>Doctor Dashboard</h2>
                <p>View your appointments, manage patient treatments and availability.</p>
            </div>
            <div class="row g-4 fade-in">
                <div class="col-md-6">
                    <div class="stat-card">
                        <div class="stat-icon teal"><i class="bi bi-calendar2-week"></i></div>
                        <div class="stat-number">{{ stats.upcoming }}</div>
                        <div class="stat-label">Upcoming Appointments</div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="stat-card">
                        <div class="stat-icon blue"><i class="bi bi-people"></i></div>
                        <div class="stat-number">{{ stats.patients }}</div>
                        <div class="stat-label">My Patients</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    `,
    setup() {
        const stats = reactive({ upcoming: '...', patients: '...' })

        onMounted(async () => {
            try {
                const token = localStorage.getItem('token')
                const res = await fetch('/api/doctor/stats', {
                    headers: { 'Authorization': 'Bearer ' + token }
                })
                if (res.ok) {
                    const data = await res.json()
                    stats.upcoming = data.upcoming
                    stats.patients = data.patients
                }
            } catch (e) {}
        })
        return { stats }
    }
}

const PatientDashboard = {
    components: { NavBar },
    template: `
    <div class="dash-page">
        <NavBar />
        <div class="container py-4">
            <div class="dash-welcome fade-in">
                <h2><i class="bi bi-emoji-smile me-2"></i>Welcome, {{ name }}</h2>
                <p>Book appointments, view your treatment history, and manage your profile.</p>
            </div>
            <div class="row g-4 fade-in">
                <div class="col-md-4">
                    <div class="stat-card">
                        <div class="stat-icon teal"><i class="bi bi-calendar-check"></i></div>
                        <div class="stat-number">{{ stats.upcoming }}</div>
                        <div class="stat-label">Upcoming Appointments</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stat-card">
                        <div class="stat-icon blue"><i class="bi bi-clipboard2-pulse"></i></div>
                        <div class="stat-number">{{ stats.completed }}</div>
                        <div class="stat-label">Completed Visits</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stat-card">
                        <div class="stat-icon amber"><i class="bi bi-hospital"></i></div>
                        <div class="stat-number">{{ stats.departments }}</div>
                        <div class="stat-label">Departments Available</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    `,
    setup() {
        const name = ref(localStorage.getItem('full_name') || localStorage.getItem('username') || '')
        const stats = reactive({ upcoming: '...', completed: '...', departments: '...' })

        onMounted(async () => {
            try {
                const token = localStorage.getItem('token')
                const res = await fetch('/api/patient/stats', {
                    headers: { 'Authorization': 'Bearer ' + token }
                })
                if (res.ok) {
                    const data = await res.json()
                    stats.upcoming = data.upcoming
                    stats.completed = data.completed
                    stats.departments = data.departments
                }
            } catch (e) {}
        })
        return { name, stats }
    }
}

const routes = [
    { path: '/', redirect: '/login' },
    { path: '/login', component: LoginPage },
    { path: '/register', component: RegisterPage },
    { path: '/admin', component: AdminDashboard, meta: { requiresAuth: true, role: 'admin' } },
    { path: '/doctor', component: DoctorDashboard, meta: { requiresAuth: true, role: 'doctor' } },
    { path: '/patient', component: PatientDashboard, meta: { requiresAuth: true, role: 'patient' } }
]

const router = createRouter({
    history: createWebHashHistory(),
    routes
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

const app = createApp({})
app.use(router)
app.mount('#app')
