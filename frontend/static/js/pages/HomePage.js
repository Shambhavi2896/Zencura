
const HomePage = {
  template: `
    <div class="landing-page">
      <guest-nav-bar></guest-nav-bar>

      <section class="hero-section">
        <div class="container text-center text-lg-start">
          <div class="row align-items-center min-vh-75 py-4">
            <div class="col-lg-6 hero-content">
              <h6 class="text-dark fw-bolder mb-2" style="letter-spacing: 0.1em;">TRUSTED HEALTHCARE PARTNER</h6>
              <h1 class="display-5 fw-bold mb-3">Premium Care For Your Family</h1>
              <p class="lead mb-4 small" style="font-size: 1.05rem; font-weight: 500;">Experience modern healthcare with ZenCura. Seamless bookings, expert staff, and digital history at your fingertips.</p>
              <div class="d-flex gap-3 justify-content-center justify-content-lg-start">
                <router-link to="/register" class="btn btn-teal px-4 py-2">Book Now</router-link>
                <router-link to="/login" class="btn btn-outline-teal px-4 py-2">Patient Portal</router-link>
              </div>
              
              <div class="mt-4 d-flex gap-4 justify-content-center justify-content-lg-start stats-row">
                <div>
                  <h4 class="fw-bolder mb-0">50+</h4>
                  <small class="text-dark fw-bold">Specialists</small>
                </div>
                <div>
                  <h4 class="fw-bolder mb-0">10k+</h4>
                  <small class="text-dark fw-bold">Patients</small>
                </div>
                <div>
                  <h4 class="fw-bolder mb-0">24/7</h4>
                  <small class="text-dark fw-bold">Support</small>
                </div>
              </div>
            </div>
            <div class="col-lg-5 offset-lg-1 mt-4 mt-lg-0">
              <div class="hero-image-wrapper">
                <img src="/static/assets/hero.png" alt="Hospital interior" class="img-fluid" style="box-shadow: var(--shadow-lg); border-radius: var(--radius-lg);">
                <div class="floating-badge top-right p-2 h6 mb-0" style="font-size:0.75rem; background: rgba(255,255,255,0.9); backdrop-filter: blur(5px); border: 1px solid rgba(255,255,255,0.5); box-shadow: var(--shadow);">
                  <i class="bi bi-shield-check text-success"></i>
                  <span>Certified Staff</span>
                </div>
                <div class="floating-badge bottom-left p-2 h6 mb-0" style="font-size:0.75rem; background: rgba(255,255,255,0.9); backdrop-filter: blur(5px); border: 1px solid rgba(255,255,255,0.5); box-shadow: var(--shadow);">
                  <i class="bi bi-clock-history text-primary"></i>
                  <span>No Wait Time</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="features-section py-4">
        <div class="container py-4">
          <div class="text-center mb-4">
            <h2 class="fw-bold h2">Why Choose ZenCura?</h2>
          </div>
          <div class="row g-3">
            <div class="col-md-4">
              <div class="panel text-center p-4">
                <div class="icon-circle mx-auto mb-3" style="width: 56px; height: 56px; background: var(--teal-soft); color: var(--accent); border-radius: 50%;">
                  <i class="bi bi-calendar-check fs-3"></i>
                </div>
                <h5 class="fw-bold h6">Easy Booking</h5>
                <p class="text-muted small mb-0">Schedule appointments with top doctors in seconds.</p>
              </div>
            </div>
            <div class="col-md-4">
              <div class="panel text-center p-4">
                <div class="icon-circle mx-auto mb-3" style="width: 56px; height: 56px; background: var(--lavender-soft); color: var(--purple); border-radius: 50%;">
                  <i class="bi bi-file-earmark-medical fs-3"></i>
                </div>
                <h5 class="fw-bold h6">Digital History</h5>
                <p class="text-muted small mb-0">Access treatments and prescriptions anytime.</p>
              </div>
            </div>
            <div class="col-md-4">
              <div class="panel text-center p-4">
                <div class="icon-circle mx-auto mb-3" style="width: 56px; height: 56px; background: var(--dusty-rose); color: #e53e3e; border-radius: 50%;">
                  <i class="bi bi-envelope-check fs-3"></i>
                </div>
                <h5 class="fw-bold h6">Instant Alerts</h5>
                <p class="text-muted small mb-0">Receive reminders and reports automatically.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <footer class="footer-landing py-4">
        <div class="container text-center">
          <div class="mb-3">
            <h4 class="fw-bold text-teal-700 mb-1">ZenCura</h4>
            <p class="small text-muted mb-0">Modern Healthcare. Modern Technology.</p>
          </div>
          <div class="d-flex justify-content-center gap-3 mb-3 footer-links small">
            <router-link to="/login">Doctor Login</router-link>
            <router-link to="/login">Admin Portal</router-link>
            <a href="#">Privacy Policy</a>
          </div>
          <p class="small text-muted mb-0">&copy; 2026 ZenCura Hospital Management. All rights reserved.</p>
        </div>
      </footer>
    </div>
  `,
  components: {
    "guest-nav-bar": GuestNavBar,
  },
};
