const DoctorDashboard = {
  template: `
    <div class="admin-layout">
        <div class="sidebar">
            <div class="sidebar-header">
                <img src="/static/assets/logo.jpg" alt="ZenCura">
                <h5>ZenCura</h5>
            </div>
            <div class="sidebar-menu">
                <p class="section-label px-2">NAVIGATION</p>
                <a class="sidebar-item" :class="{active: activeTab === 'overview'}" @click="activeTab = 'overview'">Dashboard</a>
                <a class="sidebar-item" :class="{active: activeTab === 'appointments'}" @click="switchTab('appointments')">Appointments</a>
                <a class="sidebar-item" :class="{active: activeTab === 'patients'}" @click="switchTab('patients')">My Patients</a>
                <a class="sidebar-item" :class="{active: activeTab === 'history'}" @click="activeTab = 'history'" v-show="selectedPatient">Patient History</a>
                <p class="section-label px-2 mt-4">SETTINGS</p>
                <a class="sidebar-item" :class="{active: activeTab === 'availability'}" @click="switchTab('availability')">Availability</a>
            </div>
            <div class="sidebar-footer">
                <div style="font-size:0.82rem; font-weight:600; color:var(--navy); margin-bottom:0.2rem;">{{ doctorName }}</div>
                <div style="font-size:0.75rem; color:var(--gray-400); margin-bottom:0.5rem;">{{ department }}</div>
                <button class="btn btn-sm btn-outline-secondary w-100" style="border-radius:8px; font-size:0.8rem;" @click="logout">Sign Out</button>
            </div>
        </div>

        <div class="main-content">
            <div v-show="activeTab === 'overview'" class="fade-in">
                <h5 class="fw-bold mb-1" style="color:var(--navy);">Dashboard</h5>
                <p style="font-size:0.85rem; color:var(--gray-400); margin-bottom:1.5rem;">Welcome back, {{ doctorName }}</p>

                <div class="row g-3 mb-4">
                    <div class="col-md-3 col-6">
                        <div class="metric-card">
                            <div class="metric-value">{{ stats.today }}</div>
                            <div class="metric-label">Today</div>
                        </div>
                    </div>
                    <div class="col-md-3 col-6">
                        <div class="metric-card">
                            <div class="metric-value">{{ stats.upcoming }}</div>
                            <div class="metric-label">Upcoming</div>
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
                            <div class="metric-value">{{ stats.completed }}</div>
                            <div class="metric-label">Completed</div>
                        </div>
                    </div>
                </div>

                <div class="row g-3 mb-4">
                    <div class="col-lg-7">
                        <div class="panel">
                            <div class="panel-header">Week Ahead</div>
                            <canvas id="docWeekChart" style="max-height:220px;"></canvas>
                        </div>
                    </div>
                    <div class="col-lg-5">
                        <div class="panel">
                            <div class="panel-header">Today's Schedule</div>
                            <div v-if="stats.today_schedule && stats.today_schedule.length > 0">
                                <div v-for="s in stats.today_schedule" :key="s.id" class="d-flex justify-content-between align-items-center py-2" style="border-bottom:1px solid var(--gray-100); font-size:0.85rem;">
                                    <div>
                                        <span class="fw-medium">{{ s.patient }}</span>
                                    </div>
                                    <div class="d-flex align-items-center gap-2">
                                        <span style="color:var(--gray-400);">{{ s.time }}</span>
                                        <span class="status-pill" :class="s.status.toLowerCase()">{{ s.status }}</span>
                                    </div>
                                </div>
                            </div>
                            <div v-else class="text-center py-4" style="color:var(--gray-400); font-size:0.85rem;">No appointments today</div>
                        </div>
                    </div>
                </div>
            </div>
            <div v-show="activeTab === 'appointments'" class="fade-in">
                <h5 class="fw-bold mb-1" style="color:var(--navy);">Appointments</h5>
                <p style="font-size:0.85rem; color:var(--gray-400); margin-bottom:1rem;">Manage your appointment schedule</p>

                <div class="d-flex gap-2 mb-3 flex-wrap">
                    <button v-for="f in [{key:'all',label:'All'},{key:'today',label:'Today'},{key:'week',label:'This Week'},{key:'upcoming',label:'Upcoming'},{key:'past',label:'Past'}]" :key="f.key" class="btn btn-sm" :class="aptFilter === f.key ? 'btn-dark' : 'btn-outline-secondary'" @click="aptFilter = f.key; fetchAppointments()" style="font-size:0.8rem;">{{ f.label }}</button>
                </div>

                <div class="panel p-0">
                    <table class="table table-hover table-sm align-middle mb-0" style="font-size:0.85rem;">
                        <thead><tr style="color:var(--gray-400); font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em;"><th class="ps-3">ID</th><th>Patient</th><th>Date</th><th>Time</th><th>Status</th><th>Treatment</th><th>Actions</th></tr></thead>
                        <tbody>
                            <tr v-for="apt in appointments" :key="apt.id">
                                <td class="ps-3 text-muted fw-medium">#{{ apt.id }}</td>
                                <td class="fw-medium">{{ apt.patient_name }}</td>
                                <td>{{ apt.date }}</td>
                                <td>{{ apt.time }}</td>
                                <td><span class="status-pill" :class="apt.status.toLowerCase()">{{ apt.status }}</span></td>
                                <td>
                                    <span v-if="apt.has_treatment" class="status-pill completed" style="font-size:0.68rem;">Recorded</span>
                                    <span v-else-if="apt.status === 'Completed'" style="color:var(--gray-400); font-size:0.78rem;">Pending</span>
                                    <span v-else style="color:var(--gray-300); font-size:0.78rem;">-</span>
                                </td>
                                <td>
                                    <div class="d-flex gap-1">
                                        <button v-if="apt.status === 'Booked'" class="btn btn-sm btn-outline-success" style="font-size:0.72rem; padding:0.2rem 0.5rem;" @click="updateStatus(apt.id, 'Completed')">Complete</button>
                                        <button v-if="apt.status === 'Booked'" class="btn btn-sm btn-outline-danger" style="font-size:0.72rem; padding:0.2rem 0.5rem;" @click="updateStatus(apt.id, 'Cancelled')">Cancel</button>
                                        <button v-if="apt.status === 'Completed' && !apt.has_treatment" class="btn btn-sm btn-teal" style="font-size:0.72rem; padding:0.2rem 0.5rem;" @click="openTreatmentModal(apt.id)">Add Treatment</button>
                                        <button v-if="apt.status === 'Completed' && apt.has_treatment" class="btn btn-sm btn-light" style="font-size:0.72rem; padding:0.2rem 0.5rem;" @click="openTreatmentModal(apt.id, true)">Edit Treatment</button>
                                    </div>
                                </td>
                            </tr>
                            <tr v-if="appointments.length === 0"><td colspan="7" class="text-center py-4 text-muted">No appointments found</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <div v-show="activeTab === 'patients'" class="fade-in">
                <h5 class="fw-bold mb-1" style="color:var(--navy);">My Patients</h5>
                <p style="font-size:0.85rem; color:var(--gray-400); margin-bottom:1rem;">Patients you have consulted</p>

                <div class="mb-3">
                    <input type="text" class="form-control form-control-sm" style="max-width:320px;" placeholder="Search name or contact..." v-model="patientSearch" @input="fetchPatients">
                </div>

                <div class="row g-3">
                    <div v-for="pat in patients" :key="pat.id" class="col-md-6 col-xl-4">
                        <div class="profile-card">
                            <div class="d-flex align-items-center gap-2 mb-2">
                                <div class="avatar" style="background:var(--teal-50); color:var(--teal-700);">{{ pat.full_name.charAt(0) }}</div>
                                <div>
                                    <div class="fw-bold" style="font-size:0.92rem; line-height:1.2;">{{ pat.full_name }}</div>
                                    <div style="font-size:0.78rem; color:var(--gray-400);">{{ pat.appointment_count }} visit{{ pat.appointment_count !== 1 ? 's' : '' }}</div>
                                </div>
                            </div>
                            <div class="profile-details">
                                <div><span class="detail-label">Phone</span> {{ pat.contact || '-' }}</div>
                                <div><span class="detail-label">Blood</span> {{ pat.blood_group || '-' }}</div>
                                <div><span class="detail-label">Gender</span> {{ pat.gender || '-' }}</div>
                                <div><span class="detail-label">DOB</span> {{ pat.dob || '-' }}</div>
                            </div>
                            <div class="mt-3 pt-2" style="border-top:1px solid var(--gray-100);">
                                <button class="btn btn-sm btn-light w-100" style="font-size:0.78rem;" @click="viewHistory(pat.id)">View Medical History</button>
                            </div>
                        </div>
                    </div>
                    <div v-if="patients.length === 0" class="col-12 text-center py-5" style="color:var(--gray-400); font-size:0.88rem;">No patients found</div>
                </div>
            </div>
            <div v-show="activeTab === 'history'" class="fade-in">
                <div class="d-flex align-items-center gap-2 mb-1">
                    <a style="color:var(--teal-600); cursor:pointer; font-size:0.82rem; font-weight:500;" @click="activeTab = 'patients'">My Patients</a>
                    <span style="color:var(--gray-300); font-size:0.82rem;">/</span>
                    <h5 class="fw-bold mb-0" style="color:var(--navy);">{{ historyData.patient ? historyData.patient.full_name : '' }}</h5>
                </div>
                <p style="font-size:0.85rem; color:var(--gray-400); margin-bottom:1rem;">Complete medical history</p>

                <div v-if="historyData.patient" class="panel mb-3">
                    <div class="panel-header mb-2">Patient Information</div>
                    <div class="profile-details" style="font-size:0.85rem;">
                        <div><span class="detail-label">Contact</span> {{ historyData.patient.contact || '-' }}</div>
                        <div><span class="detail-label">Gender</span> {{ historyData.patient.gender || '-' }}</div>
                        <div><span class="detail-label">Blood Group</span> {{ historyData.patient.blood_group || '-' }}</div>
                        <div><span class="detail-label">DOB</span> {{ historyData.patient.dob || '-' }}</div>
                        <div style="grid-column: 1 / -1;"><span class="detail-label">Address</span> {{ historyData.patient.address || '-' }}</div>
                    </div>
                </div>

                <div class="panel p-0">
                    <table class="table table-sm align-middle mb-0" style="font-size:0.85rem;">
                        <thead><tr style="color:var(--gray-400); font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em;"><th class="ps-3">Date</th><th>Time</th><th>Status</th><th>Diagnosis</th><th>Prescription</th><th>Notes</th><th>Next Visit</th></tr></thead>
                        <tbody>
                            <tr v-for="r in historyData.records" :key="r.appointment_id">
                                <td class="ps-3 fw-medium">{{ r.date }}</td>
                                <td>{{ r.time }}</td>
                                <td><span class="status-pill" :class="r.status.toLowerCase()">{{ r.status }}</span></td>
                                <td>{{ r.treatment ? r.treatment.diagnosis : '-' }}</td>
                                <td style="max-width:180px;">{{ r.treatment ? r.treatment.prescription : '-' }}</td>
                                <td style="max-width:150px;">{{ r.treatment ? r.treatment.notes : '-' }}</td>
                                <td>{{ r.treatment && r.treatment.next_visit ? r.treatment.next_visit : '-' }}</td>
                            </tr>
                            <tr v-if="!historyData.records || historyData.records.length === 0"><td colspan="7" class="text-center py-4 text-muted">No records found</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <div v-show="activeTab === 'availability'" class="fade-in">
                <h5 class="fw-bold mb-1" style="color:var(--navy);">Availability</h5>
                <p style="font-size:0.85rem; color:var(--gray-400); margin-bottom:1.5rem;">Set your schedule for patients</p>

                <div class="panel" style="max-width:560px;">
                    <div class="panel-header">Weekly Schedule</div>
                    <p class="text-muted small mb-3">Select the days and hours you are available for consultations.</p>

                    <div class="availability-picker mb-4">
                        <div v-for="day in weekDays" :key="day" 
                             class="day-chip" 
                             :class="{active: selectedDays.includes(day)}"
                             @click="toggleDay(day)">
                            {{ day }}
                        </div>
                    </div>

                    <div class="row g-3 mb-4" v-if="selectedDays.length > 0">
                        <div class="col-6">
                            <label class="form-label">Start Time</label>
                            <input type="time" class="form-control" v-model="availabilityHours.start">
                        </div>
                        <div class="col-6">
                            <label class="form-label">End Time</label>
                            <input type="time" class="form-control" v-model="availabilityHours.end">
                        </div>
                    </div>

                    <div v-else class="alert alert-light border border-dashed text-center mb-4">
                        Please select at least one day
                    </div>

                    <button class="btn btn-teal w-100" @click="saveAvailability" :disabled="savingAvailability || selectedDays.length === 0">
                        {{ savingAvailability ? 'Saving...' : 'Update Availability' }}
                    </button>
                    <p v-if="availabilityText" class="mt-3 text-center small text-muted">Current: {{ availabilityText }}</p>
                </div>
            </div>
        </div>
        <div class="modal fade" id="treatmentModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-lg modal-dialog-centered">
                <div class="modal-content border-0 shadow" style="border-radius:12px;">
                    <div class="modal-header" style="border-bottom:1px solid var(--gray-100); padding:1.25rem 1.5rem;">
                        <h6 class="modal-title fw-bold m-0">{{ treatmentForm.isEdit ? 'Edit Treatment' : 'Add Treatment' }}</h6>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body" style="padding:1.5rem;">
                        <form @submit.prevent="saveTreatment">
                            <div class="mb-3">
                                <label class="form-label">Diagnosis</label>
                                <textarea class="form-control" v-model="treatmentForm.diagnosis" rows="2" required placeholder="Enter diagnosis..."></textarea>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Prescription</label>
                                <textarea class="form-control" v-model="treatmentForm.prescription" rows="2" required placeholder="Enter medications and dosage..."></textarea>
                            </div>
                            <div class="row g-3">
                                <div class="col-md-5">
                                    <label class="form-label">Notes</label>
                                    <textarea class="form-control" v-model="treatmentForm.notes" rows="2" placeholder="Additional notes..."></textarea>
                                </div>
                                <div class="col-md-4">
                                    <label class="form-label">Next Visit</label>
                                    <input type="date" class="form-control" v-model="treatmentForm.next_visit">
                                </div>
                                <div class="col-md-3">
                                    <label class="form-label">Fee ($)</label>
                                    <input type="number" class="form-control" v-model="treatmentForm.amount" required min="0" step="0.01">
                                </div>
                            </div>
                            <div class="d-flex justify-content-end gap-2 mt-4">
                                <button type="button" class="btn btn-sm btn-light" data-bs-dismiss="modal">Cancel</button>
                                <button type="submit" class="btn btn-sm btn-teal px-3" :disabled="savingTreatment">{{ savingTreatment ? 'Saving...' : 'Save Treatment' }}</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
    `,
  setup() {
    const routerInstance = VueRouter.useRouter();
    const activeTab = Vue.ref("overview");
    const doctorName = Vue.ref("");
    const department = Vue.ref("");
    const stats = Vue.reactive({
      upcoming: 0,
      today: 0,
      completed: 0,
      cancelled: 0,
      patients: 0,
      today_schedule: [],
      chart_labels: [],
      chart_data: [],
    });
    const aptFilter = Vue.ref("all");
    const appointments = Vue.ref([]);
    const patients = Vue.ref([]);
    const patientSearch = Vue.ref("");
    const selectedPatient = Vue.ref(null);
    const historyData = Vue.reactive({ patient: null, records: [] });
    const availabilityText = Vue.ref("");
    const weekDays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
    const selectedDays = Vue.ref([]);
    const availabilityHours = Vue.reactive({ start: "09:00", end: "17:00" });
    const savingAvailability = Vue.ref(false);
    const treatmentForm = Vue.reactive({
      appointmentId: null,
      isEdit: false,
      diagnosis: "",
      prescription: "",
      notes: "",
      next_visit: "",
      amount: 150.00,
    });
    const savingTreatment = Vue.ref(false);
    let treatmentModalInstance = null;
    let weekChart = null;

    const fetchApi = async (url, options = {}) => {
      const token = localStorage.getItem("token");
      return await fetch(url, {
        ...options,
        headers: {
          ...options.headers,
          Authorization: "Bearer " + token,
          "Content-Type": "application/json",
        },
      });
    };

    const renderChart = () => {
      Vue.nextTick(() => {
        const ctx = document.getElementById("docWeekChart");
        if (!ctx) return;
        if (weekChart) weekChart.destroy();

        weekChart = new Chart(ctx, {
          type: "bar",
          data: {
            labels: stats.chart_labels || [],
            datasets: [
              {
                data: stats.chart_data || [],
                backgroundColor: "#99f6e4",
                hoverBackgroundColor: "#14b8a6",
                borderRadius: 4,
                borderSkipped: false,
              },
            ],
          },
          options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
              y: {
                beginAtZero: true,
                ticks: { precision: 0, font: { size: 11 } },
                grid: { color: "#f1f5f9" },
              },
              x: { grid: { display: false }, ticks: { font: { size: 11 } } },
            },
          },
        });
      });
    };
    const loadDashboard = async () => {
      try {
        const res = await fetchApi("/api/doctor/dashboard");
        if (res.ok) {
          const data = await res.json();
          Object.assign(stats, data);
          doctorName.value = data.doctor_name || "";
          department.value = data.department || "";
          renderChart();
        }
      } catch (e) {}
    };
    const fetchAppointments = async () => {
      try {
        const res = await fetchApi(
          "/api/doctor/appointments?filter=" + aptFilter.value
        );
        if (res.ok) appointments.value = await res.json();
      } catch (e) {}
    };

    const updateStatus = async (id, status) => {
      if (!confirm("Mark this appointment as " + status + "?")) return;
      try {
        const res = await fetchApi(
          "/api/doctor/appointments/" + id + "/status",
          {
            method: "PUT",
            body: JSON.stringify({ status }),
          }
        );
        if (res.ok) {
          fetchAppointments();
          loadDashboard();
        } else {
          const data = await res.json();
          alert(data.msg);
        }
      } catch (e) {
        alert("Error updating status");
      }
    };
    const fetchPatients = async () => {
      try {
        const res = await fetchApi(
          "/api/doctor/patients?search=" +
            encodeURIComponent(patientSearch.value)
        );
        if (res.ok) patients.value = await res.json();
      } catch (e) {}
    };
    const viewHistory = async (patientId) => {
      selectedPatient.value = patientId;
      try {
        const res = await fetchApi(
          "/api/doctor/patients/" + patientId + "/history"
        );
        if (res.ok) {
          const data = await res.json();
          historyData.patient = data.patient;
          historyData.records = data.records;
          activeTab.value = "history";
        }
      } catch (e) {}
    };
    const loadAvailability = async () => {
      try {
        const res = await fetchApi("/api/doctor/availability");
        if (res.ok) {
          const data = await res.json();
          availabilityText.value = data.availability;
          try {
            // Try parsing if it's JSON
            const parsed = JSON.parse(data.availability);
            selectedDays.value = parsed.days || [];
            availabilityHours.start = parsed.start || "09:00";
            availabilityHours.end = parsed.end || "17:00";
          } catch (e) {
            // Fallback for legacy text data
            selectedDays.value = [];
          }
        }
      } catch (e) {}
    };

    const toggleDay = (day) => {
      if (selectedDays.value.includes(day)) {
        selectedDays.value = selectedDays.value.filter((d) => d !== day);
      } else {
        selectedDays.value.push(day);
      }
    };

    const saveAvailability = async () => {
      savingAvailability.value = true;
      const payload = JSON.stringify({
        days: selectedDays.value,
        start: availabilityHours.start,
        end: availabilityHours.end,
      });
      try {
        const res = await fetchApi("/api/doctor/availability", {
          method: "PUT",
          body: JSON.stringify({ availability: payload }),
        });
        if (res.ok) {
          const readable = `${selectedDays.value.join(", ")} ${availabilityHours.start}-${availabilityHours.end}`;
          availabilityText.value = readable;
          alert("Availability updated successfully");
        }
      } catch (e) {
        alert("Error saving");
      } finally {
        savingAvailability.value = false;
      }
    };
    const openTreatmentModal = async (appointmentId, isEdit = false) => {
      treatmentForm.appointmentId = appointmentId;
      treatmentForm.isEdit = isEdit;

      if (isEdit) {
        try {
          const apt = appointments.value.find((a) => a.id === appointmentId);
          if (apt) {
            const res = await fetchApi(
              "/api/doctor/patients/" + apt.patient_id + "/history"
            );
            if (res.ok) {
              const data = await res.json();
              const record = data.records.find(
                (r) => r.appointment_id === appointmentId
              );
              if (record && record.treatment) {
                treatmentForm.diagnosis = record.treatment.diagnosis;
                treatmentForm.prescription = record.treatment.prescription;
                treatmentForm.notes = record.treatment.notes || "";
                treatmentForm.next_visit = record.treatment.next_visit || "";
                treatmentForm.amount = record.treatment.payment ? record.treatment.payment.amount : 150.00;
              }
            }
          }
        } catch (e) {}
      } else {
        treatmentForm.diagnosis = "";
        treatmentForm.prescription = "";
        treatmentForm.notes = "";
        treatmentForm.next_visit = "";
      }

      treatmentModalInstance.show();
    };

    const saveTreatment = async () => {
      savingTreatment.value = true;
      try {
        const method = treatmentForm.isEdit ? "PUT" : "POST";
        const res = await fetchApi(
          "/api/doctor/appointments/" +
            treatmentForm.appointmentId +
            "/treatment",
          {
            method,
            body: JSON.stringify({
              diagnosis: treatmentForm.diagnosis,
              prescription: treatmentForm.prescription,
              notes: treatmentForm.notes,
              next_visit: treatmentForm.next_visit || null,
              amount: treatmentForm.amount,
            }),
          }
        );
        const data = await res.json();
        if (res.ok) {
          treatmentModalInstance.hide();
          fetchAppointments();
        } else {
          alert(data.msg);
        }
      } catch (e) {
        alert("Error saving treatment");
      } finally {
        savingTreatment.value = false;
      }
    };
    const switchTab = (tab) => {
      activeTab.value = tab;
      if (tab === "appointments") fetchAppointments();
      if (tab === "patients") fetchPatients();
      if (tab === "availability") loadAvailability();
    };

    const logout = () => {
      localStorage.clear();
      routerInstance.push("/login");
    };

    Vue.onMounted(() => {
      treatmentModalInstance = new bootstrap.Modal(
        document.getElementById("treatmentModal")
      );
      loadDashboard();
    });

    return {
      activeTab,
      doctorName,
      department,
      stats,
      aptFilter,
      appointments,
      fetchAppointments,
      updateStatus,
      patients,
      patientSearch,
      fetchPatients,
      selectedPatient,
      historyData,
      viewHistory,
      loadAvailability,
      weekDays,
      selectedDays,
      availabilityHours,
      toggleDay,
      saveAvailability,
      availabilityText,
      savingAvailability,
      treatmentForm,
      savingTreatment,
      openTreatmentModal,
      saveTreatment,
      switchTab,
      logout,
    };
  },
};

