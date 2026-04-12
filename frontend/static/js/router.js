const routes = [
  { path: "/", component: HomePage },
  {
    path: "/login",
    component: LoginPage,
    meta: { guestOnly: true },
  },
  {
    path: "/register",
    component: RegisterPage,
    meta: { guestOnly: true },
  },
  {
    path: "/admin",
    component: AdminDashboard,
    meta: { requiresAuth: true, role: "admin" },
  },
  {
    path: "/doctor",
    component: DoctorDashboard,
    meta: { requiresAuth: true, role: "doctor" },
  },
  {
    path: "/patient",
    component: PatientDashboard,
    meta: { requiresAuth: true, role: "patient" },
  },
  {
    path: "/reports",
    component: ReportsPage,
    meta: { requiresAuth: true, role: "admin" },
  },
  { path: "/:pathMatch(.*)*", redirect: "/login" },
];

const router = VueRouter.createRouter({
  history: VueRouter.createWebHashHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("token");
  const role = localStorage.getItem("role");

  if (to.meta.requiresAuth && !token) {
    next("/login");
    return;
  }

  if (to.meta.guestOnly && token) {
    next(role === "admin" ? "/admin" : role === "doctor" ? "/doctor" : "/patient");
    return;
  }

  if (to.meta.role && to.meta.role !== role) {
    next(token ? "/" : "/login");
    return;
  }

  next();
});
