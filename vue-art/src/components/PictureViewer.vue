<script setup>
import { computed } from 'vue'

const props = defineProps({
  item: { type: Object, required: true },
  previewEnabled: { type: Boolean, default: true },
  idPrefix: { type: String, default: 'carousel' }
})

const emit = defineEmits(['preview'])
const carouselId = computed(() => `${props.idPrefix}-${props.item.id}`)
const photos = computed(() => {
  if (props.item.album_images.length) {
    return props.item.album_images.map(p => ({ id: p.id, src: p.imageToAlbum }))
  }
  return props.item.image ? [{ id: 'main', src: props.item.image }] : []
})
</script>

<template>
  <div :id="carouselId" class="carousel slide" data-bs-ride="false">
    <div class="carousel-inner">
      <div  v-for="(photo, index) in photos" :key="photo.id"
        class="carousel-item" :class="{ active: index === 0 }">
        <img :src="photo.src" :alt="item.name"
          class="image-preview" @click="previewEnabled && emit('preview', item)">
      </div>
    </div>

    <template v-if="photos.length > 1">
      <button class="carousel-control-prev" type="button"
              :data-bs-target="`#${carouselId}`" data-bs-slide="prev">
        <span class="carousel-control-prev-icon"></span>
      </button>
      <button class="carousel-control-next" type="button"
              :data-bs-target="`#${carouselId}`" data-bs-slide="next">
        <span class="carousel-control-next-icon"></span>
      </button>
    </template>
  </div>
</template>