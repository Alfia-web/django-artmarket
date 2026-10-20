<script setup>
import router from '@/router';

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
                    <ul class="navbar-nav">
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
                
                </div>
            </nav>
        </div>
    </div>
</template>
<style scoped>
</style>