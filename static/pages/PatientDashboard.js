const PatientDashboard = {
    template: `
    <div class="admin-layout">
        <div class="sidebar">
            <div class="sidebar-header">
                <img src="/static/logo.jpg" alt="ZenCura">
                <h5>ZenCura</h5>
            </div>
            <div class="sidebar-menu">
                <p class="section-label px-2">NAVIGATION</p>
                <a class="sidebar-item" :class="{active: activeTab === 'overview'}" @click="switchTab('overview')">Dashboard</a>
                <a class="sidebar-item" :class="{active: activeTab === 'doctors'}" @click="switchTab('doctors')">Find a Doctor</a>
                <a class="sidebar-item" :class="{active: activeTab === 'appointments'}" @click="switchTab('appointments')">My Appointments</a>
                <p class="section-label px-2 mt-4">ACCOUNT</p>
                <a class="sidebar-item" :class="{active: activeTab === 'profile'}" @click="switchTab('profile')">Profile Settings</a>
            </div>
            <div class="sidebar-footer">
                <div style="font-size:0.82rem; font-weight:600; color:var(--navy); margin-bottom:0.2rem;">{{ patientName }}</div>
                <div style="font-size:0.75rem; color:var(--gray-400); margin-bottom:0.5rem;">Patient Account</div>
                <button class="btn btn-sm btn-outline-secondary w-100" style="border-radius:8px; font-size:0.8rem;" @click="logout">Sign Out</button>
            </div>
        </div>

        <div class="main-content">

            <!-- OVERVIEW -->
            <div v-show="activeTab === 'overview'" class="fade-in">
                <h5 class="fw-bold mb-1" style="color:var(--navy);">Dashboard</h5>
                <p style="font-size:0.85rem; color:var(--gray-400); margin-bottom:1.5rem;">Welcome back, {{ patientName }}</p>

                <div class="row g-3 mb-4">
                    <div class="col-md-3 col-6">
                        <div class="metric-card">
                            <div class="metric-value">{{ stats.upcoming }}</div>
                            <div class="metric-label">Upcoming</div>
                        </div>
                    </div>
                    <div class="col-md-3 col-6">
                        <div class="metric-card">
                            <div class="metric-value">{{ stats.completed }}</div>
                            <div class="metric-label">Completed Visits</div>
                        </div>
                    </div>
                    <div class="col-md-3 col-6">
                        <div class="metric-card">
                            <div class="metric-value">{{ stats.cancelled }}</div>
                            <div class="metric-label">Cancelled</div>
                        </div>
                    </div>
                    <div class="col-md-3 col-6">
                        <div class="metric-card">
                            <div class="metric-value">{{ stats.total }}</div>
                            <div class="metric-label">Total Appointments</div>
                        </div>
                    </div>
                </div>

                <div class="panel">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <div class="panel-header mb-0">Upcoming Appointments</div>
                        <a style="color:var(--teal-600); cursor:pointer; font-size:0.82rem; font-weight:500;" @click="switchTab('appointments')">View all</a>
                    </div>
                    <table class="table table-sm align-middle mb-0" style="font-size:0.85rem;">
                        <thead><tr style="color:var(--gray-400); font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em;"><th class="ps-3">ID</th><th>Doctor</th><th>Department</th><th>Date</th><th>Time</th><th>Status</th></tr></thead>
                        <tbody>
                            <tr v-for="apt in stats.upcoming_appointments" :key="apt.id">
                                <td class="ps-3 text-muted fw-medium">#{{ apt.id }}</td>
                                <td class="fw-medium">{{ apt.doctor }}</td>
                                <td>{{ apt.department }}</td>
                                <td>{{ apt.date }}</td>
                                <td>{{ apt.time }}</td>
                                <td><span class="status-pill" :class="apt.status.toLowerCase()">{{ apt.status }}</span></td>
                            </tr>
                            <tr v-if="!stats.upcoming_appointments || stats.upcoming_appointments.length === 0"><td colspan="6" class="text-center py-4 text-muted">No upcoming appointments</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- FIND A DOCTOR -->
            <div v-show="activeTab === 'doctors'" class="fade-in">
                <h5 class="fw-bold mb-1" style="color:var(--navy);">Find a Doctor</h5>
                <p style="font-size:0.85rem; color:var(--gray-400); margin-bottom:1rem;">Search and book appointments with specialists</p>

                <div class="d-flex gap-2 mb-3">
                    <input type="text" class="form-control form-control-sm flex-grow-1" style="max-width:320px;" placeholder="Search name or specialization..." v-model="searchDoctors" @input="fetchDoctors">
                    <select class="form-select form-select-sm" style="max-width:200px;" v-model="filterDept" @change="fetchDoctors">
                        <option value="">All Departments</option>
                        <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
                    </select>
                </div>

                <div class="row g-3">
                    <div v-for="doc in doctorsList" :key="doc.id" class="col-md-6 col-xl-4">
                        <div class="profile-card h-100 d-flex flex-column">
                            <div class="d-flex align-items-center gap-2 mb-2">
                                <div class="avatar" style="background:var(--teal-50); color:var(--teal-700);">{{ doc.full_name.charAt(0) }}</div>
                                <div>
                                    <div class="fw-bold" style="font-size:0.92rem; line-height:1.2;">{{ doc.full_name }}</div>
                                    <div style="font-size:0.78rem; color:var(--gray-400);">{{ doc.department }}</div>
                                </div>
                            </div>
                            <div class="profile-details mb-3 flex-grow-1">
                                <div><span class="detail-label">Qual.</span> {{ doc.qualification || '—' }}</div>
                                <div><span class="detail-label">Exp.</span> {{ doc.experience || '—' }}</div>
                                <div style="grid-column: 1 / -1;"><span class="detail-label">Available</span> {{ doc.availability || 'Check Schedule' }}</div>
                            </div>
                            <div style="border-top:1px solid var(--gray-100); padding-top:0.75rem;">
                                <button class="btn btn-sm btn-teal w-100" style="font-size:0.8rem;" @click="openBookModal(doc)">Book Appointment</button>
                            </div>
                        </div>
                    </div>
                    <div v-if="doctorsList.length === 0" class="col-12 text-center py-5" style="color:var(--gray-400); font-size:0.88rem;">No doctors found matching your criteria</div>
                </div>
            </div>

            <!-- MY APPOINTMENTS -->
            <div v-show="activeTab === 'appointments'" class="fade-in">
                <h5 class="fw-bold mb-1" style="color:var(--navy);">My Appointments</h5>
                <p style="font-size:0.85rem; color:var(--gray-400); margin-bottom:1rem;">Manage your schedule and view treatments</p>

                <div class="d-flex gap-2 mb-3 flex-wrap">
                    <button v-for="f in [{key:'all',label:'All'},{key:'upcoming',label:'Upcoming'},{key:'past',label:'Past'},{key:'completed',label:'Completed'},{key:'cancelled',label:'Cancelled'}]" :key="f.key" class="btn btn-sm" :class="aptFilter === f.key ? 'btn-dark' : 'btn-outline-secondary'" @click="aptFilter = f.key; fetchAppointments()" style="font-size:0.8rem;">{{ f.label }}</button>
                </div>

                <div class="panel p-0">
                    <table class="table table-hover table-sm align-middle mb-0" style="font-size:0.85rem;">
                        <thead><tr style="color:var(--gray-400); font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em;"><th class="ps-3">ID</th><th>Doctor</th><th>Department</th><th>Date</th><th>Time</th><th>Status</th><th>Actions</th></tr></thead>
                        <tbody>
                            <template v-for="apt in appointments" :key="apt.id">
                                <tr>
                                    <td class="ps-3 text-muted fw-medium">#{{ apt.id }}</td>
                                    <td class="fw-medium">{{ apt.doctor_name }}</td>
                                    <td>{{ apt.department }}</td>
                                    <td>{{ apt.date }}</td>
                                    <td>{{ apt.time }}</td>
                                    <td><span class="status-pill" :class="apt.status.toLowerCase()">{{ apt.status }}</span></td>
                                    <td>
                                        <div class="d-flex gap-1" v-if="apt.status === 'Booked'">
                                            <button class="btn btn-sm btn-outline-teal py-0 px-2" style="font-size:0.75rem;" @click="openRescheduleModal(apt)">Reschedule</button>
                                            <button class="btn btn-sm btn-outline-danger py-0 px-2" style="font-size:0.75rem;" @click="cancelAppointment(apt.id)">Cancel</button>
                                        </div>
                                        <div class="d-flex gap-1" v-if="apt.status === 'Completed' && apt.treatment">
                                            <button class="btn btn-sm btn-light py-0 px-2" style="font-size:0.75rem;" @click="viewTreatment(apt)">View Record</button>
                                        </div>
                                    </td>
                                </tr>
                                <tr v-if="expandedTreatment === apt.id" class="table-light">
                                    <td colspan="7" class="p-3">
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
                            <tr v-if="appointments.length === 0"><td colspan="7" class="text-center py-4 text-muted">No appointments found</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- PROFILE -->
            <div v-show="activeTab === 'profile'" class="fade-in">
                <h5 class="fw-bold mb-1" style="color:var(--navy);">Profile Settings</h5>
                <p style="font-size:0.85rem; color:var(--gray-400); margin-bottom:1.5rem;">Update your personal details</p>

                <div class="panel" style="max-width:700px;">
                    <form @submit.prevent="updateProfile">
                        <div class="row g-3">
                            <div class="col-md-6">
                                <label class="form-label">Full Name</label>
                                <input type="text" class="form-control" v-model="profileForm.full_name" required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">Email</label>
                                <input type="email" class="form-control bg-light" v-model="profileForm.email" disabled>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">Contact Number</label>
                                <input type="text" class="form-control" v-model="profileForm.contact" required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">Date of Birth</label>
                                <input type="date" class="form-control" v-model="profileForm.dob">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">Gender</label>
                                <select class="form-select" v-model="profileForm.gender">
                                    <option value="">Select Gender</option>
                                    <option>Male</option><option>Female</option><option>Other</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">Blood Group</label>
                                <select class="form-select" v-model="profileForm.blood_group">
                                    <option value="">Select Blood Group</option>
                                    <option>A+</option><option>A-</option><option>B+</option><option>B-</option>
                                    <option>AB+</option><option>AB-</option><option>O+</option><option>O-</option>
                                </select>
                            </div>
                            <div class="col-12">
                                <label class="form-label">Address</label>
                                <textarea class="form-control" v-model="profileForm.address" rows="2"></textarea>
                            </div>
                        </div>
                        <div class="mt-4 pt-3" style="border-top:1px solid var(--gray-100);">
                            <button type="submit" class="btn btn-sm btn-teal px-4" :disabled="savingProfile">{{ savingProfile ? 'Saving...' : 'Save Profile' }}</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <!-- Book & Reschedule Modal -->
        <div class="modal fade" id="appointmentModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content border-0 shadow" style="border-radius:12px;">
                    <div class="modal-header" style="border-bottom:1px solid var(--gray-100); padding:1.25rem 1.5rem;">
                        <h6 class="modal-title fw-bold m-0">{{ isReschedule ? 'Reschedule Appointment' : 'Book Appointment' }}</h6>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" @click="resetBookingFlow"></button>
                    </div>
                    <div class="modal-body" style="padding:1.5rem;">
                        <div v-if="selectedDoctor && !isReschedule" class="d-flex align-items-center gap-2 mb-3 pb-3" style="border-bottom:1px solid var(--gray-100);">
                            <div class="avatar" style="background:var(--teal-50); color:var(--teal-700);">{{ selectedDoctor.full_name.charAt(0) }}</div>
                            <div>
                                <div class="fw-bold" style="font-size:0.92rem;">{{ selectedDoctor.full_name }}</div>
                                <div style="font-size:0.78rem; color:var(--gray-400);">{{ selectedDoctor.department }}</div>
                            </div>
                        </div>

                        <form @submit.prevent="submitBooking">
                            <div class="mb-3">
                                <label class="form-label">Select Date</label>
                                <input type="date" class="form-control" v-model="bookingForm.date" :min="todayDate" @change="fetchSlots" required>
                            </div>

                            <div v-if="bookingForm.date" class="mb-3">
                                <label class="form-label">Available Slots</label>
                                <div v-if="loadingSlots" class="text-muted small">Loading slots...</div>
                                <div v-else-if="availableSlots.length > 0" class="d-flex flex-wrap gap-2">
                                    <button type="button" class="btn btn-sm" v-for="slot in availableSlots" :key="slot.time"
                                            :disabled="!slot.available"
                                            :class="bookingForm.time === slot.time ? 'btn-teal' : (slot.available ? 'btn-outline-secondary' : 'btn-light text-muted')"
                                            @click="bookingForm.time = slot.time"
                                            style="font-size:0.8rem; width:70px;">
                                        {{ slot.time }}
                                    </button>
                                </div>
                                <div v-else class="text-muted small">No slots available for this date.</div>
                            </div>

                            <div v-if="bookingError" class="alert alert-danger p-2 small mb-3">{{ bookingError }}</div>

                            <div class="d-flex justify-content-end gap-2 mt-4">
                                <button type="button" class="btn btn-sm btn-light" data-bs-dismiss="modal" @click="resetBookingFlow">Cancel</button>
                                <button type="submit" class="btn btn-sm btn-teal px-3" :disabled="!bookingForm.time || savingAppointment">
                                    {{ savingAppointment ? 'Processing...' : 'Confirm' }}
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
        const routerInstance = VueRouter.useRouter()
        const activeTab = Vue.ref('overview')
        const patientName = Vue.ref('')
        
        // Stats
        const stats = Vue.reactive({ upcoming: 0, completed: 0, cancelled: 0, total: 0, upcoming_appointments: [] })

        // Doctors Search
        const searchDoctors = Vue.ref('')
        const filterDept = Vue.ref('')
        const departments = Vue.ref([])
        const doctorsList = Vue.ref([])

        // Appointments
        const aptFilter = Vue.ref('all')
        const appointments = Vue.ref([])
        const expandedTreatment = Vue.ref(null)

        // Profile
        const profileForm = Vue.reactive({ full_name: '', email: '', contact: '', dob: '', gender: '', blood_group: '', address: '' })
        const savingProfile = Vue.ref(false)

        // Booking/Reschedule Flow
        let appointmentModalInstance = null
        const isReschedule = Vue.ref(false)
        const selectedDoctor = Vue.ref(null)
        const rescheduleAptId = Vue.ref(null)
        const bookingForm = Vue.reactive({ date: '', time: '' })
        const availableSlots = Vue.ref([])
        const loadingSlots = Vue.ref(false)
        const savingAppointment = Vue.ref(false)
        const bookingError = Vue.ref('')

        const todayDate = new Date().toISOString().split('T')[0]

        const fetchApi = async (url, options = {}) => {
            const token = localStorage.getItem('token')
            return await fetch(url, {
                ...options,
                headers: { ...options.headers, 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' }
            })
        }

        // --- Data Loading --- //
        const loadDashboard = async () => {
            try {
                const res = await fetchApi('/api/patient/dashboard')
                if (res.ok) {
                    const data = await res.json()
                    Object.assign(stats, data)
                    patientName.value = data.patient_name || ''
                }
            } catch (e) {}
        }

        const fetchDepartments = async () => {
            try {
                const res = await fetchApi('/api/patient/departments')
                if (res.ok) departments.value = await res.json()
            } catch (e) {}
        }

        const fetchDoctors = async () => {
            try {
                const res = await fetchApi('/api/patient/doctors?search=' + encodeURIComponent(searchDoctors.value) + '&department=' + filterDept.value)
                if (res.ok) doctorsList.value = await res.json()
            } catch (e) {}
        }

        const fetchAppointments = async () => {
            try {
                const res = await fetchApi('/api/patient/appointments?filter=' + aptFilter.value)
                if (res.ok) appointments.value = await res.json()
            } catch (e) {}
        }

        const loadProfile = async () => {
            try {
                const res = await fetchApi('/api/patient/profile')
                if (res.ok) {
                    const data = await res.json();
                    Object.assign(profileForm, data)
                }
            } catch (e) {}
        }

        // --- Actions --- //
        const updateProfile = async () => {
            savingProfile.value = true
            try {
                const res = await fetchApi('/api/patient/profile', {
                    method: 'PUT',
                    body: JSON.stringify(profileForm)
                })
                const data = await res.json()
                if (res.ok) {
                    patientName.value = data.full_name
                    localStorage.setItem('full_name', data.full_name)
                    alert('Profile updated successfully')
                } else alert(data.msg)
            } catch (e) { alert('Failed to update profile') }
            finally { savingProfile.value = false }
        }

        const cancelAppointment = async (id) => {
            if (!confirm('Are you sure you want to cancel this appointment?')) return
            try {
                const res = await fetchApi('/api/patient/appointments/' + id + '/cancel', { method: 'PUT' })
                if (res.ok) {
                    fetchAppointments()
                    loadDashboard()
                } else alert((await res.json()).msg)
            } catch (e) { alert('Failed to cancel appointment') }
        }

        const viewTreatment = (apt) => {
            if (expandedTreatment.value === apt.id) {
                expandedTreatment.value = null;
            } else {
                expandedTreatment.value = apt.id;
            }
        }

        // --- Booking / Reschedule Flow --- //
        const fetchSlots = async () => {
            if (!bookingForm.date || !selectedDoctor.value) return;
            loadingSlots.value = true;
            availableSlots.value = [];
            bookingForm.time = '';
            
            try {
                const res = await fetchApi('/api/patient/doctors/' + selectedDoctor.value.id + '/slots?date=' + bookingForm.date)
                if (res.ok) {
                    const data = await res.json()
                    availableSlots.value = data.slots
                }
            } catch(e) {}
            finally {
                loadingSlots.value = false;
            }
        }

        const openBookModal = (doc) => {
            isReschedule.value = false
            selectedDoctor.value = doc
            bookingForm.date = ''
            bookingForm.time = ''
            availableSlots.value = []
            bookingError.value = ''
            appointmentModalInstance.show()
        }

        const openRescheduleModal = (apt) => {
            isReschedule.value = true
            rescheduleAptId.value = apt.id
            selectedDoctor.value = { id: apt.doctor_id, full_name: apt.doctor_name, department: apt.department }
            bookingForm.date = ''
            bookingForm.time = ''
            availableSlots.value = []
            bookingError.value = ''
            appointmentModalInstance.show()
        }

        const resetBookingFlow = () => {
            bookingForm.date = ''
            bookingForm.time = ''
            bookingError.value = ''
        }

        const submitBooking = async () => {
             savingAppointment.value = true;
             bookingError.value = '';
             
             let url = '/api/patient/appointments';
             let method = 'POST';
             let body = {
                 date: bookingForm.date,
                 time: bookingForm.time
             };

             if (isReschedule.value) {
                 url = '/api/patient/appointments/' + rescheduleAptId.value + '/reschedule';
                 method = 'PUT';
             } else {
                 body.doctor_id = selectedDoctor.value.id;
             }

             try {
                 const res = await fetchApi(url, { method, body: JSON.stringify(body) });
                 const data = await res.json();
                 
                 if (res.ok) {
                     appointmentModalInstance.hide();
                     fetchAppointments();
                     loadDashboard();
                     alert(isReschedule.value ? 'Appointment rescheduled successfully' : 'Appointment booked successfully');
                 } else {
                     bookingError.value = data.msg || 'An error occurred';
                 }
             } catch(e) {
                 bookingError.value = 'Failed to process request';
             } finally {
                 savingAppointment.value = false;
             }
        }

        const switchTab = (tab) => {
            activeTab.value = tab;
            if (tab === 'appointments') fetchAppointments();
            if (tab === 'doctors') {
                if (departments.value.length === 0) fetchDepartments();
                fetchDoctors();
            }
            if (tab === 'profile') loadProfile();
        }

        const logout = () => {
            localStorage.clear()
            routerInstance.push('/login')
        }

        Vue.onMounted(() => {
            appointmentModalInstance = new bootstrap.Modal(document.getElementById('appointmentModal'))
            loadDashboard()
        })

        return {
            activeTab, patientName, stats,
            searchDoctors, filterDept, departments, doctorsList, fetchDoctors,
            aptFilter, appointments, fetchAppointments, expandedTreatment, viewTreatment, cancelAppointment,
            profileForm, savingProfile, updateProfile,
            openBookModal, openRescheduleModal, fetchSlots, loadingSlots, availableSlots, bookingForm, savingAppointment, bookingError, todayDate, isReschedule, selectedDoctor, resetBookingFlow, submitBooking, switchTab, logout
        }
    }
}
