<script setup>
import { ref, onBeforeMount } from 'vue'
import axios from 'axios'
import Cookies from 'js-cookie'
import 'bootstrap-icons/font/bootstrap-icons.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import 'bootstrap/dist/css/bootstrap.min.css'
import '../assets/style.scss'
import PictureViewer from '@/components/PictureViewer.vue'
import PictureModal from '@/components/PictureModal.vue'
import useProfileStore from '@/stores/profileStore'

const profileStore = useProfileStore()
const images = ref([])
const loading = ref(false)
const page = ref(1)
const hasNext = ref(false)
const pictureModal = ref(null)
const genres = ref([])
const filters = ref({status: '', genre: null})

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get('csrftoken')
})

async function fetchGenres() {
  const r = await axios.get('/api/genres/')
  genres.value = r.data.results
}

async function fetchImages(reset = true) {
  const nextPage = reset ? 1 : page.value + 1
  loading.value = true
  const r = await axios.get('/api/images/', { params: {
        page: nextPage,
        genre: filters.value.genre,
        status: filters.value.status,
      },
    }) 
  images.value =   reset ? r.data.results : [...images.value, ...r.data.results]
  hasNext.value = !!r.data.next
  loading.value = false
}

function loadMore() {
  page.value++
  return fetchImages(false)
}

function onImagePreviewClick(item) {
  pictureModal.value.open(item)
}

function applyFilters() {
  return fetchImages(true)
}

function resetFilters() {
  filters.value = { status: '', genre: null }
  return fetchImages(true)
}

onBeforeMount(() => {
  fetchGenres()
  fetchImages()
})

</script>

<template>
  <div class="container mt-4">
    <form class="row g-2 align-items-center mb-4" @submit.prevent="applyFilters">

      <div class="col-6 col-md-auto">
        <select v-model="filters.genre" class="form-select">
          <option :value="null">Все жанры</option>
          <option v-for="g in genres" :key="g.id" :value="g.id">{{ g.name }}</option>
        </select>
      </div>

      <div class="col-6 col-md-auto">
        <select v-model="filters.status" class="form-select">
          <option value="">Любой статус</option>
          <option value="active">Идут торги</option>
          <option value="soon">Скоро начнутся</option>
          <option value="finished">Завершены</option>
        </select>
      </div>

      <div class="col-auto">
        <button class="btn btn-primary">Найти</button>
        <button type="button" class="btn btn-outline-secondary ms-2" @click="resetFilters">
          Сбросить
        </button>
      </div>
    </form>

    <div class="img-grid">
      <div v-for="item in images" :key="item.id" class="image-item">
        <div class="img-wrapper">
          <PictureViewer :item="item" @preview="onImagePreviewClick" />
        </div>
        <div class="image-name">{{ item.name }}</div>
      </div>
    </div>

    <div v-if="!loading && !images.length" class="text-center text-secondary my-4">
      Ничего не найдено
    </div>

    <div class="text-center my-3" v-if="hasNext">
      <button class="btn btn-outline-primary" :disabled="loading" @click="loadMore">
        Показать ещё
      </button>
    </div>

    <PictureModal ref="pictureModal" :current-user="profileStore.username" />
  </div>
</template>