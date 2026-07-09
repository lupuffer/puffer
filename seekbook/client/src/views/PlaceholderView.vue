<template>
  <section class="placeholder-card">
    <h1>{{ title }}</h1>
    <p>{{ description }}</p>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const props = defineProps({
  data: { type: Object, default: () => ({}) },
})

const pageKey = computed(() => route.meta.pageKey || '')
const fallbackTitles = {
  smartList: '智慧清单',
  publishSell: '发布卖书',
}
const title = computed(() => props.data.site?.pageTitles?.[pageKey.value] || fallbackTitles[pageKey.value] || '')
const description = computed(() => {
  if (pageKey.value === 'smartList') return '这里将承接教材规划、心愿书单和学习资料提醒等功能。'
  return props.data.site?.slogan || ''
})
</script>

<style scoped>
.placeholder-card {
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: var(--shadow-md);
}

.placeholder-card h1 {
  font-size: 24px;
  color: var(--gray-900);
  margin-bottom: 12px;
}

.placeholder-card p {
  font-size: 15px;
  color: var(--gray-600);
}
</style>
