<script setup>
import { computed } from 'vue'

const props = defineProps({
  item: { type: Object, required: true },
  previewEnabled: { type: Boolean, default: true }
})

const emit = defineEmits(['preview'])

const photos = computed(() => {
  if (props.item.album_images?.length) {
    return props.item.album_images.map(p => ({ id: p.id, src: p.imageToAlbum }))
  }
  return props.item.image ? [{ id: 'main', src: props.item.image }] : []
})
</script>

<template>
  <div :id="`carousel-${item.id}`" class="carousel slide" data-bs-ride="false">
    <div class="carousel-inner">
      <div  v-for="(photo, index) in photos" :key="photo.id"
        class="carousel-item" :class="{ active: index === 0 }">
        <img :src="photo.src" :alt="item.name"
          class="image-preview" @click="previewEnabled && emit('preview', item)">
      </div>
    </div>
  </div>
</template>