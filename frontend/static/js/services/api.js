const API = {
  BASE_URL: "/api",

  getToken() {
    return localStorage.getItem("token");
  },

  headers() {
    return {
      "Content-Type": "application/json",
      Authorization: `Bearer ${this.getToken()}`,
    };
  },

  async request(endpoint, options = {}) {
    const url = `${this.BASE_URL}${endpoint}`;
    const config = {
      ...options,
      headers: { ...this.headers(), ...options.headers },
    };

    const res = await fetch(url, config);
    const data = await res.json();

    if (!res.ok) throw new Error(data.msg || "Request failed");
    return data.data || data;
  },

  login(username, password) {
    return fetch(`${this.BASE_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    }).then((r) => r.json());
  },

  register(data) {
    return fetch(`${this.BASE_URL}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }).then((r) => r.json());
  },

  getDoctors(search = "") {
    return this.request(`/doctors${search ? `?search=${search}` : ""}`);
  },

  getAppointments() {
    return this.request("/patient/appointments");
  },

  bookAppointment(data) {
    return this.request("/appointments", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  updateAppointment(id, data) {
    return this.request(`/appointments/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  cancelAppointment(id) {
    return this.request(`/appointments/${id}`, { method: "DELETE" });
  },

  getAdminDoctors() {
    return this.request("/admin/doctors");
  },

  getAdminPatients() {
    return this.request("/admin/patients");
  },

  getDashboardSummary() {
    return this.request("/reports/dashboard-summary");
  },

  getAnalytics(days = 30) {
    return this.request(`/reports/analytics/appointments?days=${days}`);
  },

  exportCSV() {
    return this.request("/export-csv", { method: "POST" });
  },
};

