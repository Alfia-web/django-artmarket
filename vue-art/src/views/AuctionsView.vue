<script setup>
import { ref, computed, onBeforeMount } from 'vue'
import axios from "axios"
import Cookies from 'js-cookie'
import "bootstrap-icons/font/bootstrap-icons.min.css"
import "bootstrap/dist/js/bootstrap.bundle.min.js"
import "bootstrap/dist/css/bootstrap.min.css"
import '../assets/style.scss'

  onBeforeMount(() => {
    axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
  })

  const imageFile = ref()
  const imagePreview = ref('')
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

  async function onUpdateImage() {
     const formData = new FormData();

    formData.append('name', imageToEdit.value.name);
    formData.append('genre', imageToEdit.value.genre);

    if (imageFile.value.files[0]) {
        formData.append('image', imageFile.value.files[0]);
    }

    await axios.put(
        `/api/images/${imageToEdit.value.id}/`,
        formData
    );

    await fetchImages();
  }

  async function onFileChange() {
    imagePreview.value = URL.createObjectURL(imageFile.value.files[0])
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
              accept="image/*" required  ref="imageFile" @change="onFileChange">
              <label>Картина</label>
            </div>
          </div>
          <div class="col-auto">
              <img :src="imagePreview" style="max-height: 60px;" alt="">
          </div>
          <div class="col-auto">
            <button class="btn btn-primary">
              Добавить
            </button>
          </div>
        </div>
      </form>

        <div class="img-grid">
          <div v-for="item in images" class="image-item">
            <div class="img-wrapper">
              <img :src="item.image" :alt="item.name" class="image-preview">
              <div class="img-actions">
                <!-- кнопка редактировани -->
                <button class="btn btn-success" 
                @click="onImageEditClick(item)"
                data-bs-toggle='modal'
                data-bs-target='#exampleModal'>
                <i class="bi bi-pen"></i></button>

                <!-- кнопка закрыть -->
                <button class="btn btn-danger" @click="onRemoveClick(item)"><i class="bi bi-x"></i></button>
              </div>
            </div>

            <div class="image-name">
              {{ item.name }}
            </div>
        </div>

        <!-- бустрап модальное окно  -->
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
              <div class="row">
                <div class="col-auto">
                  <div class="form-floating">
                    <input type="file" class="form-control" 
                    accept="image/*" required  ref="imageFile" @change="onFileChange">
                    <label>Картина</label>
                  </div>
                </div>
                <div class="col-auto">
                    <img :src="imagePreview" style="max-height: 100px; padding-bottom: 4px;" alt="">
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
    </div>
  </template>

  <style lang="scss" scoped>
  </style>