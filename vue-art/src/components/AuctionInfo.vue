<script setup>
import { computed, onBeforeUnmount, onMounted, onUnmounted, ref, watch } from 'vue'
import axios from 'axios'

const props = defineProps({
  item: { type: Object, required: true },
  currentUser: {type: String, default: null}})
const emit = defineEmits(['rate'])

const auction = computed(() => props.item?.auction ?? null)
const hasAuction = computed(() => auction.value !== null)
const isOwner = computed(() => {
  return props.item.user === props.currentUser
})
const now = ref(Date.now())

let timer = null
onMounted(() => {
  timer = setInterval(() => now.value = Date.now(), 1000)
})

onUnmounted(() => {
  clearInterval(timer) 
})

const startMs = computed(function() {
  if (hasAuction.value) {
    return new Date(auction.value.start_time).getTime()
  }
  return null
})

const endMs = computed(function() {
  if (hasAuction.value) {
    return new Date(auction.value.end_time).getTime()
  }
  return null
})

const status = computed(() => {
  if (!hasAuction.value) return 'none'
  if (now.value < startMs.value) return 'soon'
  if (now.value < endMs.value) return 'active'
  return 'finished'
})

const timerLabel = computed(() => ({
  soon: 'До начала торгов',
  active: 'До окончания торгов',
  finished: 'Торги завершены',
}[status.value]))

const timerText = computed(() => {
  if (status.value === 'finished') return '00:00:00'
  const target = status.value === 'soon' ? startMs.value : endMs.value
  const s = Math.max(0, Math.floor((target - now.value) / 1000))
  const d = Math.floor(s / 86400)
  const h = Math.floor((s % 86400) / 3600)
  const m = Math.floor((s % 3600) / 60)
  const p = (n) => String(n).padStart(2, '0')
  return `${d ? d + ' д ' : ''}${p(h)}:${p(m)}:${p(s % 60)}`
})

const fmtDate = (iso) =>
  new Date(iso).toLocaleString('ru-RU', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  }).replace(',', '')
const fmtPrice = (v) => `${Number(v)} ₽`

const currentPrice = ref(null)
const rates = ref([])
const rate = ref('')
const ratesCount = computed(() => rates.value.length)

const canRate = computed(() => hasAuction.value && status.value === 'active' && !isOwner.value && 
  currentPrice.value !== null && Number(rate.value) > currentPrice.value)

function sendRate() {
  if (!canRate.value) return
  emit('rate', { auctionId: auction.value.id, price: Number(rate.value) })
  rate.value = ''
}

async function fetchRates(auction_id){
  const response = await axios.get(`/api/rates/auction/${auction_id}/`)
  currentPrice.value = response.data.current_price
  rates.value = response.data.rates
}

let updateTimer = null
watch(() => auction.value?.id, (newId) =>{
  clearInterval(updateTimer)

  if(!newId){
    currentPrice.value = null
    rates.value = []
    return
  }

  fetchRates(newId)
  updateTimer = setInterval(() => {
    if (status.value === 'finished') {
      clearInterval(updateTimer) 
    } else {
      fetchRates(newId) 
    }
  }, 5000)
}, { immediate: true })

const winner = ref(null)
async function fetchWinner(auctionId) {
  const response = await axios.get(`/api/auctions/${auctionId}/winner/`)
  winner.value = response.data.winner
}

const finishedAuctionId = computed(() => 
  status.value === 'finished' ? auction.value?.id : null
)

watch(finishedAuctionId, (id) => {
  fetchWinner(id)
}, { immediate: true })

onUnmounted(() => clearInterval(updateTimer))

const sortedRates = computed(() => 
  rates.value.toSorted((a, b) => b.add_at.localeCompare(a.add_at))
)

defineExpose({ fetchRates })
</script>

<template>
  <div class="auction-panel">
    
    <div class="rate-current">
      <span v-if="status === 'finished'" class="rate-winner">
        {{ winner ? `Победитель: ${winner.username}` : 'Победителя нет' }}
      </span>
    </div>


    <!-- о картине -->
    <h6 class="section-title">О картине</h6>
    <div class="info-row">
      <span class="info-label">Название</span>
      <span class="info-value">{{ item.name }}</span>
    </div>
    <div class="info-row">
      <span class="info-label">Продавец</span>
      <span class="info-value">{{ item.user ?? 'Не указан' }}</span>
    </div>
    <div class="info-row">
      <span class="info-label">Жанр</span>
      <span class="info-value">{{ item.genre_name ?? 'Не указан' }}</span>
    </div>

        <!-- торги -->
    <h6 class="section-title mt-4">Торги</h6>
    <template v-if="hasAuction">
      <div class="info-row">
        <span class="info-label">Начало</span>
        <span class="info-value">{{ fmtDate(auction.start_time) }}</span>
      </div>

      <div class="info-row">
        <span class="info-label">Окончание</span>
        <span class="info-value">{{ fmtDate(auction.end_time) }}</span>
      </div>

      <div class="timer-box" :class="`timer-${status}`">
        <div class="timer-label">{{ timerLabel }}</div>
        <div class="timer-value">{{ timerText }}</div>
      </div>

      <div class="rate-current">
        <span>
          <h6 class="section-title mt-4">
            {{ status === 'finished' ? 'Продана за' : (ratesCount > 0 ? 'Текущая ставка' : 'Начальная ставка') }}
          </h6>
        </span>

        <span class="rate-price">
          {{ fmtPrice(status === 'finished' && auction.final_price ? auction.final_price : currentPrice) }}
        </span>
      </div>

      <form v-if="status === 'active' && !isOwner" class="rate-row" @submit.prevent="sendRate">
        <input
          v-model="rate"
          type="number"
          class="form-control rate-input"
          :placeholder="`Ваша ставка, больше ${currentPrice} ₽`"
        >

        <button type="submit" class="rate-btn" :disabled="!canRate">
          <i class="bi bi-send-fill"></i>
        </button>
      </form>

      <div v-else-if="status === 'soon'" class="text-secondary small mt-2">
        Ставки откроются, когда начнутся торги
      </div>
    </template>

    <div v-else class="text-secondary small mt-2">
      Для этой картины аукцион ещё не создан.
    </div>
    <h6 class="section-title mt-4">
        Количество ставок: 
        <span style="color: red;">{{ ratesCount }}</span>
      </h6>
      <h6 class="section-title mt-4">
        История ставок
      </h6>

      <ul v-if="sortedRates.length" class="rates-list">
        <li v-for="r in sortedRates" :key="r.id" class="rates-item">
          <div class="rates-main">
            <div class="rates-date">{{ fmtDate(r.add_at) }}</div>
          </div>

          <div class="rates-price">{{ fmtPrice(r.price) }}</div>
        </li>
      </ul>

      <div v-else class="text-secondary small">Ставок пока нет</div>
  </div>
</template>

<style scoped>
.auction-panel {
  padding: 16px;
  background: #fff;
}
.section-title { color: #888; margin-bottom: 10px; }

.info-row {
  display: flex; justify-content: space-between; gap: 12px;
  padding: 9px 14px; margin-bottom: 8px;
  border: 1px solid #ccc; border-radius: 14px;
}
.info-label { color: #777; font-size: .9rem; }
.info-value { font-weight: 600; text-align: right; word-break: break-word; }

.timer-box {
  margin: 14px 0; padding: 12px; text-align: center;
  border-radius: 14px; background: #fdecea;
}
.timer-label { font-size: .85rem; color: #777; }
.timer-value { font-size: 1.6rem; font-weight: 700; color: #e53935; font-variant-numeric: tabular-nums; }
.timer-soon     { background: #fff6e0; }
.timer-soon .timer-value { color: #c77700; }
.timer-finished { background: #eee; }
.timer-finished .timer-value { color: #777; }

.rate-current { display: flex; justify-content: space-between; align-items: baseline; }
.rate-price { font-size: 1.3rem; font-weight: 700; color: #e53935; }

.rate-row { display: flex; gap: 10px; align-items: center; margin-top: 12px; }
.rate-input { border-radius: 14px; }
.rate-btn {
  flex: none; width: 44px; height: 44px; border: 0; border-radius: 50%;
  background: #e53935; color: #fff;
}
.rate-btn:disabled { opacity: .5; }
.rates-badge {
  display: inline-block; min-width: 22px; padding: 1px 8px; margin-left: 6px;
  border-radius: 11px; background: #eee; color: #555;
  font-size: .8rem; font-weight: 600; text-align: center;
}
.rate-winner {
  display: block;
  width: 100%;
  text-align: center;
  color: #dc3545;
  font-weight: bold;
  font-size: 18px;
}
</style>