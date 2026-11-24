<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import { Modal } from 'bootstrap'

const props = defineProps({
    genres:{ type: Array }
})

const emit = defineEmits(['update']) 
const modalElement = ref(null)
const addPhotosInput = ref(null)
const imageToEdit = ref({})
const currentItem = ref(null)
const isFiledsFull = computed(() => {
  return (
    imageToEdit.value.name?.trim() !== '' &&
    imageToEdit.value.genre != null &&
    Number(imageToEdit.value.start_price) > 0 &&
    imageToEdit.value.start_time !== '' &&
    imageToEdit.value.end_time !== '' &&
    new Date(imageToEdit.value.end_time) >
    new Date(imageToEdit.value.start_time)
  )})
const editAlbom = computed(() =>
  currentItem.value?.album_images ?? []
)

async function onImageEditClick(image) {
    const auction = image.auction
    imageToEdit.value = { 
      id: image.id, 
      name: image.name, 
      genre: image.genre,
      auctionId: auction?.id ?? null, 
      auctionStartTime: auction?.start_time ?? null,
      start_price: auction ?  Number(auction.start_price) : 1,
      start_time:  auction ? toDateTimeLocal(auction.start_time): '', 
      end_time:  auction ? toDateTimeLocal(auction.end_time) : ''}
}

async function refreshPicture() {
  emit('update')
}

async function onDeleteImage(image){
  if (editAlbom.value.length <= 1) return
  await axios.delete(`/api/album-images/${image.id}/`)
  await refreshPicture()
}

async function onAddImageToAlbum(event) {
  const files  = Array.from(event.target.files)
  event.target.value = ''
  if(!files.length)  return
    await Promise.all(files.map(file=>{
      const fd = new FormData()
      fd.append('picture', imageToEdit.value.id)
      fd.append('imageToAlbum', file)
      return axios.post('/api/album-images/', fd)
    }))
    await refreshPicture()
}

function toDateTimeLocal(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

async function onUpdateImage() {
  await axios.patch(`/api/images/${imageToEdit.value.id}/`, {
    name: imageToEdit.value.name,
    genre: imageToEdit.value.genre,})

  const auctionData = {
    image: imageToEdit.value.id,
    start_price: imageToEdit.value.start_price,
    start_time: new Date(imageToEdit.value.start_time).toISOString(),
    end_time: new Date(imageToEdit.value.end_time).toISOString(), }

  if(imageToEdit.value.auctionId){
    await axios.patch(`/api/auctions/${imageToEdit.value.auctionId}/`, auctionData)
  }
  else{
    const response = await axios.post('/api/auctions/', auctionData)
    imageToEdit.value.auctionId = response.data.id
  }
  await refreshPicture()
}

function open(item){
    currentItem.value = item
    onImageEditClick(item)
    Modal.getOrCreateInstance(modalElement.value).show()
}

defineExpose({ open })
</script>

<template>
     <!-- бустрап модальное окно - изменение картины -->
      <div class="modal fade" ref="modalElement" tabindex="-1"
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
                    <option v-for="g in props.genres" :key="g.id" :value="g.id">
                      {{ g.name }}
                    </option>
                  </select>
                  <label>Жанр</label>
                </div>
              </div>
            </div>

            <!-- ставка -->
            <div class="row g-2 mb-3">
              <div class="col">
                <label class="form-label">Начальная ставка, ₽</label>
                <input type="number" class="form-control" v-model.number="imageToEdit.start_price "required>
              </div>

              <div class="col">
                <label class="form-label">Начало торгов</label>
                <input type="datetime-local" class="form-control"
                  v-model="imageToEdit.start_time" required>
              </div>

              <div class="col">
                <label class="form-label">Окончание торгов</label>
                <input type="datetime-local" class="form-control"
                  v-model="imageToEdit.end_time" required>
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
                    data-bs-dismiss="modal" @click="onUpdateImage" :disabled="!isFiledsFull">
              Сохранить
            </button>
          </div>
        </div>
      </div>
    </div>   
</template>