<script setup>
import axios from 'axios'
import {ref} from 'vue'

import { useRouter, useRoute } from 'vue-router'
import useProfileStore from '@/stores/profileStore';


const profileStore = useProfileStore()

const username = ref("")
const password=ref("")



async function onLoginClick(params) {
    profileStore.login(username.value, password.value)
    // console.log(username.value)
    // console.log(password.value)
    // const r = axios.post('/api/profile/login',{
    //     username: username.value,
    //     password: password.value,
    // })
    // fetchMe()
}
</script>

<template>
    <div class="d-flex justify-content-center p-4">
        <form style="width: 350px" @submit.prevent.stop="onLoginClick">
        <div class="mb-3">
        <label for="exampleInputEmail1" class="form-label">Логин</label>
        <input required class="form-control" v-model="username">
        </div>
        <div class="mb-3">
        <label for="exampleInputPassword1" class="form-label">Пароль</label>
        <input required type="password" class="form-control" v-model="password">
        </div>
        <button type="submit" class="btn btn-primary">Войти</button>
        </form>
    </div>
</template>


<style scoped></style>
