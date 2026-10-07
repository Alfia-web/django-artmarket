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

// const imageFile = ref([])
const editImageFile = ref()
// const imagePreview = ref([])
// const showAlbumModal = ref(false)

const albumModalElement = ref(null)
const moreInput = ref(null)
const selectedFiles = ref([])
const isUploading = ref(false)
const editPreview = ref('')
const imageToEdit = ref({})
let nextId = 0

const canUpload = computed(() =>
  selectedFiles.value.length > 0 && imageToAdd.value.name.trim() !== '' &&
  imageToAdd.value.genre !== null && !isUploading.value
)

const imageToShow = ref()
const imageToAdd  = ref({
  name: '',
  genre: null,
  image: null
});

const loading = ref(false)
const images = ref([])
const genres = ref([])

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

async function onImageAdd(){''
  if(!canUpload.value) {
    return
  }
  isUploading.value = true
  try{
    const total = selectedFiles.value.length
    await Promise.all(
      selectedFiles.value.map((item, i)=>{
        const formData = new FormData()
        formData.append('name', total > 1 ? `${imageToAdd.value.name} ${i+1}` : imageToAdd.value.name);
        formData.append('genre', imageToAdd.value.genre);
        formData.append('image', item.file);
        return axios.post('/api/images/', formData);
      }))
    await fetchImages();
    clearSelection()
    imageToAdd.value = {name: '', genre: null, image: null}
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

function onEditFileChange(event){
  const file = event.target.files[0]
  editPreview.value = file ? URL.createObjectURL(file) : imageToEdit.value.image
}

async function onRemoveClick(image){
  await axios.delete(`/api/images/${image.id}/`)
  await fetchImages();
}

async function onImageEditClick(image) {
    imageToEdit.value = {...image};
    editPreview.value =image.image
    if(editImageFile.value){
      editImageFile.value.value = ''
    }
}

function onImagePreviewClick(image) {
  imageToShow.value = image
  const modalElement = document.getElementById('imageModal')
  const modal = Modal.getOrCreateInstance(modalElement)
  modal.show()
}

async function onUpdateImage() {
    const formData = new FormData();

  formData.append('name', imageToEdit.value.name);
  formData.append('genre', imageToEdit.value.genre);

  if (editImageFile.value.files[0]) {
      formData.append('image', editImageFile.value.files[0]);
  }

  await axios.put(
      `/api/images/${imageToEdit.value.id}/`,
      formData
  );

  await fetchImages();
}

function openAlbumModal(){
  Modal.getOrCreateInstance(albumModalElement.value).show()
}

function closeAlbumModal(){
  Modal.getInstance(albumModalElement.value)?.hide()
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
        <div class="col">
          <div class="form-floating">
            <!-- ТУТ ПОДКЛЮЧИЛ imageToAdd.name -->
            <input
              type="text"
              class="form-control"
              v-model="imageToAdd.name"
              required
            />
            <label for="floatingInput">Имя</label>
          </div>
        </div>
        <div class="col-auto">
            <!-- А ТУТ ПОДКЛЮЧИЛ К select -->
          <div class="form-floating">
            <select class="form-select" v-model="imageToAdd.genre" required>
              <option :value="g.id" v-for="g in genres">{{ g.name }}</option>
            </select>
            <label for="floatingInput">Жанры</label>
          </div>
        </div>
        <div class="col-auto">
          <div class="form-floating">
            <input type="file" class="form-control" 
            accept="image/*" multiple @change="onFileChange">
            <label>Картина</label>
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
                <img :src="item.image" :alt="item.name" class="image-preview"
                    @click="onImagePreviewClick(item)">
                <div class="img-actions" @click.stop>
                <button type="button" class="btn btn-success"
                        @click="onImageEditClick(item)"
                        data-bs-toggle="modal" data-bs-target="#exampleModal">
                  <i class="bi bi-pen"></i>
                </button>

                <button type="button" class="btn btn-danger"
                        @click.stop="onRemoveClick(item)">
                  <i class="bi bi-x"></i>
                </button>
              </div>
            </div>
          </div>
  
          <div class="image-name">
            {{ item.name }}
          </div>
        </div>
      </div>


        <!-- бустрап модальное окно - посмотреть картинку поближе -->
      <div class="modal fade" id="imageModal" tabindex="-1"
          aria-labelledby="imageModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="imageModalLabel">{{ imageToShow?.name }}</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Закрыть"></button>
            </div>
            <div class="modal-body text-center">
              <img v-if="imageToShow" :src="imageToShow.image" :alt="imageToShow.name" class="img-fluid">
            </div>
          </div>
        </div>
      </div>

      <!-- бустрап модальное окно - изменение картины -->
      <div class="modal fade" id="exampleModal" tabindex="-1"
        aria-labelledby="exampleModalLabel" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="exampleModalLabel">
                Редактирование картины
              </h5>
              <button
                type="button"
                class="btn-close"
                data-bs-dismiss="modal"
                aria-label="Закрыть"
              ></button>
            </div>
            <div class="modal-body">
              <div class="row">
                <div class="col">
                  <div class="form-floating">
                    <!-- ТУТ ПОДКЛЮЧИЛ imageToAdd.name -->
                    <input
                      type="text"
                      class="form-control"
                      v-model="imageToEdit.name"
                      required
                    />
                    <label for="floatingInput">Имя</label>
                  </div>
                </div>
                <div class="col-auto">
                    <!-- А ТУТ ПОДКЛЮЧИЛ К select -->
                  <div class="form-floating">
                    <select class="form-select" v-model="imageToEdit.genre" required>
                      <option :value="g.id" v-for="g in genres">{{ g.name }}</option>
                    </select>
                    <label for="floatingInput">Жанры</label>
                  </div>
                </div>
              </div>
            </div>
            <!-- менять картинку -->
            <div class="row px-3">
              <div class="col-auto">
                <div class="form-floating">
                  <input type="file" class="form-control" 
                  accept="image/*" required  ref="editImageFile"  @change="onEditFileChange">
                  <label>Картина</label>
                </div>
              </div>
              <div class="col-auto">
                  <img v-if="editPreview" :src="editPreview" style="max-height: 70px;" alt="">
              </div>
            </div>

            <div class="modal-footer">
              <button type="button" class="btn btn-secondary"
                data-bs-dismiss="modal">
                Закрыть
              </button>
              <button type="button" class="btn btn-primary"
              data-bs-dismiss="modal" @click="onUpdateImage">
                Сохранить
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- бустрап модальное окно - выбора картинок в альбом -->
    <div class="modal fade" id="albumModal" ref="albumModalElement" tabindex="-1">
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