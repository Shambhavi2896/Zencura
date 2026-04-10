const AUTH = {
  isAuthenticated() {
    return !!localStorage.getItem("token");
  },

  getRole() {
    return localStorage.getItem("role");
  },

  getUsername() {
    return localStorage.getItem("username");
  },

  getFullName() {
    return (
      localStorage.getItem("full_name") || localStorage.getItem("username")
    );
  },

  isAdmin() {
    return this.getRole() === "admin";
  },

  isDoctor() {
    return this.getRole() === "doctor";
  },

  isPatient() {
    return this.getRole() === "patient";
  },

  logout() {
    localStorage.clear();
  },
};

const UTILS = {
  formatDate(date) {
    return new Date(date).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  },

  formatTime(time) {
    return new Date(`2000-01-01T${time}`).toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    });
  },

  formatDateTime(datetime) {
    const date = new Date(datetime);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  },

  showAlert(message, type = "info") {
    alert(`[${type.toUpperCase()}] ${message}`);
  },

  deepClone(obj) {
    return JSON.parse(JSON.stringify(obj));
  },
};

const ROUTES = {
  LOGIN: "/login",
  REGISTER: "/register",
  ADMIN: "/admin",
  DOCTOR: "/doctor",
  PATIENT: "/patient",
  REPORTS: "/reports",
};
