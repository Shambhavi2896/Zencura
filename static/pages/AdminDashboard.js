const AdminDashboard = {
    template: `
    <div class="admin-layout">
        <div class="sidebar">
            <div class="sidebar-header">
                <img src="/static/logo.jpg" alt="ZenCura">
                <h5>ZenCura</h5>
            </div>
            <div class="sidebar-menu">
                <p class="section-label px-2">NAVIGATION</p>
                <a class="sidebar-item" :class="{active: activeTab === 'overview'}" @click="activeTab = 'overview'">Dashboard</a>
                <a class="sidebar-item" :class="{active: activeTab === 'doctors'}" @click="switchTab('doctors')">Doctors</a>
                <a class="sidebar-item" :class="{active: activeTab === 'patients'}" @click="switchTab('patients')">Patients</a>
                <a class="sidebar-item" :class="{active: activeTab === 'appointments'}" @click="switchTab('appointments')">Appointments</a>
                <p class="section-label px-2 mt-4">ADMIN</p>
                <a class="sidebar-item" @click="activeTab = 'doctors'; showBlacklisted.doctors = true; fetchDoctors()">Blacklisted Users</a>
            </div>
            <div class="sidebar-footer">
                <div style="font-size:0.82rem; font-weight:600; color:var(--navy); margin-bottom:0.5rem;">Admin Account</div>
                <button class="btn btn-sm btn-outline-secondary w-100" style="border-radius:8px; font-size:0.8rem;" @click="logout">Sign Out</button>
            </div>
        </div>

        <div class="main-content">

            <!-- OVERVIEW -->
            <div v-show="activeTab === 'overview'" class="fade-in">
                <h5 class="fw-bold mb-1" style="color:var(--navy);">Dashboard</h5>
                <p style="font-size:0.85rem; color:var(--gray-400); margin-bottom:1.5rem;">Hospital operations at a glance</p>

                <div class="row g-3 mb-4">
                    <div class="col-md-3 col-6">
                        <div class="metric-card">
                            <div class="metric-value">{{ stats.doctors }}</div>
                            <div class="metric-label">Doctors</div>
                        </div>
                    </div>
                    <div class="col-md-3 col-6">
                        <div class="metric-card">
                            <div class="metric-value">{{ stats.patients }}</div>
                            <div class="metric-label">Patients</div>
                        </div>
                    </div>
                    <div class="col-md-3 col-6">
                        <div class="metric-card">
                            <div class="metric-value">{{ stats.appointments }}</div>
                            <div class="metric-label">Appointments</div>
                        </div>
                    </div>
                    <div class="col-md-3 col-6">
                        <div class="metric-card">
                            <div class="metric-value">{{ stats.departments }}</div>
                            <div class="metric-label">Departments</div>
                        </div>
                    </div>
                </div>

                <div class="row g-3 mb-4">
                    <div class="col-md-4">
                        <div class="metric-card-sm">
                            <span class="metric-dot" style="background:#14b8a6;"></span>
                            <span class="metric-sm-value">{{ stats.booked }}</span>
                            <span class="metric-sm-label">Booked</span>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="metric-card-sm">
                            <span class="metric-dot" style="background:#22c55e;"></span>
                            <span class="metric-sm-value">{{ stats.completed }}</span>
                            <span class="metric-sm-label">Completed</span>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="metric-card-sm">
                            <span class="metric-dot" style="background:#f87171;"></span>
                            <span class="metric-sm-value">{{ stats.cancelled }}</span>
                            <span class="metric-sm-label">Cancelled</span>
                        </div>
                    </div>
                </div>

                <div class="row g-3 mb-4">
                    <div class="col-lg-7">
                        <div class="panel">
                            <div class="panel-header">Appointments by Department</div>
                            <canvas id="deptBarChart" style="max-height:240px;"></canvas>
                        </div>
                    </div>
                    <div class="col-lg-5">
                        <div class="panel">
                            <div class="panel-header">Status Breakdown</div>
                            <canvas id="statusDoughnutChart" style="max-height:240px;"></canvas>
                        </div>
                    </div>
                </div>

                <div class="panel">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <div class="panel-header mb-0">Recent Appointments</div>
                        <a style="color:var(--teal-600); cursor:pointer; font-size:0.82rem; font-weight:500;" @click="switchTab('appointments')">View all</a>
                    </div>
                    <table class="table table-sm align-middle mb-0" style="font-size:0.85rem;">
                        <thead><tr style="color:var(--gray-400); font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em;"><th>Patient</th><th>Doctor</th><th>Department</th><th>Date</th><th>Status</th></tr></thead>
                        <tbody>
                            <tr v-for="r in stats.recent" :key="r.id">
                                <td class="fw-medium">{{ r.patient }}</td>
                                <td>{{ r.doctor }}</td>
                                <td>{{ r.dept }}</td>
                                <td>{{ r.date }}</td>
                                <td><span class="status-pill" :class="r.status.toLowerCase()">{{ r.status }}</span></td>
                            </tr>
                            <tr v-if="!stats.recent || stats.recent.length === 0"><td colspan="5" class="text-center py-3 text-muted">No recent data</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- DOCTORS -->
            <div v-show="activeTab === 'doctors'" class="fade-in">
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <h5 class="fw-bold mb-0" style="color:var(--navy);">Doctors</h5>
                    <button class="btn btn-teal btn-sm" @click="openDoctorModal()">+ Add Doctor</button>
                </div>
                <p style="font-size:0.85rem; color:var(--gray-400); margin-bottom:1rem;">Manage your medical staff</p>

                <div class="d-flex gap-2 mb-3">
                    <input type="text" class="form-control form-control-sm flex-grow-1" style="max-width:320px;" placeholder="Search name or specialization..." v-model="searchQueries.doctors" @input="fetchDoctors">
                    <div class="btn-group btn-group-sm">
                        <button class="btn" :class="!showBlacklisted.doctors ? 'btn-dark' : 'btn-outline-secondary'" @click="showBlacklisted.doctors = false; fetchDoctors()">Active</button>
                        <button class="btn" :class="showBlacklisted.doctors ? 'btn-danger' : 'btn-outline-secondary'" @click="showBlacklisted.doctors = true; fetchDoctors()">Blacklisted</button>
                    </div>
                </div>

                <div class="row g-3">
                    <div v-for="doc in filteredDoctors" :key="doc.id" class="col-md-6 col-xl-4">
                        <div class="profile-card">
                            <div class="d-flex align-items-start justify-content-between mb-2">
                                <div class="d-flex align-items-center gap-2">
                                    <div class="avatar" style="background:var(--teal-50); color:var(--teal-700);">{{ doc.full_name.charAt(0) }}</div>
                                    <div>
                                        <div class="fw-bold" style="font-size:0.92rem; line-height:1.2;">{{ doc.full_name }}</div>
                                        <div style="font-size:0.78rem; color:var(--gray-400);">{{ doc.department_name }}</div>
                                    </div>
                                </div>
                                <span class="status-pill" :class="doc.is_active ? 'booked' : 'cancelled'" style="font-size:0.68rem;">{{ doc.is_active ? 'Active' : 'Blocked' }}</span>
                            </div>
                            <div class="profile-details">
                                <div><span class="detail-label">Email</span> {{ doc.email }}</div>
                                <div><span class="detail-label">Phone</span> {{ doc.contact || '—' }}</div>
                                <div><span class="detail-label">Exp.</span> {{ doc.experience || '—' }}</div>
                                <div><span class="detail-label">Qual.</span> {{ doc.qualification || '—' }}</div>
                            </div>
                            <div class="d-flex gap-2 mt-3 pt-2" style="border-top:1px solid var(--gray-100);">
                                <button class="btn btn-sm btn-light flex-grow-1" style="font-size:0.78rem;" @click="openDoctorModal(doc)">Edit</button>
                                <button class="btn btn-sm flex-grow-1" style="font-size:0.78rem;" :class="doc.is_active ? 'btn-outline-danger' : 'btn-outline-success'" @click="toggleStatus(doc.user_id, 'doctors')">{{ doc.is_active ? 'Blacklist' : 'Activate' }}</button>
                            </div>
                        </div>
                    </div>
                    <div v-if="filteredDoctors.length === 0" class="col-12 text-center py-5" style="color:var(--gray-400); font-size:0.88rem;">No {{ showBlacklisted.doctors ? 'blacklisted' : 'active' }} doctors found</div>
                </div>
            </div>

            <!-- PATIENTS -->
            <div v-show="activeTab === 'patients'" class="fade-in">
                <h5 class="fw-bold mb-1" style="color:var(--navy);">Patients</h5>
                <p style="font-size:0.85rem; color:var(--gray-400); margin-bottom:1rem;">View and manage patient records</p>

                <div class="d-flex gap-2 mb-3">
                    <input type="text" class="form-control form-control-sm flex-grow-1" style="max-width:320px;" placeholder="Search name, ID or contact..." v-model="searchQueries.patients" @input="fetchPatients">
                    <div class="btn-group btn-group-sm">
                        <button class="btn" :class="!showBlacklisted.patients ? 'btn-dark' : 'btn-outline-secondary'" @click="showBlacklisted.patients = false; fetchPatients()">Active</button>
                        <button class="btn" :class="showBlacklisted.patients ? 'btn-danger' : 'btn-outline-secondary'" @click="showBlacklisted.patients = true; fetchPatients()">Blacklisted</button>
                    </div>
                </div>

                <div class="row g-3">
                    <div v-for="pat in filteredPatients" :key="pat.id" class="col-md-6 col-xl-4">
                        <div class="profile-card">
                            <div class="d-flex align-items-start justify-content-between mb-2">
                                <div class="d-flex align-items-center gap-2">
                                    <div class="avatar" style="background:#eff6ff; color:#2563eb;">{{ pat.full_name.charAt(0) }}</div>
                                    <div>
                                        <div class="fw-bold" style="font-size:0.92rem; line-height:1.2;">{{ pat.full_name }}</div>
                                        <div style="font-size:0.78rem; color:var(--gray-400);">Patient #{{ pat.id }}</div>
                                    </div>
                                </div>
                                <span class="status-pill" :class="pat.is_active ? 'booked' : 'cancelled'" style="font-size:0.68rem;">{{ pat.is_active ? 'Active' : 'Blocked' }}</span>
                            </div>
                            <div class="profile-details">
                                <div><span class="detail-label">Email</span> {{ pat.email }}</div>
                                <div><span class="detail-label">Phone</span> {{ pat.contact || '—' }}</div>
                                <div><span class="detail-label">Blood</span> {{ pat.blood_group || '—' }}</div>
                                <div><span class="detail-label">Gender</span> {{ pat.gender || '—' }}</div>
                            </div>
                            <div class="d-flex gap-2 mt-3 pt-2" style="border-top:1px solid var(--gray-100);">
                                <button class="btn btn-sm flex-grow-1" style="font-size:0.78rem;" :class="pat.is_active ? 'btn-outline-danger' : 'btn-outline-success'" @click="toggleStatus(pat.user_id, 'patients')">{{ pat.is_active ? 'Blacklist' : 'Activate' }}</button>
                            </div>
                        </div>
                    </div>
                    <div v-if="filteredPatients.length === 0" class="col-12 text-center py-5" style="color:var(--gray-400); font-size:0.88rem;">No {{ showBlacklisted.patients ? 'blacklisted' : 'active' }} patients found</div>
                </div>
            </div>

            <!-- APPOINTMENTS -->
            <div v-show="activeTab === 'appointments'" class="fade-in">
                <h5 class="fw-bold mb-1" style="color:var(--navy);">Appointments</h5>
                <p style="font-size:0.85rem; color:var(--gray-400); margin-bottom:1rem;">All hospital appointments</p>

                <div class="d-flex gap-2 mb-3 flex-wrap">
                    <button v-for="f in ['All','Booked','Completed','Cancelled']" :key="f" class="btn btn-sm" :class="aptFilter === f ? 'btn-dark' : 'btn-outline-secondary'" @click="aptFilter = f" style="font-size:0.8rem;">{{ f }}</button>
                </div>

                <div class="panel p-0">
                    <table class="table table-hover table-sm align-middle mb-0" style="font-size:0.85rem;">
                        <thead><tr style="color:var(--gray-400); font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em;"><th class="ps-3">ID</th><th>Patient</th><th>Doctor</th><th>Department</th><th>Date</th><th>Time</th><th>Status</th><th>Actions</th></tr></thead>
                        <tbody>
                            <template v-for="apt in filteredAppointments" :key="apt.id">
                                <tr>
                                    <td class="ps-3 text-muted fw-medium">#{{ apt.id }}</td>
                                    <td class="fw-medium">{{ apt.patient_name }}</td>
                                    <td>{{ apt.doctor_name }}</td>
                                    <td>{{ apt.department_name }}</td>
                                    <td>{{ apt.date }}</td>
                                    <td>{{ apt.time }}</td>
                                    <td><span class="status-pill" :class="apt.status.toLowerCase()">{{ apt.status }}</span></td>
                                    <td>
                                        <div class="d-flex gap-1" v-if="apt.status === 'Completed' && apt.treatment">
                                            <button class="btn btn-sm btn-light py-0 px-2" style="font-size:0.75rem;" @click="viewTreatment(apt)">Record</button>
                                        </div>
                                    </td>
                                </tr>
                                <tr v-if="expandedTreatment === apt.id" class="table-light">
                                    <td colspan="8" class="p-3">
                                        <div class="bg-white p-3 rounded border" style="font-size:0.85rem;">
                                            <div class="d-flex justify-content-between align-items-center mb-2">
                                                <h6 class="fw-bold m-0" style="color:var(--teal-700);">Treatment Record</h6>
                                                <button class="btn-close btn-sm" style="font-size:0.6rem;" @click="expandedTreatment = null"></button>
                                            </div>
                                            <div class="row g-3">
                                                <div class="col-md-6">
                                                    <span class="d-block text-muted" style="font-size:0.75rem; text-transform:uppercase;">Diagnosis</span>
                                                    <div>{{ apt.treatment.diagnosis || '—' }}</div>
                                                </div>
                                                <div class="col-md-6">
                                                    <span class="d-block text-muted" style="font-size:0.75rem; text-transform:uppercase;">Prescription</span>
                                                    <div>{{ apt.treatment.prescription || '—' }}</div>
                                                </div>
                                                <div class="col-md-6">
                                                    <span class="d-block text-muted" style="font-size:0.75rem; text-transform:uppercase;">Notes</span>
                                                    <div>{{ apt.treatment.notes || '—' }}</div>
                                                </div>
                                                <div class="col-md-6">
                                                    <span class="d-block text-muted" style="font-size:0.75rem; text-transform:uppercase;">Next Visit</span>
                                                    <div>{{ apt.treatment.next_visit || 'Not specified' }}</div>
                                                </div>
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                            </template>
                            <tr v-if="filteredAppointments.length === 0"><td colspan="8" class="text-center py-4 text-muted">No appointments found</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Doctor Modal -->
        <div class="modal fade" id="doctorModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-lg modal-dialog-centered">
                <div class="modal-content border-0 shadow" style="border-radius:12px;">
                    <div class="modal-header" style="border-bottom:1px solid var(--gray-100); padding:1.25rem 1.5rem;">
                        <h6 class="modal-title fw-bold m-0">{{ docForm.id ? 'Edit Doctor' : 'Add Doctor' }}</h6>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body" style="padding:1.5rem;">
                        <form @submit.prevent="saveDoctor">
                            <div class="row g-3" v-if="!docForm.id">
                                <div class="col-md-6"><label class="form-label">Username</label><input type="text" class="form-control form-control-sm" v-model="docForm.username" required></div>
                                <div class="col-md-6"><label class="form-label">Email</label><input type="email" class="form-control form-control-sm" v-model="docForm.email" required></div>
                            </div>
                            <div class="row g-3 mt-0">
                                <div class="col-md-6"><label class="form-label">Full Name</label><input type="text" class="form-control form-control-sm" v-model="docForm.full_name" required></div>
                                <div class="col-md-6"><label class="form-label">Department</label><select class="form-select form-select-sm" v-model="docForm.department_id" required><option value="" disabled>Select</option><option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option></select></div>
                                <div class="col-md-6"><label class="form-label">Contact</label><input type="text" class="form-control form-control-sm" v-model="docForm.contact"></div>
                                <div class="col-md-6"><label class="form-label">Experience</label><input type="text" class="form-control form-control-sm" v-model="docForm.experience" placeholder="e.g. 5 years"></div>
                                <div class="col-md-6"><label class="form-label">Qualification</label><input type="text" class="form-control form-control-sm" v-model="docForm.qualification"></div>
                                <div class="col-md-6"><label class="form-label">Availability</label><input type="text" class="form-control form-control-sm" v-model="docForm.availability" placeholder="e.g. Mon-Fri 09:00-17:00"></div>
                                <div class="col-md-6"><label class="form-label">Password <small class="text-muted" v-if="docForm.id">(leave blank to keep)</small></label><input type="password" class="form-control form-control-sm" v-model="docForm.password" :required="!docForm.id"></div>
                            </div>
                            <div class="d-flex justify-content-end gap-2 mt-4">
                                <button type="button" class="btn btn-sm btn-light" data-bs-dismiss="modal">Cancel</button>
                                <button type="submit" class="btn btn-sm btn-teal px-3" :disabled="saving">{{ saving ? 'Saving...' : (docForm.id ? 'Update' : 'Create') }}</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
    `,
    setup() {
        const router = VueRouter.useRouter()
        const activeTab = Vue.ref('overview')
        const aptFilter = Vue.ref('All')
        const stats = Vue.reactive({ doctors: 0, patients: 0, appointments: 0, departments: 0, booked: 0, completed: 0, cancelled: 0, recent: [] })
        const showBlacklisted = Vue.reactive({ doctors: false, patients: false })
        const doctors = Vue.ref([])
        const patients = Vue.ref([])
        const appointments = Vue.ref([])
        const departments = Vue.ref([])
        const expandedTreatment = Vue.ref(null)
        const searchQueries = Vue.reactive({ doctors: '', patients: '' })
        const docForm = Vue.reactive({ id: null, username: '', email: '', full_name: '', department_id: '', contact: '', experience: '', qualification: '', availability: '', password: '' })
        const saving = Vue.ref(false)
        let doctorModalInstance = null
        let barChart = null
        let doughnutChart = null

        const filteredDoctors = Vue.computed(() => doctors.value.filter(d => showBlacklisted.doctors ? !d.is_active : d.is_active))
        const filteredPatients = Vue.computed(() => patients.value.filter(p => showBlacklisted.patients ? !p.is_active : p.is_active))
        const filteredAppointments = Vue.computed(() => aptFilter.value === 'All' ? appointments.value : appointments.value.filter(a => a.status === aptFilter.value))

        const fetchApi = async (url, options = {}) => {
            const token = localStorage.getItem('token')
            return await fetch(url, { ...options, headers: { ...options.headers, 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' } })
        }

        const renderCharts = () => {
            Vue.nextTick(() => {
                const barCtx = document.getElementById('deptBarChart')
                const doughCtx = document.getElementById('statusDoughnutChart')
                if (!barCtx || !doughCtx) return
                if (barChart) barChart.destroy()
                if (doughnutChart) doughnutChart.destroy()

                barChart = new Chart(barCtx, {
                    type: 'bar',
                    data: { labels: stats.chart_labels || [], datasets: [{ data: stats.chart_data || [], backgroundColor: '#99f6e4', hoverBackgroundColor: '#14b8a6', borderRadius: 4, borderSkipped: false }] },
                    options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { precision: 0, font: { size: 11 } }, grid: { color: '#f1f5f9' } }, x: { grid: { display: false }, ticks: { font: { size: 11 } } } } }
                })

                doughnutChart = new Chart(doughCtx, {
                    type: 'doughnut',
                    data: { labels: ['Booked', 'Completed', 'Cancelled'], datasets: [{ data: [stats.booked, stats.completed, stats.cancelled], backgroundColor: ['#5eead4', '#86efac', '#fca5a5'], borderWidth: 0, spacing: 2 }] },
                    options: { responsive: true, cutout: '70%', plugins: { legend: { position: 'bottom', labels: { padding: 16, usePointStyle: true, pointStyle: 'circle', font: { size: 11 } } } } }
                })
            })
        }

        Vue.onMounted(async () => {
            doctorModalInstance = new bootstrap.Modal(document.getElementById('doctorModal'))
            try {
                let res = await fetchApi('/api/admin/stats')
                if (res.ok) { Object.assign(stats, await res.json()); renderCharts() }
                res = await fetchApi('/api/departments')
                if (res.ok) departments.value = await res.json()
            } catch (e) {}
        })

        const switchTab = (tab) => {
            activeTab.value = tab
            if (tab === 'doctors') fetchDoctors()
            if (tab === 'patients') fetchPatients()
            if (tab === 'appointments' && appointments.value.length === 0) fetchAppointments()
        }
        const fetchDoctors = async () => { const res = await fetchApi('/api/admin/doctors?search=' + encodeURIComponent(searchQueries.doctors)); if (res.ok) doctors.value = await res.json() }
        const fetchPatients = async () => { const res = await fetchApi('/api/admin/patients?search=' + encodeURIComponent(searchQueries.patients)); if (res.ok) patients.value = await res.json() }
        const fetchAppointments = async () => { const res = await fetchApi('/api/admin/appointments'); if (res.ok) appointments.value = await res.json() }

        const openDoctorModal = (doc = null) => {
            if (doc) { Object.assign(docForm, { id: doc.id, username: doc.username, email: doc.email, full_name: doc.full_name, department_id: doc.department_id, contact: doc.contact, experience: doc.experience, qualification: doc.qualification, availability: doc.availability, password: '' }) }
            else { Object.assign(docForm, { id: null, username: '', email: '', full_name: '', department_id: '', contact: '', experience: '', qualification: '', availability: '', password: '' }) }
            doctorModalInstance.show()
        }
        const saveDoctor = async () => {
            saving.value = true
            try {
                const url = docForm.id ? '/api/admin/doctors/' + docForm.id : '/api/admin/doctors'
                const res = await fetchApi(url, { method: docForm.id ? 'PUT' : 'POST', body: JSON.stringify(docForm) })
                const data = await res.json()
                if (res.ok) { doctorModalInstance.hide(); fetchDoctors(); let s = await fetchApi('/api/admin/stats'); if (s.ok) Object.assign(stats, await s.json()) }
                else alert(data.msg)
            } catch (e) { alert('Error submitting form') } finally { saving.value = false }
        }
        const toggleStatus = async (userId, type) => {
            if (!confirm("Change this user's status?")) return
            try {
                const res = await fetchApi('/api/admin/users/' + userId + '/toggle_status', { method: 'PUT' })
                if (res.ok) { type === 'doctors' ? fetchDoctors() : fetchPatients() }
                else alert((await res.json()).msg)
            } catch (e) { alert('Could not update status') }
        }

        const viewTreatment = (apt) => {
            if (expandedTreatment.value === apt.id) {
                expandedTreatment.value = null;
            } else {
                expandedTreatment.value = apt.id;
            }
        }

        const logout = () => { localStorage.clear(); router.push('/login') }

        return { activeTab, aptFilter, stats, showBlacklisted, doctors, patients, appointments, departments, searchQueries, filteredDoctors, filteredPatients, filteredAppointments, docForm, saving, switchTab, fetchDoctors, fetchPatients, fetchAppointments, openDoctorModal, saveDoctor, toggleStatus, expandedTreatment, viewTreatment, logout }
    }
}
