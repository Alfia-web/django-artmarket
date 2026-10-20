import { defineStore } from "pinia"
import {ref, onBeforeMount} from 'vue'

const useProfileStore = defineStore('profileStore',()=>{
    const isAuthenticated = ref(false)
    const userName = ref()

    async function fetchMe(){
        const r = await axios.get("/api/profile/me/")
        axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
        isAuthenticated.value = r.data.is_authenticated
        userName.value = r.data.is_authenticated ? r.data.userName : null
    }

    async function login(username, password) {
        console.log(username.value)
        console.log(password.value)
        const r = axios.post('/api/profile/login',{
            username: username.value,
            password: password.value,
        })
        fetchMe()
    }

    async function logout(params) {
        await axios.post("api/profile/logout/")
        fetchMe()
    }

    onBeforeMount(()=>{
    fetchMe()
    })

    return{
        isAuthenticated,
        userName,

        fetchMe, 
        login,
        logout
    }
})

export default useProfileStore