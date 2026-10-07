<script setup>
import { ref, onBeforeMount } from 'vue'
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

const imageFile = ref([])
const editImageFile = ref()
const imagePreview = ref([])
const showAlbumModal = ref(false)

const imageToShow = ref()
const imageToAdd  = ref({
  name: '',
  genre: null,
  image: null
});
const imageToEdit = ref([])
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

async function onImageAdd(){
  const formData = new FormData()
  formData.append('name', imageToAdd.value.name);
  formData.append('genre', imageToAdd.value.genre);
  formData.append('image', imageFile.value.files[0]);

  await axios.post('/api/images/', formData);
  await fetchImages();
}

async function onRemoveClick(image){
  await axios.delete(`/api/images/${image.id}/`)
  await fetchImages();
}

async function onImageEditClick(image) {
    imageToEdit.value = {...image};
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

function onFileChange(event) {
imagePreview.value = Array.from(event.target.files).map(file => ({
  file: file,
  url: URL.createObjectURL(file)
  }))

  const modalElemet = document.getElementById('albumModal')
  const modal = Modal.getOrCreateInstance(modalElemet)
  modal.show() 
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
            accept="image/*"  ref="imageFile" multiple @change="onFileChange">
            <label>Картина</label>
          </div>
        </div>
        <!-- <div class="col-auto d-flex gap-2">
          <div v-for="preview in imagePreview" :key="preview">
              <img :src="preview" style="max-height: 60px;" alt="">
          </div>
        </div> -->
        <div class="col-auto">
          <button class="btn btn-primary">
            Добавить
          </button>
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
                  accept="image/*" required  ref="editImageFile" multiple @change="onFileChange">
                  <label>Картина</label>
                </div>
              </div>
              <div class="col-auto">
                  <img :src="imagePreview" style="max-height: 70px; padding-bottom: 4px;" alt="">
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
    <div class="modal fade" id="albumModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Выбранные картины</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Закрыть"></button>
          </div>
          <div class="modal-body">
            <div class="row g-3">
              <div v-for="p in imagePreview" :key="p.url" class="col-4">
                <div class="card">
                  <img :src="p.url" class="card-img-top"
                      style="height: 180px; object-fit: contain;" alt="Предпросмотр">
                  <div class="card-body">
                    <p class="card-text">{{ p.file.name }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
            <button type="button" class="btn btn-primary" data-bs-dismiss="modal">Сохранить</button>
          </div>
        </div>
      </div>
    </div>
</template>

<style lang="scss" scoped>
</style>