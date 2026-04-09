const DoctorDashboard = {
    components: { NavBar },
    template: `
    <div class="dash-page">
        <NavBar />
        <div class="container py-4">
            <div class="dash-welcome fade-in">
                <h2>Doctor Dashboard</h2>
                <p>View your appointments, manage patient treatments and availability.</p>
            </div>
            <div class="row g-4 fade-in">
                <div class="col-md-6">
                    <div class="metric-card">
                        <div class="metric-value">{{ stats.upcoming }}</div>
                        <div class="metric-label">Upcoming Appointments</div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="metric-card">
                        <div class="metric-value">{{ stats.patients }}</div>
                        <div class="metric-label">My Patients</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    `,
    setup() {
        const stats = Vue.reactive({ upcoming: '...', patients: '...' })

        Vue.onMounted(async () => {
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
