
const GuestNavBar = {
  template: `
    <nav class="navbar navbar-expand-lg navbar-zen fixed-top">
        <div class="container">
            <router-link to="/" class="navbar-brand d-flex align-items-center gap-2">
                <img src="/static/assets/logo.jpg" alt="ZenCura" style="width:38px; height:38px; border-radius:10px; object-fit:contain;">
                <span>ZenCura</span>
            </router-link>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#guestNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="guestNav">
                <ul class="navbar-nav ms-auto align-items-center gap-3 mt-3 mt-lg-0">
                    <li class="nav-item">
                        <router-link to="/" class="nav-link fw-semibold">Home</router-link>
                    </li>
                    <li class="nav-item">
                        <router-link to="/login" class="btn btn-outline-teal px-4">Login</router-link>
                    </li>
                    <li class="nav-item">
                        <router-link to="/register" class="btn btn-teal px-4">Register</router-link>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
  `
};
