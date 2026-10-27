<script setup>
import { ref, onMounted } from 'vue'
import { Modal } from 'bootstrap'
// объявялет входной параметр 
// required - родитель его передал
import AuctionInfo from '@/components/AuctionInfo.vue'

defineProps({
  item: { type: Object, required: true }
})
const emit = defineEmits(['bid'])
const imageToShow = ref(null)
const viewerKey = ref(0)
const imageShowModalElement = ref(null)

function onImagePreviewClick(item, index = 0) {
  const photos = item.album_images ?? []
  if (!photos.length) return
  imageToShow.value = { name: item.name, photos, index }
  viewerKey.value++
  Modal.getOrCreateInstance(imageShowModalElement.value).show()
}

const isOpen = ref(false)
onMounted(() => {
  const el = imageShowModalElement.value
  el.addEventListener('show.bs.modal',   () => (isOpen.value = true))
  el.addEventListener('hidden.bs.modal', () => (isOpen.value = false))
})
</script>

<template>
    <div>
        <div :id="`carousel-${item.id}`" class="carousel slide" data-ride="carousel">
            <div class="carousel-inner">
            <div v-for="(photo, index) in item.album_images" :key="photo.id"
            class="carousel-item" :class="{ active: index === 0 }">
            <img :src="photo.imageToAlbum" :alt="item.name" class="image-preview"
                @click="onImagePreviewClick(item, index)">
            </div>
            </div>
        </div>

        <div class="modal fade" id="imageModal" ref="imageShowModalElement" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-lg modal-dialog-centered">
            <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">{{ imageToShow?.name }}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Закрыть"></button>
            </div>

            <div class="modal-body p-0">
                <div v-if="imageToShow" :key="viewerKey" id="viewerCarousel"
                    class="carousel slide viewer-carousel" data-bs-interval="false">

                <div v-if="imageToShow.photos.length > 1" class="carousel-indicators">
                    <button v-for="(photo, i) in imageToShow.photos" :key="photo.id" type="button"
                            data-bs-target="#viewerCarousel" :data-bs-slide-to="i"
                            :class="{ active: i === imageToShow.index }"
                            :aria-current="i === imageToShow.index ? 'true' : undefined"
                            :aria-label="`Слайд ${i + 1}`"></button>
                </div>


                <div class="carousel-inner">
                    <div v-for="(photo, i) in imageToShow.photos" :key="photo.id"
                        class="carousel-item" :class="{ active: i === imageToShow.index }">
                    <img :src="photo.imageToAlbum" :alt="imageToShow.name" class="d-block mx-auto viewer-img">
                    </div>
                </div>

                <template v-if="imageToShow.photos.length > 1">
                    <button class="carousel-control-prev" type="button"
                            data-bs-target="#viewerCarousel" data-bs-slide="prev">
                    <span class="carousel-control-prev-icon"></span>
                    </button>
                    <button class="carousel-control-next" type="button"
                            data-bs-target="#viewerCarousel" data-bs-slide="next">
                    <span class="carousel-control-next-icon"></span>
                    </button>
                </template>
                </div>
            </div>
            </div>
        </div>
        </div>
    </div>
</template>
