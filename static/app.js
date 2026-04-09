// ZenCura HMS - App Entry Point
// Components and pages are loaded via separate script files
// Router is defined in utils/router.js

const app = Vue.createApp({
    template: `<router-view />`,
})

app.use(router)
app.mount('#app')
