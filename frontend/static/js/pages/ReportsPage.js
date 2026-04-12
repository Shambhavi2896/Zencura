const ReportsPage = {
  template: `
    <div class="admin-layout">
      <div class="sidebar">
        <div class="sidebar-header">
          <img src="/static/assets/logo.jpg" alt="ZenCura">
          <h5>ZenCura</h5>
        </div>
        <div class="sidebar-menu">
          <p class="section-label px-2">NAVIGATION</p>
          <a class="sidebar-item" @click="goTo('/admin')">Dashboard</a>
          <a class="sidebar-item" @click="goTo('/admin')">Doctors</a>
          <a class="sidebar-item" @click="goTo('/admin')">Patients</a>
          <a class="sidebar-item" @click="goTo('/admin')">Appointments</a>
          <a class="sidebar-item active">Reports Hub</a>
          <p class="section-label px-2 mt-4">ADMIN</p>
          <a class="sidebar-item" @click="goTo('/admin')">Back To Admin</a>
        </div>
        <div class="sidebar-footer">
          <div style="font-size:0.82rem; font-weight:600; color:var(--navy); margin-bottom:0.5rem;">Admin Account</div>
          <button class="btn btn-sm btn-outline-secondary w-100" style="border-radius:8px; font-size:0.8rem;" @click="logout">Sign Out</button>
        </div>
      </div>

      <div class="main-content">
        <div class="d-flex justify-content-between align-items-center flex-wrap gap-3 mb-4">
          <div>
            <h2 class="fw-bold mb-1">Reports Hub</h2>
            <p class="text-muted mb-0">Monthly reporting, payment visibility, and generated archives for the admin team.</p>
          </div>
          <div class="d-flex gap-2">
            <button class="btn btn-outline-teal" @click="goTo('/admin')">
              <i class="bi bi-grid me-2"></i>Admin Dashboard
            </button>
          </div>
        </div>

        <div v-if="loadingOverview" class="panel text-center py-5 mb-4">
          <div class="spinner-border text-info mb-3"></div>
          <div class="text-muted">Loading reporting overview...</div>
        </div>

        <template v-else>
          <div class="row g-3 mb-4">
            <div class="col-md-3 col-6">
              <div class="metric-card">
                <div class="section-label mb-2">{{ overview.summary.month }}</div>
                <div class="metric-value">{{ overview.summary.appointments }}</div>
                <div class="metric-label">Appointments</div>
              </div>
            </div>
            <div class="col-md-3 col-6">
              <div class="metric-card">
                <div class="section-label mb-2">Collected</div>
                <div class="metric-value">{{ compactCurrency(overview.summary.revenue) }}</div>
                <div class="metric-label">Revenue</div>
              </div>
            </div>
            <div class="col-md-3 col-6">
              <div class="metric-card">
                <div class="section-label mb-2">Pending</div>
                <div class="metric-value">{{ compactCurrency(overview.summary.pending_revenue) }}</div>
                <div class="metric-label">Unpaid treatments</div>
              </div>
            </div>
            <div class="col-md-3 col-6">
              <div class="metric-card">
                <div class="section-label mb-2">Patients Seen</div>
                <div class="metric-value">{{ overview.summary.patients_seen }}</div>
                <div class="metric-label">Unique patients</div>
              </div>
            </div>
          </div>

          <div class="row g-3 mb-4">
            <div class="col-lg-8">
              <div class="panel">
                <div class="panel-header">Recent Appointment Trend</div>
                <canvas id="reportsTrendChart" style="max-height:260px;"></canvas>
              </div>
            </div>
            <div class="col-lg-4">
              <div class="panel">
                <div class="panel-header">Payment Status Mix</div>
                <canvas id="paymentStatusChart" style="max-height:260px;"></canvas>
              </div>
            </div>
          </div>

          <div class="panel mb-4">
            <div class="d-flex justify-content-between align-items-center flex-wrap gap-3 mb-3">
              <div>
                <div class="panel-header mb-1">Monthly Report Segment</div>
                <div class="text-muted small">Pick a month and review appointments, payments, departments, and billing activity.</div>
              </div>
              <div class="d-flex align-items-center gap-2 flex-wrap justify-content-end">
                <input type="month" class="form-control" style="max-width: 190px;" v-model="selectedMonth" />
                <button class="btn btn-outline-teal text-nowrap" @click="generateMonthlyReport" :disabled="generatingReport">
                  <span v-if="generatingReport" class="spinner-border spinner-border-sm me-2"></span>
                  Generate Monthly Report
                </button>
                <button class="btn btn-teal" @click="loadMonthlyReport" :disabled="loadingMonthly">
                  <span v-if="loadingMonthly" class="spinner-border spinner-border-sm me-2"></span>
                  Load Report
                </button>
              </div>
            </div>

            <div v-if="monthlyError" class="alert alert-danger mb-3">{{ monthlyError }}</div>
            <div v-if="generationMessage" class="alert alert-success mb-3">{{ generationMessage }}</div>

            <template v-if="monthlyReport">
              <div class="row g-3 mb-4">
                <div class="col-md-2 col-6">
                  <div class="metric-card">
                    <div class="section-label mb-2">{{ monthlyReport.month }}</div>
                    <div class="metric-value">{{ monthlyReport.metrics.total_appointments }}</div>
                    <div class="metric-label">Total</div>
                  </div>
                </div>
                <div class="col-md-2 col-6">
                  <div class="metric-card">
                    <div class="section-label mb-2">Completed</div>
                    <div class="metric-value">{{ monthlyReport.metrics.completed_appointments }}</div>
                    <div class="metric-label">Visits</div>
                  </div>
                </div>
                <div class="col-md-2 col-6">
                  <div class="metric-card">
                    <div class="section-label mb-2">Cancelled</div>
                    <div class="metric-value">{{ monthlyReport.metrics.cancelled_appointments }}</div>
                    <div class="metric-label">Appointments</div>
                  </div>
                </div>
                <div class="col-md-2 col-6">
                  <div class="metric-card">
                    <div class="section-label mb-2">Revenue</div>
                    <div class="metric-value">{{ compactCurrency(monthlyReport.metrics.total_revenue) }}</div>
                    <div class="metric-label">Collected</div>
                  </div>
                </div>
                <div class="col-md-2 col-6">
                  <div class="metric-card">
                    <div class="section-label mb-2">Pending</div>
                    <div class="metric-value">{{ compactCurrency(monthlyReport.metrics.pending_revenue) }}</div>
                    <div class="metric-label">Outstanding</div>
                  </div>
                </div>
                <div class="col-md-2 col-6">
                  <div class="metric-card">
                    <div class="section-label mb-2">Patients</div>
                    <div class="metric-value">{{ monthlyReport.metrics.unique_patients }}</div>
                    <div class="metric-label">Seen</div>
                  </div>
                </div>
              </div>

              <div class="row g-3 mb-4">
                <div class="col-lg-4">
                  <div class="panel h-100">
                    <div class="panel-header">Payment Breakdown</div>
                    <div class="d-grid gap-2">
                      <template v-for="item in monthlyReport.payment_status" :key="item.status">
                        <div v-if="['Pending', 'Completed', 'Booked'].includes(item.status)" class="d-flex justify-content-between align-items-center border rounded px-3 py-2">
                          <div>
                            <div class="fw-semibold">{{ item.status }}</div>
                            <div class="small text-muted">{{ item.count }} transaction(s)</div>
                          </div>
                          <div class="fw-semibold">{{ formatCurrency(item.amount) }}</div>
                        </div>
                      </template>
                      <div v-if="monthlyReport.payment_status.filter(s => ['Pending', 'Completed', 'Booked'].includes(s.status)).length === 0" class="text-center text-muted py-4">
                        No pending or completed activity for this month.
                      </div>
                    </div>
                  </div>
                </div>

                <div class="col-lg-8">
                  <div class="panel h-100">
                    <div class="panel-header">Doctor Performance</div>
                    <table class="table table-sm align-middle">
                      <thead>
                        <tr>
                          <th>Doctor</th>
                          <th>Department</th>
                          <th>Appointments</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="doctor in monthlyReport.doctor_performance" :key="doctor.name + doctor.department">
                          <td class="fw-semibold">{{ doctor.name }}</td>
                          <td>{{ doctor.department }}</td>
                          <td>{{ doctor.appointments }}</td>
                        </tr>
                        <tr v-if="monthlyReport.doctor_performance.length === 0">
                          <td colspan="3" class="text-center text-muted py-4">No doctor activity for this month.</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>

              <div class="row g-3 mb-4">
                <div class="col-lg-5">
                  <div class="panel h-100">
                    <div class="panel-header">Department Breakdown</div>
                    <table class="table table-sm align-middle">
                      <thead>
                        <tr>
                          <th>Department</th>
                          <th>Appointments</th>
                          <th>Completed</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="department in monthlyReport.department_breakdown" :key="department.name">
                          <td class="fw-semibold">{{ department.name }}</td>
                          <td>{{ department.appointments }}</td>
                          <td>{{ department.completed }}</td>
                        </tr>
                        <tr v-if="monthlyReport.department_breakdown.length === 0">
                          <td colspan="3" class="text-center text-muted py-4">No department stats available.</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                <div class="col-lg-7">
                  <div class="panel h-100">
                    <div class="panel-header">Recent Billing Activity</div>
                    <table class="table table-sm align-middle">
                      <thead>
                        <tr>
                          <th>Patient</th>
                          <th>Doctor</th>
                          <th>Diagnosis</th>
                          <th>Amount</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        <template v-for="item in monthlyReport.recent_billings" :key="item.id">
                          <tr v-if="['Pending', 'Completed', 'Booked', 'Paid'].includes(item.status) && item.status !== 'Paid'">
                            <td class="fw-semibold">{{ item.patient }}</td>
                            <td>{{ item.doctor }}</td>
                            <td>{{ item.diagnosis }}</td>
                            <td>{{ formatCurrency(item.amount) }}</td>
                            <td><span class="status-pill" :class="statusClass(item.status)">{{ item.status }}</span></td>
                          </tr>
                        </template>
                        <tr v-if="monthlyReport.recent_billings.filter(b => b.status !== 'Paid').length === 0">
                          <td colspan="5" class="text-center text-muted py-4">No billing entries for this month.</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </template>
          </div>

          <div class="panel">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <div>
                <div class="panel-header mb-0">Generated Monthly Archives</div>
                <div class="small text-muted">These files appear only after the monthly report task generates an HTML archive.</div>
              </div>
              <span class="small text-muted">{{ overview.archives.length }} file(s)</span>
            </div>
            <div class="row g-3">
              <div class="col-lg-4">
                <div class="d-grid gap-2">
                  <button
                    v-for="archive in overview.archives"
                    :key="archive.name"
                    class="btn text-start border"
                    :class="selectedArchive && selectedArchive.name === archive.name ? 'btn-teal' : 'btn-light'"
                    @click="selectedArchive = archive"
                  >
                    <i class="bi bi-file-earmark-bar-graph me-2"></i>{{ archive.name }}
                  </button>
                  <div v-if="overview.archives.length === 0" class="text-center text-muted py-4 border rounded bg-light">
                    No generated monthly reports found yet.
                    <div class="small mt-2">Use the Generate Monthly Report button above while Redis and Celery are running.</div>
                  </div>
                </div>
              </div>
              <div class="col-lg-8">
                <div v-if="selectedArchive" class="border rounded overflow-hidden" style="height: 70vh; background:#f8fafc;">
                  <div class="d-flex justify-content-between align-items-center border-bottom px-3 py-2 bg-light">
                    <strong>{{ selectedArchive.name }}</strong>
                    <a :href="selectedArchive.url" target="_blank" class="btn btn-sm btn-dark">Open File</a>
                  </div>
                  <iframe :src="selectedArchive.url" style="width:100%; height:calc(70vh - 49px); border:0;"></iframe>
                </div>
                <div v-else class="border rounded d-flex justify-content-center align-items-center text-muted" style="height: 70vh;">
                  Select an archive to preview the generated monthly report.
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
  `,

  setup() {
    const router = VueRouter.useRouter();
    const loadingOverview = Vue.ref(true);
    const loadingMonthly = Vue.ref(false);
    const generatingReport = Vue.ref(false);
    const monthlyError = Vue.ref("");
    const generationMessage = Vue.ref("");
    const selectedArchive = Vue.ref(null);
    const selectedMonth = Vue.ref(new Date().toISOString().slice(0, 7));
    const monthlyReport = Vue.ref(null);
    const overview = Vue.reactive({
      summary: {
        month: "",
        appointments: 0,
        revenue: 0,
        pending_revenue: 0,
        patients_seen: 0,
      },
      daily_trend: { labels: [], appointments: [], completed: [] },
      payment_status: [],
      departments: [],
      top_doctors: [],
      recent_payments: [],
      archives: [],
    });

    let trendChart = null;
    let paymentChart = null;

    const goTo = (path) => router.push(path);
    const logout = () => {
      localStorage.clear();
      router.push("/login");
    };

    const formatCurrency = (value) =>
      new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 2,
      }).format(value || 0);

    const compactCurrency = (value) =>
      new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        notation: "compact",
        maximumFractionDigits: 1,
      }).format(value || 0);

    const statusClass = (status) => {
      const normalized = (status || "").toLowerCase();
      if (normalized === "completed") return "completed";
      if (normalized === "pending" || normalized === "booked") return "booked";
      return "cancelled";
    };

    const authHeaders = () => ({
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    });

    const renderCharts = () => {
      if (trendChart) {
        trendChart.destroy();
      }
      if (paymentChart) {
        paymentChart.destroy();
      }

      const trendContext = document.getElementById("reportsTrendChart");
      const paymentContext = document.getElementById("paymentStatusChart");

      if (trendContext) {
        trendChart = new Chart(trendContext, {
          type: "line",
          data: {
            labels: overview.daily_trend.labels,
            datasets: [
              {
                label: "Appointments",
                data: overview.daily_trend.appointments,
                borderColor: "#0d9488",
                backgroundColor: "rgba(13, 148, 136, 0.15)",
                tension: 0.4,
                fill: true,
                pointBackgroundColor: "#0d9488",
                pointBorderColor: "#000",
                pointBorderWidth: 1.5,
                pointRadius: 4,
              },
              {
                label: "Completed",
                data: overview.daily_trend.completed,
                borderColor: "#8b5cf6",
                backgroundColor: "rgba(139, 92, 246, 0.1)",
                tension: 0.4,
                fill: true,
                pointBackgroundColor: "#8b5cf6",
                pointBorderColor: "#000",
                pointBorderWidth: 1.5,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: "top", labels: { usePointStyle: true, boxWidth: 6, font: { weight: 'bold' } } } },
            scales: {
                y: { grid: { color: 'rgba(0,0,0,0.03)' } },
                x: { grid: { display: false } }
            }
          },
        });
      }

      if (paymentContext) {
        paymentChart = new Chart(paymentContext, {
          type: "doughnut",
          data: {
            labels: overview.payment_status.map((item) => item.status),
            datasets: [
              {
                data: overview.payment_status.map((item) => item.amount),
                backgroundColor: ["#10b981", "#f59e0b", "#f43f5e", "#6366f1"],
                hoverOffset: 10,
                borderColor: "#000",
                borderWidth: 1.5,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: "bottom" } },
          },
        });
      }
    };

    const loadOverview = async () => {
      loadingOverview.value = true;
      try {
        const res = await fetch("/api/reports/overview", {
          headers: authHeaders(),
        });
        if (!res.ok) {
          return;
        }

        const json = await res.json();
        const data = json.data || json;
        overview.summary = data.summary || overview.summary;
        overview.daily_trend = data.daily_trend || overview.daily_trend;
        overview.payment_status = data.payment_status || [];
        overview.departments = data.departments || [];
        overview.top_doctors = data.top_doctors || [];
        overview.recent_payments = data.recent_payments || [];
        overview.archives = data.archives || [];
        selectedArchive.value = overview.archives[0] || null;
      } catch (error) {
        console.error("Error loading reports overview:", error);
      } finally {
        loadingOverview.value = false;
        Vue.nextTick(renderCharts);
      }
    };

    const loadMonthlyReport = async () => {
      monthlyError.value = "";
      loadingMonthly.value = true;
      try {
        const [year, month] = selectedMonth.value.split("-");
        const res = await fetch(`/api/reports/monthly/${year}/${parseInt(month, 10)}`, {
          headers: authHeaders(),
        });

        if (!res.ok) {
          const json = await res.json();
          monthlyError.value = json.msg || "Failed to load monthly report";
          return;
        }

        const json = await res.json();
        monthlyReport.value = json.data || json;
      } catch (error) {
        monthlyError.value = "Unable to load the monthly report";
      } finally {
        loadingMonthly.value = false;
      }
    };

    const generateMonthlyReport = async () => {
      generationMessage.value = "";
      monthlyError.value = "";
      generatingReport.value = true;

      try {
        const res = await fetch("/api/admin/test/monthly-report", {
          method: "POST",
          headers: authHeaders(),
        });

        const json = await res.json();
        if (!res.ok) {
          monthlyError.value = json.msg || "Failed to trigger monthly report generation";
          return;
        }

        generationMessage.value = "Monthly report generation started. Refreshing archives in a few seconds.";
        setTimeout(async () => {
          await loadOverview();
        }, 3000);
      } catch (error) {
        monthlyError.value = "Unable to trigger monthly report generation";
      } finally {
        generatingReport.value = false;
      }
    };

    Vue.onMounted(async () => {
      await loadOverview();
      await loadMonthlyReport();
    });

    return {
      compactCurrency,
      formatCurrency,
      generatingReport,
      generationMessage,
      generateMonthlyReport,
      goTo,
      loadingMonthly,
      loadingOverview,
      loadMonthlyReport,
      logout,
      monthlyError,
      monthlyReport,
      overview,
      selectedArchive,
      selectedMonth,
      statusClass,
    };
  },
};
