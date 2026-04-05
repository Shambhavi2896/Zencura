const AdminDashboard = {
    components: { NavBar },
    template: `
    <div class="dash-page pb-5">
        <NavBar />
        <div class="container fade-in">
            <div class="dash-welcome">
                <h2><i class="bi bi-shield-check me-2"></i>Admin Dashboard</h2>
                <p>Manage doctors, patients and appointments across ZenCura Hospital.</p>
            </div>

            <!-- Tabs Navigation -->
            <ul class="nav nav-pills mb-4 gap-2" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" data-bs-toggle="pill" data-bs-target="#overview" type="button" role="tab">Overview</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" data-bs-toggle="pill" data-bs-target="#doctors" type="button" role="tab" @click="fetchDoctors">Doctors</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" data-bs-toggle="pill" data-bs-target="#patients" type="button" role="tab" @click="fetchPatients">Patients</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" data-bs-toggle="pill" data-bs-target="#appointments" type="button" role="tab" @click="fetchAppointments">Appointments</button>
                </li>
            </ul>

            <div class="tab-content" id="adminTabsContent">
                
                <!-- Overview Tab -->
                <div class="tab-pane fade show active" id="overview" role="tabpanel">
                    <div class="row g-4">
                        <div class="col-md-4">
                            <div class="stat-card">
                                <div class="stat-icon teal"><i class="bi bi-heart-pulse"></i></div>
                                <div class="stat-number">{{ stats.doctors }}</div>
                                <div class="stat-label">Registered Doctors</div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="stat-card">
                                <div class="stat-icon blue"><i class="bi bi-people"></i></div>
                                <div class="stat-number">{{ stats.patients }}</div>
                                <div class="stat-label">Registered Patients</div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="stat-card">
                                <div class="stat-icon amber"><i class="bi bi-calendar-check"></i></div>
                                <div class="stat-number">{{ stats.appointments }}</div>
                                <div class="stat-label">Total Appointments</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Doctors Tab -->
                <div class="tab-pane fade" id="doctors" role="tabpanel">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <div class="input-icon-wrap w-50">
                            <i class="bi bi-search"></i>
                            <input type="text" class="form-control" placeholder="Search by name or specialization..." v-model="searchQueries.doctors" @input="fetchDoctors">
                        </div>
                        <button class="btn btn-teal px-4" @click="openDoctorModal()"><i class="bi bi-plus-lg me-1"></i> Add Doctor</button>
                    </div>
                    <div class="table-responsive bg-white rounded-3 shadow-sm border border-light">
                        <table class="table table-hover align-middle mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th>Name</th>
                                    <th>Department</th>
                                    <th>Contact</th>
                                    <th>Status</th>
                                    <th class="text-end">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="doc in doctors" :key="doc.id">
                                    <td>
                                        <div class="fw-bold">{{ doc.full_name }}</div>
                                        <small class="text-muted">{{ doc.username }} | {{ doc.email }}</small>
                                    </td>
                                    <td>{{ doc.department_name }}</td>
                                    <td>{{ doc.contact }}</td>
                                    <td>
                                        <span class="badge" :class="doc.is_active ? 'bg-success' : 'bg-danger'">
                                            {{ doc.is_active ? 'Active' : 'Blacklisted' }}
                                        </span>
                                    </td>
                                    <td class="text-end">
                                        <button class="btn btn-sm btn-light me-2" @click="openDoctorModal(doc)">Edit</button>
                                        <button class="btn btn-sm" :class="doc.is_active ? 'btn-outline-danger' : 'btn-outline-success'" @click="toggleStatus(doc.user_id, 'doctors')">
                                            {{ doc.is_active ? 'Blacklist' : 'Activate' }}
                                        </button>
                                    </td>
                                </tr>
                                <tr v-if="doctors.length === 0">
                                    <td colspan="5" class="text-center py-4 text-muted">No doctors found</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Patients Tab -->
                <div class="tab-pane fade" id="patients" role="tabpanel">
                    <div class="mb-3">
                        <div class="input-icon-wrap w-50">
                            <i class="bi bi-search"></i>
                            <input type="text" class="form-control" placeholder="Search by name, ID or contact..." v-model="searchQueries.patients" @input="fetchPatients">
                        </div>
                    </div>
                    <div class="table-responsive bg-white rounded-3 shadow-sm border border-light">
                        <table class="table table-hover align-middle mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th>ID</th>
                                    <th>Patient Name</th>
                                    <th>Contact</th>
                                    <th>Blood Group</th>
                                    <th>Status</th>
                                    <th class="text-end">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="pat in patients" :key="pat.id">
                                    <td class="fw-bold text-muted">#{{ pat.id }}</td>
                                    <td>
                                        <div class="fw-bold">{{ pat.full_name }}</div>
                                        <small class="text-muted">{{ pat.username }} | {{ pat.email }}</small>
                                    </td>
                                    <td>{{ pat.contact }}</td>
                                    <td><span class="badge bg-secondary">{{ pat.blood_group || 'N/A' }}</span></td>
                                    <td>
                                        <span class="badge" :class="pat.is_active ? 'bg-success' : 'bg-danger'">
                                            {{ pat.is_active ? 'Active' : 'Blacklisted' }}
                                        </span>
                                    </td>
                                    <td class="text-end">
                                        <button class="btn btn-sm" :class="pat.is_active ? 'btn-outline-danger' : 'btn-outline-success'" @click="toggleStatus(pat.user_id, 'patients')">
                                            {{ pat.is_active ? 'Blacklist' : 'Activate' }}
                                        </button>
                                    </td>
                                </tr>
                                <tr v-if="patients.length === 0">
                                    <td colspan="6" class="text-center py-4 text-muted">No patients found</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Appointments Tab -->
                <div class="tab-pane fade" id="appointments" role="tabpanel">
                    <div class="table-responsive bg-white rounded-3 shadow-sm border border-light">
                        <table class="table table-hover align-middle mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th>ID</th>
                                    <th>Patient</th>
                                    <th>Doctor</th>
                                    <th>Date & Time</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="apt in appointments" :key="apt.id">
                                    <td class="fw-bold text-muted">#{{ apt.id }}</td>
                                    <td>{{ apt.patient_name }}</td>
                                    <td>
                                        <div class="fw-bold">{{ apt.doctor_name }}</div>
                                        <small class="text-muted">{{ apt.department_name }}</small>
                                    </td>
                                    <td>
                                        <div class="fw-bold">{{ apt.date }}</div>
                                        <small class="text-muted">{{ apt.time }}</small>
                                    </td>
                                    <td>
                                        <span class="badge" :class="{'bg-success': apt.status=='Completed', 'bg-warning text-dark': apt.status=='Booked', 'bg-danger': apt.status=='Cancelled'}">
                                            {{ apt.status }}
                                        </span>
                                    </td>
                                </tr>
                                <tr v-if="appointments.length === 0">
                                    <td colspan="5" class="text-center py-4 text-muted">No appointments found</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

            </div>
        </div>

        <!-- Doctor Modal -->
        <div class="modal fade" id="doctorModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-lg modal-dialog-centered">
                <div class="modal-content border-0 shadow-lg" style="border-radius:16px;">
                    <div class="modal-header border-bottom-0 pb-0">
                        <h5 class="modal-title fw-bold">{{ docForm.id ? 'Edit Doctor Profile' : 'Add New Doctor' }}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <form @submit.prevent="saveDoctor">
                            <div class="row g-3 mb-3" v-if="!docForm.id">
                                <div class="col-md-6">
                                    <label class="form-label">Username</label>
                                    <input type="text" class="form-control" v-model="docForm.username" required>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Email</label>
                                    <input type="email" class="form-control" v-model="docForm.email" required>
                                </div>
                            </div>
                            <div class="row g-3">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Full Name</label>
                                    <input type="text" class="form-control" v-model="docForm.full_name" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Department</label>
                                    <select class="form-select" v-model="docForm.department_id" required>
                                        <option value="" disabled>Select Dept</option>
                                        <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Contact</label>
                                    <input type="text" class="form-control" v-model="docForm.contact">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Experience</label>
                                    <input type="text" class="form-control" v-model="docForm.experience" placeholder="e.g. 5 years">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Qualification</label>
                                    <input type="text" class="form-control" v-model="docForm.qualification">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Availability</label>
                                    <input type="text" class="form-control" v-model="docForm.availability" placeholder="e.g. Mon-Fri 09:00-17:00">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Password <small class="text-muted" v-if="docForm.id">(leave blank to keep current)</small></label>
                                    <input type="password" class="form-control" v-model="docForm.password" :required="!docForm.id">
                                </div>
                            </div>
                            <div class="d-flex justify-content-end gap-2 mt-4">
                                <button type="button" class="btn btn-light" data-bs-dismiss="modal">Cancel</button>
                                <button type="submit" class="btn btn-teal px-4" :disabled="saving">
                                    <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                                    Save Doctor
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>

    </div>
    `,
    setup() {
        const stats = Vue.reactive({ doctors: '...', patients: '...', appointments: '...' })
        const doctors = Vue.ref([])
        const patients = Vue.ref([])
        const appointments = Vue.ref([])
        const departments = Vue.ref([])
        
        const searchQueries = Vue.reactive({ doctors: '', patients: '' })
        const docForm = Vue.reactive({
            id: null, username: '', email: '', full_name: '', department_id: '',
            contact: '', experience: '', qualification: '', availability: '', password: ''
        })
        const saving = Vue.ref(false)
        let doctorModalInstance = null

        const fetchApi = async (url, options = {}) => {
            const token = localStorage.getItem('token')
            return await fetch(url, {
                ...options,
                headers: { ...options.headers, 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' }
            })
        }

        Vue.onMounted(async () => {
            doctorModalInstance = new bootstrap.Modal(document.getElementById('doctorModal'))
            // Load stats & departments initially
            try {
                let res = await fetchApi('/api/admin/stats')
                if (res.ok) {
                    const data = await res.json()
                    Object.assign(stats, data)
                }
                res = await fetchApi('/api/departments')
                if (res.ok) departments.value = await res.json()
            } catch (e) {}
        })

        const fetchDoctors = async () => {
            const res = await fetchApi('/api/admin/doctors?search=' + encodeURIComponent(searchQueries.doctors))
            if (res.ok) doctors.value = await res.json()
        }

        const fetchPatients = async () => {
            const res = await fetchApi('/api/admin/patients?search=' + encodeURIComponent(searchQueries.patients))
            if (res.ok) patients.value = await res.json()
        }

        const fetchAppointments = async () => {
            const res = await fetchApi('/api/admin/appointments')
            if (res.ok) appointments.value = await res.json()
        }

        const openDoctorModal = (doc = null) => {
            if (doc) {
                Object.assign(docForm, {
                    id: doc.id, username: doc.username, email: doc.email, full_name: doc.full_name,
                    department_id: doc.department_id, contact: doc.contact, experience: doc.experience,
                    qualification: doc.qualification, availability: doc.availability, password: ''
                })
            } else {
                Object.assign(docForm, {
                    id: null, username: '', email: '', full_name: '', department_id: '',
                    contact: '', experience: '', qualification: '', availability: '', password: ''
                })
            }
            doctorModalInstance.show()
        }

        const saveDoctor = async () => {
            saving.value = true
            try {
                const url = docForm.id ? `/api/admin/doctors/${docForm.id}` : '/api/admin/doctors'
                const method = docForm.id ? 'PUT' : 'POST'
                
                const res = await fetchApi(url, {
                    method,
                    body: JSON.stringify(docForm)
                })
                const data = await res.json()
                if (res.ok) {
                    doctorModalInstance.hide()
                    fetchDoctors()
                    
                    // Refresh stats since doctor count might change
                    let s_res = await fetchApi('/api/admin/stats')
                    if (s_res.ok) Object.assign(stats, await s_res.json())
                } else {
                    alert(data.msg)
                }
            } catch (e) {
                alert('Error submitting form')
            } finally {
                saving.value = false
            }
        }

        const toggleStatus = async (userId, type) => {
            if (!confirm("Are you sure you want to change this user's status?")) return
            try {
                const res = await fetchApi(`/api/admin/users/${userId}/toggle_status`, { method: 'PUT' })
                if (res.ok) {
                    if (type === 'doctors') fetchDoctors()
                    else fetchPatients()
                } else {
                    const data = await res.json()
                    alert(data.msg)
                }
            } catch (e) {
                alert('Could not update status')
            }
        }

        return { 
            stats, doctors, patients, appointments, departments,
            searchQueries, docForm, saving,
            fetchDoctors, fetchPatients, fetchAppointments,
            openDoctorModal, saveDoctor, toggleStatus
        }
    }
}
