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

const images = ref([])
const loading = ref(false)
const page = ref(1)
const hasNext = ref(false)
const pictureModal = ref(null)

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get('csrftoken')
})

async function fetchImages(reset = true) {
  if (reset) page.value = 1
  loading.value = true
  const r = await axios.get('/api/images/', { params: { page: page.value } })
  const list = r.data.results 
  images.value = reset ? list : [...images.value, ...list]
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

onBeforeMount(fetchImages)
</script>

<template>
  <div class="container mt-4">
    <div class="img-grid">
      <div v-for="item in images" :key="item.id" class="image-item">
        <div class="img-wrapper">
          <PictureViewer :item="item" @preview="onImagePreviewClick" />
        </div>
        <div class="image-name">{{ item.name }}</div>
      </div>
    </div>

    <div class="text-center my-3" v-if="hasNext">
      <button class="btn btn-outline-primary" :disabled="loading" @click="loadMore">
        Показать ещё
      </button>
    </div>

    <PictureModal ref="pictureModal" />
  </div>
</template>