<script setup>
import router from '@/router';
import axios from 'axios';
import { onBeforeMount, ref } from 'vue';
import useProfileStore from '@/stores/profileStore';
import { storeToRefs } from 'pinia';

// const isAuthenticated = ref(false)
// const userName = ref()

// async function fetchMe(){
//     const r = await axios.get("/api/profile/me/")
//     axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
//     isAuthenticated.value = r.data.is_authenticated
//     userName.value = r.data.is_authenticated ? r.data.userName : null
// }

// onBeforeMount(()=>{
//     fetchMe()
// })

const profileStore = useProfileStore()
const{
    isAuthenticated,
    userName
} = storeToRefs(profileStore)

async function onLogoutButtonClick(params) {
    profileStore.logout()
}

</script>
<template>
    <div  styly="background-color: #D8A2A2">
    <div class="container">
            <nav class="navbar navbar-expand-lg">
                <a class="navbar-brand" href="#">Navbar</a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavDropdown" aria-controls="navbarNavDropdown" aria-expanded="false" aria-label="Toggle navigation">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNavDropdown">
                    <ul class="navbar-nav me-auto">
                    <li class="nav-item active">
                    <router-link class="nav-link" to="/">Профиль</router-link>  
                    </li>
                    <li class="nav-item">
                        <router-link class="nav-link" to="/auctions">Аукционы</router-link>  
                    </li>
                    <li class="nav-item">
                        <router-link  class="nav-link"   to="/login">Вход</router-link>
                    </li>
                    <!-- <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="navbarDropdownMenuLink" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                        Dropdown link
                        </a>
                        <div class="dropdown-menu" aria-labelledby="navbarDropdownMenuLink">
                        <a class="dropdown-item" href="#">Action</a>
                        <a class="dropdown-item" href="#">Another action</a>
                        <a class="dropdown-item" href="#">Something else here</a>
                        </div>
                    </li> -->
                    </ul>
                    <div>
                        Авторизован ли: {{ userName }}
                        <button v-if="isAuthenticated" class="btn btn-outline-success" 
                            @click="onLogoutButtonClick">
                            Выйти
                        </button>
                    </div>
                </div>
            </nav>
        </div>
    </div>
</template>
<style scoped>
</style>