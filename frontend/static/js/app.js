const app = Vue.createApp({
  template: `<router-view />`,
});

app.use(router);
app.mount("#app");

