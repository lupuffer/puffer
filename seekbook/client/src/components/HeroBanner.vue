<template>
  <section class="hero-section">
    <h1><i class="fas fa-book-open"></i> {{ heroTitle }}</h1>
    <p>{{ heroSubtitle }}</p>
    <form class="hero-search" @submit.prevent="submitSearch">
      <input v-model="keyword" type="text" :placeholder="searchPlaceholder" />
      <button class="btn" type="submit">
        <i class="fas fa-search"></i> {{ searchButton }}
      </button>
    </form>
  </section>
</template>

<script setup>
import { computed, inject, ref } from 'vue'

const props = defineProps({
  hero: { type: Object, default: null },
})

const emit = defineEmits(['search'])
const appData = inject('appData', { value: {} })
const keyword = ref('')

const heroData = computed(() => props.hero ?? appData.value?.home?.hero ?? {})
const heroTitle = computed(() => heroData.value.title || '')
const heroSubtitle = computed(() => heroData.value.subtitle || '')
const searchPlaceholder = computed(() => heroData.value.searchPlaceholder || '')
const searchButton = computed(() => heroData.value.searchButton || '')

const submitSearch = () => {
  emit('search', keyword.value.trim())
}
</script>

<style scoped>
.hero-section {
  background: linear-gradient(135deg, var(--primary-blue) 0%, #3b82f6 100%);
  color: white;
  padding: 60px 40px;
  border-radius: 16px;
  margin-bottom: 32px;
  text-align: center;
}

.hero-section h1 {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 16px;
}

.hero-section p {
  font-size: 18px;
  opacity: 0.9;
  margin-bottom: 32px;
}

.hero-search {
  max-width: 600px;
  margin: 0 auto;
  display: flex;
  gap: 12px;
}

.hero-search input {
  flex: 1;
  padding: 16px 20px;
  border: none;
  border-radius: 12px;
  font-size: 16px;
}

.hero-search .btn {
  padding: 16px 32px;
  background: var(--gray-900);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.hero-search .btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

@media (max-width: 768px) {
  .hero-section h1 {
    font-size: 28px;
  }

  .hero-search {
    flex-direction: column;
  }
}
</style>
