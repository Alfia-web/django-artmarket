<script setup>
import { ref, computed, onBeforeMount } from 'vue'
import axios from "axios"
import Cookies from 'js-cookie'
import "bootstrap-icons/font/bootstrap-icons.min.css"
import "bootstrap/dist/js/bootstrap.bundle.min.js"
import "bootstrap/dist/css/bootstrap.min.css"
import { Modal } from "bootstrap"
import '../assets/style.scss'

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
})

const loading = ref(false)
const images = ref([])
const genres = ref([])

const imageToAdd  = ref({
  name: '',
  genre: null,
  image: null
});
const selectedFiles = ref([])
const isUploading = ref(false)
let nextId = 0

const imageToShow = ref()
const imageToEdit = ref({})

const albumCreateModalElement = ref(null)
const imageShowModalElement = ref(null)
const moreInput = ref(null) 
const addPhotosInput = ref(null) 

const canUpload = computed(() =>
  selectedFiles.value.length > 0 && imageToAdd.value.name.trim() !== '' &&
  imageToAdd.value.genre !== null && !isUploading.value
)

const editAlbom = computed(() =>
  images.value.find(i => i.id === imageToEdit.value.id)?.album_images ?? []
)

async function fetchImages() {
  loading.value = true;
  const r = await axios.get('/api/images/');
  console.log(r.data)
  images.value = r.data;
  loading.value = false;
}

async function fetchGenres(){
  loading.value = true;
  const r = await axios.get('/api/genres/');
  console.log(r.data)
  genres.value = r.data;
  loading.value = false;
}

onBeforeMount(async () => {
  await fetchImages();
  await fetchGenres();
})

async function onImageAdd(){
  if(!canUpload.value) {
    return
  }
  isUploading.value = true
  try{
    const formData = new FormData()
    formData.append('name', imageToAdd.value.name)
    formData.append('genre', imageToAdd.value.genre)
    selectedFiles.value.forEach(item => formData.append('photos', item.file))

    await axios.post('/api/images/', formData)
    await fetchImages()

    clearSelection()
    imageToAdd.value = { name: '', genre: null }
    closeAlbumModal()
  } 
  catch(e){
    console.error(e)
    alert('Не удалось загрузить фотографии')
  }
  finally{
    isUploading.value = false
  }
}

// function onEditFileChange(event){
//   const file = event.target.files[0]
//   editPreview.value = file ? URL.createObjectURL(file) : imageToEdit.value.image
// }

async function onDeleteImage(image){
  if (editAlbom.value.length <= 1) return
  await axios.delete(`/api/album-images/${image.id}/`)
  await fetchImages()
}

async function onImageEditClick(image) {
    imageToEdit.value = { id: image.id, name: image.name, genre: image.genre }
}

async function onAddImageToAlbum(event) {
  const files  = Array.from(event.target.files)
  event.target.value = ''
  if(!files.length)  return
  try{
    await Promise.all(files.map(file=>{
      const fd = new FormData()
      fd.append('picture', imageToEdit.value.id)
      fd.append('imageToAlbum', file)
      return axios.post('/api/album-images/', fd)
    }))
    await fetchImages()
  }
  catch(e){
    console.error(e.response?.data ?? e)
    alert('Не удалось добавить фотографии')
  }
}

function onImagePreviewClick(image, index=0) {
  const picture = image.album_images?.[index]
  if (!picture) return
  imageToShow.value = { name: image.name, url: picture.imageToAlbum }
  Modal.getOrCreateInstance(imageShowModalElement.value).show()
}

async function onUpdateImage() {
  await axios.patch(`/api/images/${imageToEdit.value.id}/`, {
    name: imageToEdit.value.name,
    genre: imageToEdit.value.genre,
  })
  await fetchImages()
}

async function onRemoveClick(item) {
  if (!confirm(`Удалить «${item.name}» вместе со всеми фото?`)) return
  await axios.delete(`/api/images/${item.id}/`)
  await fetchImages()
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
              <div :id="`carousel-${item.id}`" class="carousel slide" data-ride="carousel">
                <div class="carousel-inner">
                  <div v-for="(photo, index) in item.album_images" :key="photo.id"
                  class="carousel-item" :class="{ active: index === 0 }">
                    <img :src="photo.imageToAlbum" :alt="item.name" class="image-preview"
                      @click="onImagePreviewClick(item, index)">
                  </div>
                </div>
                <button v-if="item.album_images?.length>1" class="carousel-control-prev" type="button"
                    :data-bs-target="`#carousel-${item.id}`" data-bs-slide="prev">
                    <span class="carousel-control-prev-icon"></span>
                </button>
                <button v-if="item.album_images?.length > 1" class="carousel-control-next" type="button"
                    :data-bs-target="`#carousel-${item.id}`" data-bs-slide="next">
                    <span class="carousel-control-next-icon"></span>
                </button>
              </div>

              <div class="img-actions" @click.stop>
                <button type="button" class="btn btn-success" @click="onImageEditClick(item)"
                        data-bs-toggle="modal" data-bs-target="#exampleModal">
                  <i class="bi bi-pen"></i>
                </button>

                <button type="button" class="btn btn-danger"
                      @click.stop="onRemoveClick(item)">
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
    </div>

        <!-- бустрап модальное окно - посмотреть картинку поближе -->
      <div class="modal fade" id="imageModal" tabindex="-1"
          aria-labelledby="imageModalLabel" aria-hidden="true" ref="imageShowModalElement">
        <div class="modal-dialog modal-lg">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="imageModalLabel">{{ imageToShow?.name }}</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Закрыть"></button>
            </div>
            <div class="modal-body text-center">
              <img v-if="imageToShow" :src="imageToShow.url" :alt="imageToShow.name" class="img-fluid">
            </div>
          </div>
        </div>
      </div>

      <!-- бустрап модальное окно - изменение картины -->
      <div class="modal fade" id="exampleModal" tabindex="-1"
         aria-labelledby="exampleModalLabel" aria-hidden="true">

      <div class="modal-dialog modal-lg modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="exampleModalLabel">
              Редактирование альбома
            </h5>
            <button type="button" class="btn-close"
                    data-bs-dismiss="modal" aria-label="Закрыть"></button>
          </div>

          <div class="modal-body">
            <div class="row g-2 mb-3">
              <div class="col">
                <div class="form-floating">
                  <input type="text" class="form-control"
                        v-model="imageToEdit.name" required>
                  <label>Название</label>
                </div>
              </div>

              <div class="col-auto">
                <div class="form-floating">
                  <select class="form-select"
                          v-model="imageToEdit.genre" required>
                    <option v-for="g in genres"
                            :key="g.id" :value="g.id">
                      {{ g.name }}
                    </option>
                  </select>
                  <label>Жанр</label>
                </div>
              </div>
            </div>

            <div class="row g-2 mb-3">
              <div v-for="picture in editAlbom"
                  :key="picture.id" class="col-4">

                <div class="position-relative">
                  <img :src="picture.imageToAlbum" alt=""
                      style="height: 110px; width: 100%; object-fit: cover;"
                      class="rounded">

                  <button type="button"
                          class="btn btn-danger btn-sm position-absolute top-0 end-0 m-1"
                          :disabled="editAlbom.length <= 1"
                          :title="editAlbom.length <= 1
                            ? 'В альбоме должно остаться хотя бы одно фото'
                            : 'Удалить фото'"
                          @click="onDeleteImage(picture)">
                    <i class="bi bi-x"></i>
                  </button>
                </div>
              </div>
            </div>

            <input type="file" class="d-none" accept="image/*" multiple
                  ref="addPhotosInput" @change="onAddImageToAlbum">

            <button type="button" class="btn btn-outline-secondary"
                    @click="addPhotosInput.click()">
              Добавить фото
            </button>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-primary"
                    data-bs-dismiss="modal" @click="onUpdateImage">
              Сохранить
            </button>
          </div>
        </div>
      </div>
    </div>   

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
</template>

<style lang="scss" scoped>
</style>