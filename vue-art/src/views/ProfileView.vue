<script setup>
import { ref, computed, onBeforeMount,  onMounted, onUnmounted, watch } from 'vue'
import axios from "axios"
import Cookies from 'js-cookie'
import "bootstrap-icons/font/bootstrap-icons.min.css"
import "bootstrap/dist/css/bootstrap.min.css"
import { Modal } from "bootstrap"
import '../assets/style.scss'
import useProfileStore from '@/stores/profileStore'
import { storeToRefs } from 'pinia'
import PictureViewer from '@/components/PictureViewer.vue'
import PictureModal from '@/components/PictureModal.vue'
import PictureEditModal from '@/components/PictureEditModal.vue'

const emit = defineEmits(['rate'])
onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
})

const {isAuthenticated} = storeToRefs(useProfileStore())

const loading = ref(false)
const images = ref([])
const genres = ref([])
const page = ref(1)
const hasNext = ref(false)
const editModal = ref(null)
const imageToAdd  = ref({
  name: '',
  genre: null,
  image: null,
  start_price: 1,
  start_time: '',
  end_time: '',
});

const selectedFiles = ref([])
const isUploading = ref(false)
let nextId = 0
const pictureModal = ref(null)

async function onRate(data) {
  console.log('onRate вызвана:', data)
  await axios.post('/api/rates/',{
    auction_id: data.auctionId,
    price: data.price,
  })    
}

function onImagePreviewClick(item) {
  pictureModal.value.open(item)
}

const albumCreateModalElement = ref(null)
const moreInput = ref(null) 

const canUpload = computed(() =>
  selectedFiles.value.length > 0 &&
  imageToAdd.value.name.trim() !== '' &&
  imageToAdd.value.genre !== null &&
  imageToAdd.value.start_price > 0 &&
  imageToAdd.value.start_time !== '' &&
  imageToAdd.value.end_time !== '' &&
  new Date(imageToAdd.value.end_time) >
      new Date(imageToAdd.value.start_time)
) 

async function fetchMyPictures(reset=true){
    if(!isAuthenticated.value) {
      images.value = []
      page.value = 1
      hasNext.value = false
      return
    }
    const nextPage = reset ? 1 : page.value + 1
    loading.value = true;
    const r = await axios.get('/api/images/my/', {params: { page: nextPage}});
    images.value =   reset ? r.data.results : [...images.value, ...r.data.results]
    page.value = nextPage
    hasNext.value = !!r.data.next
    loading.value = false
}

function loadMore() {
  return fetchMyPictures(false)
}

watch(isAuthenticated, fetchMyPictures, {immediate: true})

async function fetchGenres(){
  loading.value = true;
  const r = await axios.get('/api/genres/');
  console.log(r.data)
  genres.value = r.data.results;
  loading.value = false;
}

onBeforeMount(fetchGenres)

async function onImageAdd(){
  if(!canUpload.value) return
  isUploading.value = true
    const formData = new FormData()
    formData.append('name', imageToAdd.value.name)
    formData.append('genre', imageToAdd.value.genre)
    formData.append('start_price', imageToAdd.value.start_price)
    formData.append('start_time', imageToAdd.value.start_time)
    formData.append('end_time', imageToAdd.value.end_time)
    selectedFiles.value.forEach(item => formData.append('photos', item.file))

    await axios.post('/api/images/', formData)
    await fetchMyPictures()

    clearSelection()
    imageToAdd.value = {  name: '',
        genre: null,
        image: null,
        start_price: 1,
        start_time: '',
        end_time: ''
      }
    closeAlbumModal()
    isUploading.value = false
}

async function onRemoveClick(item) {
  if (!confirm(`Удалить «${item.name}» вместе со всеми фото?`)) return
  await axios.delete(`/api/images/${item.id}/`)
  await fetchMyPictures()
}

function openAlbumModal(){
  Modal.getOrCreateInstance(albumCreateModalElement.value).show()
}

function closeAlbumModal(){
  Modal.getInstance(albumCreateModalElement.value)?.hide()
}

function onFileChange(event) {
  for (const file of event.target.files) {
    selectedFiles.value.push({ id: nextId++, file, url: URL.createObjectURL(file) })
  }
  event.target.value = ''
  openAlbumModal()
}

function removePreview(id){
  const i = selectedFiles.value.findIndex(f=>f.id===id)
  if(i===-1){
    return
  } 
  URL.revokeObjectURL(selectedFiles.value[i].url)
  selectedFiles.value.splice(i,1)
  if(!selectedFiles.value.length) {
    closeAlbumModal()
  }
}

function clearSelection() {
  selectedFiles.value.forEach(f => URL.revokeObjectURL(f.url))
  selectedFiles.value = []
}

function onCancelAlbum() {
  clearSelection()
  closeAlbumModal()
}

const now = ref(Date.now())
let timeTimer =null

onMounted(()=>{
  timeTimer = setInterval(()=>{
    now.value = Date.now()
  }, 1000)
})

onUnmounted(()=>{
  clearInterval(timeTimer)
})

function canEditPicture(item){
  const startTime = item.auction?.start_time
  if(!startTime) return true
  return now.value < new Date(startTime).getTime()
}
</script>

<template>
  <div class="container mt-4">
      <!-- ТУТ ПОДКЛЮЧИЛ обработчик отправки формы -->
    <form @submit.prevent.stop="onImageAdd">
      <div class="row">
        <div class="col-auto">
          <div class="form-floating">
            <input type="file" class="form-control" 
            accept="image/*" multiple @change="onFileChange">
            <label>Добавить новую картинку или альбом </label>
          </div>
        </div>
        <div class="col-auto" v-if="selectedFiles.length">
          <button type="button" class="btn btn-outline-secondary" @click="openAlbumModal">
            Фото: {{ selectedFiles.length }}
          </button>
        </div>
        <div class="col-auto">
          <button class="btn btn-primary">Добавить</button>
        </div>
      </div>
    </form>

    <div class="img-grid">
      <div v-for="item in images" :key="item.id" class="image-item">
                    <div>
          <div class="img-wrapper">
            <PictureViewer :item="item" @preview="onImagePreviewClick" />
            <div class="img-actions" @click.stop v-if="canEditPicture(item)">
              <button type="button" class="btn btn-success" @click="editModal.open(item)"">
                <i class="bi bi-pen"></i>
              </button>
              <button type="button" class="btn btn-danger" @click.stop="onRemoveClick(item)" >
                <i class="bi bi-x"></i>
              </button>
            </div>
          </div>

          <div class="image-name">
            {{ item.name }}
          </div>
        </div>
        </div>
      </div>

      <PictureModal ref="pictureModal" @rate="onRate" />
      <PictureEditModal ref="editModal" :genres="genres" @update="fetchMyPictures"/>

    <!-- бустрап модальное окно - новый альбом -->
    <div class="modal fade" id="albumModal" ref="albumCreateModalElement" tabindex="-1">
      <div class="modal-dialog modal-lg modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Новый альбом ({{ selectedFiles.length }})</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Закрыть"></button>
          </div>

          <div class="modal-body">
            <div class="row g-2 mb-3">
              <div class="col">
                <input type="text" class="form-control" placeholder="Название" v-model="imageToAdd.name">
              </div>
              <div class="col-auto">
                <select class="form-select" v-model="imageToAdd.genre">
                  <option :value="null" disabled>Жанр</option>
                  <option v-for="g in genres" :key="g.id" :value="g.id">{{ g.name }}</option>
                </select>
              </div>
            </div>

            <div class="row g-3">
              <div v-for="p in selectedFiles" :key="p.id" class="col-4">
                <div class="card position-relative">
                  <button type="button" class="btn btn-danger btn-sm position-absolute top-0 end-0 m-1"
                          style="z-index: 1" @click="removePreview(p.id)">
                    <i class="bi bi-x"></i>
                  </button>
                  <img :src="p.url" class="card-img-top"
                      style="height: 180px; object-fit: contain;" alt="Предпросмотр">
                  <div class="card-body p-2">
                    <p class="card-text small text-truncate mb-0">{{ p.file.name }}</p>
                  </div>
                </div>
              </div>
            </div>

          <!-- ставка -->
          <div class="row g-2 mb-3">
            <div class="col">
              <label class="form-label">Начальная ставка, ₽</label>
              <input type="number" class="form-control" v-model.number="imageToAdd.start_price"
                min="0.01" step="0.01"required>
            </div>

            <div class="col">
              <label class="form-label">Начало торгов</label>
              <input type="datetime-local" class="form-control"
                v-model="imageToAdd.start_time" required>
            </div>

            <div class="col">
              <label class="form-label">Окончание торгов</label>
              <input type="datetime-local" class="form-control"
                v-model="imageToAdd.end_time" required>
            </div>
          </div>
        </div>

          <div class="modal-footer">
            <input type="file" class="d-none" accept="image/*" multiple
                  ref="moreInput" @change="onFileChange">
            <button type="button" class="btn btn-outline-secondary me-auto" @click="moreInput.click()">
              Добавить ещё
            </button>
            <button type="button" class="btn btn-secondary" @click="onCancelAlbum">Отмена</button>
            <button type="button" class="btn btn-primary" :disabled="!canUpload" @click="onImageAdd">
              Загрузить
            </button>
          </div>
        </div>
      </div>
    </div>
    <div class="text-center my-3" v-if="hasNext">
    <button class="btn btn-outline-primary" :disabled="loading" @click="loadMore">
      Показать ещё
    </button>
  </div>
  </div>
</template>
<style lang="scss" scoped>
</style>