import { defineStore } from "pinia"
import {ref, onBeforeMount} from 'vue'
import axios from 'axios'
import Cookies from 'js-cookie'

const useProfileStore = defineStore('profileStore',()=>{
    const isAuthenticated = ref(false)
    const username = ref()

    axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
    axios.defaults.baseURL = 'http://localhost:8000/'
    axios.defaults.withCredentials = true

    async function fetchMe(){
        const r = await axios.get("/api/profile/me/")
        isAuthenticated.value = r.data.is_authenticated
        username.value = r.data.is_authenticated ? r.data.username : null
    }

    async function login(username, password) {
        console.log(username)
        console.log(password)
        const r = await axios.post('/api/profile/login/',{
            username: username,
            password: password,
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
        username,

        fetchMe, 
        login,
        logout
    }
})

export default useProfileStore