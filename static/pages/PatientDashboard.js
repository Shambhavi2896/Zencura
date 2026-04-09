const PatientDashboard = {
    components: { NavBar },
    template: `
    <div class="dash-page">
        <NavBar />
        <div class="container py-4">
            <div class="dash-welcome fade-in">
                <h2>Welcome, {{ name }}</h2>
                <p>Book appointments, view your treatment history, and manage your profile.</p>
            </div>
            <div class="row g-4 fade-in">
                <div class="col-md-4">
                    <div class="metric-card">
                        <div class="metric-value">{{ stats.upcoming }}</div>
                        <div class="metric-label">Upcoming Appointments</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="metric-card">
                        <div class="metric-value">{{ stats.completed }}</div>
                        <div class="metric-label">Completed Visits</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="metric-card">
                        <div class="metric-value">{{ stats.departments }}</div>
                        <div class="metric-label">Departments Available</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    `,
    setup() {
        const name = Vue.ref(localStorage.getItem('full_name') || localStorage.getItem('username') || '')
        const stats = Vue.reactive({ upcoming: '...', completed: '...', departments: '...' })

        Vue.onMounted(async () => {
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
