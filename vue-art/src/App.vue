<script setup>

import NavBar from './components/NavBar.vue';
import router from '@/router';

</script>
<template>
    <nav-bar></nav-bar>

    <div class="container">
      <router-view></router-view>
    </div>

</template>
<style scoped>
</style>