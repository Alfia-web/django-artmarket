<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps({
  item: { type: Object, required: true }})
const emit = defineEmits(['bid'])

const demo = {
  start_price: 1,
  current_bid: 1500,
  final_price: null,
  start_at: '2026-10-20T07:20',
  end_at: '2026-12-29T07:20',
}
const auction = computed(() => props.item.auction ?? demo)

const now = ref(Date.now())
let timer = null
onMounted(() => { timer = setInterval(() => (now.value = Date.now()), 1000) })
onBeforeUnmount(() => clearInterval(timer))

const startMs = computed(() => new Date(auction.value.start_at).getTime())
const endMs = computed(() => new Date(auction.value.end_at).getTime())

const status = computed(() => {
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
const fmtPrice = (v) => `${Number(v).toFixed(2)} ₽`

const currentPrice = computed(() => auction.value.current_bid ?? auction.value.start_price)

// ставка
const bid = ref('')
const canBid = computed(() => Number(bid.value) > currentPrice.value)

function sendBid() {
  if (!canBid.value) return
  emit('bid', { id: props.item.id, amount: Number(bid.value) })
  bid.value = ''
}
</script>

<template>
  <div class="auction-panel">
    <!-- О картине -->
    <h6 class="section-title">О картине</h6>
    <div class="info-row">
      <span class="info-label">Название</span>
      <span class="info-value">{{ item.name }}</span>
    </div>
    <div class="info-row">
      <span class="info-label">Продавец</span>
      <span class="info-value">{{ item.user_name ?? 'Не указан' }}</span>
    </div>
    <div class="info-row">
      <span class="info-label">Жанр</span>
      <span class="info-value">{{ item.genre_name ?? 'Не указан' }}</span>
    </div>

    <!-- Торги -->
    <h6 class="section-title mt-4">Торги</h6>
    <div class="info-row">
      <span class="info-label">Начало</span>
      <span class="info-value">{{ fmtDate(auction.start_at) }}</span>
    </div>
    <div class="info-row">
      <span class="info-label">Окончание</span>
      <span class="info-value">{{ fmtDate(auction.end_at) }}</span>
    </div>

    <div class="timer-box" :class="`timer-${status}`">
      <div class="timer-label">{{ timerLabel }}</div>
      <div class="timer-value">{{ timerText }}</div>
    </div>

    <div class="bid-current">
      <span class="info-label">
        {{ status === 'finished' ? 'Продана за' : (auction.current_bid ? 'Текущая ставка' : 'Начальная ставка') }}
      </span>
      <span class="bid-price">
        {{ fmtPrice(status === 'finished' && auction.final_price ? auction.final_price : currentPrice) }}
      </span>
    </div>

    <form v-if="status === 'active'" class="bid-row" @submit.prevent="sendBid">
      <input v-model="bid" type="number" :min="currentPrice + 1" step="1"
             class="form-control bid-input" :placeholder="`Ваша ставка, больше ${currentPrice} ₽`">
      <button type="submit" class="bid-btn" :disabled="!canBid" aria-label="Сделать ставку">
        <i class="bi bi-send-fill"></i>
      </button>
    </form>
    <div v-else-if="status === 'soon'" class="text-secondary small mt-2">
      Ставки откроются, когда начнутся торги
    </div>
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

.bid-current { display: flex; justify-content: space-between; align-items: baseline; }
.bid-price { font-size: 1.3rem; font-weight: 700; color: #e53935; }

.bid-row { display: flex; gap: 10px; align-items: center; margin-top: 12px; }
.bid-input { border-radius: 14px; }
.bid-btn {
  flex: none; width: 44px; height: 44px; border: 0; border-radius: 50%;
  background: #e53935; color: #fff;
}
.bid-btn:disabled { opacity: .5; }
</style>