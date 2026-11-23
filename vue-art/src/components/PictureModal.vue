<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { Modal } from 'bootstrap'
import PictureViewer from '@/components/PictureViewer.vue'
import AuctionInfo  from '@/components/AuctionInfo.vue'
import useProfileStore from '@/stores/profileStore'

const profileStore = useProfileStore()
const el = ref(null)
const item = ref(null)
const auctionInfo = ref(null)

function open(picture) {
  item.value = picture
  Modal.getOrCreateInstance(el.value).show()
}

async function onRate(data) {
  await axios.post('/api/rates/', {
    auction_id: data.auctionId,
    price: data.price,
  })
  await auctionInfo.value?.fetchRates(data.auctionId)
}

defineExpose({ open })
</script>

<template>
  <div class="modal fade" tabindex="-1" ref="el">
    <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{ item?.name }}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Закрыть"></button>
        </div>

        <div class="modal-body">
          <div class="row g-4" v-if="item">
            <div class="col-lg-7">
              <PictureViewer :item="item" :preview-enabled="false" id-prefix="modal-carousel" />
            </div>
            <div class="col-lg-5">
              <AuctionInfo ref="auctionInfo":item="item" :current-user="profileStore.username" @rate="onRate" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>