const RegisterPage = {
  template: `
    <div class="auth-page-wrapper">
        <guest-nav-bar></guest-nav-bar>
        <div class="auth-page">
            <div class="auth-card register-card fade-in">
                <img src="/static/assets/logo.jpg" class="auth-logo" alt="ZenCura">
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
  components: {
    "guest-nav-bar": GuestNavBar,
  },
  setup() {
    const form = Vue.reactive({
      username: "",
      email: "",
      password: "",
      full_name: "",
      contact: "",
      gender: "",
      dob: "",
      blood_group: "",
      address: "",
    });
    const error = Vue.ref("");
    const success = Vue.ref("");
    const loading = Vue.ref(false);
    const router = VueRouter.useRouter();

    const register = async () => {
      error.value = "";
      success.value = "";
      loading.value = true;
      try {
        const res = await fetch("/api/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(form),
        });
        const data = await res.json();
        if (!res.ok) {
          error.value = data.msg || "Registration failed";
          return;
        }
        success.value = data.msg;
        setTimeout(() => router.push("/login"), 1500);
      } catch (e) {
        error.value = "Something went wrong. Try again.";
      } finally {
        loading.value = false;
      }
    };

    return { form, error, success, loading, register };
  },
};

