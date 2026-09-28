<script setup>
import { ref, computed, onBeforeMount } from 'vue'
import axios from "axios"
import Cookies from 'js-cookie'
import "bootstrap-icons/font/bootstrap-icons.min.css"
import "bootstrap/dist/js/bootstrap.bundle.min.js"
import "bootstrap/dist/css/bootstrap.min.css"

  onBeforeMount(() => {
    axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
  })

  const imageToAdd  = ref({
    name: '',
    genre: null
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

  async function onLoadClick(params) {
    await fetchImages()
  }

  onBeforeMount(async () => {
    await fetchImages();
    await fetchGenres();
  })

  let c = computed(() => {
    return a.value + b.value
  })

  async function onImageAdd(){
    await axios.post("/api/images/", {
      ...imageToAdd.value,
    });
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
    await axios.put(`/api/images/${imageToEdit.value.id}/`,{
      name: imageToEdit.value.name,
      genre: imageToEdit.value.genre
    });
    await fetchImages();
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
            <button class="btn btn-primary">
              Добавить
            </button>
          </div>
        </div>
      </form>

      <div v-for="item in images" class="image-item">
        {{item.name}}

        <!-- кнопка редактировани -->
        <button class="btn btn-success" 
          @click="onImageEditClick(item)"
          data-bs-toggle='modal'
          data-bs-target='#exampleModal'>
          <i class="bi bi-pen"></i></button>
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

        <!-- кнопка закрыть -->
        <button class="btn btn-danger" @click="onRemoveClick(item)"><i class="bi bi-x"></i></button>
      </div>
    </div>
  </template>

  <style lang="scss" scoped>
  .image-item{
    padding: 0.5rem;
    margin: 0.5rem 0;
    border: 1px solid;
    border-radius: 8px;
    display: grid;
    grid-template-columns: 1fr auto auto;
    align-items: center;
    gap: 8px;
  }

  </style>