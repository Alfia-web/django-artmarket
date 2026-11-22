    
<script setup>
import { ref, onMounted } from 'vue'
import axios  from 'axios'

const raiting = ref([])

async function fetchRaiting() {
  const response = await axios.get('/api/auctions/raiting/')
  raiting.value = response.data
}

onMounted(()=>{
  fetchRaiting()
})

const fmtPrice = (v) => `${Number(v)} ₽`

async function exportExele() {
  const response = await axios.get(`/api/auctions/raiting/export/excel/`, {
    responseType: 'blob'
  })
  const blob = new Blob([response.data])
  const link = document.createElement('a')
  const url = window.URL.createObjectURL(blob)

  link.href = url
  link.download = 'raiting.xlsx'

  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}
</script>

<template>
  <div class="container mt-4">
    <h6 class="section-title mt-4">
      Рейтинг покупателей
    </h6>

    <div class="d-flex justify-content-center gap-3 mb-3" >
      <button class="btn btn-outline-success" @click="exportExele()">
        Скачать Excel
      </button>
      <button class="btn btn-outline-primary">
        Скачать Word
      </button>
    </div>

    <table v-if="raiting.length" class="rating-table">
      <thead>
        <tr>
          <th>Место</th>
          <th>Пользователь</th>
          <th>Выигрышей</th>
          <th class="text-end">Общая сумма покупок</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(user, index) in raiting" :key="user.user_id">
          <td>{{ index + 1 }}</td>
          <td class="rating-username">{{ user.username }}</td>
          <td>{{ user.auctions_won }}</td>
          <td class="text-end rates-price">{{ fmtPrice(user.total_spent) }}</td>
        </tr>
      </tbody>
    </table>

    <div v-else class="text-secondary small">
      Рейтинг пока пуст
    </div>
  </div>
</template>

<style lang="scss" scoped>
.rating-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0 8px;         

  th {
    padding: 10px 14px;
    font-weight: 700;
  }

  td {
    padding: 10px 14px;
    background: #fff;
    border-top: 1px solid #ddd;
    border-bottom: 1px solid #ddd;
  }
  td:first-child {
    border-left: 1px solid #ddd;
    border-radius: 14px 0 0 14px;
    width: 80px;
  }
  td:last-child {
    border-right: 1px solid #ddd;
    border-radius: 0 14px 14px 0;
  }
}
</style>